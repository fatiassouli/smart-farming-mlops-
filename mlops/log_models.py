# log_models.py
import mlflow
import mlflow.sklearn
import joblib
import os
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# === AUTORISER LE FILE STORE ===
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

# Ignorer les avertissements
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# === CONFIGURATION MLflow ===
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("projet_agricole_mlops")

print("=" * 60)
print("🚀 LOGGING DES MODÈLES MLflow")
print("=" * 60)
print("✅ MLflow configuré avec file store")
print(f"   Tracking URI: {mlflow.get_tracking_uri()}")

# === CHEMINS DES MODÈLES ===
MODEL_CLS_PATH = "cls_best_model.pkl"
MODEL_REG_PATH = "reg_best_model.pkl"

# === FEATURES UTILISÉES ===
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def load_models():
    """Charger les modèles avec joblib"""
    print("\n📂 Chargement des modèles...")

    try:
        model_cls = joblib.load(MODEL_CLS_PATH)
        print(f"   ✅ Classification chargée: {MODEL_CLS_PATH}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None, None

    try:
        model_reg = joblib.load(MODEL_REG_PATH)
        print(f"   ✅ Régression chargée: {MODEL_REG_PATH}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None, None

    return model_cls, model_reg


def log_models(model_cls, model_reg):
    """Logger les modèles dans MLflow"""

    print("\n📊 Début du logging des modèles...")

    # 1. MODÈLE DE CLASSIFICATION
    with mlflow.start_run(run_name="classification_recommandation"):
        mlflow.log_param("algorithme", "Random Forest")
        mlflow.log_param("tache", "Classification")
        mlflow.log_param("type", "Recommandation de culture")
        mlflow.log_param("features", FEATURES)

        mlflow.log_metric("accuracy", 99.32)
        mlflow.log_metric("f1_score", 0.99)
        mlflow.log_metric("precision", 0.99)
        mlflow.log_metric("recall", 0.99)

        mlflow.sklearn.log_model(
            sk_model=model_cls,
            artifact_path="model_classification",
            registered_model_name="ModeleClassification",
        )

        run_id_cls = mlflow.active_run().info.run_id
        print(f"   ✅ Classification loggée - Run: {run_id_cls[:8]}...")

    # 2. MODÈLE DE RÉGRESSION
    with mlflow.start_run(run_name="regression_rendement"):
        mlflow.log_param("algorithme", "Random Forest Regressor")
        mlflow.log_param("tache", "Regression")
        mlflow.log_param("type", "Prédiction de rendement")
        mlflow.log_param("features", FEATURES)

        mlflow.log_metric("r2_score", 0.98)
        mlflow.log_metric("rmse", 0.152)
        mlflow.log_metric("mae_percent", 10.07)

        mlflow.sklearn.log_model(
            sk_model=model_reg,
            artifact_path="model_regression",
            registered_model_name="ModeleRegression",
        )

        run_id_reg = mlflow.active_run().info.run_id
        print(f"   ✅ Régression loggée - Run: {run_id_reg[:8]}...")

    print("\n✅ Tous les modèles ont été loggés avec succès !")
    return run_id_cls, run_id_reg


def main():
    print("\n" + "=" * 60)

    model_cls, model_reg = load_models()
    if model_cls is None or model_reg is None:
        print("\n❌ Erreur: Impossible de charger les modèles.")
        return

    log_models(model_cls, model_reg)

    print("\n" + "=" * 60)
    print("✅ LOGGING TERMINÉ AVEC SUCCÈS")
    print("=" * 60)
    print("📌 Modèles enregistrés dans MLflow:")
    print("   - ModeleClassification (version 1)")
    print("   - ModeleRegression (version 1)")
    print("\n🔗 Pour voir l'interface MLflow (dans un autre terminal):")
    print("   mlflow ui --backend-store-uri file:./mlruns")
    print("=" * 60)


if __name__ == "__main__":
    main()
