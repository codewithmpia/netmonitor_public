/**
 * floating-refresh-button.js
 * Module réutilisable pour créer un bouton flottant de rafraîchissement automatique
 */

// Variables globales pour le suivi de l'état du bouton
let autoRefreshEnabled = true;
let refreshInterval;
let countdownInterval;
let countdownValue = 5;
let buttonContainer = null;

/**
 * Crée et initialise le bouton flottant de rafraîchissement
 * @param {Function} refreshFunction - Fonction à exécuter lors du rafraîchissement
 * @param {number} refreshTime - Intervalle de rafraîchissement en millisecondes
 * @param {string} position - Position du bouton (bottom-right, bottom-left, etc.)
 * @param {string} color - Couleur du bouton (sky, blue, green, etc.)
 * @param {boolean} showImmediately - Si le bouton doit être affiché immédiatement
 */
function initFloatingRefreshButton(refreshFunction, refreshTime = 5000, position = 'bottom-right', color = 'sky', showImmediately = false) {
    // Créer le bouton flottant de rafraîchissement
    createFloatingRefreshButton(position, color);

    // Si le bouton ne doit pas être affiché immédiatement, le cacher
    if (!showImmediately && buttonContainer) {
        buttonContainer.style.display = 'none';
    }

    // Démarrer le rafraîchissement automatique seulement si le bouton est visible
    if (showImmediately) {
        refreshInterval = setInterval(refreshFunction, refreshTime);
        startCountdown();
    }
    
    // Rendre la fonction de rafraîchissement disponible globalement pour les gestionnaires d'événements
    window.currentRefreshFunction = refreshFunction;
    window.refreshTime = refreshTime;
}

/**
 * Affiche le bouton flottant s'il existe
 */
function showFloatingButton() {
    if (buttonContainer) {
        buttonContainer.style.display = 'block';
        
        // Si le rafraîchissement automatique est activé, démarrer l'intervalle
        if (autoRefreshEnabled && window.currentRefreshFunction) {
            if (!refreshInterval) {
                refreshInterval = setInterval(window.currentRefreshFunction, window.refreshTime || 5000);
                startCountdown();
            }
        }
    }
}

/**
 * Cache le bouton flottant s'il existe et arrête les intervalles
 */
function hideFloatingButton() {
    if (buttonContainer) {
        buttonContainer.style.display = 'none';
        
        // Arrêter les intervalles
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
        
        if (countdownInterval) {
            clearInterval(countdownInterval);
            countdownInterval = null;
        }
    }
}

/**
 * Crée le bouton flottant de rafraîchissement
 * @param {string} position - Position du bouton
 * @param {string} color - Couleur du bouton
 */
function createFloatingRefreshButton(position = 'bottom-right', color = 'sky') {
    // Déterminer les classes de position
    let positionClasses = 'fixed z-50 ';
    switch (position) {
        case 'bottom-right':
            positionClasses += 'bottom-8 right-8';
            break;
        case 'bottom-left':
            positionClasses += 'bottom-8 left-8';
            break;
        case 'top-right':
            positionClasses += 'top-8 right-8';
            break;
        case 'top-left':
            positionClasses += 'top-8 left-8';
            break;
        default:
            positionClasses += 'bottom-8 right-8';
    }

    // Créer les éléments nécessaires
    buttonContainer = document.createElement('div');
    buttonContainer.id = 'floating-refresh-button-container';
    buttonContainer.className = positionClasses;

    const buttonWrapper = document.createElement('div');
    buttonWrapper.className = 'relative';

    // Créer le bouton principal
    const refreshButton = document.createElement('button');
    refreshButton.id = 'floating-refresh-button';
    refreshButton.className = `flex items-center justify-center w-16 h-16 rounded-full shadow-lg bg-${color}-600 text-white hover:bg-${color}-700 focus:outline-none hover:scale-110 transition-all duration-300 transform shadow-xl`;

    // Créer l'icône à l'intérieur du bouton
    const buttonIcon = document.createElement('div');
    buttonIcon.className = 'relative';
    buttonIcon.innerHTML = `
       <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-8 w-8 animate-spin" style="animation-duration:3s" viewBox="0 0 24 24"><path d="M21.5 2v6h-6m-13 14v-6h6M2 11.5a10 10 0 0 1 18.8-4.3m1.2 5.3a10 10 0 0 1-18.8 4.2"/></svg>
        <div id="countdown-circle" class="absolute inset-0 flex items-center justify-center text-xl font-bold">${countdownValue}</div>
    `;

    // Créer un élément pour afficher le statut du rafraîchissement (tooltip)
    const refreshStatus = document.createElement('div');
    refreshStatus.id = 'refresh-status';
    refreshStatus.className = 'absolute -top-10 left-1/2 transform -translate-x-1/2 bg-white px-4 py-2 rounded-lg shadow-md text-sky-600 font-medium text-sm whitespace-nowrap opacity-0 transition-opacity duration-300';
    refreshStatus.textContent = 'Rafraîchissement automatique activé';

    // Assembler les éléments
    refreshButton.appendChild(buttonIcon);
    buttonWrapper.appendChild(refreshButton);
    buttonWrapper.appendChild(refreshStatus);
    buttonContainer.appendChild(buttonWrapper);

    // Ajouter au document
    document.body.appendChild(buttonContainer);

    // Ajouter le gestionnaire d'événements
    refreshButton.addEventListener('click', toggleAutoRefresh);

    // Ajouter un tooltip au survol
    refreshButton.addEventListener('mouseenter', function () {
        refreshStatus.classList.add('opacity-100');
    });

    refreshButton.addEventListener('mouseleave', function () {
        refreshStatus.classList.remove('opacity-100');
    });

    // Ajouter une animation de pulsation
    addPulsation(refreshButton);
}

/**
 * Ajoute une animation de pulsation au bouton
 * @param {HTMLElement} button - Élément bouton
 */
function addPulsation(button) {
    // Créer un élément pour l'animation de pulsation
    const pulseRing = document.createElement('div');
    pulseRing.className = 'absolute inset-0 rounded-full animate-ping opacity-30 bg-sky-400';

    // Réduire la durée et l'opacité pour un effet plus subtil
    pulseRing.style.animationDuration = '2s';

    // Insérer l'élément de pulsation avant l'icône
    button.insertBefore(pulseRing, button.firstChild);
}

/**
 * Démarre le compte à rebours visuel
 */
function startCountdown() {
    countdownValue = 5;
    updateCountdownDisplay();

    countdownInterval = setInterval(function () {
        countdownValue -= 1;
        if (countdownValue <= 0) {
            countdownValue = 5;
        }
        updateCountdownDisplay();
    }, 1000);
}

/**
 * Met à jour l'affichage du compteur
 */
function updateCountdownDisplay() {
    const countdownElem = document.getElementById('countdown-circle');
    if (countdownElem) {
        countdownElem.textContent = countdownValue;
    }
}

/**
 * Bascule l'état du rafraîchissement automatique
 */
function toggleAutoRefresh() {
    const button = document.getElementById('floating-refresh-button');
    const statusText = document.getElementById('refresh-status');
    const iconContainer = button.querySelector('svg');
    const pulseRing = button.querySelector('.animate-ping');

    // Inverser l'état actuel
    autoRefreshEnabled = !autoRefreshEnabled;

    if (autoRefreshEnabled) {
        // Activer le rafraîchissement automatique
        button.classList.remove('bg-gray-500', 'hover:bg-gray-600');
        button.classList.add('bg-sky-600', 'hover:bg-sky-700');
        iconContainer.classList.add('animate-spin');

        // Réactiver l'animation de pulsation
        if (pulseRing) {
            pulseRing.classList.remove('hidden');
        }

        statusText.textContent = 'Rafraîchissement automatique activé';

        // Démarrer le rafraîchissement
        if (window.currentRefreshFunction) {
            refreshInterval = setInterval(window.currentRefreshFunction, window.refreshTime || 5000);
        }
        startCountdown();
    } else {
        // Désactiver le rafraîchissement automatique
        button.classList.remove('bg-sky-600', 'hover:bg-sky-700');
        button.classList.add('bg-gray-500', 'hover:bg-gray-600');
        iconContainer.classList.remove('animate-spin');

        // Désactiver l'animation de pulsation
        if (pulseRing) {
            pulseRing.classList.add('hidden');
        }

        statusText.textContent = 'Rafraîchissement automatique désactivé';

        // Arrêter les intervalles
        clearInterval(refreshInterval);
        clearInterval(countdownInterval);

        // Afficher "OFF" dans le compteur
        const countdownElem = document.getElementById('countdown-circle');
        if (countdownElem) {
            countdownElem.textContent = 'OFF';
            countdownElem.classList.add('text-xs');
        }
    }

    // Afficher le statut brièvement
    statusText.classList.add('opacity-100');
    setTimeout(() => {
        statusText.classList.remove('opacity-100');
    }, 2000);

    // Cliquer sur le bouton déclenche également un rafraîchissement immédiat
    if (window.currentRefreshFunction) {
        window.currentRefreshFunction();
    }
}

// Exposer les fonctions utiles
window.initFloatingRefreshButton = initFloatingRefreshButton;
window.toggleAutoRefresh = toggleAutoRefresh;
window.showFloatingButton = showFloatingButton;
window.hideFloatingButton = hideFloatingButton;