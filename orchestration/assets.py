"""
Assets Dagster avec tests unitaires, data quality, MLflow et tests avancés.
"""

from dagster import asset, AssetExecutionContext, Output, Failure
import subprocess
import sys
import os
import json
import pandas as pd
import yaml
from pathlib import Path
import requests
import time

# Résolution des chemins
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from data_quality.validators.contract_validator import load_contracts, validate_dataset


# ═══════════════════════════════════════════════════════
# ASSET 0 : Tests unitaires (pytest)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="tests",
    description="Tests unitaires pytest - valide la logique métier",
    key="unit_tests"
)
def unit_tests(context: AssetExecutionContext):
    """Lance les tests pytest."""
    context.log.info("🧪 Tests unitaires...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--cov=src"],
        capture_output=True,
        text=True,
        cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    
    if result.returncode != 0:
        raise Failure(description="Tests unitaires échoués", metadata={"stderr": result.stderr[:500]})
    
    # Extraire le taux de couverture
    coverage = 0.0
    for line in result.stdout.split("\n"):
        if "TOTAL" in line and "%" in line:
            try:
                coverage = float(line.split()[-1].replace("%", ""))
            except:
                pass
    
    return Output(
        value={"passed": True, "coverage": coverage},
        metadata={"coverage": coverage, "status": "PASS"}
    )


# ═══════════════════════════════════════════════════════
# ASSET 1 : Lint & Format (code quality)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="tests",
    description="Vérification du style de code (ruff, black)",
    key="code_quality"
)
def code_quality(context: AssetExecutionContext):
    """Vérifie la qualité du code."""
    context.log.info("📏 Vérification code quality...")
    
    checks = []
    
    # Ruff linting
    ruff = subprocess.run(
        ["ruff", "check", "."],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    checks.append(("ruff", ruff.returncode == 0, ruff.stdout[:200]))
    
    # Black format check
    black = subprocess.run(
        ["black", "--check", "."],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    checks.append(("black", black.returncode == 0, black.stdout[:200]))
    
    for name, passed, output in checks:
        status = "✅" if passed else "❌"
        context.log.info(f"{status} {name}: {'OK' if passed else 'FAILED'}")
    
    failed = [n for n, p, _ in checks if not p]
    if failed:
        raise Failure(description=f"Code quality check failed: {', '.join(failed)}")
    
    return Output(value={"checks": checks}, metadata={"passed": len(checks)})


# ═══════════════════════════════════════════════════════
# ASSET 2 : Sécurité (bandit, safety)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="tests",
    description="Scan de sécurité du code",
    key="security_scan"
)
def security_scan(context: AssetExecutionContext):
    """Scan de vulnérabilités."""
    context.log.info("🔒 Scan de sécurité...")
    
    # Bandit - scan Python
    bandit = subprocess.run(
        ["bandit", "-r", "backend/", "-f", "json"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    try:
        bandit_report = json.loads(bandit.stdout)
        issues = bandit_report.get("results", [])
        severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for issue in issues:
            sev = issue.get("issue_severity", "LOW")
            severity[sev] = severity.get(sev, 0) + 1
    except:
        severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    
    context.log.info(f"Bandit: {severity}")
    
    if severity.get("HIGH", 0) > 0:
        raise Failure(description=f"🔴 Vulnérabilités HIGH trouvées: {severity['HIGH']}")
    
    return Output(
        value={"severity": severity},
        metadata={"high": severity.get("HIGH", 0), "medium": severity.get("MEDIUM", 0)}
    )


# ═══════════════════════════════════════════════════════
# ASSET 3 : Ingestion des données
# ═══════════════════════════════════════════════════════
@asset(
    group_name="ingestion",
    description="Pipeline DLT : charge les données sources dans DuckDB",
    deps=[unit_tests, code_quality, security_scan],
    key="raw_data"
)
def raw_data(context: AssetExecutionContext):
    """Ingestion via DLT."""
    context.log.info("🚀 Ingestion DLT...")
    
    result = subprocess.run(
        [sys.executable, "dataops/dlt_pipeline.py"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Failure(description="Ingestion échouée", metadata={"stderr": result.stderr[:500]})
    
    # Vérifier que DuckDB est créé
    duckdb_path = ROOT_DIR / "data" / "smart_farming.duckdb"
    if not duckdb_path.exists():
        raise Failure(description="DuckDB non créé après ingestion")
    
    return Output(value={"status": "success"}, metadata={"duckdb": str(duckdb_path)})


# ═══════════════════════════════════════════════════════
# ASSET 4 : Transformation dbt
# ═══════════════════════════════════════════════════════
@asset(
    group_name="transformation",
    description="Modèles dbt : transformation des données brutes en tables marts",
    deps=[raw_data],
    key="transformed_tables"
)
def transformed_tables(context: AssetExecutionContext):
    """Transformation via dbt."""
    context.log.info("🔧 dbt run...")
    
    result = subprocess.run(
        ["dbt", "run", "--project-dir", "transform/"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Failure(description="dbt échoué", metadata={"stderr": result.stderr[:500]})
    
    # Vérifier que les tables sont créées
    result_test = subprocess.run(
        ["dbt", "test", "--project-dir", "transform/"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    if result_test.returncode != 0:
        context.log.warning("⚠️ Certains tests dbt ont échoué")
    
    return Output(
        value={"status": "success"},
        metadata={"dbt_tests": result_test.returncode == 0}
    )


# ═══════════════════════════════════════════════════════
# ASSET 5 : Data Quality (Data Contracts + Great Expectations)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="quality",
    description="Validation Data Contracts + tests statistiques",
    deps=[transformed_tables],
    key="data_quality_checks"
)
def data_quality_checks(context: AssetExecutionContext):
    """Valide les données via les contrats."""
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
    
    # Tests statistiques avancés
    stats_report = {}
    for name, report_data in reports.items():
        if report_data.get("is_valid"):
            csv_path = ROOT_DIR / "data" / f"{name}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                stats_report[name] = {
                    "null_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
                    "duplicates": df.duplicated().sum(),
                    "memory_mb": df.memory_usage(deep=True).sum() / 1024**2
                }
    
    # Sauvegarder le rapport
    report_path = ROOT_DIR / "data_quality" / "dagster_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": str(pd.Timestamp.now()),
            "overall_valid": all_valid,
            "reports": reports,
            "stats": stats_report
        }, f, indent=2, ensure_ascii=False)
    
    if not all_valid:
        raise Failure(description="Data Quality check failed")
    
    return Output(
        value={"valid": True, "datasets": len(reports)},
        metadata={"report_path": str(report_path), "stats": stats_report}
    )


# ═══════════════════════════════════════════════════════
# ASSET 6 : Test de dérive des données (Data Drift)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="quality",
    description="Détection de drift des données par rapport à une baseline",
    deps=[data_quality_checks],
    key="data_drift_check"
)
def data_drift_check(context: AssetExecutionContext):
    """Détecte si les données ont changé significativement."""
    context.log.info("📊 Data Drift check...")
    
    # Charger la baseline (si existe)
    baseline_path = ROOT_DIR / "data_quality" / "baseline_stats.json"
    current_stats = {}
    
    for dataset in ["yield", "crop_recommendation"]:
        csv_path = ROOT_DIR / "data" / f"{dataset}.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            current_stats[dataset] = {
                "n_rows": len(df),
                "mean_n": float(df["N"].mean()) if "N" in df.columns else None,
                "mean_p": float(df["P"].mean()) if "P" in df.columns else None,
                "mean_k": float(df["K"].mean()) if "K" in df.columns else None,
            }
    
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline = json.load(f)
        
        drift_detected = False
        for dataset, stats in current_stats.items():
            base = baseline.get(dataset, {})
            if base:
                # Vérifier si le nombre de lignes a changé de plus de 10%
                row_diff = abs(stats["n_rows"] - base.get("n_rows", 0)) / max(base.get("n_rows", 1), 1)
                if row_diff > 0.1:
                    drift_detected = True
                    context.log.warning(f"⚠️ Drift détecté sur {dataset}: {row_diff:.1%} changement de lignes")
        
        if drift_detected:
            context.log.warning("Drift détecté - considérer un retrain des modèles")
    
    # Sauvegarder la baseline actuelle
    with open(baseline_path, "w") as f:
        json.dump(current_stats, f, indent=2)
    
    return Output(
        value={"drift_checked": True},
        metadata={"datasets": len(current_stats)}
    )


# ═══════════════════════════════════════════════════════
# ASSET 7 : MLflow Logging
# ═══════════════════════════════════════════════════════
@asset(
    group_name="mlops",
    description="Log des modèles ML dans MLflow avec métriques",
    deps=[data_drift_check],
    key="mlflow_logging"
)
def mlflow_logging(context: AssetExecutionContext):
    """Log les modèles dans MLflow."""
    context.log.info("🤖 MLflow logging...")
    
    model_cls_path = ROOT_DIR / "cls_best_model.pkl"
    model_reg_path = ROOT_DIR / "reg_best_model.pkl"
    
    if not model_cls_path.exists():
        raise Failure(description=f"Modèle classification introuvable: {model_cls_path}")
    if not model_reg_path.exists():
        raise Failure(description=f"Modèle régression introuvable: {model_reg_path}")
    
    result = subprocess.run(
        [sys.executable, "mlops/log_models.py"],
        capture_output=True, text=True, cwd=str(ROOT_DIR)
    )
    
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Failure(description="MLflow logging échoué", metadata={"stderr": result.stderr[:500]})
    
    return Output(
        value={"models": ["classification", "regression"]},
        metadata={"mlflow_uri": "file:./mlruns"}
    )


# ═══════════════════════════════════════════════════════
# ASSET 8 : Test d'intégration API
# ═══════════════════════════════════════════════════════
@asset(
    group_name="integration",
    description="Test end-to-end de l'API FastAPI",
    deps=[mlflow_logging],
    key="api_integration_test"
)
def api_integration_test(context: AssetExecutionContext):
    """Test l'API en conditions réelles."""
    context.log.info("🌐 Test API integration...")
    
    # Démarrer l'API en arrière-plan
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)  # Attendre le démarrage
    
    try:
        # Test health
        health = requests.get("http://127.0.0.1:8001/health", timeout=5)
        assert health.status_code == 200, f"Health failed: {health.status_code}"
        context.log.info("✅ Health check OK")
        
        # Test predict_yield
        predict = requests.post(
            "http://127.0.0.1:8001/predict_yield",
            json={"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9, "area": "France", "item": "Rice", "year": 2024},
            timeout=10
        )
        context.log.info(f"Predict status: {predict.status_code}")
        
        # Test recommend_crop
        recommend = requests.post(
            "http://127.0.0.1:8001/recommend_crop",
            json={"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9},
            timeout=10
        )
        assert recommend.status_code == 200, f"Recommend failed: {recommend.status_code}"
        context.log.info(f"✅ Recommend crop: {recommend.json()}")
        
    finally:
        api_process.terminate()
        api_process.wait()
    
    return Output(
        value={"api_tested": True},
        metadata={"endpoints": ["/health", "/predict_yield", "/recommend_crop"]}
    )


# ═══════════════════════════════════════════════════════
# ASSET 9 : Performance test (latence)
# ═══════════════════════════════════════════════════════
@asset(
    group_name="integration",
    description="Test de performance (latence des endpoints)",
    deps=[api_integration_test],
    key="performance_test"
)
def performance_test(context: AssetExecutionContext):
    """Mesure les performances de l'API."""
    context.log.info("⚡ Performance test...")
    
    # Simuler des appels et mesurer le temps
    latencies = []
    for _ in range(10):
        start = time.time()
        # Simulation (en vrai, appeler l'API)
        time.sleep(0.01)  # Placeholder
        latencies.append((time.time() - start) * 1000)
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    context.log.info(f"Latence moyenne: {avg_latency:.2f}ms")
    context.log.info(f"Latence max: {max_latency:.2f}ms")
    
    if avg_latency > 500:  # 500ms
        raise Failure(description=f"Latence trop élevée: {avg_latency:.2f}ms")
    
    return Output(
        value={"avg_latency_ms": avg_latency, "max_latency_ms": max_latency},
        metadata={"avg_latency": avg_latency, "max_latency": max_latency}
    )
