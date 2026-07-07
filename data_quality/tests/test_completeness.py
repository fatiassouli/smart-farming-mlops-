"""
test_completeness.py
Critère d'acceptation 1 : COMPLÉTUDE
- Toutes les colonnes attendues sont présentes
- Aucune valeur manquante (NaN/null) sur les colonnes obligatoires
- Volume de données minimum respecté (pas de fichier tronqué)
"""
import pytest


# ---------------------------------------------------------------------------
# yield.csv
# ---------------------------------------------------------------------------
def test_yield_columns_present(yield_df, yield_schema):
    expected = set(yield_schema.column_names())
    actual = set(yield_df.columns)
    missing = expected - actual
    assert not missing, f"Colonnes manquantes dans yield.csv : {missing}"


def test_yield_no_missing_values(yield_df, yield_schema):
    for col in yield_schema.columns:
        if not col.nullable:
            n_null = yield_df[col.name].isnull().sum()
            assert n_null == 0, (
                f"yield.csv : {n_null} valeurs manquantes dans la colonne "
                f"obligatoire '{col.name}'"
            )


def test_yield_min_row_count(yield_df, yield_schema):
    assert len(yield_df) >= yield_schema.min_rows, (
        f"yield.csv contient seulement {len(yield_df)} lignes "
        f"(minimum attendu : {yield_schema.min_rows})"
    )


def test_yield_no_empty_dataframe(yield_df):
    assert not yield_df.empty, "yield.csv est vide"


# ---------------------------------------------------------------------------
# Crop_recommendation.csv
# ---------------------------------------------------------------------------
def test_crop_columns_present(crop_df, crop_schema):
    expected = set(crop_schema.column_names())
    actual = set(crop_df.columns)
    missing = expected - actual
    assert not missing, f"Colonnes manquantes dans Crop_recommendation.csv : {missing}"


def test_crop_no_missing_values(crop_df, crop_schema):
    for col in crop_schema.columns:
        if not col.nullable:
            n_null = crop_df[col.name].isnull().sum()
            assert n_null == 0, (
                f"Crop_recommendation.csv : {n_null} valeurs manquantes dans "
                f"la colonne obligatoire '{col.name}'"
            )


def test_crop_min_row_count(crop_df, crop_schema):
    assert len(crop_df) >= crop_schema.min_rows, (
        f"Crop_recommendation.csv contient seulement {len(crop_df)} lignes "
        f"(minimum attendu : {crop_schema.min_rows})"
    )


def test_crop_no_empty_dataframe(crop_df):
    assert not crop_df.empty, "Crop_recommendation.csv est vide"