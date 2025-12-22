"""
views.py

Ce module contient les vues de l'application Flask.
"""

import os
from datetime import datetime
import json

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    jsonify,
    current_app
)
from flask.views import MethodView

from .utils import (
    make_json_serializable,
    prepare_chart_data,
    paginate_history_files
)
from .errors import get_forms_errors
from .forms import UploadForm


class IndexView(MethodView):
    template_name = "index.html"

    def get(self):
        return render_template(self.template_name)
    

class DashBoardView(MethodView):
    template_name = "dashboard.html"
    
    def get(self):
        # Récupération du répertoire de données
        data_dir = current_app.config["DATA_DIR"]
        metrics_dir = os.path.join(data_dir, 'metrics')

        # Récupération des clients
        clients = []
        
        # Vérification de l'existence du répertoire
        if not os.path.exists(metrics_dir):
            clients = []
        
        # Parcourir le répertoire des métriques
        for hostname in os.listdir(metrics_dir):
            client_dir = os.path.join(metrics_dir, hostname)
            
            if not os.path.isdir(client_dir):
                continue
            
            # Récupération des dernières métriques
            latest_file = os.path.join(client_dir, 'latest.json')
            
            if not os.path.exists(latest_file):
                continue
            
            try:
                with open(latest_file, 'r') as f:
                    metrics = json.load(f)
                
                # Création d'un objet client avec ses métriques
                client = {
                    'hostname': hostname,
                    'metrics': metrics,
                    'last_update': datetime.fromtimestamp(os.path.getmtime(latest_file)).strftime('%d/%m/%Y %H:%M:%S'),
                    'status': 'Online' if (datetime.now() - datetime.fromtimestamp(os.path.getmtime(latest_file))).total_seconds() < 300 else 'Offline'
                }
                
                # Ajout du client à la liste
                clients.append(client)
                
            except Exception as e:
                print(f"Erreur lors de la lecture des métriques pour {hostname}: {str(e)}")
        
        # Tri des clients par nom d'hôte
        clients.sort(key=lambda x: x['hostname'])

        # Ajouter le support pour le format JSON
        if request.args.get('format') == 'json':
            return jsonify({
                "clients": clients
            })

        ctx = {
            "clients": clients,
        }
        
        return render_template(self.template_name, **ctx)  
    

class ClientMetricsView(MethodView):
    """
    Vue pour afficher les métriques d'un client spécifique.
    Permet de visualiser les métriques actuelles ou historiques.
    """
    template_name = "client_metrics.html"
    
    def get(self, hostname, file=None):
        """
        Affiche les métriques d'un client spécifique ou télécharge le fichier de métriques.
        Supporte également le format JSON pour les requêtes AJAX.
        Args:
            hostname (str): Nom d'hôte du client
            file (str, optional): Nom du fichier de métriques à afficher
        """
        # Vérifier si c'est une demande de téléchargement
        download = request.args.get('download') == 'true'
        
        # Vérifier si c'est une demande de format JSON
        format_json = request.args.get('format') == 'json'
        
        # Récupérer le numéro de page depuis la requête (par défaut: 1)
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            # Si le format est invalide (comme "4?format=json"), extraire la première partie
            page_str = request.args.get('page', '1')
            if '?' in page_str:
                page_str = page_str.split('?')[0]
            page = int(page_str) if page_str.isdigit() else 1
        
        # Nombre d'éléments par page
        per_page = 10
        
        # Initialisation des variables pour éviter les erreurs
        metrics = {}
        chart_data = {}
        history_files = []
        current_file = ""
        current_file_display = "Aucune donnée"
        metrics_file = None
        pagination = {
            'has_prev': False,
            'has_next': False,
            'page': page,
            'pages': 1,
            'total': 0,
            'prev_page': None,
            'next_page': None
        }
        
        try:
            # Récupération du répertoire de données
            data_dir = current_app.config["DATA_DIR"]
            metrics_dir = os.path.join(data_dir, 'metrics')
            
            # Vérification de l'existence du répertoire
            if not os.path.exists(metrics_dir):
                if format_json:
                    return jsonify({
                        "error": "Le répertoire des métriques n'existe pas."
                    }), 404
                flash("Le répertoire des métriques n'existe pas.", "danger")
                return redirect(url_for("dashboard"))
            
            client_dir = os.path.join(metrics_dir, hostname)
            
            # Vérification de l'existence du répertoire du client
            if not os.path.exists(client_dir):
                if format_json:
                    return jsonify({
                        "error": f"Aucun client trouvé avec le nom d'hôte : {hostname}"
                    }), 404
                flash(f"Aucun client trouvé avec le nom d'hôte : {hostname}", "danger")
                return redirect(url_for("dashboard"))
            
            # Déterminer quel fichier de métriques charger
            if file and os.path.exists(os.path.join(client_dir, file)):
                metrics_file = os.path.join(client_dir, file)
            else:
                # Utiliser latest.json ou le fichier le plus récent
                latest_file = os.path.join(client_dir, "latest.json")
                
                if not os.path.exists(latest_file):
                    # Chercher le fichier de métriques le plus récent
                    available_files = [f for f in os.listdir(client_dir) if f.endswith('.json')]
                    
                    if not available_files:
                        ctx = {
                            "hostname": hostname,
                            "metrics": {},
                            "chart_data": {},
                            "history_files": [],
                            "current_file": "",
                            "current_file_display": "Aucune donnée",
                            "pagination": pagination
                        }

                        if format_json:
                            return jsonify(ctx)
                        
                        flash(f"Aucune métrique disponible pour {hostname}", "warning")

                        return render_template(self.template_name, **ctx)
                    
                    # Trier par date de modification (le plus récent en premier)
                    available_files.sort(key=lambda x: os.path.getmtime(os.path.join(client_dir, x)), reverse=True)
                    metrics_file = os.path.join(client_dir, available_files[0])
                else:
                    metrics_file = latest_file
            
            # Si c'est une demande de téléchargement et que nous avons un fichier valide
            if download and metrics_file:
                # Obtenir le nom du fichier à partir du chemin complet
                filename = os.path.basename(metrics_file)
                
                # Renvoyer le fichier en tant que pièce jointe
                return send_file(
                    metrics_file, 
                    mimetype='application/json',
                    as_attachment=True,
                    download_name=filename
                )
            
            # Charger les données du fichier pour l'affichage normal
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                
                # Préparation des données pour Chart.js
                chart_data = prepare_chart_data(metrics)
                
                # Récupérer la liste des fichiers de métriques historiques
                history_files = [f for f in os.listdir(client_dir) if f.endswith('.json') and f != 'latest.json']
                history_files.sort(key=lambda x: os.path.getmtime(os.path.join(client_dir, x)), reverse=True)
                
                # Préparer les informations sur les fichiers historiques
                history_info = []

                for history_file in history_files:
                    file_path = os.path.join(client_dir, history_file)
                    timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Pour les fichiers au format "metrics-YYYYMMDD-HHMMSS.json"
                    display_name = history_file

                    if history_file.startswith('metrics-'):
                        date_str = history_file.replace('metrics-', '').replace('.json', '')

                        try:
                            date_obj = datetime.strptime(date_str, '%Y%m%d-%H%M%S')
                            display_name = date_obj.strftime('%d/%m/%Y %H:%M:%S')

                        except:
                            pass
                    
                    history_info.append({
                        'filename': history_file,
                        'display_name': display_name,
                        'timestamp': timestamp.strftime('%d/%m/%Y %H:%M:%S')
                    })
                
                # Ajouter l'information sur le fichier actuel
                current_file = os.path.basename(metrics_file)
                current_file_display = current_file

                if current_file == 'latest.json':
                    current_file_display = "Dernières métriques"

                elif current_file.startswith('metrics-'):
                    date_str = current_file.replace('metrics-', '').replace('.json', '')
                    try:
                        date_obj = datetime.strptime(date_str, '%Y%m%d-%H%M%S')
                        current_file_display = date_obj.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        pass
                
                # Pagination des fichiers historiques
                history_files, pagination = paginate_history_files(history_info, page, per_page)
                
            except Exception as e:
                error_msg = f"Erreur lors de la lecture du fichier de métriques : {str(e)}"
                if format_json:
                    return jsonify({
                        "error": error_msg,
                        "hostname": hostname,
                        "metrics": {},
                        "chart_data": {},
                        "history_files": [],
                        "current_file": "",
                        "current_file_display": "Erreur",
                        "pagination": pagination
                    }), 500
                flash(error_msg, "danger")
        
        # Garder les variables initiales vides 
        except Exception as e:
            error_msg = f"Erreur lors de l'accès aux métriques : {str(e)}"

            if format_json:
                return jsonify({
                    "error": error_msg,
                    "hostname": hostname,
                    "metrics": {},
                    "chart_data": {},
                    "history_files": [],
                    "current_file": "",
                    "current_file_display": "Erreur",
                    "pagination": pagination
                }), 500
            flash(error_msg, "danger")
        
        # Les variables déjà initialisées seront utilisées
        ctx = {
            "hostname": hostname,
            "metrics": metrics,
            "chart_data": chart_data,
            "history_files": history_files,
            "current_file": current_file,
            "current_file_display": current_file_display,
            "pagination": pagination
        }
        
        # Retourner JSON si demandé
        if format_json:
            # Nous devons nous assurer que tous les objets sont JSON sérialisables
            return jsonify(make_json_serializable(ctx))
        
        # Sinon, retourner le template HTML
        return render_template(self.template_name, **ctx)


class FilesView(MethodView):
    template_name = "files.html"
    form_class = UploadForm

    def get(self):
        form = self.form_class()

        try:
            files = []

            # Parcourir le répertoire de téléchargement
            for root, _, filenames in os.walk(current_app.config["UPLOAD_FOLDER"]):
                for filename in filenames:
                    file_path = os.path.join(root, filename)

                    # Informations sur le fichier
                    file_info = {
                        "name": filename,
                        "size": os.path.getsize(file_path),
                        "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%d/%m/%Y"),
                    }

                    files.append(file_info)

        except Exception as e:
            flash(f"Erreur lors de la récupération des fichiers : {e}", "danger")
            files = []
            
        ctx = {
            "form": form,
            "files": files
        }
        return render_template(self.template_name, **ctx)
    
    def post(self):
        form = self.form_class()

        if form.validate_on_submit():
            file = form.file.data

            filename = file.filename
            # Utilisation de BASE_DIR qui est probablement un objet Path
            file_path = f"{current_app.config["UPLOAD_FOLDER"]}/{filename}"
            file.save(file_path)
            
            #flash("Fichier téléchargé avec succès.", "success")
            return redirect(url_for("files"))
        
        elif form.errors:
            # Affichage des erreurs de validation
            get_forms_errors(form)

        ctx = {
            "form": form
        }
        return render_template(self.template_name, **ctx)
    

class DownloadView(MethodView):
    def get(self, filename):
        # Sécurisation du chemin pour éviter les attaques de traversée de répertoire
        if os.path.basename(filename) != filename:
            flash("Nom de fichier invalide.", "danger")
            return redirect(url_for("files"))
            
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        
        if os.path.exists(file_path):
            # Ajout du type MIME pour améliorer la compatibilité
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            flash("Le fichier demandé n'existe pas.", "danger")
            return redirect(url_for("files"))


class DeleteFileView(MethodView):
    def post(self, filename):
        # Sécurisation du chemin pour éviter les attaques de traversée de répertoire
        if os.path.basename(filename) != filename:
            flash("Nom de fichier invalide.", "danger")
            return redirect(url_for("files"))
            
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                flash("Fichier supprimé avec succès.", "success")
            else:
                flash("Le fichier demandé n'existe pas.", "danger")
        except PermissionError:
            flash("Impossible de supprimer le fichier. Vérifiez les permissions.", "danger")
        except Exception as e:
            flash(f"Erreur lors de la suppression: {str(e)}", "danger")
            
        return redirect(url_for("files"))
    

class AboutView(MethodView):
    template_name = "about.html"

    def get(self):
        return render_template(self.template_name)
    

class LegalNoticeView(MethodView):
    template_name = "legal_notice.html"

    def get(self):
        return render_template(self.template_name)