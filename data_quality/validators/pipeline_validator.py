"""
pipeline_validator.py
Orchestrateur du pipeline de qualité des données. Exécute successivement :
  1. La suite de tests pytest (completeness / validity / consistency)
  2. La validation des Data Contracts (contract_validator.py)
Puis génère un rapport consolidé (JSON) utilisable en CI/CD.

Usage :
    python validators/pipeline_validator.py
    python validators/pipeline_validator.py --report path/vers/rapport.json
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

# =============================================================================
# RÉSOLUTION DES CHEMINS
# =============================================================================
# Ce fichier est dans : smart-farming-mlops-/data_quality/validators/pipeline_validator.py
# On remonte 3 niveaux pour atteindre la racine du repo :
# validators/ -> data_quality/ -> smart-farming-mlops-/
CURRENT_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
DATA_QUALITY_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE))

sys.path.insert(0, DATA_QUALITY_DIR)

from validators.contract_validator import load_contracts, validate_dataset  # noqa: E402


def run_pytest_suite():
    """Exécute la suite de tests pytest et capture le résultat."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    result = subprocess.run(cmd, cwd=DATA_QUALITY_DIR, capture_output=True, text=True)
    return {
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_contract_validation():
    """Valide chaque dataset contre son Data Contract."""
    contracts = load_contracts()
    reports = {}
    for name in contracts:
        report = validate_dataset(name, contracts)
        reports[name] = report.to_dict()
    return reports


def build_report():
    pytest_result = run_pytest_suite()
    contract_results = run_contract_validation()

    all_contracts_valid = all(r["is_valid"] for r in contract_results.values())
    overall_status = "PASS" if (pytest_result["passed"] and all_contracts_valid) else "FAIL"

    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "overall_status": overall_status,
        "pytest": {
            "passed": pytest_result["passed"],
            "returncode": pytest_result["returncode"],
        },
        "contracts": contract_results,
        "pytest_stdout": pytest_result["stdout"],
    }


def print_summary(report):
    print("=" * 70)
    print(f"RAPPORT DE QUALITE DES DONNEES - {report['generated_at']}")
    print("=" * 70)
    print(f"Statut global : {report['overall_status']}")
    print(f"Tests pytest  : {'OK' if report['pytest']['passed'] else 'ECHEC'}")
    print("-" * 70)
    for dataset_name, result in report["contracts"].items():
        status = "OK" if result["is_valid"] else "ECHEC"
        print(f"Contrat [{dataset_name}] : {status} "
              f"({result['n_rows']} lignes, {result['n_violations']} violation(s))")
        for v in result["violations"]:
            print(f"    - [{v['rule']}] {v['column']} : {v['detail']}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Pipeline de validation qualité des données")
    parser.add_argument("--report", default=os.path.join(DATA_QUALITY_DIR, "pipeline_report.json"),
                         help="Chemin du rapport JSON de sortie")
    args = parser.parse_args()

    report = build_report()
    print_summary(report)

    # Créer le dossier du rapport si nécessaire
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nRapport écrit dans : {args.report}")

    sys.exit(0 if report["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()