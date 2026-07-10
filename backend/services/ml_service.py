"""
backend/services/ml_service.py
Service ML unifié : recommandation de culture (classification) + prédiction de rendement (régression).

Interface attendue par backend/main.py et backend/api/routes/*.py :
    ml_service.load()                      -> charge les modèles, met à jour les flags *_ready
    ml_service.classification_ready        -> bool
    ml_service.regression_ready            -> bool
    ml_service.recommend_crop(payload)     -> (crop_name: str, confidence: float)  # confidence en %
    ml_service.predict_yield(payload)      -> float                                # en tonnes/hectare
"""

import os
import logging
import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger("smart_farming_api")

_THIS_FILE = os.path.abspath(__file__)
_SERVICES_DIR = os.path.dirname(_THIS_FILE)  # backend/services
_BACKEND_DIR = os.path.dirname(_SERVICES_DIR)  # backend
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)  # racine du repo
MODELS_DIR = os.path.join(_PROJECT_ROOT, "models")

YEAR_MIN = 1961  # confirmé par le notebook régression
YIELD_UNIT_DIVISOR = 10_000  # dataset FAO en hg/ha -> conversion en t/ha


class MLService:
    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.classification_ready = False
        self.regression_ready = False

        # --- classification ---
        self.cls_model = None
        self.cls_scaler = None
        self.cls_label_encoder = None
        self.cls_feature_columns = None

        # --- régression ---
        self.reg_model = None
        self.reg_scaler = None
        self.reg_area_means = None
        self.reg_feature_columns = None
        self._area_fallback = None
        self.available_items = []

    def load(self):
        """Charge les 4 fichiers classification + les 4 fichiers régression.
        Chaque bloc est indépendant : si l'un plante, l'autre peut quand même
        se charger (les flags *_ready reflètent l'état réel)."""
        try:
            self.cls_model = joblib.load(
                os.path.join(self.models_dir, "cls_best_model.pkl")
            )
            self.cls_scaler = joblib.load(
                os.path.join(self.models_dir, "cls_scaler.pkl")
            )
            self.cls_label_encoder = joblib.load(
                os.path.join(self.models_dir, "cls_label_encoder.pkl")
            )
            self.cls_feature_columns = joblib.load(
                os.path.join(self.models_dir, "cls_feature_columns.pkl")
            )
            self.classification_ready = True
        except Exception as exc:
            logger.error("Échec chargement modèle classification : %s", exc)
            self.classification_ready = False

        try:
            self.reg_model = joblib.load(
                os.path.join(self.models_dir, "reg_best_model.pkl")
            )
            self.reg_scaler = joblib.load(
                os.path.join(self.models_dir, "reg_scaler.pkl")
            )
            self.reg_area_means = joblib.load(
                os.path.join(self.models_dir, "reg_area_means.pkl")
            )
            self.reg_feature_columns = joblib.load(
                os.path.join(self.models_dir, "reg_feature_columns.pkl")
            )
            self._area_fallback = float(self.reg_area_means.mean())
            self.available_items = [
                c.replace("Item_", "")
                for c in self.reg_feature_columns
                if c.startswith("Item_")
            ]
            self.regression_ready = True
        except Exception as exc:
            logger.error("Échec chargement modèle régression : %s", exc)
            self.regression_ready = False

    # ---------------- Classification ----------------
    def _engineer_cls_features(self, payload) -> pd.DataFrame:
        row = {
            "N": payload.N,
            "P": payload.P,
            "K": payload.K,
            "temperature": payload.temperature,
            "humidity": payload.humidity,
            "ph": payload.ph,
            "rainfall": payload.rainfall,
        }
        df_row = pd.DataFrame([row])
        df_row["NPK_total"] = df_row["N"] + df_row["P"] + df_row["K"]
        df_row["NP_ratio"] = df_row["N"] / (df_row["P"] + 1e-6)
        df_row["NK_ratio"] = df_row["N"] / (df_row["K"] + 1e-6)
        df_row["heat_humidity"] = df_row["temperature"] * df_row["humidity"] / 100
        df_row["rain_temp"] = df_row["rainfall"] * df_row["temperature"]
        return df_row[self.cls_feature_columns]  # ordre exact attendu par le scaler

    def recommend_crop(self, payload):
        """payload : instance de SoilClimateFeatures (N, P, K, temperature, humidity, ph, rainfall).
        Retourne (crop_name: str, confidence: float en %)."""
        df_row = self._engineer_cls_features(payload)
        X_scaled = self.cls_scaler.transform(df_row)

        pred_encoded = self.cls_model.predict(X_scaled)[0]
        predicted_crop = self.cls_label_encoder.inverse_transform([pred_encoded])[0]

        confidence = 100.0
        if hasattr(self.cls_model, "predict_proba"):
            proba = self.cls_model.predict_proba(X_scaled)[0]
            confidence = round(float(max(proba)) * 100, 2)

        return predicted_crop, confidence

    # ---------------- Régression ----------------
    def _encode_area(self, area: str) -> float:
        if area in self.reg_area_means.index:
            return float(self.reg_area_means.loc[area])
        return self._area_fallback

    def predict_yield(self, payload) -> float:
        """payload : instance de YieldRequest (area, item, year).
        Retourne le rendement prédit en tonnes/hectare (t/ha)."""
        item = payload.item
        if item not in self.available_items:
            raise ValueError(
                f"Culture '{item}' non gérée par le modèle. "
                f"Cultures disponibles : {self.available_items}"
            )

        row = {col: 0.0 for col in self.reg_feature_columns}
        row["Area_encoded"] = self._encode_area(payload.area)
        row["Year_norm"] = payload.year - YEAR_MIN
        row[f"Item_{item}"] = 1.0

        df_row = pd.DataFrame([row])[self.reg_feature_columns]
        X_scaled = self.reg_scaler.transform(df_row)

        log_pred = self.reg_model.predict(X_scaled)[0]
        value_hg_ha = float(np.expm1(log_pred))
        value_tha = value_hg_ha / YIELD_UNIT_DIVISOR

        return round(value_tha, 4)


# --- Instance unique importée par main.py et les routes ---
ml_service = MLService()


# --- Test rapide en local (simule les objets Pydantic avec une classe simple) ---
if __name__ == "__main__":

    class _FakeCropPayload:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    class _FakeYieldPayload:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    ml_service.load()
    print("classification_ready :", ml_service.classification_ready)
    print("regression_ready     :", ml_service.regression_ready)

    print("\n=== Test classification ===")
    payload_cls = _FakeCropPayload(
        N=90, P=42, K=43, temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9
    )
    print(ml_service.recommend_crop(payload_cls))

    print("\n=== Test régression ===")
    payload_yield = _FakeYieldPayload(area="Afghanistan", year=2016, item="Maize")
    print(ml_service.predict_yield(payload_yield))
    payload_yield2 = _FakeYieldPayload(
        area="Pays_Inconnu_Test", year=2020, item="Wheat"
    )
    print(ml_service.predict_yield(payload_yield2))
