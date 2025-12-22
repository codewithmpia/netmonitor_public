"""
    settings.py
    
    Ce fichier contient la configuration de l'application Flask.
"""

from pathlib import Path
import uuid

from flask import Flask
from flask_minify import Minify


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = str(BASE_DIR / "data")

UPLOAD_FOLDER = str(BASE_DIR / "data/files")

# La clé de sécurité de l'application
SECRET_KEY = str(uuid.uuid4())

# Initialisation de l'application Flask
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "web/assets/templates"),
    static_folder=str(BASE_DIR / "web/assets/static"),
)

app.config["SECRET_KEY"] = SECRET_KEY

# 
app.config["DATA_DIR"] = DATA_DIR

# Dossier de téléchargement
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Limite de taille de fichier pour les téléchargements
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 Go

# Optimisation de la mise en cache des templates
# pour éviter de recharger les templates à chaque requête
app.config["TEMPLATES_AUTO_RELOAD"] = False
app.jinja_env.cache = {}
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Configuration de Flask-Minify pour la minification 
# des fichiers CSS, JS et HTML
Minify(app=app, html=True, js=True, cssless=True)

# Filtres personnalisés pour Jinja2
from .filters import (
    format_bytes,
)

app.jinja_env.filters["format_bytes"] = format_bytes

# Gestion des erreurs
from .errors import (
    page_not_found,
    internal_server_error,
)
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)

# Les routes de l'application
from .views import (
    IndexView,
    DashBoardView,
    ClientMetricsView,
    FilesView,
    DownloadView,
    DeleteFileView,
    AboutView,
    LegalNoticeView,
)

# Routes pour la page d'accueil
app.add_url_rule(
    "/", 
    view_func=IndexView.as_view("index")
)
# Routes pour le tableau de bord
app.add_url_rule(
    "/dashboard/", 
    view_func=DashBoardView.as_view("dashboard")
)
# Routes pour les métriques des clients
app.add_url_rule(
    "/dashboard/<path:hostname>/", 
    view_func=ClientMetricsView.as_view("client_metrics")
)
app.add_url_rule(
    '/data/metrics/<hostname>/<file>/', 
    view_func=ClientMetricsView.as_view('client_metrics_file')
)
# Routes pour la gestion des fichiers
app.add_url_rule(
    "/files/", 
    view_func=FilesView.as_view("files")
)
app.add_url_rule(
    "/files/download/<path:filename>/", 
    view_func=DownloadView.as_view("download")
)
app.add_url_rule(
    "/files/delete/<path:filename>/", 
    view_func=DeleteFileView.as_view("delete")
)
# Routes pour les pages d'informations
app.add_url_rule(
    "/about/", 
    view_func=AboutView.as_view("about")
)
app.add_url_rule(
    "/legal-notice/", 
    view_func=LegalNoticeView.as_view("legal_notice")
)