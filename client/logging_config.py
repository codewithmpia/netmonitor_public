"""
logging_config.py

Configuration du logger pour le client NetMonitor.
"""
import logging


def setup_logger(level=logging.INFO):
    """
    Configure le logger pour le client NetMonitor
    Args:
        level: Niveau de logging (par défaut: INFO)
    Returns:
        Logger: Logger principal configuré
    """
    # Configuration de base
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Création et configuration du logger principal
    logger = logging.getLogger('client')
    logger.setLevel(level)
    
    return logger