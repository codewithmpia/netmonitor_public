"""
handlers.py

Ce module gère les messages reçus des clients.
"""
import json
import time


class MessageHandler:
    """Gère les messages reçus des clients"""
    
    def __init__(self, client_manager, storage_manager, logger, buffer_size=4096):
        """
        Initialise le gestionnaire de messages
        Args:
            client_manager: Gestionnaire de clients
            storage_manager: Gestionnaire de stockage
            logger: Logger pour les messages
            buffer_size (int): Taille du buffer pour l'envoi des données
        """
        self.client_manager = client_manager
        self.storage_manager = storage_manager
        self.logger = logger
        self.buffer_size = buffer_size
    
    def process_data(self, client_id, data):
        """
        Traite les données reçues d'un client
        Args:
            client_id (str): ID du client
            data (bytes): Données reçues
        Returns:
            bool: True si le client est toujours connecté, False sinon
        """
        try:
            # Décodage des données
            decoded_data = data.decode('utf-8')
            
            # Ajout au buffer du client
            client = self.client_manager.get_client(client_id)
            if not client:
                return False
                
            self.client_manager.add_to_buffer(client_id, decoded_data)
            buffer = self.client_manager.get_buffer(client_id)
            
            # Recherche du marqueur de fin
            end_marker = "\n#END#\n"
            
            # Traitement des messages complets
            updated_buffer = buffer
            
            # Traitement des messages normaux
            while end_marker in updated_buffer:
                message, updated_buffer = updated_buffer.split(end_marker, 1)
                self.handle_message(client_id, message)
            
            # Mise à jour du buffer
            self.client_manager.set_buffer(client_id, updated_buffer)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing data from client {client_id}: {str(e)}")
            self.client_manager.remove_client(client_id)
            return False
    
    def handle_message(self, client_id, message):
        """
        Traite un message complet
        Args:
            client_id (str): ID du client
            message (str): Message à traiter
        """
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'registration':
                # Enregistrement d'un client
                client_info = data.get('data')
                self.client_manager.set_client_info(client_id, client_info)
                
                # Envoi de l'ID au client
                self.send_message(client_id, {
                    'status': 'registered',
                    'client_id': client_id
                })
                
            elif message_type == 'metrics':
                # Réception de métriques
                metrics_data = data.get('data')
                client = self.client_manager.get_client(client_id)
                if client and client['info']:
                    hostname = client['info'].get('hostname', 'unknown')
                    self.storage_manager.store_metrics(hostname, metrics_data)
                
            elif message_type == 'disconnect':
                # Déconnexion d'un client
                self.logger.info(f"Client {client_id} requested disconnection")
                self.client_manager.remove_client(client_id)
                
            else:
                self.logger.warning(f"Unknown message type from client {client_id}: {message_type}")
                
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON received from client {client_id}")
        except Exception as e:
            self.logger.error(f"Error handling message from client {client_id}: {str(e)}")
    
    def send_message(self, client_id, data):
        """
        Envoie un message à un client
        Args:
            client_id (str): ID du client
            data (dict): Données à envoyer
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        client = self.client_manager.get_client(client_id)
        
        if not client:
            return False
        
        client_socket = client['socket']
        
        try:
            # Conversion en JSON et ajout du marqueur
            json_data = json.dumps(data)
            data_with_marker = json_data + "\n#END#\n"
            data_bytes = data_with_marker.encode('utf-8')
            
            # Envoi des données
            total_sent = 0
            data_length = len(data_bytes)
            
            while total_sent < data_length:
                sent = client_socket.send(data_bytes[total_sent:total_sent + self.buffer_size])
                
                if sent == 0:
                    self.logger.error(f"Socket connection broken for client {client_id}")
                    self.client_manager.remove_client(client_id)
                    return False
                
                total_sent += sent
                
                if total_sent < data_length:
                    time.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending data to client {client_id}: {str(e)}")
            self.client_manager.remove_client(client_id)
            return False