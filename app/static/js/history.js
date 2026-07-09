/* ============================================
   HISTORY JS — AgriSmart (VERSION CORRIGÉE)
   ============================================ */

let historyData = [];

document.addEventListener('DOMContentLoaded', function () {
    loadHistoryData();
});

async function loadHistoryData() {
    try {
        const resp = await fetch('/api/predictions');
        historyData = await resp.json();
        renderTable(historyData);
    } catch (err) {
        console.error('Erreur chargement historique:', err);
        document.getElementById('history-tbody').innerHTML =
            '<tr><td colspan="10" class="text-center text-danger py-4">Erreur de chargement</td></tr>';
    }
}

function renderTable(data) {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center py-5">
            <div class="empty-state">
                <i class="fas fa-chart-line fa-2x mb-3 text-muted"></i>
                <p>Aucune prédiction pour le moment</p>
                <a href="/prediction" class="btn-empty-action"><i class="fas fa-plus-circle me-2"></i>Faire une prédiction</a>
            </div></td></tr>`;
        return;
    }
    const ratingColors = ['','#ef4444','#f97316','#eab308','#22c55e','#16a34a'];
    tbody.innerHTML = data.map((p, i) => `
        <tr>
            <td>${i + 1}</td>
            <td><small>${p.date || '—'}</small></td>
            <td><span style="font-size:1.2rem">${p.icon || '🌱'}</span> <strong>${(p.crop_display || p.crop || '—')}</strong></td>
            <td><strong>${p.yield_tha || '—'} t/ha</strong></td>
            <td>${p.temperature != null ? p.temperature + '°C' : '—'}</td>
            <td>${p.humidity != null ? p.humidity + '%' : '—'}</td>
            <td>${p.rainfall != null ? p.rainfall + ' mm' : '—'}</td>
            <td>${p.N != null ? p.N + '-' + p.P + '-' + p.K : '—'}</td>
            <td>${p.ph != null ? p.ph : '—'}</td>
            <td><span style="color:${ratingColors[p.rating] || '#94a3b8'};font-weight:600">${p.rating_label || '—'}</span></td>
        </tr>
    `).join('');
}

function filterTable() {
    const q = (document.getElementById('search-input')?.value || '').toLowerCase();
    const filtered = historyData.filter(p =>
        (p.crop || '').toLowerCase().includes(q) ||
        (p.country || '').toLowerCase().includes(q) ||
        (p.rating_label || '').toLowerCase().includes(q)
    );
    renderTable(filtered);
}

function clearHistory() {
    if (!confirm('Supprimer tout l\'historique ? Cette action est irréversible.')) return;
    fetch('/api/predictions/clear', { method: 'POST' })
        .then(() => { historyData = []; renderTable([]); })
        .catch(() => alert('Fonctionnalité disponible en local uniquement.'));
}

window.filterTable  = filterTable;
window.clearHistory = clearHistory;
