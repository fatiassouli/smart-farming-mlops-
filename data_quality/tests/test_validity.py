"""
test_validity.py
Critère d'acceptation 2 : VALIDITÉ
- Les types de données sont corrects
- Les valeurs numériques respectent les plages définies dans schemas.py
- Les valeurs catégorielles appartiennent aux ensembles autorisés
"""

import pandas as pd
import pytest


def _assert_numeric_range(df, col_name, min_value, max_value, dataset_label):
    if min_value is not None:
        below = df[df[col_name] < min_value]
        assert below.empty, (
            f"{dataset_label} : {len(below)} valeurs de '{col_name}' "
            f"sous le minimum autorisé ({min_value})"
        )
    if max_value is not None:
        above = df[df[col_name] > max_value]
        assert above.empty, (
            f"{dataset_label} : {len(above)} valeurs de '{col_name}' "
            f"au-dessus du maximum autorisé ({max_value})"
        )


def _assert_allowed_values(df, col_name, allowed_values, dataset_label):
    invalid = set(df[col_name].unique()) - set(allowed_values)
    assert (
        not invalid
    ), f"{dataset_label} : valeurs non autorisées dans '{col_name}' : {invalid}"


# ---------------------------------------------------------------------------
# yield.csv
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "col_name", ["Area Code", "Element Code", "Item Code", "Year Code", "Year", "Value"]
)
def test_yield_numeric_dtype(yield_df, col_name):
    assert pd.api.types.is_integer_dtype(
        yield_df[col_name]
    ), f"yield.csv : la colonne '{col_name}' devrait être de type entier"


def test_yield_value_range(yield_df, yield_schema):
    spec = yield_schema.get("Value")
    _assert_numeric_range(
        yield_df, "Value", spec.min_value, spec.max_value, "yield.csv"
    )


def test_yield_year_range(yield_df, yield_schema):
    spec = yield_schema.get("Year")
    _assert_numeric_range(yield_df, "Year", spec.min_value, spec.max_value, "yield.csv")


def test_yield_item_allowed_values(yield_df, yield_schema):
    spec = yield_schema.get("Item")
    _assert_allowed_values(yield_df, "Item", spec.allowed_values, "yield.csv")


def test_yield_unit_allowed_values(yield_df, yield_schema):
    spec = yield_schema.get("Unit")
    _assert_allowed_values(yield_df, "Unit", spec.allowed_values, "yield.csv")


def test_yield_no_negative_value(yield_df):
    assert (
        yield_df["Value"] >= 0
    ).all(), "yield.csv : des rendements négatifs ont été détectés"


# ---------------------------------------------------------------------------
# Crop_recommendation.csv
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("col_name", ["N", "P", "K"])
def test_crop_integer_dtype(crop_df, col_name):
    assert pd.api.types.is_integer_dtype(
        crop_df[col_name]
    ), f"Crop_recommendation.csv : la colonne '{col_name}' devrait être de type entier"


@pytest.mark.parametrize("col_name", ["temperature", "humidity", "ph", "rainfall"])
def test_crop_float_dtype(crop_df, col_name):
    assert pd.api.types.is_float_dtype(
        crop_df[col_name]
    ), f"Crop_recommendation.csv : la colonne '{col_name}' devrait être de type flottant"


@pytest.mark.parametrize(
    "col_name", ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
)
def test_crop_value_ranges(crop_df, crop_schema, col_name):
    spec = crop_schema.get(col_name)
    _assert_numeric_range(
        crop_df, col_name, spec.min_value, spec.max_value, "Crop_recommendation.csv"
    )


def test_crop_label_allowed_values(crop_df, crop_schema):
    spec = crop_schema.get("label")
    _assert_allowed_values(
        crop_df, "label", spec.allowed_values, "Crop_recommendation.csv"
    )


def test_crop_ph_is_physically_plausible(crop_df):
    # Le pH d'un sol est borné entre 0 et 14 par définition physique
    assert (
        crop_df["ph"].between(0, 14).all()
    ), "Crop_recommendation.csv : des valeurs de pH hors de l'échelle physique [0, 14]"
