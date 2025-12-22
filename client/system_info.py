"""
system_info.py

Module de collecte d'informations système pour NetMonitor
"""
import psutil
import json
import socket
import platform
import logging
from datetime import datetime

# Utilisation d'un logger spécifique pour ce module
logger = logging.getLogger('client.metrics')


class SystemMonitor:
    """Classe pour collecter et formater les informations système"""
    
    def __init__(self):
        """Initialisation du moniteur système"""
        self.hostname = socket.gethostname()
        logger.info(f"Hostname détecté: {self.hostname}")
        
        # Récupération de l'adresse IP de manière robuste
        self.ip_address = self._get_ip_address()
        
        # Récupération des informations sur la plateforme
        self.platform, self.platform_version = self._get_platform_info()
        
        logger.info(f"SystemMonitor initialized for {self.hostname} ({self.ip_address})")
    
    def _get_ip_address(self):
        """Récupère l'adresse IP de la machine de manière robuste"""
        try:
            # Méthode standard
            ip_address = socket.gethostbyname(self.hostname)
            logger.info(f"IP obtenue par hostname: {ip_address}")
            return ip_address

        except socket.gaierror as e:
            logger.warning(f"Impossible de résoudre le hostname: {e}")
            # Méthode alternative en cas d'échec de la résolution du nom d'hôte
            try:
                # Création d'une connexion socket pour déterminer l'interface réseau utilisée
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Ne se connecte pas réellement à Google (juste pour déterminer l'interface)
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
                s.close()
                logger.info(f"IP obtenue via connexion socket: {ip_address}")
                return ip_address

            except Exception as e:
                # Fallback sur localhost en dernier recours
                logger.warning(f"Could not determine IP address, using localhost: {e}")
                return "127.0.0.1"
    
    def _get_platform_info(self):
        """Récupère les informations sur la plateforme"""
        try:
            platform_name = platform.system()
            platform_version = platform.version()
            
            logger.info(f"Plateforme détectée: {platform_name}")
            logger.info(f"Version de la plateforme: {platform_version}")
            logger.debug(f"Python version: {platform.python_version()}")
            logger.debug(f"Machine: {platform.machine()}")
            logger.debug(f"Processor: {platform.processor()}")

            return platform_name, platform_version

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations de plateforme: {e}")
            return "Unknown", "Unknown"
    
    def get_basic_info(self):
        """Renvoie les informations de base sur la machine"""
        return {
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_cpu_info(self):
        """Collecte des informations sur l'utilisation du CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_percent_avg": sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0,
                "cpu_freq_current": cpu_freq.current if cpu_freq else None,
                "cpu_freq_max": cpu_freq.max if cpu_freq else None,
                "cpu_count_logical": cpu_count,
                "cpu_count_physical": psutil.cpu_count(logical=False)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des informations CPU: {e}")
            return {
                "cpu_percent": [],
                "cpu_percent_avg": 0,
                "error": str(e)
            }
    
    def get_memory_info(self):
        """Collecte des informations sur l'utilisation de la mémoire"""
        try:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                "virtual_memory": {
                    "total": virtual_memory.total,
                    "available": virtual_memory.available,
                    "used": virtual_memory.used,
                    "percent": virtual_memory.percent
                },
                "swap_memory": {
                    "total": swap_memory.total,
                    "used": swap_memory.used,
                    "free": swap_memory.free,
                    "percent": swap_memory.percent
                }
            }
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des informations mémoire: {e}")
            return {
                "virtual_memory": {"percent": 0},
                "swap_memory": {"percent": 0},
                "error": str(e)
            }
    
    def get_disk_info(self):
        """Collecte des informations sur l'utilisation du disque"""
        try:
            disk_partitions = psutil.disk_partitions()
            disk_info = []
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    })
                    
                except (PermissionError, FileNotFoundError):
                    # Certains points de montage peuvent ne pas être accessibles
                    continue
            
            return {"partitions": disk_info}
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des informations disque: {e}")
            return {"partitions": [], "error": str(e)}
    
    def get_network_info(self):
        """Collecte des informations sur le trafic réseau"""
        try:
            net_io_counters = psutil.net_io_counters(pernic=True)
            network_info = {}
            
            for interface, stats in net_io_counters.items():
                network_info[interface] = {
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errin": stats.errin,
                    "errout": stats.errout,
                    "dropin": stats.dropin,
                    "dropout": stats.dropout
                }
            
            return network_info
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des informations réseau: {e}")
            return {"error": str(e)}
    
    def get_all_metrics(self):
        """Collecte toutes les métriques système"""
        all_metrics = {
            **self.get_basic_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info()
        }
        return all_metrics
    
    def get_metrics_json(self, optimize=False):
        """
        Renvoie les métriques au format JSON
        
        Args:
            optimize (bool): Si True, renvoie un ensemble réduit de métriques
                            pour éviter la fragmentation des paquets
        """
        metrics = self.get_all_metrics()
        
        if optimize:
            # Réduction des métriques pour éviter la fragmentation des paquets
            # mais en incluant les informations essentielles pour le tableau de bord
            optimized = {
                "hostname": metrics["hostname"],
                "ip_address": metrics["ip_address"],
                "platform": metrics["platform"],
                "platform_version": metrics["platform_version"],
                "timestamp": metrics["timestamp"],
                "cpu_percent": metrics["cpu"]["cpu_percent_avg"],
                "memory_percent": metrics["memory"]["virtual_memory"]["percent"],
                "disk_percent": self._calculate_avg_disk_percent(metrics["disk"]["partitions"])
            }
            return json.dumps(optimized)
        
        return json.dumps(metrics)
    
    def _calculate_avg_disk_percent(self, partitions):
        """Calcule le pourcentage d'utilisation moyen des disques"""
        if not partitions:
            return 0
        return sum(p["percent"] for p in partitions) / len(partitions)