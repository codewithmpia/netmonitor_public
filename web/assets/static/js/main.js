// Script pour la gestion du menu mobile 
document.addEventListener('DOMContentLoaded', function () {
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarMenu = document.getElementById('navbar-menu');
    const menuIcon = document.getElementById('menu-icon');
    const closeIcon = document.getElementById('close-icon');

    navbarToggle.addEventListener('click', function () {
        // Bascule l'affichage du menu
        if (navbarMenu.classList.contains('hidden')) {
            // Ouvre le menu
            navbarMenu.classList.remove('hidden');
            navbarMenu.classList.add('flex', 'flex-col');

            // Change l'icône en X
            menuIcon.classList.add('hidden');
            closeIcon.classList.remove('hidden');
        } else {
            // Ferme le menu
            navbarMenu.classList.add('hidden');
            navbarMenu.classList.remove('flex', 'flex-col');

            // Change l'icône en hamburger
            closeIcon.classList.add('hidden');
            menuIcon.classList.remove('hidden');
        }
    });

    // Gestion de l'affichage au redimensionnement de la fenêtre
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 640) { // 640px est la limite sm dans Tailwind
            // Sur écran large
            navbarMenu.classList.remove('hidden', 'flex-col');
            navbarMenu.classList.add('flex');

            // Assure que l'icône hamburger est visible pour le prochain retour en mode mobile
            closeIcon.classList.add('hidden');
            menuIcon.classList.remove('hidden');
        } else {
            // Sur mobile
            if (!navbarMenu.classList.contains('hidden') && !navbarMenu.classList.contains('flex-col')) {
                navbarMenu.classList.add('hidden');
            }
        }
    });
});