"""
server.py

Ce module gère le serveur NetMonitor, qui reçoit et stocke les métriques système.
Il utilise des sockets pour la communication réseau et gère plusieurs clients simultanément.
Il utilise le module select pour gérer les connexions non-bloquantes.
Il utilise également des gestionnaires pour les clients, le stockage et le traitement des messages.
"""
import socket
import select

from .utils import setup_logger
from .client import ClientManager
from .storage import StorageManager
from .handlers import MessageHandler


class NetMonitorServer:
    """Serveur pour la réception et le stockage des métriques système"""
    
    def __init__(self, host='0.0.0.0', port=9000, data_dir='./data', debug=False):
        """
        Initialisation du serveur NetMonitor
        Args:
            host (str): Adresse d'écoute du serveur
            port (int): Port d'écoute du serveur
            data_dir (str): Répertoire de stockage des données
            debug (bool): Activer les logs de debug
        """
        self.host = host
        self.port = port
        self.data_dir = data_dir
        self.debug = debug
        
        # Configuration du logger
        self.logger = setup_logger('server', debug)
        
        # Initialisation des composants
        self.client_manager = ClientManager(self.logger)
        self.storage_manager = StorageManager(data_dir, self.logger)
        self.message_handler = MessageHandler(
            self.client_manager, 
            self.storage_manager,
            self.logger
        )
        
        self.server_socket = None
        self.running = False
        self.buffer_size = 4096
        
        self.logger.info(f"Server initialized - will listen on {host}:{port}")
    
    def setup_socket(self):
        """Configure le socket serveur"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.server_socket.setblocking(False)
            self.logger.info(f"Server listening on {self.host}:{self.port}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error setting up server socket: {str(e)}")
            return False
    
    def run(self):
        """Démarre le serveur"""
        if not self.setup_socket():
            return
        
        self.running = True
        self.logger.info("Server started")
        
        try:
            while self.running:
                # Préparation des sockets à surveiller
                read_sockets = [self.server_socket] + self.client_manager.get_all_sockets()
                
                # Attente d'activité
                readable, _, exceptional = select.select(read_sockets, [], read_sockets, 1.0)
                
                for sock in readable:
                    if sock is self.server_socket:
                        # Nouvelle connexion
                        client_socket, client_addr = self.server_socket.accept()
                        client_socket.setblocking(False)
                        self.client_manager.add_client(client_socket, client_addr)
                    else:
                        # Données d'un client existant
                        client_id = self.client_manager.find_client_by_socket(sock)
                        
                        if client_id:
                            try:
                                data = sock.recv(self.buffer_size)
                                if not data:
                                    # Connexion fermée
                                    self.logger.info(f"Client {client_id} disconnected")
                                    self.client_manager.remove_client(client_id)
                                else:
                                    # Traitement des données
                                    self.message_handler.process_data(client_id, data)
                            except Exception as e:
                                self.logger.error(f"Error receiving data from client {client_id}: {str(e)}")
                                self.client_manager.remove_client(client_id)
                
                # Gestion des sockets en erreur
                for sock in exceptional:
                    client_id = self.client_manager.find_client_by_socket(sock)

                    if client_id:
                        self.logger.warning(f"Socket exception for client {client_id}")
                        self.client_manager.remove_client(client_id)
                
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """Arrête le serveur"""
        self.running = False
        
        # Fermeture des connexions clientes
        clients = list(self.client_manager.clients.keys())

        for client_id in clients:
            self.client_manager.remove_client(client_id)
        
        # Fermeture du socket serveur
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("Server stopped")