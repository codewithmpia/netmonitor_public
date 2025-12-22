"""
utils.py

Ce module contient des fonctions utilitaires pour le serveur NetMonitor.
"""
import os
import uuid
import logging
from datetime import datetime


def setup_logger(name, debug=False):
    """Configure et retourne un logger"""
    level = logging.DEBUG if debug else logging.INFO
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Ne pas propager aux loggers parents
    logger.propagate = False
    
    # Retirer les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Créer un handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter simple
    if debug:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def generate_uuid():
    """Génère un identifiant unique"""
    return str(uuid.uuid4())


def get_timestamp():
    """Retourne le timestamp actuel au format ISO"""
    return datetime.now().isoformat()


def format_timestamp(format='%Y%m%d-%H%M%S'):
    """Retourne le timestamp actuel dans le format demandé"""
    return datetime.now().strftime(format)


def ensure_dir(directory):
    """S'assure qu'un répertoire existe"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def sanitize_path(path):
    """Sécurise un chemin de fichier en extrayant juste le nom de base"""
    return os.path.basename(path)