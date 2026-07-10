"""
AgriSmart – Flask Web Application (VERSION CORRIGÉE)
Connecte les vrais modèles ML (classification + régression) à l'interface web.
Usage: python app.py depuis le dossier app/
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
import sys

# ── Résoudre le chemin vers utils/ ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils.predictor import (
    predict_crop,
    predict_yield,
    CROP_CLASSES,
    COUNTRIES,
    get_model_status,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "agrismart-secret-2026"

# Stockage des prédictions (fichier JSON dans le dossier app)
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "predictions.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# ── Données réelles du dataset pour le dashboard (par défaut) ───
DATASET_CROP_DISTRIBUTION = {
    "rice": 100,
    "maize": 100,
    "chickpea": 100,
    "kidneybeans": 100,
    "pigeonpeas": 100,
    "mothbeans": 100,
    "mungbean": 100,
    "blackgram": 100,
    "lentil": 100,
    "pomegranate": 100,
    "banana": 100,
    "mango": 100,
    "grapes": 100,
    "watermelon": 100,
    "muskmelon": 100,
    "apple": 100,
    "orange": 100,
    "papaya": 100,
    "coconut": 100,
    "cotton": 100,
    "jute": 100,
    "coffee": 100,
}

DATASET_YIELD_BY_CROP = {
    "Cassava": 9.28,
    "Maize": 2.94,
    "Plantains and others": 8.63,
    "Potatoes": 15.01,
    "Rice, paddy": 3.02,
    "Sorghum": 1.71,
    "Soybeans": 1.42,
    "Sweet potatoes": 8.99,
    "Wheat": 2.46,
    "Yams": 8.09,
}

DATASET_YEAR_MIN = 1961
DATASET_YEAR_MAX = 2030
CURRENT_YEAR = datetime.now().year

# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════


def load_predictions():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_prediction(record):
    preds = load_predictions()
    preds.insert(0, record)
    preds = preds[:200]
    # ensure_ascii=True encode les emojis en \uXXXX — aucun problème cp1252 sur Windows
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(preds, f, ensure_ascii=True, indent=2)


def rate_yield(yield_tha):
    if yield_tha < 1:
        return 1, "Faible"
    if yield_tha < 2.5:
        return 2, "Moyen"
    if yield_tha < 4:
        return 3, "Bon"
    if yield_tha < 6:
        return 4, "Très bon"
    return 5, "Excellent"


# ════════════════════════════════════════════════════════════════
# ROUTES PAGES
# ════════════════════════════════════════════════════════════════


@app.route("/")
def home():
    # Dict complet attendu par home.html : {nom: {description, avg_yield, image}}
    CROPS_DATA = {
        "rice": {
            "description": "Variété à haut rendement pour conditions humides",
            "avg_yield": 4.5,
        },
        "wheat": {
            "description": "Blé résistant à la sécheresse, climat tempéré",
            "avg_yield": 3.2,
        },
        "maize": {
            "description": "Maïs à croissance rapide, rendement élevé",
            "avg_yield": 5.8,
        },
        "cotton": {
            "description": "Coton de qualité supérieure pour le textile",
            "avg_yield": 2.1,
        },
        "coffee": {
            "description": "Café Arabica pour le marché d'exportation",
            "avg_yield": 1.5,
        },
        "banana": {
            "description": "Banane tropicale sucrée pour le marché local",
            "avg_yield": 35.0,
        },
        "mango": {
            "description": "Mangue Alphonso à haute valeur marchande",
            "avg_yield": 12.0,
        },
        "coconut": {
            "description": "Noix de coco multi-usage pour divers produits",
            "avg_yield": 80.0,
        },
        "chickpea": {
            "description": "Pois chiche riche en protéines, sol aride",
            "avg_yield": 1.2,
        },
        "kidneybeans": {
            "description": "Haricots rouges riches en nutriments",
            "avg_yield": 1.5,
        },
        "lentil": {
            "description": "Lentilles légumineuses à haute valeur nutritive",
            "avg_yield": 1.0,
        },
        "pomegranate": {
            "description": "Grenade antioxydante à haute valeur",
            "avg_yield": 8.0,
        },
        "grapes": {
            "description": "Raisins pour vins fins et raisins secs",
            "avg_yield": 15.0,
        },
        "watermelon": {
            "description": "Pastèque rafraîchissante, climat chaud",
            "avg_yield": 20.0,
        },
        "muskmelon": {
            "description": "Melon savoureux pour marchés locaux",
            "avg_yield": 14.0,
        },
        "apple": {"description": "Pomme croquante pour exportation", "avg_yield": 25.0},
        "orange": {
            "description": "Orange riche en vitamine C, demande élevée",
            "avg_yield": 20.0,
        },
        "papaya": {
            "description": "Papaye tropicale riche en enzymes digestives",
            "avg_yield": 35.0,
        },
        "pigeonpeas": {
            "description": "Pois d'Angole, légumineuse résistante",
            "avg_yield": 1.3,
        },
        "mothbeans": {
            "description": "Haricot mite, excellente résistance sécheresse",
            "avg_yield": 0.9,
        },
        "mungbean": {
            "description": "Haricot mungo, germination rapide",
            "avg_yield": 1.5,
        },
        "blackgram": {
            "description": "Gramme noir riche en protéines végétales",
            "avg_yield": 1.0,
        },
        "jute": {
            "description": "Jute fibre naturelle pour textiles et emballages",
            "avg_yield": 2.5,
        },
    }
    return render_template("pages/home.html", crops=CROPS_DATA)


@app.route("/prediction")
def prediction():
    years = list(range(DATASET_YEAR_MIN, DATASET_YEAR_MAX + 1))
    return render_template(
        "pages/prediction.html",
        countries=COUNTRIES,
        years=years,
        current_year=CURRENT_YEAR,
    )


@app.route("/catalog")
def catalog():
    """Full crop catalog page"""
    return render_template("pages/catalog.html", crops=CROPS_DATA)


@app.route("/dashboard")
def dashboard():
    return render_template("pages/dashboard.html")


@app.route("/results")
def results():
    return render_template("pages/results.html")


@app.route("/history")
def history():
    return render_template("pages/history.html")


# ════════════════════════════════════════════════════════════════
# API – PRÉDICTION ML (POST)
# ════════════════════════════════════════════════════════════════


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Appelle les vrais modèles ML et retourne le résultat complet.
    Body JSON: {N, P, K, temperature, humidity, ph, rainfall, country, year}
    """
    data = request.get_json(force=True) or {}
    try:
        N = float(data["N"])
        P = float(data["P"])
        K = float(data["K"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        ph = float(data["ph"])
        rainfall = float(data["rainfall"])
        country = str(data.get("country", "Morocco"))
        year = int(data.get("year", CURRENT_YEAR))
    except (KeyError, ValueError) as e:
        return jsonify({"success": False, "error": f"Paramètre invalide : {e}"}), 400

    # ── Étape 1 : Classification ─────────────────────────────────
    crop_name, confidence, icon = predict_crop(
        N, P, K, temperature, humidity, ph, rainfall
    )

    # ── Étape 2 : Régression ─────────────────────────────────────
    yield_tha, yield_hgha, reg_crop = predict_yield(crop_name, country, year)

    rating, rating_label = rate_yield(yield_tha)

    # ── Sauvegarde historique ────────────────────────────────────
    record = {
        "id": datetime.now().timestamp(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crop": crop_name,
        "crop_display": crop_name.capitalize(),
        "icon": icon,
        "confidence": confidence,
        "yield_tha": yield_tha,
        "yield_hgha": int(yield_hgha),
        "reg_crop": reg_crop,
        "rating": rating,
        "rating_label": rating_label,
        "country": country,
        "year": year,
        "N": N,
        "P": P,
        "K": K,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall,
    }
    save_prediction(record)

    return jsonify({"success": True, **record})


# ════════════════════════════════════════════════════════════════
# API – HISTORIQUE
# ════════════════════════════════════════════════════════════════


@app.route("/api/predictions")
def get_predictions():
    return jsonify(load_predictions())


# ════════════════════════════════════════════════════════════════
# API – DASHBOARD STATS
# ════════════════════════════════════════════════════════════════


@app.route("/api/dashboard-stats")
def dashboard_stats():
    """
    Retourne les stats du dashboard.
    Par défaut : données du dataset.
    Après prédictions : données réelles + historique.
    """
    preds = load_predictions()

    # ── Distribution des cultures ────────────────────────────────
    if preds:
        # Basé sur l'historique des prédictions
        crop_counts = {}
        for p in preds:
            c = p.get("crop_display", p.get("crop", "Unknown")).capitalize()
            crop_counts[c] = crop_counts.get(c, 0) + 1
        top_crops = sorted(crop_counts.items(), key=lambda x: -x[1])[:8]
        dist_labels = [x[0] for x in top_crops]
        dist_data = [x[1] for x in top_crops]
    else:
        # Données réelles du dataset (équilibré 100 par culture)
        top_crops_dataset = [
            ("Rice", 100),
            ("Maize", 100),
            ("Cotton", 100),
            ("Coffee", 100),
            ("Banana", 100),
            ("Wheat", 100),
            ("Coconut", 100),
            ("Mango", 100),
        ]
        dist_labels = [x[0] for x in top_crops_dataset]
        dist_data = [x[1] for x in top_crops_dataset]

    # ── Rendement moyen par culture (données réelles dataset) ───
    yield_labels = list(DATASET_YIELD_BY_CROP.keys())
    yield_data = list(DATASET_YIELD_BY_CROP.values())

    # ── Tendances des rendements (évolution annuelle dataset) ───
    # Rendement mondial moyen par décennie depuis les données
    trend_labels = [
        "1961-1970",
        "1971-1980",
        "1981-1990",
        "1991-2000",
        "2001-2010",
        "2011-2016",
    ]
    trend_data = [1.8, 2.1, 2.6, 3.1, 3.7, 4.2]  # t/ha moyennes mondiales

    # ── Conditions climatiques moyennes du dataset ───────────────
    import pandas as pd
    import os as _os

    # Chercher le CSV dans plusieurs emplacements
    _data_candidates = [
        _os.path.join(BASE_DIR, "data", "Crop_recommendation.csv"),
        _os.path.join(
            _os.path.dirname(BASE_DIR),
            "projet_ML_akhirversion",
            "data",
            "Crop_recommendation.csv",
        ),
        _os.path.join(_os.path.dirname(BASE_DIR), "data", "Crop_recommendation.csv"),
    ]
    crop_csv = next(
        (p for p in _data_candidates if _os.path.exists(p)), _data_candidates[0]
    )
    try:
        df = pd.read_csv(crop_csv)
        climate_means = {
            "Température (°C)": round(float(df["temperature"].mean()), 1),
            "Humidité (%)": round(float(df["humidity"].mean()), 1),
            "Pluie/10 (mm)": round(float(df["rainfall"].mean() / 10), 1),
            "pH×10": round(float(df["ph"].mean() * 10), 1),
            "Azote (N)": round(float(df["N"].mean()), 1),
            "Phosphore (P)": round(float(df["P"].mean()), 1),
            "Potassium (K)": round(float(df["K"].mean()), 1),
        }
    except:
        climate_means = {
            "Température (°C)": 25.6,
            "Humidité (%)": 71.5,
            "Pluie/10 (mm)": 10.3,
            "pH×10": 62.0,
            "Azote (N)": 50.6,
            "Phosphore (P)": 53.4,
            "Potassium (K)": 48.1,
        }

    # ── Pays analysés (des prédictions) ─────────────────────────
    countries_in_preds = list({p.get("country", "") for p in preds if p.get("country")})
    total_countries = len(countries_in_preds) if countries_in_preds else len(COUNTRIES)

    avg_yield = (
        round(sum(p.get("yield_tha", 0) for p in preds) / max(len(preds), 1), 2)
        if preds
        else round(sum(DATASET_YIELD_BY_CROP.values()) / len(DATASET_YIELD_BY_CROP), 2)
    )
    avg_conf = (
        round(sum(p.get("confidence", 0) for p in preds) / max(len(preds), 1), 1)
        if preds
        else 0
    )

    return jsonify(
        {
            "total_predictions": len(preds),
            "total_crops": len(CROP_CLASSES),
            "avg_yield": avg_yield,
            "avg_confidence": avg_conf,
            "total_countries": total_countries,
            "data_source": "predictions" if preds else "dataset",
            "dataset_info": {
                "crop_samples": 2200,
                "yield_records": 56717,
                "year_range": f"{DATASET_YEAR_MIN}–2016",
                "countries": len(COUNTRIES),
            },
            "crop_distribution": {"labels": dist_labels, "data": dist_data},
            "top_crops": {"labels": yield_labels, "data": yield_data},
            "yield_trends": {"labels": trend_labels, "data": trend_data},
            "climate_conditions": {
                "labels": list(climate_means.keys()),
                "data": list(climate_means.values()),
            },
            "recent_predictions": preds[:5],
        }
    )


# ════════════════════════════════════════════════════════════════
# API – STATUT DES MODÈLES
# ════════════════════════════════════════════════════════════════


@app.route("/api/model-status")
def model_status():
    return jsonify(get_model_status())


if __name__ == "__main__":
    print("🌱 AgriSmart démarré sur http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)


# ── Effacer l'historique ────────────────────────────────────────
@app.route("/api/predictions/clear", methods=["POST"])
def clear_predictions():
    with open(DATA_FILE, "w") as f:
        json.dump([], f)
    return jsonify({"success": True})
