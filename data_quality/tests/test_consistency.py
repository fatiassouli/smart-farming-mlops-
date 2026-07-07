"""
test_consistency.py
Critère d'acceptation 3 : COHÉRENCE
- Cohérence interne des colonnes censées être constantes
- Cohérence des clés (pas de doublons)
- Cohérence référentielle (mapping code <-> libellé stable)
- Cohérence de la distribution attendue (classes équilibrées)
"""
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# yield.csv
# ---------------------------------------------------------------------------
def test_yield_constant_columns(yield_df, yield_schema):
    for col_name in yield_schema.constant_columns:
        n_unique = yield_df[col_name].nunique()
        assert n_unique == 1, (
            f"yield.csv : la colonne '{col_name}' devrait être constante, "
            f"mais {n_unique} valeurs distinctes trouvées"
        )


def test_yield_year_equals_year_code(yield_df):
    mismatched = yield_df[yield_df["Year"] != yield_df["Year Code"]]
    assert mismatched.empty, (
        f"yield.csv : {len(mismatched)} lignes où 'Year' != 'Year Code'"
    )


def test_yield_no_duplicate_key(yield_df, yield_schema):
    key_cols = list(yield_schema.unique_key)
    n_dup = yield_df.duplicated(subset=key_cols).sum()
    assert n_dup == 0, (
        f"yield.csv : {n_dup} doublons détectés sur la clé {key_cols}"
    )


def test_yield_area_code_area_mapping_stable(yield_df):
    # Un même Area Code doit toujours correspondre au même libellé Area
    mapping = yield_df.groupby("Area Code")["Area"].nunique()
    inconsistent = mapping[mapping > 1]
    assert inconsistent.empty, (
        f"yield.csv : Area Code associé à plusieurs libellés Area : "
        f"{list(inconsistent.index)}"
    )


def test_yield_item_code_item_mapping_stable(yield_df):
    mapping = yield_df.groupby("Item Code")["Item"].nunique()
    inconsistent = mapping[mapping > 1]
    assert inconsistent.empty, (
        f"yield.csv : Item Code associé à plusieurs libellés Item : "
        f"{list(inconsistent.index)}"
    )


# ---------------------------------------------------------------------------
# Crop_recommendation.csv
# ---------------------------------------------------------------------------
def test_crop_no_full_duplicate_rows(crop_df):
    n_dup = crop_df.duplicated().sum()
    assert n_dup == 0, f"Crop_recommendation.csv : {n_dup} lignes strictement dupliquées"


def test_crop_classes_are_balanced(crop_df, crop_schema):
    """
    Le dataset Kaggle est construit pour être parfaitement équilibré
    (100 échantillons par culture, 22 cultures = 2200 lignes).
    Une classe sous/sur-représentée est un signal de corruption du fichier.
    """
    counts = crop_df["label"].value_counts()
    expected_per_class = len(crop_df) // len(crop_schema.get("label").allowed_values)
    off_balance = counts[counts != expected_per_class]
    assert off_balance.empty, (
        f"Crop_recommendation.csv : classes déséquilibrées (attendu "
        f"{expected_per_class}/classe) : {off_balance.to_dict()}"
    )


def test_crop_all_labels_present(crop_df, crop_schema):
    expected_labels = set(crop_schema.get("label").allowed_values)
    actual_labels = set(crop_df["label"].unique())
    missing = expected_labels - actual_labels
    assert not missing, f"Crop_recommendation.csv : cultures absentes du fichier : {missing}"