"""
connection.py

Gère la communication réseau entre le client et le serveur NetMonitor.
"""
import socket
import time
import json
import logging

logger = logging.getLogger('client.connection')


class ServerConnection:
    """Gère la connexion et les communications avec le serveur NetMonitor"""
    
    def __init__(self, server_host, server_port, buffer_size=4096):
        """
        Initialise la connexion au serveur
        Args:
            server_host (str): Adresse du serveur
            server_port (int): Port du serveur
            buffer_size (int): Taille du buffer pour les communications
        """
        self.server_host = server_host
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.socket = None
        self.client_id = None
    
    def connect(self, registration_data):
        """
        Établit la connexion avec le serveur et enregistre le client
        Args:
            registration_data (dict): Données d'enregistrement à envoyer
        Returns:
            str: ID du client attribué par le serveur, ou None en cas d'échec
        """
        try:
            # Création d'un socket TCP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            logger.info(f"Connected to server {self.server_host}:{self.server_port}")
            
            # Envoi des informations de base pour l'identification
            self.send_data(json.dumps({
                "type": "registration",
                "data": registration_data
            }))
            
            # Attente de la réponse du serveur avec l'ID attribué
            response = self.receive_data()
            if not response:
                return None
                
            response_data = json.loads(response)
            
            if "client_id" in response_data:
                self.client_id = response_data["client_id"]
                logger.info(f"Registered with server - assigned ID: {self.client_id}")
                return self.client_id
            else:
                logger.error("Failed to register with server - no client ID received")
                return None
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            self.close()
            return None
    
    def send_data(self, data):
        """
        Envoie des données au serveur avec gestion des limites de buffer
        Cette méthode gère la fragmentation des données si nécessaire
        Args:
            data (str): Données à envoyer (chaîne JSON) 
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        if not self.socket:
            return False
        
        try:
            # Ajout d'un marqueur de fin pour la reconstitution côté serveur
            data_with_marker = data + "\n#END#\n"
            data_bytes = data_with_marker.encode('utf-8')
            
            # Si les données sont plus grandes que la taille du buffer,
            # on les envoie en plusieurs fragments
            total_sent = 0
            data_length = len(data_bytes)
            
            while total_sent < data_length:
                # Envoi d'un fragment de données
                fragment = data_bytes[total_sent:total_sent + self.buffer_size]
                sent = self.socket.send(fragment)
                
                if sent == 0:
                    logger.error("Socket connection broken")
                    self.close()
                    return False
                
                total_sent += sent
                
                # Petit délai pour éviter la congestion
                if total_sent < data_length:
                    time.sleep(0.01)
            
            logger.debug(f"Sent {total_sent} bytes of data to server")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            self.close()
            return False
    
    def receive_data(self):
        """
        Reçoit des données du serveur avec gestion des limites de buffer
        Cette méthode gère la réception de données potentiellement fragmentées
        Returns:
            str: Données reçues, ou None en cas d'erreur
        """
        if not self.socket:
            return None
            
        try:
            received_data = ""
            end_marker = "\n#END#\n"
            
            while end_marker not in received_data:
                chunk = self.socket.recv(self.buffer_size).decode('utf-8')
                
                if not chunk:
                    logger.error("Socket connection broken during receive")
                    self.close()
                    return None
                    
                received_data += chunk
                
                # Si on a reçu une grande quantité de données mais pas de marqueur,
                # on attend un peu pour laisser le temps au reste d'arriver
                if len(received_data) > self.buffer_size and end_marker not in received_data:
                    time.sleep(0.1)
            
            # On supprime le marqueur de fin
            received_data = received_data.replace(end_marker, "")
            return received_data
            
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
            self.close()
            return None
    
    def close(self):
        """Ferme la connexion au serveur"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
    def is_connected(self):
        """Vérifie si la connexion est établie"""
        return self.socket is not None and self.client_id is not None