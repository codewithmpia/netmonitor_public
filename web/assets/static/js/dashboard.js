// dashboard.js

// Fonction pour initialiser le tableau de bord
document.addEventListener('DOMContentLoaded', function () {
    // Initialiser le bouton flottant de rafraîchissement, mais ne pas l'afficher immédiatement
    initFloatingRefreshButton(fetchDashboardData, 5000, 'bottom-right', 'sky', false);
    
    // Récupérer les données initiales
    fetchDashboardData();
});

// Fonction pour récupérer les données du tableau de bord via AJAX
function fetchDashboardData() {
    // Afficher un indicateur de chargement si nécessaire
    const dashboardContainer = document.querySelector('.max-w-screen-lg.mx-auto.px-4');
    if (dashboardContainer) {
        dashboardContainer.classList.add('opacity-75');
    }

    // Construire l'URL pour la requête AJAX
    const url = new URL(window.location.href);
    url.searchParams.set('format', 'json');

    // Faire une requête AJAX
    fetch(url.toString())
        .then(response => {
            if (!response.ok) {
                console.error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            // Vérifier le type de contenu
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error(`Type de contenu non valide: ${contentType}`);
                return response.text().then(text => {
                    console.error("Réponse non-JSON reçue:", text.substring(0, 200) + "...");
                    throw new Error('Réponse non-JSON reçue du serveur');
                });
            }

            return response.json();
        })
        .then(data => {
            // Vérifier que les données sont valides
            if (!data || !Array.isArray(data.clients)) {
                console.error("Format de données invalide:", data);
                throw new Error('Format de données invalide');
            }

            // Mettre à jour les clients dans l'interface
            updateDashboardUI(data.clients);
            
            // Afficher ou cacher le bouton flottant selon qu'il y a des clients ou non
            if (data.clients && data.clients.length > 0) {
                showFloatingButton();
            } else {
                hideFloatingButton();
            }

            // Restaurer l'opacité
            if (dashboardContainer) {
                dashboardContainer.classList.remove('opacity-75');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données:', error);

            // Cacher le bouton flottant en cas d'erreur
            hideFloatingButton();
            
            // Restaurer l'opacité en cas d'erreur
            if (dashboardContainer) {
                dashboardContainer.classList.remove('opacity-75');
            }
        });
}

// Fonction pour mettre à jour l'interface du tableau de bord
function updateDashboardUI(clients) {
    // Trouver le conteneur des clients
    const clientsContainer = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3.gap-4');
    if (!clientsContainer) return;

    // Mettre à jour le nombre de machines surveillées
    const clientsCountElem = document.querySelector('h2.text-xl.font-semibold.text-sky-800.mb-4');
    if (clientsCountElem) {
        clientsCountElem.textContent = `Machines surveillées (${clients.length})`;
    }

    // Si aucun client, afficher un message
    if (clients.length === 0) {
        // Cacher le bouton flottant s'il n'y a pas de clients
        hideFloatingButton();
        
        // Vérifier si le message "aucune machine" existe déjà
        let noClientsMessage = document.querySelector('.bg-white.rounded-lg.shadow-md.p-8.text-center');

        // Si le message n'existe pas, créer toute la structure
        if (!noClientsMessage) {
            // Vider le conteneur des clients
            clientsContainer.innerHTML = '';

            // Créer le message "aucune machine"
            const messageContainer = document.createElement('div');
            messageContainer.className = 'bg-white rounded-lg shadow-md p-8 text-center';
            messageContainer.innerHTML = `
                <div class="bg-gray-100 p-4 rounded-full inline-flex mx-auto mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                        <line x1="8" y1="21" x2="16" y2="21"></line>
                        <line x1="12" y1="17" x2="12" y2="21"></line>
                    </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-800 mb-2">Aucune machine connectée</h3>
                <p class="text-gray-600 mb-6">Aucune machine ne transmet actuellement des métriques au serveur.</p>
                <p class="text-gray-500 text-sm">Exécutez le client NetMonitor sur les machines que vous souhaitez surveiller.</p>
            `;

            // Remplacer le conteneur des clients par le message
            clientsContainer.parentNode.replaceChild(messageContainer, clientsContainer);
        }

        return;
    } else {
        // Afficher le bouton flottant s'il y a des clients
        showFloatingButton();
    }

    // Si le conteneur des clients n'existe pas (car remplacé par le message "aucune machine")
    if (!document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3.gap-4')) {
        // Recréer le conteneur des clients
        const newClientsContainer = document.createElement('div');
        newClientsContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4';

        // Remplacer le message "aucune machine" par le conteneur des clients
        const noClientsMessage = document.querySelector('.bg-white.rounded-lg.shadow-md.p-8.text-center');
        if (noClientsMessage) {
            noClientsMessage.parentNode.replaceChild(newClientsContainer, noClientsMessage);
            clientsContainer = newClientsContainer;
        }
    }

    // Vider le conteneur des clients
    clientsContainer.innerHTML = '';

    // Ajouter les clients
    clients.forEach(client => {
        // Création de la carte client
        const clientCard = document.createElement('a');
        clientCard.href = `/dashboard/${client.hostname}`;
        clientCard.className = `bg-white rounded-lg shadow-md p-4 border-l-4 ${client.status === 'Online' ? 'border-green-500' : 'border-gray-400'} hover:shadow-lg transition-all duration-300`;

        // Déterminer le pourcentage d'utilisation du disque
        let diskPercent = 0;
        let diskDisplay = 'N/A';
        if (client.metrics.disk && client.metrics.disk.partitions) {
            let rootPartition = client.metrics.disk.partitions.find(p => p.mountpoint === '/');
            if (rootPartition) {
                diskPercent = rootPartition.percent;
                diskDisplay = `${rootPartition.percent}%`;
            } else if (client.metrics.disk.partitions.length > 0) {
                diskPercent = client.metrics.disk.partitions[0].percent;
                diskDisplay = `${client.metrics.disk.partitions[0].percent}%`;
            }
        }

        // Déterminer la couleur de la barre de disque en fonction du pourcentage
        let diskBarColor = 'bg-sky-600';
        if (diskPercent > 90) {
            diskBarColor = 'bg-red-500';
        } else if (diskPercent > 70) {
            diskBarColor = 'bg-amber-500';
        }

        // Construire le contenu de la carte
        clientCard.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-medium text-gray-900">${client.hostname}</h3>
                    <p class="text-sm text-gray-500">Dernière mise à jour: ${client.last_update}</p>
                </div>
                <span class="px-2 py-1 rounded-full text-xs font-medium ${client.status === 'Online' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    ${client.status}
                </span>
            </div>
            
            <!-- Utilisation CPU -->
            <div class="mt-3">
                <div class="flex justify-between items-center text-sm mb-1">
                    <span class="font-medium text-gray-700">CPU</span>
                    <span class="text-gray-600">
                        ${client.metrics.cpu && client.metrics.cpu.cpu_percent_avg !== undefined ? `${client.metrics.cpu.cpu_percent_avg}%` : 'N/A'}
                    </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-sky-600 h-2 rounded-full" style="width: ${client.metrics.cpu && client.metrics.cpu.cpu_percent_avg !== undefined ? client.metrics.cpu.cpu_percent_avg : 0}%"></div>
                </div>
            </div>
            
            <!-- Utilisation Mémoire -->
            <div class="mt-3">
                <div class="flex justify-between items-center text-sm mb-1">
                    <span class="font-medium text-gray-700">Mémoire</span>
                    <span class="text-gray-600">
                        ${client.metrics.memory && client.metrics.memory.virtual_memory && client.metrics.memory.virtual_memory.percent !== undefined ? `${client.metrics.memory.virtual_memory.percent}%` : 'N/A'}
                    </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-sky-600 h-2 rounded-full" style="width: ${client.metrics.memory && client.metrics.memory.virtual_memory && client.metrics.memory.virtual_memory.percent !== undefined ? client.metrics.memory.virtual_memory.percent : 0}%"></div>
                </div>
            </div>

            <!-- Utilisation Disque -->
            <div class="mt-3">
                <div class="flex justify-between items-center text-sm mb-1">
                    <span class="font-medium text-gray-700">Disque</span>
                    <span class="text-gray-600">${diskDisplay}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="${diskBarColor} h-2 rounded-full" style="width: ${diskPercent}%"></div>
                </div>
            </div>
        `;

        // Ajouter la carte au conteneur
        clientsContainer.appendChild(clientCard);
    });
}