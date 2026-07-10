"""
Configuration du projet Smart Farming MLOps
-------------------------------------------
Ce fichier centralise tous les chemins et paramètres
utilisés par le pipeline d'ingestion.
"""

from pathlib import Path

# Racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================
# Dossiers
# ============================

DATA_DIR = BASE_DIR / "data" / "raw"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

# Création automatique des dossiers s'ils n'existent pas
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ============================
# Fichiers CSV
# ============================

CROP_DATASET = DATA_DIR / "Crop_recommendation.csv"
YIELD_DATASET = DATA_DIR / "yield.csv"

# ============================
# Base DuckDB
# ============================

DUCKDB_PATH = DATABASE_DIR / "smart_farming.duckdb"

# ============================
# Noms des tables
# ============================

CROP_TABLE = "crop_recommendation"
YIELD_TABLE = "yield"

# ============================
# Paramètres du pipeline
# ============================

PIPELINE_NAME = "smart_farming_pipeline"
DESTINATION = "duckdb"

# ============================
# Paramètres de nettoyage
# ============================

REMOVE_DUPLICATES = True
REMOVE_EXTRA_SPACES = True
DROP_EMPTY_ROWS = True
