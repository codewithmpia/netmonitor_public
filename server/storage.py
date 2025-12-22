"""
storage.py

Ce module gère le stockage des métriques sur le serveur.
"""
import os
import json

from .utils import ensure_dir, format_timestamp


class StorageManager:
    """Gère le stockage des métriques"""
    
    def __init__(self, data_dir, logger):
        """
        Initialise le gestionnaire de stockage
        Args:
            data_dir (str): Répertoire de base pour le stockage
            logger: Logger pour les messages
        """
        self.data_dir = data_dir
        self.files_dir = os.path.join(data_dir, 'files')
        self.metrics_dir = os.path.join(data_dir, 'metrics')
        self.logger = logger
        
        # Création des répertoires de base
        ensure_dir(self.data_dir)
        ensure_dir(self.files_dir)  # Conservé pour l'interface web
        ensure_dir(self.metrics_dir)
    
    def store_metrics(self, hostname, metrics, store_history=True):
        """
        Stocke les métriques d'un client
        Args:
            hostname (str): Nom d'hôte du client
            metrics (dict): Métriques à stocker
            store_history (bool): Si True, stocke aussi les métriques dans l'historique
        """
        # Répertoire pour ce client
        client_dir = os.path.join(self.metrics_dir, hostname)
        ensure_dir(client_dir)
        
        # Stockage des dernières métriques
        latest_path = os.path.join(client_dir, "latest.json")
        with open(latest_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Stockage dans l'historique si demandé
        if store_history:
            timestamp = format_timestamp()
            history_path = os.path.join(client_dir, f"metrics-{timestamp}.json")
            
            with open(history_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
        self.logger.debug(f"Metrics stored for client {hostname}")