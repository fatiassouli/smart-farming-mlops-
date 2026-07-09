/* ============================================
   DASHBOARD JS — AgriSmart (VERSION CORRIGÉE)
   Données réelles du dataset par défaut,
   mises à jour après chaque prédiction.
   ============================================ */

let cropDistributionChart, topCropsChart, yieldTrendsChart, climateRadarChart;

const COLORS = {
    greens:  ['#1B4332','#2D6A4F','#40916C','#52B788','#74C69D','#95D5B2','#B7E4C7','#D8F3DC'],
    golds:   ['#F59E0B','#FBBF24','#FCD34D','#FDE68A','#FEF3C7'],
    blues:   ['#0369A1','#0284C7','#0EA5E9','#38BDF8','#7DD3FC'],
    oranges: ['#C2410C','#EA580C','#F97316','#FB923C','#FDBA74'],
};

document.addEventListener('DOMContentLoaded', function () {
    updateDateDisplay();
    loadDashboardData();
    setInterval(loadDashboardData, 60000); // refresh toutes les 60s
});

function updateDateDisplay() {
    const now = new Date();
    const dayEl  = document.getElementById('current-date');
    const fullEl = document.getElementById('current-date-full');
    if (dayEl)  dayEl.textContent  = now.toLocaleDateString('fr-FR', { weekday: 'long' });
    if (fullEl) fullEl.textContent = now.toLocaleDateString('fr-FR', { year:'numeric', month:'long', day:'numeric' });
}

async function loadDashboardData() {
    try {
        const resp = await fetch('/api/dashboard-stats');
        const data = await resp.json();
        updateKPIs(data);
        buildCharts(data);
        buildRecentTable(data.recent_predictions || []);
        updateDataSourceBadge(data);
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

function refreshDashboard() { loadDashboardData(); }

// ── KPIs ──────────────────────────────────────────────────────
function updateKPIs(data) {
    animVal('total-predictions', data.total_predictions);
    animVal('total-crops', data.total_crops);
    setElText('avg-yield', data.avg_yield.toFixed(2));
    animVal('total-countries', data.total_countries);
}

function animVal(id, end) {
    const el = document.getElementById(id);
    if (!el) return;
    const dur = 800, step = 16;
    const inc = end / (dur / step);
    let cur = 0;
    const t = setInterval(() => {
        cur = Math.min(cur + inc, end);
        el.textContent = Number.isInteger(end) ? Math.round(cur) : cur.toFixed(2);
        if (cur >= end) clearInterval(t);
    }, step);
}

function setElText(id, txt) {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
}

function updateDataSourceBadge(data) {
    const badge = document.getElementById('data-source-badge');
    if (!badge) return;
    if (data.data_source === 'predictions') {
        badge.innerHTML = `<i class="fas fa-database me-1"></i> Données : ${data.total_predictions} prédiction(s) utilisateur`;
        badge.className = 'badge bg-success ms-2';
    } else {
        const info = data.dataset_info || {};
        badge.innerHTML = `<i class="fas fa-table me-1"></i> Données du dataset (${info.crop_samples || 2200} cultures · ${info.yield_records || 56717} rendements · ${info.year_range || '1961–2016'})`;
        badge.className = 'badge bg-info text-dark ms-2';
    }
}

// ── Graphiques ────────────────────────────────────────────────
function buildCharts(data) {
    buildCropDist(data.crop_distribution);
    buildTopCrops(data.top_crops);
    buildYieldTrends(data.yield_trends);
    buildClimateRadar(data.climate_conditions);
}

function buildCropDist(d) {
    const ctx = document.getElementById('cropDistributionChart');
    if (!ctx) return;
    if (cropDistributionChart) cropDistributionChart.destroy();
    cropDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: d.labels,
            datasets: [{ data: d.data, backgroundColor: COLORS.greens, borderWidth: 2, borderColor: '#0f1a12' }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 11 } } },
                tooltip: { callbacks: { label: (c) => ` ${c.label}: ${c.parsed}` } }
            }
        }
    });
}

function buildTopCrops(d) {
    const ctx = document.getElementById('topCropsChart');
    if (!ctx) return;
    if (topCropsChart) topCropsChart.destroy();
    topCropsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: d.labels,
            datasets: [{
                label: 'Rendement moyen (t/ha)',
                data: d.data,
                backgroundColor: COLORS.golds,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#94a3b8' } } },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.05)' },
                     title: { display: true, text: 't/ha', color: '#94a3b8' } }
            }
        }
    });
}

function buildYieldTrends(d) {
    const ctx = document.getElementById('yieldTrendsChart');
    if (!ctx) return;
    if (yieldTrendsChart) yieldTrendsChart.destroy();
    yieldTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: d.labels,
            datasets: [{
                label: 'Rendement moyen mondial (t/ha)',
                data: d.data,
                borderColor: '#52B788',
                backgroundColor: 'rgba(82,183,136,0.15)',
                tension: 0.4, fill: true, pointRadius: 5,
                pointBackgroundColor: '#52B788'
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#94a3b8' } } },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.05)' },
                     title: { display: true, text: 't/ha', color: '#94a3b8' } }
            }
        }
    });
}

function buildClimateRadar(d) {
    const ctx = document.getElementById('climateRadarChart');
    if (!ctx) return;
    if (climateRadarChart) climateRadarChart.destroy();
    climateRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: d.labels,
            datasets: [{
                label: 'Conditions moyennes (dataset)',
                data: d.data,
                borderColor: '#F59E0B',
                backgroundColor: 'rgba(245,158,11,0.15)',
                pointBackgroundColor: '#F59E0B'
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#94a3b8' } } },
            scales: {
                r: {
                    ticks: { color: '#94a3b8', backdropColor: 'transparent' },
                    grid:  { color: 'rgba(148,163,184,0.1)' },
                    pointLabels: { color: '#94a3b8', font: { size: 11 } }
                }
            }
        }
    });
}

// ── Tableau des prédictions récentes ─────────────────────────
function buildRecentTable(preds) {
    const tbody = document.getElementById('recent-predictions');
    if (!tbody) return;
    if (!preds || preds.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">
            <i class="fas fa-seedling me-2"></i>Aucune prédiction encore — <a href="/prediction">Faites la première !</a>
        </td></tr>`;
        return;
    }
    tbody.innerHTML = preds.map(p => {
        const ratingColors = ['','#ef4444','#f97316','#eab308','#22c55e','#16a34a'];
        const col = ratingColors[p.rating] || '#94a3b8';
        return `<tr>
            <td>${p.date || '—'}</td>
            <td>${p.country || '—'}</td>
            <td><span style="font-size:1.1rem">${p.icon || '🌱'}</span> ${p.crop_display || p.crop || '—'}</td>
            <td><strong>${p.yield_tha || '—'} t/ha</strong></td>
            <td><span style="color:${col};font-weight:600">${p.rating_label || '—'}</span></td>
        </tr>`;
    }).join('');
}

function exportDashboardData() {
    fetch('/api/dashboard-stats').then(r => r.json()).then(data => {
        let csv = 'AgriSmart — Export Dashboard\n\n';
        csv += `Total prédictions,${data.total_predictions}\n`;
        csv += `Cultures disponibles,${data.total_crops}\n`;
        csv += `Rendement moyen (t/ha),${data.avg_yield}\n`;
        csv += `Pays analysés,${data.total_countries}\n\n`;
        csv += 'Source données,' + (data.data_source === 'predictions' ? 'Historique utilisateur' : 'Dataset agricole mondial') + '\n';

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href = url; a.download = 'agrismart_dashboard.csv';
        document.body.appendChild(a); a.click();
        document.body.removeChild(a); URL.revokeObjectURL(url);
    });
}

window.refreshDashboard = refreshDashboard;
window.exportDashboardData = exportDashboardData;
