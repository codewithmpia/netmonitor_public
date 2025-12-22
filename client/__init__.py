"""
__init__.py

NetMonitorClient est un client pour le serveur NetMonitor. 
Il permet de surveiller les métriques système et de les envoyer au serveur.

Il utilise la bibliothèque psutil pour collecter des informations sur le 
système et le module socket pour la communication réseau.
"""
from .client import NetMonitorClient

__all__ = ["NetMonitorClient"]

__version__ = "1.0.0"
__author__ = "Mpia Mimpiya PULUDISU"
__email__ = "mpia-mimpiya.puludisu02@etud.univ-paris8.fr"