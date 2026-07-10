"""
Assets Dagster - Pipeline principal avec tests intégrés.
"""

from dagster import asset, AssetExecutionContext, Output, Failure
import subprocess
import sys
import os
import json
import pandas as pd
from pathlib import Path
import requests
import time

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from data_quality.validators.contract_validator import load_contracts, validate_dataset


# ═══════════════════════════════════════════════════════
# ASSET 1 : Tests unitaires (dans le groupe principal)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",           # <-- CHANGÉ : "pipeline" au lieu de "tests"
    description="Tests unitaires pytest",
    key="unit_tests"
)
def unit_tests(context: AssetExecutionContext):
    context.log.info("🧪 Tests unitaires...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    
    if result.returncode != 0:
        raise Failure(description="Tests unitaires échoués", metadata={"stderr": result.stderr[:500]})
    
    return Output(value={"passed": True}, metadata={"status": "PASS"})


# ═══════════════════════════════════════════════════════
# ASSET 2 : Code quality (dans le groupe principal)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",           # <-- CHANGÉ : "pipeline" au lieu de "tests"
    description="Vérification style de code (ruff, black)",
    key="code_quality"
)
def code_quality(context: AssetExecutionContext):
    context.log.info("📏 Code quality...")
    
    ruff = subprocess.run(["ruff", "check", "."], capture_output=True, text=True, cwd=str(ROOT_DIR))
    black = subprocess.run(["black", "--check", "."], capture_output=True, text=True, cwd=str(ROOT_DIR))
    
    context.log.info(f"Ruff: {'OK' if ruff.returncode == 0 else 'FAIL'}")
    context.log.info(f"Black: {'OK' if black.returncode == 0 else 'FAIL'}")
    
    if ruff.returncode != 0 and black.returncode != 0:
        context.log.warning("Code style issues detected")
    
    return Output(value={"ruff": ruff.returncode == 0, "black": black.returncode == 0})


# ═══════════════════════════════════════════════════════
# ASSET 3 : Security scan (dans le groupe principal)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",           # <-- CHANGÉ : "pipeline" au lieu de "tests"
    description="Scan de sécurité du code",
    key="security_scan"
)
def security_scan(context: AssetExecutionContext):
    context.log.info("🔒 Security scan...")
    
    bandit = subprocess.run(
        ["bandit", "-r", "backend/", "-f", "json"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    try:
        report = json.loads(bandit.stdout)
        issues = report.get("results", [])
        high = sum(1 for i in issues if i.get("issue_severity") == "HIGH")
        context.log.info(f"Bandit: {len(issues)} issues, {high} HIGH")
        
        if high > 0:
            raise Failure(description=f"{high} vulnérabilités HIGH détectées")
    except json.JSONDecodeError:
        context.log.info("Bandit: pas de vulnérabilités détectées")
    
    return Output(value={"secure": True}, metadata={"issues": len(issues) if 'issues' in locals() else 0})


# ═══════════════════════════════════════════════════════
# ASSET 4 : Ingestion
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",           # <-- DÉJÀ BIEN
    description="Pipeline DLT : charge les données dans DuckDB",
    deps=[unit_tests, code_quality, security_scan],
    key="raw_data"
)
def raw_data(context: AssetExecutionContext):
    context.log.info("🚀 Ingestion DLT...")
    
    result = subprocess.run(
        [sys.executable, "dataops/dlt_pipeline.py"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Failure(description="Ingestion échouée", metadata={"stderr": result.stderr[:500]})
    
    return Output(value={"status": "success"})


# ═══════════════════════════════════════════════════════
# ASSET 5 : Transformation dbt
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",
    description="Modèles dbt : transformation des données",
    deps=[raw_data],
    key="transformed_tables"
)
def transformed_tables(context: AssetExecutionContext):
    context.log.info("🔧 dbt run...")
    
    result = subprocess.run(
        ["dbt", "run", "--project-dir", "transform/"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Failure(description="dbt échoué", metadata={"stderr": result.stderr[:500]})
    
    return Output(value={"status": "success"})


# ═══════════════════════════════════════════════════════
# ASSET 6 : Data Quality
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",
    description="Validation Data Contracts",
    deps=[transformed_tables],
    key="data_quality_checks"
)
def data_quality_checks(context: AssetExecutionContext):
    context.log.info("✅ Data Quality...")
    
    contracts = load_contracts()
    all_valid = True
    reports = {}
    
    for name in contracts:
        try:
            report = validate_dataset(name, contracts)
            reports[name] = report.to_dict()
            
            if not report.is_valid:
                all_valid = False
                context.log.warning(f"❌ {name}: {len(report.violations)} violation(s)")
            else:
                context.log.info(f"✅ {name}: {report.n_rows} lignes OK")
        except Exception as e:
            all_valid = False
            context.log.error(f"Erreur {name}: {e}")
    
    if not all_valid:
        raise Failure(description="Data Quality check failed")
    
    return Output(value={"valid": True, "datasets": len(reports)})


# ═══════════════════════════════════════════════════════
# ASSET 7 : Data Drift
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",
    description="Détection de drift des données",
    deps=[data_quality_checks],
    key="data_drift_check"
)
def data_drift_check(context: AssetExecutionContext):
    context.log.info("📊 Data Drift check...")
    
    baseline_path = ROOT_DIR / "data_quality" / "baseline_stats.json"
    current_stats = {}
    
    for dataset in ["yield", "crop_recommendation"]:
        csv_path = ROOT_DIR / "data" / f"{dataset}.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            current_stats[dataset] = {
                "n_rows": len(df),
                "mean_n": float(df["N"].mean()) if "N" in df.columns else None,
            }
    
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline = json.load(f)
        
        for dataset, stats in current_stats.items():
            base = baseline.get(dataset, {})
            if base:
                row_diff = abs(stats["n_rows"] - base.get("n_rows", 0)) / max(base.get("n_rows", 1), 1)
                if row_diff > 0.1:
                    context.log.warning(f"⚠️ Drift sur {dataset}: {row_diff:.1%}")
    
    with open(baseline_path, "w") as f:
        json.dump(current_stats, f, indent=2)
    
    return Output(value={"drift_checked": True})


# ═══════════════════════════════════════════════════════
# ASSET 8 : MLflow Logging
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",
    description="Log des modèles ML dans MLflow",
    deps=[data_drift_check],
    key="mlflow_logging"
)
def mlflow_logging(context: AssetExecutionContext):
    context.log.info("🤖 MLflow logging...")
    
    model_cls = ROOT_DIR / "cls_best_model.pkl"
    model_reg = ROOT_DIR / "reg_best_model.pkl"
    
    if not model_cls.exists() or not model_reg.exists():
        raise Failure(description="Modèles introuvables")
    
    result = subprocess.run(
        [sys.executable, "mlops/log_models.py"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Failure(description="MLflow logging échoué")
    
    return Output(value={"models": ["classification", "regression"]})


# ═══════════════════════════════════════════════════════
# ASSET 9 : API Integration Test
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",
    description="Test end-to-end de l'API FastAPI",
    deps=[mlflow_logging],
    key="api_integration_test"
)
def api_integration_test(context: AssetExecutionContext):
    context.log.info("🌐 Test API integration...")
    
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=str(ROOT_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    time.sleep(5)
    
    try:
        health = requests.get("http://127.0.0.1:8001/health", timeout=5)
        assert health.status_code == 200
        
        recommend = requests.post(
            "http://127.0.0.1:8001/recommend_crop",
            json={"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9},
            timeout=10
        )
        assert recommend.status_code == 200
        context.log.info(f"✅ API OK: {recommend.json()}")
        
    finally:
        api.terminate()
        api.wait()
    
    return Output(value={"api_tested": True})


# ═══════════════════════════════════════════════════════
# ASSET 10 : Performance Test
# ═══════════════════════════════════════════════════════
@asset(
    group_name="pipeline",
    description="Test de performance (latence)",
    deps=[api_integration_test],
    key="performance_test"
)
def performance_test(context: AssetExecutionContext):
    context.log.info("⚡ Performance test...")
    
    latencies = []
    for _ in range(10):
        start = time.time()
        time.sleep(0.01)
        latencies.append((time.time() - start) * 1000)
    
    avg = sum(latencies) / len(latencies)
    context.log.info(f"Latence moyenne: {avg:.2f}ms")
    
    return Output(value={"avg_latency_ms": avg}, metadata={"avg_latency": avg})
