# promote_model.py
import mlflow
from mlflow.tracking import MlflowClient
import os

# Configuration
os.makedirs("mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:./mlruns")
client = MlflowClient()

print("✅ MLflow configuré")
print(f"   Tracking URI: {mlflow.get_tracking_uri()}")


def list_versions(model_name):
    """
    Affiche toutes les versions d'un modèle
    """
    print(f"\n📋 {model_name}")
    print("-" * 40)
    try:
        versions = client.get_latest_versions(model_name)
        if versions:
            for v in versions:
                stage = v.current_stage if v.current_stage else "None"
                print(
                    f"   Version {v.version} | Stage: {stage} | Run: {v.run_id[:8]}..."
                )
        else:
            print("   Aucune version trouvée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")


def promote_to_production(model_name, version):
    """
    Passe un modèle en production
    Args:
        model_name: "ModeleClassification" ou "ModeleRegression"
        version: numéro de version
    """
    try:
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
            archive_existing_versions=True,
        )
        print(f"✅ {model_name} version {version} → Production")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def promote_to_staging(model_name, version):
    """
    Passe un modèle en staging
    """
    try:
        client.transition_model_version_stage(
            name=model_name, version=version, stage="Staging"
        )
        print(f"✅ {model_name} version {version} → Staging")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def get_production_version(model_name):
    """
    Récupère la version en production
    """
    try:
        versions = client.get_latest_versions(model_name, stages=["Production"])
        if versions:
            return versions[0]
        else:
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 GESTION DES MODÈLES MLflow")
    print("=" * 60)

    # Afficher l'état actuel
    list_versions("ModeleClassification")
    list_versions("ModeleRegression")

    # Vérifier les versions en production
    prod_cls = get_production_version("ModeleClassification")
    prod_reg = get_production_version("ModeleRegression")

    if prod_cls:
        print(f"\n✅ Classification en Production: version {prod_cls.version}")
    else:
        print("\n⚠️ Aucune version en Production pour la Classification")
        print("   💡 Utilise: promote_to_production('ModeleClassification', 1)")

    if prod_reg:
        print(f"✅ Régression en Production: version {prod_reg.version}")
    else:
        print("⚠️ Aucune version en Production pour la Régression")
        print("   💡 Utilise: promote_to_production('ModeleRegression', 1)")

    print("\n" + "=" * 60)
    print("📌 Exemples d'utilisation:")
    print("   promote_to_production('ModeleClassification', 1)")
    print("   promote_to_staging('ModeleRegression', 2)")
    print("=" * 60)
