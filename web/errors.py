"""
    errors.py
    
    Ce module gère les erreurs de l'application Flask.
"""

from flask import (
    render_template,
    flash
)


def get_forms_errors(form):
    """Affiche les erreurs de validation du formulaire."""
    for _, errros in form.errors.items():
        for error in errros:
            flash(error, "danger")
    

def page_not_found(e):
    e.description = "La page que vous recherchez n'existe pas."
    return render_template("404.html", status=404)


def internal_server_error(e):
    e.description = "Une erreur interne est survenue. Veuillez réessayer plus tard."
    return render_template("500.html", status=500)