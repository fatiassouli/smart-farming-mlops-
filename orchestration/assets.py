"""
Assets Dagster pour le pipeline Smart Farming.
Chaque asset matérialise une étape du pipeline et utilise
les modules existants des autres personnes.
"""

from dagster import asset, AssetExecutionContext
import subprocess
import sys
import os

# Ajouter la racine du projet au path pour les imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# ═══════════════════════════════════════════════════════
# ASSET 1 : Ingestion des données (Personne 2)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="ingestion",
    description="Pipeline DLT : charge les données sources dans DuckDB",
    key="raw_data"
)
def raw_data(context: AssetExecutionContext):
    context.log.info("🚀 Lancement ingestion DLT...")
    
    result = subprocess.run(
        [sys.executable, "dataops/dlt_pipeline.py"],
        capture_output=True,
        text=True,
        cwd=ROOT_DIR
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError(f"Ingestion échouée : {result.stderr}")
    
    return {"status": "success", "step": "ingestion"}


# ═══════════════════════════════════════════════════════
# ASSET 2 : Transformation dbt (Personne 3)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="transformation",
    description="Modèles dbt : transformation des données brutes en tables marts",
    deps=[raw_data],
    key="transformed_tables"
)
def transformed_tables(context: AssetExecutionContext):
    context.log.info("🔧 Lancement des transformations dbt...")
    
    result = subprocess.run(
        ["dbt", "run", "--project-dir", "transform/"],
        capture_output=True,
        text=True,
        cwd=ROOT_DIR
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError(f"dbt échoué : {result.stderr}")
    
    return {"status": "success", "step": "dbt"}


# ═══════════════════════════════════════════════════════
# ASSET 3 : Tests de qualité (Personne 4)
# Utilise TON pipeline_validator.py existant
# ═══════════════════════════════════════════════════════
@asset(
    group_name="quality",
    description="Validation des Data Contracts + tests pytest",
    deps=[transformed_tables],
    key="data_quality_checks"
)
def data_quality_checks(context: AssetExecutionContext):
    context.log.info("✅ Lancement des tests de qualité...")
    
    result = subprocess.run(
        [sys.executable, "data_quality/validators/pipeline_validator.py"],
        capture_output=True,
        text=True,
        cwd=ROOT_DIR
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError(f"Qualité échouée : {result.stderr}")
    
    return {"status": "success", "step": "quality"}


# ═══════════════════════════════════════════════════════
# ASSET 4 : Logging MLflow (Personne 6)
# Utilise TON log_models.py existant
# ═══════════════════════════════════════════════════════
@asset(
    group_name="mlops",
    description="Log des modèles ML dans MLflow Registry",
    deps=[data_quality_checks],
    key="mlflow_logging"
)
def mlflow_logging(context: AssetExecutionContext):
    context.log.info("🤖 Logging des modèles dans MLflow...")
    
    result = subprocess.run(
        [sys.executable, "mlops/log_models.py"],
        capture_output=True,
        text=True,
        cwd=ROOT_DIR
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError(f"MLflow échoué : {result.stderr}")
    
    return {"status": "success", "step": "mlflow"}
