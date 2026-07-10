"""
conftest.py
Fixtures pytest partagées par toute la suite de tests de qualité des données.
Toutes les dépendances (chemins, DataFrames, schémas) sont centralisées ici.
"""

import os
import sys
import pandas as pd
import pytest

# =============================================================================
# RÉSOLUTION DES CHEMINS
# =============================================================================
# Ce fichier est dans : smart-farming-mlops-/data_quality/tests/conftest.py
CURRENT_FILE = os.path.abspath(__file__)
# Remonte 3 niveaux : tests/ -> data_quality/ -> racine du repo
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))

sys.path.insert(0, os.path.dirname(os.path.dirname(CURRENT_FILE)))

from tests.schemas import YIELD_SCHEMA, CROP_SCHEMA  # noqa: E402

# =============================================================================
# CHEMINS DES DONNÉES (dans data/raw/ à la racine du repo)
# =============================================================================
DATA_DIR = os.path.join(ROOT_DIR, "data", "raw")
YIELD_PATH = os.path.join(DATA_DIR, "yield.csv")
CROP_PATH = os.path.join(DATA_DIR, "Crop_recommendation.csv")


# =============================================================================
# FIXTURES
# =============================================================================
@pytest.fixture(scope="session")
def yield_path():
    """Chemin vers le fichier yield.csv"""
    if not os.path.exists(YIELD_PATH):
        pytest.skip(f"Fichier non trouvé: {YIELD_PATH}")
    return YIELD_PATH


@pytest.fixture(scope="session")
def crop_path():
    """Chemin vers le fichier Crop_recommendation.csv"""
    if not os.path.exists(CROP_PATH):
        pytest.skip(f"Fichier non trouvé: {CROP_PATH}")
    return CROP_PATH


@pytest.fixture(scope="session")
def yield_df():
    """Dataset FAO : rendement agricole (hg/ha) par pays / culture / année."""
    if not os.path.exists(YIELD_PATH):
        pytest.skip(f"Fichier yield.csv non trouvé à: {YIELD_PATH}")
    return pd.read_csv(YIELD_PATH)


@pytest.fixture(scope="session")
def crop_df():
    """Dataset Kaggle : recommandation de culture selon paramètres agro-climatiques."""
    if not os.path.exists(CROP_PATH):
        pytest.skip(f"Fichier Crop_recommendation.csv non trouvé à: {CROP_PATH}")
    return pd.read_csv(CROP_PATH)


@pytest.fixture(scope="session")
def yield_schema():
    return YIELD_SCHEMA


@pytest.fixture(scope="session")
def crop_schema():
    return CROP_SCHEMA  # trigger rerun
