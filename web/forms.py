"""
forms.py

Ce module contient les formulaires de l'application Flask.
"""

from flask_wtf import FlaskForm
from wtforms.fields import (
    FileField,
    SubmitField
)
from flask_wtf.file import FileRequired, FileAllowed


class UploadForm(FlaskForm):
    file = FileField(
        label="Fichier",
        validators=[
            FileRequired(message="Aucun fichier sélectionné."),
            FileAllowed(
                upload_set=[
                    "pdf",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "py",
                    "csv",
                    "txt",
                    "json",
                    "xml",
                    "zip",
                    "tar",
                    "gz",
                    "jpg",
                    "jpeg",
                    "png",
                    "svg",
                    "mp3",
                    "wav",
                    "mp4",
                    "avi",
                    "mov",
                    "mkv",
                    "iso"
                ],
                message="Format de fichier non autorisé."
            )
        ]
    )
    submit = SubmitField(label="Téléverser")