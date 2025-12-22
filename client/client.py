"""
client.py

Client NetMonitor - Collecte et envoie des métriques système au serveur
"""
import json
import time

from .system_info import SystemMonitor
from .connection import ServerConnection
from .logging_config import setup_logger

# Configuration du logger
logger = setup_logger()


class NetMonitorClient:
    """Client pour la collecte et l'envoi de métriques système"""
    
    def __init__(self, server_host, server_port, interval=5):
        """
        Initialisation du client NetMonitor
        Args:
            server_host (str): Adresse du serveur
            server_port (int): Port du serveur
            interval (int): Intervalle en secondes entre les envois de métriques
        """
        self.server_host = server_host
        self.server_port = server_port
        self.interval = interval
        self.monitor = SystemMonitor()
        self.connection = ServerConnection(server_host, server_port)
        self.running = False
        logger.info(f"Client initialized - will connect to {server_host}:{server_port}")
    
    def connect(self):
        """Établit la connexion avec le serveur"""
        basic_info = self.monitor.get_basic_info()
        client_id = self.connection.connect(basic_info)
        return client_id is not None
    
    def send_metrics(self, optimize=True):
        """
        Envoie les métriques système au serveur
        Args:
            optimize (bool): Si True, envoie un ensemble réduit de métriques
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        if not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            # Collecte des métriques
            metrics_json = self.monitor.get_metrics_json(optimize=optimize)
            metrics_data = json.loads(metrics_json)
            
            # Vérification des données essentielles
            if not metrics_data.get('hostname'):
                logger.warning("Les métriques ne contiennent pas de hostname")
            if not metrics_data.get('ip_address'):
                logger.warning("Les métriques ne contiennent pas d'adresse IP")
            if not metrics_data.get('platform') and not optimize:
                logger.warning("Les métriques ne contiennent pas de plateforme")
            
            # Construction du message à envoyer
            message = json.dumps({
                "type": "metrics",
                "client_id": self.connection.client_id,
                "data": metrics_data
            })
            
            # Envoi des métriques
            return self.connection.send_data(message)
            
        except Exception as e:
            logger.error(f"Error sending metrics: {str(e)}")
            return False
   
    def start_monitoring(self):
        """Démarre le processus de surveillance et d'envoi périodique des métriques"""
        self.running = True
        
        if not self.connect():
            logger.error("Failed to connect to server, monitoring not started")
            return False
            
        logger.info(f"Starting monitoring - sending metrics every {self.interval} seconds")
        
        try:
            while self.running:
                # Utilisation de optimize=False pour envoyer les métriques complètes
                if self.send_metrics(optimize=False):
                    logger.debug("Metrics sent successfully")
                else:
                    logger.warning("Failed to send metrics, attempting to reconnect...")
                    if not self.connect():
                        time.sleep(10)  # Wait before retry
                        continue
                        
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
            self.stop()
    
    def stop(self):
        """Arrête le client"""
        self.running = False
        
        if self.connection.is_connected():
            try:
                # Envoi d'un message de déconnexion
                self.connection.send_data(json.dumps({
                    "type": "disconnect",
                    "client_id": self.connection.client_id
                }))
            except:
                pass
            
        self.connection.close()
        logger.info("Client stopped")