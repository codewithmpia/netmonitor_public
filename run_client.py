#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement du client NetMonitor.

Ce script permet de lancer le client NetMonitor avec des options de configuration
pour se connecter à un serveur NetMonitor. Il utilise argparse pour gérer les arguments
de la ligne de commande.

Usage :
    python3 run_client.py --host <adresse_serveur> --port <port_serveur> --interval <intervalle_mise_a_jour>

Exemples :
    python3 run_client.py --host localhost --port 9000

    python3 run_client.py --host 192.168.1.256 --port 5000 --interval 10

Arguments :
    --host      Adresse IP ou nom de domaine du serveur NetMonitor (défaut : localhost)
    --port      Port sur lequel le serveur écoute (défaut : 9000)
    --interval  Intervalle de mise à jour des métriques en secondes (défaut : 5)
"""
import argparse

from client import NetMonitorClient


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='NetMonitor Client')
    parser.add_argument('--host', default='localhost', help='Server host address')
    parser.add_argument('--port', type=int, default=9000, help='Server port')
    parser.add_argument('--interval', type=int, default=5, help='Interval between metrics updates (seconds)')
    
    args = parser.parse_args()
    
    client = NetMonitorClient(args.host, args.port, args.interval)
    
    client.start_monitoring()


if __name__ == "__main__":
    main()