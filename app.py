"""
AgriSmart – Flask Web Application
Connecte les modèles ML (classification + régression) à une interface web.

Usage:
    python app.py
Puis ouvrir http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify
import os
import datetime

from utils.predictor import predict_crop, predict_yield, COUNTRIES

# ── Configuration Flask ──────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))


# ════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════


@app.route("/")
def index():
    """Page d'accueil."""
    return render_template("index.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    """Page de prédiction : formulaire + traitement."""
    current_year = datetime.datetime.now().year
    DATASET_YEAR_MIN = 2000
    DATASET_YEAR_MAX = 2026
    years = list(range(DATASET_YEAR_MIN, DATASET_YEAR_MAX + 1))

    if request.method == "GET":
        return render_template(
            "predict.html",
            countries=COUNTRIES,
            years=years,
            current_year=current_year,
        )

    # ── POST : exécuter le pipeline complet ──────────────────────
    try:
        N = float(request.form["N"])
        P = float(request.form["P"])
        K = float(request.form["K"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        ph = float(request.form["ph"])
        rainfall = float(request.form["rainfall"])
        country = request.form["country"]
        year = int(request.form["year"])
    except (KeyError, ValueError) as e:
        return render_template(
            "predict.html",
            error=f"Entrée invalide : {e}",
            countries=COUNTRIES,
            years=years,
            current_year=current_year,
        )

    # Étape 1 — Classification
    crop_name, confidence, icon = predict_crop(
        N, P, K, temperature, humidity, ph, rainfall
    )

    # Étape 2 — Régression
    yield_tha, yield_hgha, reg_crop = predict_yield(crop_name, country, year)

    # Évaluation qualitative
    if yield_tha < 1:
        rating, rating_label = 1, "Faible"
    elif yield_tha < 2.5:
        rating, rating_label = 2, "Moyen"
    elif yield_tha < 4:
        rating, rating_label = 3, "Bon"
    elif yield_tha < 6:
        rating, rating_label = 4, "Très bon"
    else:
        rating, rating_label = 5, "Excellent"

    return render_template(
        "result.html",
        # Entrées réaffichées
        N=N,
        P=P,
        K=K,
        temperature=temperature,
        humidity=humidity,
        ph=ph,
        rainfall=rainfall,
        country=country,
        year=year,
        # Classification
        crop_name=crop_name.capitalize(),
        crop_name_raw=crop_name,
        confidence=confidence,
        icon=icon,
        # Régression
        yield_tha=yield_tha,
        yield_hgha=int(yield_hgha),
        reg_crop=reg_crop,
        # Évaluation
        rating=rating,
        rating_label=rating_label,
        rating_stars="⭐" * rating + "☆" * (5 - rating),
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Endpoint API (optionnel, pour AJAX)."""
    data = request.get_json(force=True)
    try:
        crop_name, confidence, icon = predict_crop(
            float(data["N"]),
            float(data["P"]),
            float(data["K"]),
            float(data["temperature"]),
            float(data["humidity"]),
            float(data["ph"]),
            float(data["rainfall"]),
        )
        yield_tha, yield_hgha, reg_crop = predict_yield(
            crop_name, data.get("country", "Morocco"), int(data.get("year", 2025))
        )
        return jsonify(
            {
                "crop": crop_name,
                "confidence": confidence,
                "icon": icon,
                "yield_tha": yield_tha,
                "yield_hgha": yield_hgha,
                "reg_crop": reg_crop,
                "status": "ok",
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ════════════════════════════════════════════════════════════════
# LANCEMENT
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
