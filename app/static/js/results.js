/* ============================================
   RESULTS JS - Smart Agriculture AI
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Animation des barres de progression
    animateProgressBars();
    
    // Gestion de l'export
    setupExportButton();
});

/**
 * Anime les barres de progression avec un délai
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    
    progressBars.forEach((bar, index) => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = targetWidth;
        }, 300 + (index * 200));
    });
}

/**
 * Configure le bouton d'export
 */
function setupExportButton() {
    const exportBtn = document.querySelector('.btn-outline-agriOrder');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportResults);
    }
}

/**
 * Exporte les résultats en PDF
 */
function exportResults() {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Export des résultats',
            text: 'Choisissez le format d\'export',
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#1e5e41',
            cancelButtonColor: '#64748b',
            confirmButtonText: 'PDF',
            cancelButtonText: 'Annuler',
            showDenyButton: true,
            denyButtonColor: '#0284c7',
            denyButtonText: 'CSV'
        }).then((result) => {
            if (result.isConfirmed) {
                // Export PDF
                window.print();
            } else if (result.isDenied) {
                // Export CSV
                generateCSV();
            }
        });
    } else {
        // Fallback
        window.print();
    }
}

/**
 * Génère un fichier CSV à partir des résultats
 */
function generateCSV() {
    // Récupération des données depuis la page
    const cropName = document.querySelector('.crop-title')?.textContent || 'N/A';
    const confidence = document.querySelector('.confidence-badge')?.textContent?.trim() || 'N/A';
    const yieldValue = document.querySelector('.yield-value')?.textContent?.trim() || 'N/A';
    const country = document.querySelector('.yield-context')?.textContent?.trim() || 'N/A';
    
    // Récupération des paramètres
    const params = [];
    document.querySelectorAll('.parameter-item').forEach(item => {
        const label = item.querySelector('.param-label')?.textContent || '';
        const value = item.querySelector('.param-value')?.textContent || '';
        params.push({ label, value });
    });
    
    // Construction du CSV
    let csv = 'Résultats de la Prédiction Agricole\n\n';
    csv += `Culture recommandée,${cropName}\n`;
    csv += `Confiance,${confidence}\n`;
    csv += `Rendement estimé,${yieldValue}\n`;
    csv += `Localisation,${country}\n\n`;
    csv += 'Paramètre,Valeur\n';
    params.forEach(p => {
        csv += `${p.label},${p.value}\n`;
    });
    
    // Téléchargement
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `prediction_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    // Notification
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Export réussi',
            text: 'Le fichier CSV a été téléchargé',
            icon: 'success',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2500,
            timerProgressBar: true
        });
    }
}

/**
 * Fonction pour imprimer les résultats
 */
function printResults() {
    window.print();
}

/**
 * Fonction pour retourner à la page de prédiction
 */
function newPrediction() {
    window.location.href = '/prediction';
}

// Exposition des fonctions globales
window.exportResults = exportResults;
window.printResults = printResults;
window.newPrediction = newPrediction;