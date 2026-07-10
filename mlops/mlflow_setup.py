# mlflow_setup.py
import mlflow
import os


def setup_mlflow():
    """
    Configuration centralisée de MLflow
    Utilise le stockage fichier (compatible avec mlflow-skinny)
    """
    # Créer le dossier pour les artefacts
    os.makedirs("mlruns", exist_ok=True)

    # Configuration du tracking URI (stockage fichier)
    mlflow.set_tracking_uri("file:./mlruns")

    # Définir l'expérience par défaut
    mlflow.set_experiment("projet_agricole_mlops")

    print("✅ MLflow configuré avec succès !")
    print(f"   Tracking URI: {mlflow.get_tracking_uri()}")
    print("   Expérience: projet_agricole_mlops")

    return mlflow


if __name__ == "__main__":
    setup_mlflow()
