// client.js

// Variables globales pour les graphiques
let cpuChart, memoryChart, diskChart, networkChart;

// Fonction pour initialiser tous les graphiques et le bouton
document.addEventListener('DOMContentLoaded', function () {
    // Configuration des graphiques avec un style cohérent
    Chart.defaults.font.family = "'Inter', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.color = '#64748b';
    
    // Initialiser le bouton flottant de rafraîchissement, mais ne pas l'afficher immédiatement
    initFloatingRefreshButton(fetchLatestMetrics, 5000, 'bottom-right', 'sky', false);
    
    // Vérifier si nous avons des données pour afficher le bouton
    if (chartData && (chartData.cpu || chartData.memory || chartData.disk || chartData.network)) {
        showFloatingButton();
    } else {
        hideFloatingButton();
    }
    
    // Création du graphique CPU
    if (chartData.cpu) {
        const cpuCtx = document.getElementById('cpuChart').getContext('2d');
        cpuChart = new Chart(cpuCtx, {
            type: 'bar',
            data: chartData.cpu,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.dataset.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Utilisation (%)'
                        }
                    }
                },
                animation: {
                    duration: 500 // Animation plus rapide pour les mises à jour
                }
            }
        });
    }

    // Création du graphique Mémoire
    if (chartData.memory) {
        const memoryCtx = document.getElementById('memoryChart').getContext('2d');
        memoryChart = new Chart(memoryCtx, {
            type: 'doughnut',
            data: chartData.memory,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Conversion des octets en format lisible
                                const bytes = context.raw;
                                const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To'];
                                if (bytes === 0) return '0 octets';
                                const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
                                return context.label + ': ' +
                                    (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
                            }
                        }
                    }
                },
                animation: {
                    duration: 500
                }
            }
        });
    }

    // Création du graphique Disque
    if (chartData.disk) {
        const diskCtx = document.getElementById('diskChart').getContext('2d');
        diskChart = new Chart(diskCtx, {
            type: 'bar',
            data: chartData.disk,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Conversion des octets en format lisible
                                const bytes = context.raw;
                                const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To'];
                                if (bytes === 0) return '0 octets';
                                const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
                                return context.dataset.label + ': ' +
                                    (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                        ticks: {
                            callback: function (value) {
                                // Conversion des octets en format lisible
                                const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To'];
                                if (value === 0) return '0';
                                const i = parseInt(Math.floor(Math.log(value) / Math.log(1024)));
                                return (value / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
                            }
                        }
                    }
                },
                animation: {
                    duration: 500
                }
            }
        });
    }

    // Création du graphique Réseau
    if (chartData.network) {
        const networkCtx = document.getElementById('networkChart').getContext('2d');
        networkChart = new Chart(networkCtx, {
            type: 'bar',
            data: chartData.network,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Conversion des octets en format lisible
                                const bytes = context.raw;
                                const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To'];
                                if (bytes === 0) return '0 octets';
                                const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
                                return context.dataset.label + ': ' +
                                    (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: function (value) {
                                // Conversion des octets en format lisible
                                if (value === 0) return '0';
                                const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To'];
                                const i = parseInt(Math.floor(Math.log(value) / Math.log(1024)));
                                return (value / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
                            }
                        }
                    }
                },
                animation: {
                    duration: 500
                }
            }
        });
    }
});

// Fonction pour télécharger un fichier de métriques
function downloadMetricsFile(hostname, filename) {
    // Approche 1: Rediriger vers la même URL mais avec un paramètre de téléchargement
    const downloadUrl = `{{ url_for('client_metrics_file', hostname=hostname, file='__FILENAME__') }}`.replace('__FILENAME__', filename) + '?download=true';

    // Vérifier si les données actuelles correspondent au fichier à télécharger
    if ('{{ current_file }}' === filename) {
        // Approche 2: Si c'est le fichier actuellement affiché, utiliser ses données directement
        const blob = new Blob([JSON.stringify(metricsData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;

        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } else {
        // Si ce n'est pas le fichier actuel, créer un formulaire temporaire et le soumettre
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = `{{ url_for('client_metrics_file', hostname=hostname, file='') }}` + filename;

        const downloadInput = document.createElement('input');
        downloadInput.type = 'hidden';
        downloadInput.name = 'download';
        downloadInput.value = 'true';

        form.appendChild(downloadInput);
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    }

    return false;
}

// Fonction pour charger les dernières données métriques via AJAX
function fetchLatestMetrics() {
    // Afficher l'indicateur de chargement
    const statusIndicator = document.getElementById('updateStatus');
    if (statusIndicator) {
        statusIndicator.innerHTML = 'Mise à jour en cours...';
        statusIndicator.classList.remove('text-green-600');
        statusIndicator.classList.add('text-yellow-600');
    }

    // Récupérer le hostname de différentes manières possibles
    let hostname;
    
    // 1. Essayer la balise meta
    const metaHostname = document.querySelector('meta[name="client-hostname"]');
    if (metaHostname) {
        hostname = metaHostname.getAttribute('content');
    } 
    // 2. Essayer la variable globale définie dans le template
    else if (window.clientHostname) {
        hostname = window.clientHostname;
    }
    // 3. Essayer de l'extraire de l'URL
    else {
        const pathParts = window.location.pathname.split('/');
        // Supposant un chemin comme /client_metrics/hostname ou /client/metrics/hostname/
        for (let i = 0; i < pathParts.length; i++) {
            if (pathParts[i] === 'client_metrics' || pathParts[i] === 'metrics') {
                hostname = pathParts[i+1];
                break;
            }
        }
    }
    
    // Construire une nouvelle URL basée sur l'URL actuelle
    const url = new URL(window.location.href);
    
    // Conserver le paramètre page existant s'il existe
    // Si page n'existe pas encore, utiliser 1 comme valeur par défaut
    if (!url.searchParams.has('page')) {
        url.searchParams.set('page', '1');
    }
    
    // Ajouter le paramètre format=json
    url.searchParams.set('format', 'json');
    
    // Faire une requête AJAX vers l'URL formatée correctement
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
            // Vérifier que les données sont complètes
            if (!data || !data.chart_data) {
                console.error("Format de données incomplet:", data);
                hideFloatingButton(); // Cacher le bouton s'il n'y a pas de données
                throw new Error('Format de données incomplet');
            }
            
            // Afficher le bouton puisqu'on a des données
            showFloatingButton();
            
            // Mettre à jour les données et les graphiques
            updateCharts(data.chart_data);
            
            // Mettre à jour les infos système
            updateSystemInfo(data.metrics);
            
            // Mettre à jour la liste des fichiers historiques si présente
            if (data.history_files) {
                updateHistoryFiles(data.history_files, data.hostname);
            }
            
            // Mettre à jour la pagination si présente
            if (data.pagination) {
                updatePagination(data.pagination);
            }
            
            // Mettre à jour l'indicateur de statut
            if (statusIndicator) {
                statusIndicator.innerHTML = 'Données mises à jour';
                statusIndicator.classList.remove('text-yellow-600');
                statusIndicator.classList.add('text-green-600');
                
                // Effacer le message après quelques secondes
                setTimeout(() => {
                    statusIndicator.innerHTML = 'Actualisé à ' + new Date().toLocaleTimeString();
                }, 1000);
            }
            
            // Mettre à jour l'horodatage
            const timestampElement = document.getElementById('lastUpdateTime');
            if (timestampElement) {
                timestampElement.textContent = new Date().toLocaleTimeString();
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données:', error);
            
            // Cacher le bouton en cas d'erreur persistante
            hideFloatingButton();
            
            // Mettre à jour l'indicateur de statut en cas d'erreur
            if (statusIndicator) {
                statusIndicator.innerHTML = 'Erreur de mise à jour';
                statusIndicator.classList.remove('text-yellow-600', 'text-green-600');
                statusIndicator.classList.add('text-red-600');
            }
        });
}

// Fonction pour mettre à jour les graphiques avec les nouvelles données
function updateCharts(newChartData) {
    // Mettre à jour le graphique CPU
    if (newChartData.cpu && cpuChart) {
        cpuChart.data.labels = newChartData.cpu.labels;
        cpuChart.data.datasets[0].data = newChartData.cpu.datasets[0].data;
        cpuChart.update();
    }
    
    // Mettre à jour le graphique Mémoire
    if (newChartData.memory && memoryChart) {
        memoryChart.data.labels = newChartData.memory.labels;
        memoryChart.data.datasets[0].data = newChartData.memory.datasets[0].data;
        memoryChart.update();
    }
    
    // Mettre à jour le graphique Disque
    if (newChartData.disk && diskChart) {
        diskChart.data.labels = newChartData.disk.labels;
        diskChart.data.datasets[0].data = newChartData.disk.datasets[0].data;
        diskChart.data.datasets[1].data = newChartData.disk.datasets[1].data;
        diskChart.update();
    }
    
    // Mettre à jour le graphique Réseau
    if (newChartData.network && networkChart) {
        networkChart.data.labels = newChartData.network.labels;
        networkChart.data.datasets[0].data = newChartData.network.datasets[0].data;
        networkChart.data.datasets[1].data = newChartData.network.datasets[1].data;
        networkChart.update();
    }
}

// Fonction pour mettre à jour les informations système dans l'interface
function updateSystemInfo(metrics) {
    if (!metrics) return;
    
    // Mettre à jour les informations de base du système
    const hostnameElem = document.querySelector('.text-xl.font-semibold.text-sky-800');
    if (hostnameElem) {
        hostnameElem.textContent = metrics.current_file_display || hostnameElem.textContent;
    }
    
    // Mettre à jour l'horodatage des métriques
    const timestampElem = document.querySelector('.text-sm.text-sky-600');
    if (timestampElem && metrics.timestamp) {
        const formattedTimestamp = metrics.timestamp.replace('T', ' ').replace('Z', '').replace('.', ' ');
        timestampElem.textContent = 'Métriques collectées: ' + formattedTimestamp;
    }
    
    // Trouver tous les éléments de métriques et les mettre à jour
    document.querySelectorAll('.p-3.bg-gray-50.rounded-lg p.text-sm').forEach(elem => {
        // Hostname
        if (elem.innerHTML.includes('<span class="font-medium">Hôte:</span>')) {
            elem.innerHTML = `<span class="font-medium">Hôte:</span> ${metrics.hostname || 'N/A'}`;
        }
        // IP
        else if (elem.innerHTML.includes('<span class="font-medium">IP:</span>')) {
            elem.innerHTML = `<span class="font-medium">IP:</span> ${metrics.ip_address || 'N/A'}`;
        }
        // Plateforme
        else if (elem.innerHTML.includes('<span class="font-medium">Plateforme:</span>')) {
            elem.innerHTML = `<span class="font-medium">Plateforme:</span> ${metrics.platform || 'N/A'}`;
        }
        // Utilisation moyenne CPU
        else if (elem.innerHTML.includes('<span class="font-medium">Utilisation moyenne:</span>')) {
            if (metrics.cpu && metrics.cpu.cpu_percent_avg !== undefined) {
                elem.innerHTML = `<span class="font-medium">Utilisation moyenne:</span> ${metrics.cpu.cpu_percent_avg}%`;
            }
        }
        // Cœurs logiques
        else if (elem.innerHTML.includes('<span class="font-medium">Cœurs logiques:</span>')) {
            if (metrics.cpu && metrics.cpu.cpu_count_logical !== undefined) {
                elem.innerHTML = `<span class="font-medium">Cœurs logiques:</span> ${metrics.cpu.cpu_count_logical}`;
            }
        }
        // Cœurs physiques
        else if (elem.innerHTML.includes('<span class="font-medium">Cœurs physiques:</span>')) {
            if (metrics.cpu && metrics.cpu.cpu_count_physical !== undefined) {
                elem.innerHTML = `<span class="font-medium">Cœurs physiques:</span> ${metrics.cpu.cpu_count_physical}`;
            }
        }
        // Utilisation mémoire
        else if (elem.innerHTML.includes('<span class="font-medium">Utilisation:</span>')) {
            if (metrics.memory && metrics.memory.virtual_memory && metrics.memory.virtual_memory.percent !== undefined) {
                elem.innerHTML = `<span class="font-medium">Utilisation:</span> ${metrics.memory.virtual_memory.percent}%`;
            }
        }
        // SWAP
        else if (elem.innerHTML.includes('<span class="font-medium">SWAP:</span>')) {
            if (metrics.memory && metrics.memory.swap_memory && metrics.memory.swap_memory.percent !== undefined) {
                elem.innerHTML = `<span class="font-medium">SWAP:</span> ${metrics.memory.swap_memory.percent}%`;
            }
        }
        // Mémoire totale
        else if (elem.innerHTML.includes('<span class="font-medium">Total:</span>')) {
            if (metrics.memory && metrics.memory.virtual_memory && metrics.memory.virtual_memory.total !== undefined) {
                // Formater la taille en unités lisibles
                const bytes = metrics.memory.virtual_memory.total;
                const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To'];
                if (bytes === 0) {
                    elem.innerHTML = `<span class="font-medium">Total:</span> 0 octets`;
                } else {
                    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
                    const formattedSize = (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
                    elem.innerHTML = `<span class="font-medium">Total:</span> ${formattedSize}`;
                }
            }
        }
    });
}

// Fonction pour mettre à jour les fichiers historiques
function updateHistoryFiles(historyFiles, hostname) {
    // Vérifier si les données sont valides
    if (!historyFiles || !Array.isArray(historyFiles)) return;
    
    // Trouver le tableau d'historique
    const historyTable = document.querySelector('.history-files-table tbody');
    if (!historyTable) {
        console.error("Table d'historique non trouvée dans le DOM");
        return;
    }
    
    // Vider le tableau existant
    historyTable.innerHTML = '';
    
    // Ajouter les nouvelles lignes
    historyFiles.forEach(file => {
        // Créer une URL directe pour le téléchargement sans passer par aucune fonction JavaScript
        const downloadUrl = `/data/metrics/${hostname}/${file.filename}?download=true`;
        
        // Créer une ligne de tableau
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        // Ajouter le contenu HTML
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-8 w-8 text-sky-500">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 18v-6M8 15h8"/></svg>
                    </div>
                    <div class="ml-3">
                        <div class="text-sm font-medium text-gray-900">${file.filename}</div>
                    </div>
                </div>
            </td>
            <td class="hidden sm:table-cell px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">
                    ${file.display_name}
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="${downloadUrl}" class="flex items-center justify-end text-sky-600 hover:text-sky-800 transition-colors" download>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-5 w-5" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                </a>
            </td>
        `;
        
        // Ajouter la ligne au tableau
        historyTable.appendChild(row);
    });
}

// Fonction pour mettre à jour la pagination
function updatePagination(pagination) {
    if (!pagination) return;
    
    // Rechercher le conteneur de pagination
    let paginationContainer = document.querySelector('.pagination-container');
    const historyContainer = document.querySelector('.history-files-table').closest('.bg-white.rounded-lg.shadow-md');
    
    // Si la pagination est nécessaire (plus d'une page)
    if (pagination.pages > 1) {
        // Si le conteneur de pagination n'existe pas encore, le créer
        if (!paginationContainer) {
            paginationContainer = document.createElement('div');
            paginationContainer.className = 'mt-4 flex items-center justify-between pagination-container';
            
            // Créer la section d'information
            const paginationInfo = document.createElement('div');
            paginationInfo.className = 'text-sm text-gray-500 pagination-info';
            
            // Créer la section des boutons
            const paginationButtons = document.createElement('div');
            paginationButtons.className = 'flex space-x-1';
            
            // Ajouter les éléments au conteneur
            paginationContainer.appendChild(paginationInfo);
            paginationContainer.appendChild(paginationButtons);
            
            // Ajouter le conteneur de pagination après le tableau d'historique
            if (historyContainer) {
                const innerContainer = historyContainer.querySelector('.p-6');
                if (innerContainer) {
                    innerContainer.appendChild(paginationContainer);
                } else {
                    historyContainer.appendChild(paginationContainer);
                }
            }
        }
        
        // Mettre à jour les informations de pagination
        const paginationInfo = paginationContainer.querySelector('.pagination-info');
        if (paginationInfo) {
            if (pagination.total > 0) {
                paginationInfo.textContent = `Affichage de ${pagination.first_item} à ${pagination.last_item} sur ${pagination.total} fichiers`;
            } else {
                paginationInfo.textContent = 'Aucun fichier';
            }
        }
        
        // Mettre à jour les boutons de pagination
        const paginationButtons = paginationContainer.querySelector('.flex.space-x-1');
        if (paginationButtons) {
            // Vider les boutons existants
            paginationButtons.innerHTML = '';
            
            // Créer le bouton "Précédent"
            if (pagination.has_prev) {
                const prevButton = document.createElement('a');
                prevButton.className = 'pagination-prev px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50';
                prevButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="lucide lucide-arrow-left-icon lucide-arrow-left" viewBox="0 0 24 24"><path d="m12 19-7-7 7-7M19 12H5"/></svg>`;
                
                // Créer l'URL avec la page précédente
                const url = new URL(window.location.href);
                url.searchParams.set('page', pagination.prev_page);
                prevButton.href = url.toString();
                
                paginationButtons.appendChild(prevButton);
            } else {
                const prevButton = document.createElement('span');
                prevButton.className = 'pagination-prev px-4 py-2 border border-gray-200 rounded-md text-sm font-medium text-gray-400 bg-gray-50 cursor-not-allowed';
                prevButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="lucide lucide-arrow-left-icon lucide-arrow-left" viewBox="0 0 24 24"><path d="m12 19-7-7 7-7M19 12H5"/></svg>`;
                paginationButtons.appendChild(prevButton);
            }
            
            // Créer les numéros de page
            if (pagination.page_range) {
                pagination.page_range.forEach(p => {
                    const pageButton = document.createElement('a');
                    if (p === pagination.page) {
                        pageButton.className = 'pagination-page px-4 py-2 border border-sky-500 bg-sky-50 text-sky-600 rounded-md text-sm font-medium';
                    } else {
                        pageButton.className = 'pagination-page px-4 py-2 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md text-sm font-medium';
                    }
                    pageButton.textContent = p;
                    
                    // Créer l'URL avec le numéro de page
                    const url = new URL(window.location.href);
                    url.searchParams.set('page', p);
                    pageButton.href = url.toString();
                    
                    paginationButtons.appendChild(pageButton);
                });
            } else {
                // Si page_range n'est pas fourni, générer des numéros de page limités
                // Par exemple, afficher 5 pages autour de la page courante
                const startPage = Math.max(1, pagination.page - 2);
                const endPage = Math.min(pagination.pages, pagination.page + 2);
                
                for (let p = startPage; p <= endPage; p++) {
                    const pageButton = document.createElement('a');
                    if (p === pagination.page) {
                        pageButton.className = 'pagination-page px-4 py-2 border border-sky-500 bg-sky-50 text-sky-600 rounded-md text-sm font-medium';
                    } else {
                        pageButton.className = 'pagination-page px-4 py-2 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md text-sm font-medium';
                    }
                    pageButton.textContent = p;
                    
                    // Créer l'URL avec le numéro de page
                    const url = new URL(window.location.href);
                    url.searchParams.set('page', p);
                    pageButton.href = url.toString();
                    
                    paginationButtons.appendChild(pageButton);
                }
            }
            
            // Créer le bouton "Suivant"
            if (pagination.has_next) {
                const nextButton = document.createElement('a');
                nextButton.className = 'pagination-next px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50';
                nextButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="lucide lucide-arrow-right-icon lucide-arrow-right" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;
                
                // Créer l'URL avec la page suivante
                const url = new URL(window.location.href);
                url.searchParams.set('page', pagination.next_page);
                nextButton.href = url.toString();
                
                paginationButtons.appendChild(nextButton);
            } else {
                const nextButton = document.createElement('span');
                nextButton.className = 'pagination-next px-4 py-2 border border-gray-200 rounded-md text-sm font-medium text-gray-400 bg-gray-50 cursor-not-allowed';
                nextButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="lucide lucide-arrow-right-icon lucide-arrow-right" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;
                paginationButtons.appendChild(nextButton);
            }
        }
        
        // Afficher le conteneur de pagination
        paginationContainer.style.display = 'flex';
    } else if (paginationContainer) {
        // Si la pagination n'est plus nécessaire, la cacher
        paginationContainer.style.display = 'none';
    }
}

// Exemple d'utilisation pour tester
/*
updatePagination({
    page: 2,
    pages: 5,
    has_prev: true,
    has_next: true,
    prev_page: 1,
    next_page: 3,
    first_item: 11,
    last_item: 20,
    total: 47,
    page_range: [1, 2, 3, 4, 5]
});
*/