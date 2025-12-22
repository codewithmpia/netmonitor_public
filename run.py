#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démarrage pour NetMonitor (serveur + application web)
"""

import threading
import signal
import os
import sys

from web.settings import app, DATA_DIR
from server import NetMonitorServer

# Configuration
HOST = '0.0.0.0'
SERVER_PORT = 9000
WEB_PORT = 5000
DATA_DIR = DATA_DIR
DEBUG = True

# Instance du serveur
server = None

def run_server():
    """Fonction exécutée dans un thread pour démarrer le serveur NetMonitor"""
    global server
    server = NetMonitorServer(
        host=HOST, 
        port=SERVER_PORT, 
        data_dir=DATA_DIR,
        debug=DEBUG
    )
    server.run()

def handle_exit():
    """Gère la fermeture propre des deux applications lors d'une interruption"""
    print("\nArrêt en cours...")
    
    # Arrêt du serveur NetMonitor
    if server:
        server.stop()
    
    # Sortie du programme
    sys.exit(0)

if __name__ == "__main__":
    # Configuration du gestionnaire de signal pour CTRL+C
    signal.signal(signal.SIGINT, handle_exit)
    
    # S'assurer que le répertoire de données existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Démarrage du serveur dans un thread séparé
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
    server_thread.start()
    
    print(f"Serveur NetMonitor démarré sur {HOST}:{SERVER_PORT}")
    print(f"Application web démarrée sur {HOST}:{WEB_PORT}")
    print("Appuyez sur CTRL+C pour arrêter les deux applications")
    
    # Démarrage de l'application web Flask (dans le thread principal)
    app.run(host=HOST, port=WEB_PORT, debug=DEBUG, use_reloader=True)