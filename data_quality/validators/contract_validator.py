"""
contract_validator.py
Charge data_contracts.yml et valide un DataFrame par rapport au contrat
correspondant. Utilisé en standalone ou orchestré par pipeline_validator.py.

Usage CLI :
    python validators/contract_validator.py --dataset yield
    python validators/contract_validator.py --dataset crop_recommendation
    python validators/contract_validator.py --all
"""
import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import List

import pandas as pd
import yaml

# =============================================================================
# RÉSOLUTION DES CHEMINS
# =============================================================================
# Ce fichier est dans : smart-farming-mlops-/data_quality/validators/contract_validator.py
# On remonte 3 niveaux pour atteindre la racine du repo :
# validators/ -> data_quality/ -> smart-farming-mlops-/
CURRENT_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
DATA_QUALITY_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE))

CONTRACTS_PATH = os.path.join(DATA_QUALITY_DIR, "contracts", "data_contracts.yml")

_TYPE_CHECKERS = {
    "integer": pd.api.types.is_integer_dtype,
    "float": pd.api.types.is_float_dtype,
    "string": lambda s: pd.api.types.is_string_dtype(s) or s.dtype == object,
}


@dataclass
class Violation:
    dataset: str
    column: str
    rule: str
    detail: str


@dataclass
class ValidationReport:
    dataset: str
    n_rows: int
    violations: List[Violation] = field(default_factory=list)

    @property
    def is_valid(self):
        return len(self.violations) == 0

    def to_dict(self):
        return {
            "dataset": self.dataset,
            "n_rows": self.n_rows,
            "is_valid": self.is_valid,
            "n_violations": len(self.violations),
            "violations": [v.__dict__ for v in self.violations],
        }


def load_contracts(path=CONTRACTS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {c["dataset"]: c for c in data["contracts"]}


def _validate_column(df, col_spec, dataset_name, violations):
    name = col_spec["name"]
    if name not in df.columns:
        violations.append(Violation(dataset_name, name, "missing_column",
                                     "Colonne absente du DataFrame"))
        return

    series = df[name]

    if not col_spec.get("nullable", False):
        n_null = series.isnull().sum()
        if n_null > 0:
            violations.append(Violation(dataset_name, name, "nullability",
                                         f"{n_null} valeurs nulles trouvées"))

    expected_type = col_spec.get("type")
    checker = _TYPE_CHECKERS.get(expected_type)
    if checker is not None and not checker(series):
        violations.append(Violation(dataset_name, name, "dtype",
                                     f"Type attendu '{expected_type}', obtenu '{series.dtype}'"))

    if "min" in col_spec:
        n_below = (series < col_spec["min"]).sum()
        if n_below > 0:
            violations.append(Violation(dataset_name, name, "range_min",
                                         f"{n_below} valeurs < {col_spec['min']}"))

    if "max" in col_spec:
        n_above = (series > col_spec["max"]).sum()
        if n_above > 0:
            violations.append(Violation(dataset_name, name, "range_max",
                                         f"{n_above} valeurs > {col_spec['max']}"))

    if col_spec.get("allowed_values"):
        invalid = set(series.unique()) - set(col_spec["allowed_values"])
        if invalid:
            violations.append(Violation(dataset_name, name, "allowed_values",
                                         f"valeurs non autorisées : {invalid}"))


def validate_dataframe(df: pd.DataFrame, contract: dict) -> ValidationReport:
    dataset_name = contract["dataset"]
    violations: List[Violation] = []

    # SLA : volume minimum
    min_rows = contract.get("sla", {}).get("min_rows", 0)
    if len(df) < min_rows:
        violations.append(Violation(dataset_name, "*", "min_rows",
                                     f"{len(df)} lignes < minimum contractuel {min_rows}"))

    # Clé unique
    unique_key = contract.get("unique_key")
    if unique_key:
        n_dup = df.duplicated(subset=unique_key).sum()
        if n_dup > 0:
            violations.append(Violation(dataset_name, str(unique_key), "unique_key",
                                         f"{n_dup} doublons sur la clé"))

    # Colonnes constantes
    for col_name in contract.get("constant_columns", []) or []:
        if col_name in df.columns and df[col_name].nunique() != 1:
            violations.append(Violation(dataset_name, col_name, "constant_column",
                                         f"{df[col_name].nunique()} valeurs distinctes (attendu 1)"))

    # Schéma colonne par colonne
    for col_spec in contract["schema"]:
        _validate_column(df, col_spec, dataset_name, violations)

    return ValidationReport(dataset=dataset_name, n_rows=len(df), violations=violations)


def validate_dataset(dataset_name: str, contracts: dict = None) -> ValidationReport:
    contracts = contracts or load_contracts()
    if dataset_name not in contracts:
        raise KeyError(f"Aucun contrat trouvé pour le dataset '{dataset_name}'")
    contract = contracts[dataset_name]
    # Le chemin du fichier est relatif à la racine du repo
    csv_path = os.path.join(ROOT_DIR, contract["file"])
    
    # Vérifier que le fichier existe
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Fichier non trouvé: {csv_path} (vérifier data_contracts.yml)")
    
    df = pd.read_csv(csv_path)
    return validate_dataframe(df, contract)


def main():
    parser = argparse.ArgumentParser(description="Validateur de Data Contracts")
    parser.add_argument("--dataset", help="Nom du dataset à valider (yield | crop_recommendation)")
    parser.add_argument("--all", action="store_true", help="Valider tous les datasets du contrat")
    args = parser.parse_args()

    contracts = load_contracts()
    targets = list(contracts.keys()) if args.all or not args.dataset else [args.dataset]

    exit_code = 0
    for name in targets:
        try:
            report = validate_dataset(name, contracts)
            status = "OK" if report.is_valid else "ECHEC"
            print(f"[{status}] {name} - {report.n_rows} lignes - {len(report.violations)} violation(s)")
            for v in report.violations:
                print(f"    - [{v.rule}] {v.column} : {v.detail}")
            if not report.is_valid:
                exit_code = 1
        except FileNotFoundError as e:
            print(f"[ERREUR] {name} : {e}")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()