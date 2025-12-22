"""
utils.py

Ce module contient des fonctions utilitaires pour l'application Flask.
"""

import math

def make_json_serializable(obj):
    """
    Convertit les objets non sérialisables en JSON en versions sérialisables 
    Args:
        obj: Objet à convertir     
    Returns:
        Object: Version sérialisable de l'objet
    """
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, range):
        return list(obj)
    elif hasattr(obj, '__dict__'):  # Pour les objets personnalisés
        return make_json_serializable(obj.__dict__)
    else:
        return obj
    

def prepare_chart_data(metrics):
    """
    Prépare les données pour Chart.js
    Args:
        metrics (dict): Données des métriques du client     
    Returns:
        dict: Données formatées pour Chart.js
    """
    # Vérifier que metrics est bien un dictionnaire
    if not isinstance(metrics, dict):
        return {}
            
    chart_data = {}
        
    # Données CPU
    if 'cpu' in metrics and isinstance(metrics['cpu'], dict) and 'cpu_percent' in metrics['cpu']:
        cpu_data = {
            'labels': [f'CPU {i}' for i in range(len(metrics['cpu']['cpu_percent']))],
            'datasets': [{
                'label': 'Utilisation CPU (%)',
                'data': metrics['cpu']['cpu_percent'],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(255, 205, 86, 0.5)',
                ] * 10,  # Répète les couleurs si besoin
                'borderColor': [
                    'rgb(54, 162, 235)',
                    'rgb(75, 192, 192)',
                    'rgb(255, 159, 64)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 99, 132)',
                    'rgb(255, 205, 86)',
                ] * 10,
                'borderWidth': 1
            }]
        }
        chart_data['cpu'] = cpu_data
        
    # Données mémoire
    if 'memory' in metrics and isinstance(metrics['memory'], dict) and 'virtual_memory' in metrics['memory']:
        vm = metrics['memory']['virtual_memory']
        if isinstance(vm, dict):
            used = vm.get('used', 0)
            available = vm.get('available', 0)
                
            # Si 'available' n'est pas disponible, essayer de le calculer
            if available == 0 and 'total' in vm:
                available = vm['total'] - used
                
            memory_data = {
                'labels': ['Utilisée', 'Disponible'],
                'datasets': [{
                    'label': 'Mémoire (octets)',
                    'data': [used, available],
                    'backgroundColor': [
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                    ],
                    'borderColor': [
                        'rgb(54, 162, 235)',
                        'rgb(75, 192, 192)',
                    ],
                    'borderWidth': 1
                }]
            }
            chart_data['memory'] = memory_data
        
    # Données disque
    if 'disk' in metrics and isinstance(metrics['disk'], dict) and 'partitions' in metrics['disk']:
        partitions = metrics['disk']['partitions']
        if isinstance(partitions, list) and partitions:
            disk_labels = []
            disk_used = []
            disk_free = []
                
            for disk in partitions:
                if not isinstance(disk, dict):
                    continue
                        
                # Ignore les partitions système peu importantes sous macOS
                mountpoint = disk.get('mountpoint', '')
                if mountpoint.startswith('/System/Volumes') and mountpoint not in ['/', '/System/Volumes/Data']:
                    continue
                    
                # Pour des noms plus courts
                if mountpoint.startswith('/System/Volumes/'):
                    display_name = mountpoint.replace('/System/Volumes/', '')
                else:
                    display_name = mountpoint
                    
                disk_labels.append(display_name)
                disk_used.append(disk.get('used', 0))
                total = disk.get('total', 0)
                disk_free.append(total - disk.get('used', 0) if total >= disk.get('used', 0) else 0)
                
            # Si trop de disques, limiter aux 8 plus grands
            if len(disk_labels) > 8:
                # Trier par utilisation totale décroissante
                disk_data = sorted(zip(disk_labels, disk_used, disk_free), 
                                    key=lambda x: x[1] + x[2], reverse=True)
                # Prendre les 8 premiers
                disk_data = disk_data[:8]
                # Désemballer
                disk_labels, disk_used, disk_free = zip(*disk_data)
                
            disk_data = {
                'labels': disk_labels,
                'datasets': [
                    {
                        'label': 'Utilisé',
                        'data': disk_used,
                        'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                        'borderColor': 'rgb(255, 99, 132)',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Libre',
                        'data': disk_free,
                        'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                        'borderColor': 'rgb(75, 192, 192)',
                        'borderWidth': 1
                    }
                ]
            }
            chart_data['disk'] = disk_data
        
    # Données réseau
    if 'network' in metrics and isinstance(metrics['network'], dict):
        network = metrics['network']
        # Filtrer les interfaces avec du trafic
        active_interfaces = {}

        for name, interface in network.items():
            if not isinstance(interface, dict):
                continue
            if interface.get('bytes_sent', 0) > 0 or interface.get('bytes_recv', 0) > 0:
                active_interfaces[name] = interface
            
        # Si trop d'interfaces, garder seulement les plus actives
        if len(active_interfaces) > 8:
            # Trier par trafic total décroissant
            sorted_interfaces = sorted(
                active_interfaces.items(),
                key=lambda x: x[1].get('bytes_sent', 0) + x[1].get('bytes_recv', 0),
                reverse=True
            )
            # Prendre les 8 premières
            active_interfaces = dict(sorted_interfaces[:8])
            
        if active_interfaces:
            net_labels = list(active_interfaces.keys())
            net_sent = [active_interfaces[name].get('bytes_sent', 0) for name in net_labels]
            net_recv = [active_interfaces[name].get('bytes_recv', 0) for name in net_labels]
                
            network_data = {
                'labels': net_labels,
                'datasets': [
                    {
                        'label': 'Envoyé (octets)',
                        'data': net_sent,
                        'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                        'borderColor': 'rgb(54, 162, 235)',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Reçu (octets)',
                        'data': net_recv,
                        'backgroundColor': 'rgba(255, 159, 64, 0.5)',
                        'borderColor': 'rgb(255, 159, 64)',
                        'borderWidth': 1
                    }
                ]
            }
            chart_data['network'] = network_data
        
    return chart_data



def paginate_history_files(files, page, per_page):
    """
    Pagine les fichiers historiques.
    Args:
        files (list): Liste complète des fichiers historiques
        page (int): Numéro de page actuel
        per_page (int): Nombre d'éléments par page 
    Returns:
        tuple: (Liste paginée, informations de pagination)
    """
    # Nombre total d'éléments
    total = len(files)
        
    # Nombre total de pages
    pages = math.ceil(total / per_page) if total > 0 else 1
        
    # Ajuster la page si elle est hors limites
    if page < 1:
        page = 1
    elif page > pages:
        page = pages
        
    # Calculer les indices de début et de fin
    start = (page - 1) * per_page
    end = min(start + per_page, total)
        
    # Extraire la tranche
    paginated_files = files[start:end]
        
    # Calculer l'index du premier et du dernier élément affichés
    first_item = start + 1 if total > 0 else 0
    last_item = end
        
    # Créer les informations de pagination
    pagination = {
        'has_prev': page > 1,
        'has_next': page < pages,
        'page': page,
        'pages': pages,
        'total': total,
        'per_page': per_page,
        'first_item': first_item,
        'last_item': last_item,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < pages else None,
        'page_range': list(range(max(1, page - 2), min(pages + 1, page + 3)))  # Convertir en liste
    }
        
    return paginated_files, pagination



