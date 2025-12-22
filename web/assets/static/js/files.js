// Script pour la barre de progression
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('uploadForm');
    const formContainer = document.getElementById('formContainer');
    const fileInput = document.getElementById('fileInput');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const successMessage = document.getElementById('successMessage');

    // Intercepter la soumission du formulaire
    form.addEventListener('submit', function (e) {
        // Vérifier si un fichier est sélectionné
        if (fileInput.files.length === 0) {
            return; // Laisser le formulaire être soumis normalement pour afficher les erreurs de validation
        }

        e.preventDefault(); // Empêcher la soumission normale du formulaire

        // Obtenir le token CSRF
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        // Créer un objet FormData pour envoyer les données
        const formData = new FormData();
        formData.append('csrf_token', csrfToken);
        formData.append('file', fileInput.files[0]);

        // Créer une requête AJAX
        const xhr = new XMLHttpRequest();

        // Configurer la requête
        xhr.open('POST', form.action || window.location.href, true);

        // Masquer le formulaire
        formContainer.style.display = 'none';

        // Afficher la barre de progression
        progressContainer.classList.remove('hidden');

        // Écouter l'événement de progression
        xhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percentComplete + '%';
                progressText.textContent = percentComplete + '% - ' + (percentComplete < 100 ? 'Téléchargement en cours...' : 'Finalisation...');
            }
        });

        // Écouter l'événement de fin de téléchargement
        xhr.addEventListener('load', function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                // Téléchargement réussi
                progressBar.style.width = '100%';
                progressText.textContent = 'Téléchargement terminé avec succès !';

                // Masquer la barre de progression
                progressContainer.classList.add('hidden');

                // Afficher le message de succès
                successMessage.classList.remove('hidden');

                // Attendre un court instant pour que l'utilisateur voie le message de succès
                setTimeout(function () {
                    // Recharger la page pour afficher le nouveau fichier et les messages flash de Flask
                    window.location.reload();
                }, 1500);
            } else {
                // Erreur lors du téléchargement
                progressContainer.classList.add('bg-red-100');
                progressBar.classList.remove('bg-sky-600');
                progressBar.classList.add('bg-red-600');
                progressText.textContent = 'Erreur lors du téléchargement';

                // Réafficher le formulaire après un court délai
                setTimeout(function () {
                    formContainer.style.display = 'block';
                    progressContainer.classList.add('hidden');
                    progressBar.style.width = '0%';
                    progressBar.classList.remove('bg-red-600');
                    progressBar.classList.add('bg-sky-600');
                }, 2000);
            }
        });

        // Écouter l'événement d'erreur
        xhr.addEventListener('error', function () {
            progressContainer.classList.add('bg-red-100');
            progressBar.classList.remove('bg-sky-600');
            progressBar.classList.add('bg-red-600');
            progressText.textContent = 'Erreur de connexion';

            // Réafficher le formulaire après un court délai
            setTimeout(function () {
                formContainer.style.display = 'block';
                progressContainer.classList.add('hidden');
                progressBar.style.width = '0%';
                progressBar.classList.remove('bg-red-600');
                progressBar.classList.add('bg-sky-600');
            }, 2000);
        });

        // Écouter l'événement d'abandon
        xhr.addEventListener('abort', function () {
            progressText.textContent = 'Téléchargement annulé';

            // Réafficher le formulaire après un court délai
            setTimeout(function () {
                formContainer.style.display = 'block';
                progressContainer.classList.add('hidden');
                progressBar.style.width = '0%';
            }, 2000);
        });

        // Envoyer la requête
        xhr.send(formData);
    });
});