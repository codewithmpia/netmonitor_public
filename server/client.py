"""
client.py

Ce module gère les clients connectés au serveur.
"""
from .utils import generate_uuid, get_timestamp


class ClientManager:
    """Gère les clients connectés au serveur"""
    
    def __init__(self, logger):
        """
        Initialise le gestionnaire de clients
        Args:
            logger: Logger pour les messages
        """
        self.clients = {}  # {client_id: client_data}
        self.logger = logger
    
    def add_client(self, socket, addr):
        """
        Ajoute un nouveau client
        Args:
            socket: Socket du client
            addr: Adresse du client (ip, port)
        Returns:
            str: ID du client
        """
        client_id = generate_uuid()
        
        self.clients[client_id] = {
            'socket': socket,
            'addr': addr,
            'info': None,
            'buffer': '',
            'connected_at': get_timestamp()
        }
        
        self.logger.info(f"New connection from {addr}, assigned ID: {client_id}")
        return client_id
    
    def get_client(self, client_id):
        """Retourne les données d'un client"""
        return self.clients.get(client_id)
    
    def set_client_info(self, client_id, info):
        """Définit les informations d'un client"""
        if client_id in self.clients:
            self.clients[client_id]['info'] = info
            hostname = info.get('hostname', 'unknown')
            self.logger.info(f"Client {client_id} registered: {hostname}")
    
    def add_to_buffer(self, client_id, data):
        """Ajoute des données au buffer d'un client"""
        if client_id in self.clients:
            self.clients[client_id]['buffer'] += data
    
    def get_buffer(self, client_id):
        """Retourne le buffer d'un client"""
        if client_id in self.clients:
            return self.clients[client_id]['buffer']
        return ''
    
    def set_buffer(self, client_id, data):
        """Définit le buffer d'un client"""
        if client_id in self.clients:
            self.clients[client_id]['buffer'] = data
    
    def remove_client(self, client_id):
        """Supprime un client"""
        if client_id in self.clients:
            client = self.clients[client_id]
            
            # Fermeture du socket
            try:
                client['socket'].close()
            except:
                pass
            
            # Suppression du client
            del self.clients[client_id]
            self.logger.info(f"Client {client_id} disconnected and removed")
    
    def get_all_sockets(self):
        """Retourne tous les sockets clients"""
        return [client['socket'] for client in self.clients.values()]
    
    def find_client_by_socket(self, sock):
        """Trouve l'ID d'un client à partir de son socket"""
        for client_id, client in self.clients.items():
            if client['socket'] == sock:
                return client_id
        return None