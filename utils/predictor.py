"""
AgriSmart — ML Predictor Module
Charge les modèles entraînés depuis artifacts/ et fournit les fonctions de prédiction.
"""

import os
import numpy as np
import joblib

# ════════════════════════════════════════════════════════════════
# CHEMINS DES ARTIFACTS
# ════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chercher les artifacts dans plusieurs emplacements possibles :
# 1. projet_ML_fixed/artifacts/  (dossier corrigé)
# 2. projet_ML_akhirversion/artifacts/  (dossier original — contient reg_best_model.pkl 600MB)
# 3. ../artifacts/  (si lancé depuis app/)
_candidates = [
    os.path.join(BASE_DIR, "artifacts"),
    os.path.join(os.path.dirname(BASE_DIR), "projet_ML_akhirversion", "artifacts"),
    os.path.join(os.path.dirname(BASE_DIR), "artifacts"),
    os.path.join(BASE_DIR, "..", "artifacts"),
]

def _find_artifacts_dir():
    for path in _candidates:
        p = os.path.normpath(path)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "cls_best_model.pkl")):
            return p
    # Fallback : premier candidat
    return os.path.normpath(_candidates[0])

ARTIFACTS_DIR = _find_artifacts_dir()
print(f"[AgriSmart] Artifacts chargés depuis : {ARTIFACTS_DIR}")

# ── Classification artifacts ────────────────────────────────────
CLS_MODEL_PATH         = os.path.join(ARTIFACTS_DIR, "cls_best_model.pkl")
CLS_SCALER_PATH        = os.path.join(ARTIFACTS_DIR, "cls_scaler.pkl")
CLS_LABEL_ENCODER_PATH = os.path.join(ARTIFACTS_DIR, "cls_label_encoder.pkl")
CLS_FEATURE_COLS_PATH  = os.path.join(ARTIFACTS_DIR, "cls_feature_columns.pkl")

# ── Regression artifacts ────────────────────────────────────────
REG_MODEL_PATH        = os.path.join(ARTIFACTS_DIR, "reg_best_model.pkl")
REG_SCALER_PATH       = os.path.join(ARTIFACTS_DIR, "reg_scaler.pkl")
REG_OHE_PATH          = os.path.join(ARTIFACTS_DIR, "reg_ohe_item.pkl")
REG_FEATURE_COLS_PATH = os.path.join(ARTIFACTS_DIR, "reg_feature_columns.pkl")
REG_AREA_MEANS_PATH   = os.path.join(ARTIFACTS_DIR, "reg_area_means.pkl")


# ════════════════════════════════════════════════════════════════
# CHARGEMENT DES MODÈLES (avec fallback mock)
# ════════════════════════════════════════════════════════════════

def _safe_load(path, name):
    """Charge un fichier pickle avec gestion d'erreur."""
    try:
        return joblib.load(path)
    except FileNotFoundError:
        print(f"⚠️  Artifact manquant : {name} ({path})")
        return None
    except Exception as e:
        print(f"⚠️  Erreur chargement {name} : {e}")
        return None


# Classification
_cls_model        = _safe_load(CLS_MODEL_PATH, "cls_model")
_cls_scaler       = _safe_load(CLS_SCALER_PATH, "cls_scaler")
_cls_label_enc    = _safe_load(CLS_LABEL_ENCODER_PATH, "cls_label_encoder")
_cls_feature_cols = _safe_load(CLS_FEATURE_COLS_PATH, "cls_feature_cols")

# Regression
_reg_model        = _safe_load(REG_MODEL_PATH, "reg_model")
_reg_scaler       = _safe_load(REG_SCALER_PATH, "reg_scaler")
_reg_ohe          = _safe_load(REG_OHE_PATH, "reg_ohe")
_reg_feature_cols = _safe_load(REG_FEATURE_COLS_PATH, "reg_feature_cols")
_reg_area_means   = _safe_load(REG_AREA_MEANS_PATH, "reg_area_means")

# ════════════════════════════════════════════════════════════════
# CORRECTION 1 — Convertir _reg_area_means en dict Python
# (joblib sauvegarde une pandas Series → .keys() ambigü en bool)
# ════════════════════════════════════════════════════════════════
if _reg_area_means is not None:
    import pandas as pd
    if isinstance(_reg_area_means, pd.Series):
        _reg_area_means = _reg_area_means.to_dict()


# ════════════════════════════════════════════════════════════════
# CONSTANTES & MAPPINGS
# ════════════════════════════════════════════════════════════════

# Classes de culture (depuis le label encoder)
CROP_CLASSES = list(_cls_label_enc.classes_) if _cls_label_enc is not None else [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas",
    "mothbeans", "mungbean", "blackgram", "lentil", "pomegranate",
    "banana", "mango", "grapes", "watermelon", "muskmelon",
    "apple", "orange", "papaya", "coconut", "cotton",
    "jute", "coffee"
]

# ════════════════════════════════════════════════════════════════
# CORRECTION 2 — Utiliser "is not None" au lieu de vérité booléenne
# sur _reg_area_means (maintenant dict, mais sécurisé partout)
# ════════════════════════════════════════════════════════════════
COUNTRIES = sorted(_reg_area_means.keys()) if _reg_area_means is not None else [
    "Afghanistan", "Albania", "Algeria", "Angola", "Argentina", "Armenia", "Australia",
    "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Belarus", "Belgium",
    "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana",
    "Brazil", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
    "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia",
    "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji",
    "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece",
    "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Kyrgyzstan",
    "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania",
    "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta",
    "Mauritania", "Mauritius", "Mexico", "Moldova", "Mongolia", "Montenegro",
    "Morocco", "Mozambique", "Myanmar", "Namibia", "Nepal", "Netherlands",
    "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "Norway",
    "Oman", "Pakistan", "Panama", "Papua New Guinea", "Paraguay", "Peru",
    "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
    "Saudi Arabia", "Senegal", "Serbia", "Sierra Leone", "Singapore", "Slovakia",
    "Slovenia", "Somalia", "South Africa", "South Korea", "Spain", "Sri Lanka",
    "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania",
    "Thailand", "Timor-Leste", "Togo", "Trinidad and Tobago", "Tunisia", "Turkey",
    "Turkmenistan", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States", "Uruguay", "Uzbekistan", "Venezuela", "Vietnam", "Yemen",
    "Zambia", "Zimbabwe"
]

# ════════════════════════════════════════════════════════════════
# CORRECTION 3 — Utiliser "is not None" pour _reg_ohe aussi
# ════════════════════════════════════════════════════════════════
REG_CROPS = list(_reg_ohe.categories_[0]) if _reg_ohe is not None else [
    "Rice, paddy", "Maize", "Wheat", "Soybeans", "Sorghum",
    "Cassava", "Plantains and others", "Barley"
]

# Mapping classification → régression
CROP_TO_REG = {
    "rice":        "Rice, paddy",
    "maize":       "Maize",
    "chickpea":    "Wheat",
    "kidneybeans": "Soybeans",
    "pigeonpeas":  "Sorghum",
    "mothbeans":   "Soybeans",
    "mungbean":    "Soybeans",
    "blackgram":   "Soybeans",
    "lentil":      "Wheat",
    "pomegranate": "Cassava",
    "banana":      "Plantains and others",
    "mango":       "Cassava",
    "grapes":      "Cassava",
    "watermelon":  "Cassava",
    "muskmelon":   "Cassava",
    "apple":       "Wheat",
    "orange":      "Cassava",
    "papaya":      "Cassava",
    "coconut":     "Cassava",
    "cotton":      "Soybeans",
    "jute":        "Soybeans",
    "coffee":      "Cassava",
}

# Icônes par culture
CROP_ICONS = {
    "rice": "🌾", "maize": "🌽", "chickpea": "🟡", "kidneybeans": "🫘",
    "pigeonpeas": "🌱", "mothbeans": "🌿", "mungbean": "💚", "blackgram": "⚫",
    "lentil": "🔴", "pomegranate": "🍎", "banana": "🍌", "mango": "🥭",
    "grapes": "🍇", "watermelon": "🍉", "muskmelon": "🍈", "apple": "🍏",
    "orange": "🍊", "papaya": "🧡", "coconut": "🥥", "cotton": "🌸",
    "jute": "🌾", "coffee": "☕",
}


# ════════════════════════════════════════════════════════════════
# FONCTIONS DE PRÉDICTION
# ════════════════════════════════════════════════════════════════

def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Étape 1 — Classification : prédit la meilleure culture.

    Args:
        N, P, K: Teneurs en azote, phosphore, potassium
        temperature: Température (°C)
        humidity: Humidité (%)
        ph: pH du sol
        rainfall: Précipitations (mm)

    Returns:
        tuple: (crop_name: str, probability: float, icon: str)
    """
    NPK_total     = N + P + K
    NP_ratio      = N / (P + 1)
    NK_ratio      = N / (K + 1)
    heat_humidity = temperature * humidity
    rain_temp     = rainfall * temperature

    import pandas as pd
    row_cls = {'N': N, 'P': P, 'K': K, 'temperature': temperature,
               'humidity': humidity, 'ph': ph, 'rainfall': rainfall,
               'NPK_total': NPK_total, 'NP_ratio': NP_ratio, 'NK_ratio': NK_ratio,
               'heat_humidity': heat_humidity, 'rain_temp': rain_temp}
    x = pd.DataFrame([row_cls], columns=_cls_feature_cols if _cls_feature_cols else list(row_cls.keys()))

    if _cls_model is not None and _cls_scaler is not None:
        x_scaled  = _cls_scaler.transform(x)
        pred_enc  = _cls_model.predict(x_scaled)[0]
        crop_name = _cls_label_enc.inverse_transform([pred_enc])[0]
        try:
            proba = float(np.max(_cls_model.predict_proba(x_scaled)))
        except AttributeError:
            proba = 1.0
    else:
        crop_name, proba = _mock_crop_prediction(N, P, K, temperature, humidity, ph, rainfall)

    icon = CROP_ICONS.get(crop_name, "🌱")
    return crop_name, round(proba * 100, 1), icon


def predict_yield(crop_name, country, year):
    """
    Étape 2 — Régression : estime le rendement (t/ha).

    Args:
        crop_name: Nom de la culture (classification)
        country: Pays
        year: Année

    Returns:
        tuple: (yield_tha: float, yield_hgha: float, reg_crop: str)
    """
    reg_crop = CROP_TO_REG.get(crop_name.lower(), "Wheat")

    if _reg_model is not None and _reg_scaler is not None and _reg_area_means is not None:
        import pandas as pd

        # --- Area encoding (supporte dict ET pandas Series) ---
        if isinstance(_reg_area_means, dict):
            area_encoded = float(_reg_area_means.get(
                country, np.mean(list(_reg_area_means.values()))
            ))
        else:
            area_encoded = float(
                _reg_area_means[country]
                if country in _reg_area_means.index
                else _reg_area_means.mean()
            )

        year_norm = year - 1961   # cohérent avec Year_norm du notebook

        # --- Construire DataFrame avec les bons noms de colonnes ---
        ohe_cols = [c for c in _reg_feature_cols if c.startswith("Item_")]
        ohe_row  = {c: (1.0 if c == f"Item_{reg_crop}" else 0.0) for c in ohe_cols}
        row      = {"Area_encoded": area_encoded, "Year_norm": year_norm, **ohe_row}
        x_df     = pd.DataFrame([row], columns=_reg_feature_cols)
        x_scaled = _reg_scaler.transform(x_df)
        log_pred = float(_reg_model.predict(x_scaled)[0])
        yield_hgha = np.expm1(log_pred)   # reconvertir depuis l'espace log
    else:
        yield_hgha = _mock_yield_prediction(crop_name, country, year)

    yield_tha = round(yield_hgha / 10000, 2)
    return max(yield_tha, 0.01), round(max(yield_hgha, 100), 0), reg_crop


# ════════════════════════════════════════════════════════════════
# FALLBACK MOCK
# ════════════════════════════════════════════════════════════════

def _mock_crop_prediction(N, P, K, temperature, humidity, ph, rainfall):
    import random
    moisture_score = (rainfall / 300) * (humidity / 100)
    nutrient_score = (N + P + K) / 300
    temp_score     = 1 - abs(temperature - 25) / 25
    ph_score       = 1 - abs(ph - 6.5) / 3.5
    total_score    = (moisture_score + nutrient_score + temp_score + ph_score) / 4

    if rainfall > 200 and humidity > 70 and temperature > 20:
        candidates = ["rice", "banana", "coconut", "jute"]
    elif rainfall > 100 and temperature > 20:
        candidates = ["maize", "cotton", "coffee"]
    elif temperature > 25 and humidity < 50:
        candidates = ["chickpea", "lentil", "mungbean", "blackgram"]
    elif ph < 6 and temperature < 20:
        candidates = ["apple", "grapes", "pomegranate"]
    else:
        candidates = ["wheat", "barley"]

    valid = [c for c in candidates if c in CROP_CLASSES]
    if not valid:
        valid = CROP_CLASSES
    crop       = random.choice(valid)
    confidence = min(0.95, max(0.6, total_score + random.uniform(-0.1, 0.1)))
    return crop, confidence


def _mock_yield_prediction(crop_name, country, year):
    import random
    base_yields = {
        "rice": 4.5, "maize": 5.8, "wheat": 3.2, "cotton": 1.8,
        "banana": 30.0, "mango": 8.0, "grapes": 15.0, "apple": 25.0,
        "orange": 20.0, "coffee": 1.5, "coconut": 12.0, "jute": 2.5,
        "chickpea": 1.2, "lentil": 1.0, "mungbean": 1.5, "blackgram": 1.0,
    }
    base           = base_yields.get(crop_name.lower(), 3.0)
    country_factor = (hash(country) % 40 - 20) / 100
    year_factor    = (year - 2020) * 0.02
    random_factor  = random.uniform(-0.15, 0.15)
    yield_tha      = base * (1 + country_factor + year_factor + random_factor)
    return max(0.1, round(yield_tha, 2)) * 10000


# ════════════════════════════════════════════════════════════════
# UTILITAIRES
# ════════════════════════════════════════════════════════════════

def get_model_status():
    return {
        "crop_classifier": {
            "status":     "loaded" if _cls_model is not None else "mock",
            "model_path": CLS_MODEL_PATH,
            "exists":     os.path.exists(CLS_MODEL_PATH),
            "classes":    len(CROP_CLASSES)
        },
        "yield_regressor": {
            "status":     "loaded" if _reg_model is not None else "mock",
            "model_path": REG_MODEL_PATH,
            "exists":     os.path.exists(REG_MODEL_PATH),
            "countries":  len(COUNTRIES),
            "reg_crops":  len(REG_CROPS)
        }
    }