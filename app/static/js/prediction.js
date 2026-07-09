/* ============================================
   PREDICTION JS — AgriSmart (VERSION CORRIGÉE)
   Connecté aux vrais modèles ML via /api/predict
   ============================================ */

let lastResult = null;

document.addEventListener('DOMContentLoaded', function () {
    const form     = document.getElementById('prediction-form');
    const phRange  = document.getElementById('ph');
    const phValue  = document.getElementById('phValue');
    const btnDemo  = document.getElementById('btn-demo');
    const btnReset = document.getElementById('btn-reset');

    // ── pH slider ─────────────────────────────────────────────
    phRange.addEventListener('input', function () {
        phValue.innerText = parseFloat(this.value).toFixed(1);
    });

    // ── Bouton Exemple ────────────────────────────────────────
    btnDemo.addEventListener('click', function () {
        document.getElementById('nitrogen').value    = 90;
        document.getElementById('phosphorus').value  = 42;
        document.getElementById('potassium').value   = 43;
        phRange.value    = 6.5;
        phValue.innerText = '6.5';
        document.getElementById('temperature').value = 25;
        document.getElementById('humidity').value    = 75;
        document.getElementById('rainfall').value    = 200;
        // Sélectionner Morocco
        const sel = document.getElementById('country');
        for (let i = 0; i < sel.options.length; i++) {
            if (sel.options[i].value === 'Morocco') { sel.selectedIndex = i; break; }
        }
        // Année courante
        const ySel = document.getElementById('prediction_year');
        const curY = new Date().getFullYear().toString();
        for (let i = 0; i < ySel.options.length; i++) {
            if (ySel.options[i].value === curY) { ySel.selectedIndex = i; break; }
        }
        showToast('Exemple chargé', 'Les données de test ont été insérées', 'success');
    });

    // ── Reset ─────────────────────────────────────────────────
    btnReset.addEventListener('click', function () {
        setTimeout(() => {
            phValue.innerText = '6.5';
            phRange.value = 6.5;
            document.getElementById('results-section').style.display = 'none';
            showToast('Formulaire réinitialisé', 'Tous les champs ont été remis à zéro', 'info');
        }, 10);
    });

    // ── Soumission → appel API ML ─────────────────────────────
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!validateForm()) return;

        const payload = {
            N:           parseFloat(document.getElementById('nitrogen').value),
            P:           parseFloat(document.getElementById('phosphorus').value),
            K:           parseFloat(document.getElementById('potassium').value),
            ph:          parseFloat(phRange.value),
            temperature: parseFloat(document.getElementById('temperature').value),
            humidity:    parseFloat(document.getElementById('humidity').value),
            rainfall:    parseFloat(document.getElementById('rainfall').value),
            country:     document.getElementById('country').value,
            year:        parseInt(document.getElementById('prediction_year').value),
        };

        // Loader
        Swal.fire({
            title: 'Analyse en cours…',
            text: 'Les modèles ML analysent vos données',
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            didOpen: () => Swal.showLoading()
        });

        try {
            const resp = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            Swal.close();

            if (!data.success) {
                Swal.fire({ title: 'Erreur', text: data.error || 'Erreur inconnue', icon: 'error' });
                return;
            }

            lastResult = { ...data, ...payload };
            displayResults(data, payload);

        } catch (err) {
            Swal.close();
            Swal.fire({ title: 'Erreur réseau', text: 'Impossible de contacter le serveur', icon: 'error' });
        }
    });
});

// ── Validation ─────────────────────────────────────────────────
function validateForm() {
    const required = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'rainfall', 'country'];
    let ok = true;
    required.forEach(id => {
        const el = document.getElementById(id);
        const wrap = el.closest('.input-group-agriculture');
        if (!el.value || el.value.trim() === '') {
            if (wrap) wrap.classList.add('is-invalid');
            ok = false;
        } else {
            if (wrap) wrap.classList.remove('is-invalid');
        }
    });
    if (!ok) {
        Swal.fire({
            title: 'Champs incomplets',
            text: 'Veuillez remplir tous les champs obligatoires',
            icon: 'warning',
            confirmButtonColor: '#1B4332'
        });
    }
    return ok;
}

// ── Affichage des résultats ────────────────────────────────────
function displayResults(data, payload) {
    // Basique
    document.getElementById('res-icon').textContent       = data.icon || '🌱';
    document.getElementById('res-crop').textContent       = data.crop_display || data.crop;
    document.getElementById('res-confidence').textContent = data.confidence;
    document.getElementById('res-yield-tha').textContent  = data.yield_tha;
    document.getElementById('res-yield-hgha').textContent = Number(data.yield_hgha).toLocaleString('fr-FR');
    document.getElementById('res-country').textContent    = data.country;
    document.getElementById('res-year').textContent       = data.year;
    document.getElementById('res-reg-crop').textContent   = data.reg_crop;
    document.getElementById('res-reg-crop2').textContent  = data.reg_crop;
    document.getElementById('res-rating-label').textContent = data.rating_label;

    // Étoiles
    const stars = '⭐'.repeat(data.rating) + '☆'.repeat(5 - data.rating);
    document.getElementById('res-stars').textContent = stars;

    // Barre de progression (max 15 t/ha)
    const pct = Math.min((data.yield_tha / 15) * 100, 100).toFixed(1);
    const bar = document.getElementById('res-progress');
    bar.style.width = '0%';
    setTimeout(() => {
        bar.style.transition = 'width 1s ease-out';
        bar.style.width = pct + '%';
    }, 300);

    // Paramètres saisis
    document.getElementById('p-N').textContent       = payload.N;
    document.getElementById('p-P').textContent       = payload.P;
    document.getElementById('p-K').textContent       = payload.K;
    document.getElementById('p-ph').textContent      = payload.ph;
    document.getElementById('p-temp').textContent    = payload.temperature + '°C';
    document.getElementById('p-hum').textContent     = payload.humidity + '%';
    document.getElementById('p-rain').textContent    = payload.rainfall + ' mm';
    document.getElementById('p-country').textContent = payload.country;

    // Texte contextuel
    document.getElementById('res-info-text').innerHTML =
        `Cette recommandation est générée par deux modèles ML : un <strong>classifieur Random Forest</strong> 
         qui a identifié <strong>${data.crop_display || data.crop}</strong> parmi ${22} cultures 
         (confiance : ${data.confidence}%), et un <strong>régresseur</strong> qui estime le rendement 
         en tonnes/ha pour <strong>${data.country}</strong> en <strong>${data.year}</strong>. 
         La culture de régression utilisée est <em>${data.reg_crop}</em>. 
         Les résultats sont indicatifs et doivent être complétés par l'expertise d'un agronome.`;

    // Afficher la section résultats
    const section = document.getElementById('results-section');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Export CSV ─────────────────────────────────────────────────
function exportResultsPage() {
    if (!lastResult) { showToast('Aucune prédiction', 'Lancez d\'abord une prédiction', 'warning'); return; }
    const r = lastResult;
    let csv = 'AgriSmart — Résultat de Prédiction\n\n';
    csv += `Date,${new Date().toLocaleString('fr-FR')}\n`;
    csv += `Culture recommandée,${r.crop_display || r.crop}\n`;
    csv += `Confiance (%),${r.confidence}\n`;
    csv += `Rendement estimé (t/ha),${r.yield_tha}\n`;
    csv += `Rendement brut (kg/ha),${r.yield_hgha}\n`;
    csv += `Évaluation,${r.rating_label}\n`;
    csv += `Pays,${r.country}\n`;
    csv += `Année,${r.year}\n\n`;
    csv += `Paramètre,Valeur\n`;
    csv += `Azote (N),${r.N}\n`;
    csv += `Phosphore (P),${r.P}\n`;
    csv += `Potassium (K),${r.K}\n`;
    csv += `pH,${r.ph}\n`;
    csv += `Température (°C),${r.temperature}\n`;
    csv += `Humidité (%),${r.humidity}\n`;
    csv += `Précipitations (mm),${r.rainfall}\n`;

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `agrismart_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Export réussi', 'Le fichier CSV a été téléchargé', 'success');
}

function scrollToForm() {
    document.getElementById('prediction-form').scrollIntoView({ behavior: 'smooth' });
}

function showToast(title, text, icon) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({ title, text, icon, toast: true, position: 'top-end',
                    showConfirmButton: false, timer: 2500, timerProgressBar: true });
    }
}

window.exportResultsPage = exportResultsPage;
window.scrollToForm = scrollToForm;
