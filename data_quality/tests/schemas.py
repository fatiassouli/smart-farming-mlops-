"""
schemas.py
Définit les règles de validation (schéma, types, plages, catégories autorisées)
pour les deux jeux de données du projet :
  - yield.csv               -> rendements agricoles FAO (1961-2016)
  - Crop_recommendation.csv -> recommandation de culture (Kaggle)

Ces règles sont la source de vérité unique, utilisées par :
  - test_completeness.py / test_validity.py / test_consistency.py
  - contract_validator.py (via data_contracts.yml, généré à partir de ce fichier)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Any


@dataclass
class ColumnSpec:
    name: str
    dtype: str  # "int", "float", "str"
    nullable: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None


@dataclass
class DatasetSchema:
    name: str
    columns: List[ColumnSpec]
    min_rows: int
    unique_key: Optional[Tuple[str, ...]] = None
    constant_columns: Optional[List[str]] = field(default_factory=list)

    def column_names(self):
        return [c.name for c in self.columns]

    def get(self, col_name):
        for c in self.columns:
            if c.name == col_name:
                return c
        raise KeyError(f"Colonne inconnue dans le schéma : {col_name}")


# --------------------------------------------------------------------------
# Schéma : yield.csv (FAOSTAT)
# --------------------------------------------------------------------------
YIELD_SCHEMA = DatasetSchema(
    name="yield",
    min_rows=50000,
    unique_key=("Area Code", "Item Code", "Year Code"),
    constant_columns=["Domain Code", "Domain", "Element", "Element Code", "Unit"],
    columns=[
        ColumnSpec("Domain Code", "str", allowed_values=["QC"]),
        ColumnSpec("Domain", "str", allowed_values=["Crops"]),
        ColumnSpec("Area Code", "int", min_value=1),
        ColumnSpec("Area", "str"),
        ColumnSpec("Element Code", "int"),
        ColumnSpec("Element", "str", allowed_values=["Yield"]),
        ColumnSpec("Item Code", "int"),
        ColumnSpec(
            "Item",
            "str",
            allowed_values=[
                "Maize",
                "Potatoes",
                "Rice, paddy",
                "Wheat",
                "Sorghum",
                "Soybeans",
                "Cassava",
                "Yams",
                "Sweet potatoes",
                "Plantains and others",
            ],
        ),
        ColumnSpec("Year Code", "int", min_value=1961, max_value=2016),
        ColumnSpec("Year", "int", min_value=1961, max_value=2016),
        ColumnSpec("Unit", "str", allowed_values=["hg/ha"]),
        ColumnSpec("Value", "int", min_value=0, max_value=2_000_000),
    ],
)

# --------------------------------------------------------------------------
# Schéma : Crop_recommendation.csv (Kaggle)
# --------------------------------------------------------------------------
CROP_LABELS = [
    "rice",
    "maize",
    "chickpea",
    "kidneybeans",
    "pigeonpeas",
    "mothbeans",
    "mungbean",
    "blackgram",
    "lentil",
    "pomegranate",
    "banana",
    "mango",
    "grapes",
    "watermelon",
    "muskmelon",
    "apple",
    "orange",
    "papaya",
    "coconut",
    "cotton",
    "jute",
    "coffee",
]

CROP_SCHEMA = DatasetSchema(
    name="crop_recommendation",
    min_rows=2200,
    unique_key=None,  # pas de clé naturelle, dataset expérimental équilibré
    constant_columns=[],
    columns=[
        ColumnSpec("N", "int", min_value=0, max_value=140),
        ColumnSpec("P", "int", min_value=5, max_value=145),
        ColumnSpec("K", "int", min_value=5, max_value=205),
        ColumnSpec("temperature", "float", min_value=8.0, max_value=45.0),
        ColumnSpec("humidity", "float", min_value=14.0, max_value=100.0),
        ColumnSpec("ph", "float", min_value=3.5, max_value=10.0),
        ColumnSpec("rainfall", "float", min_value=20.0, max_value=300.0),
        ColumnSpec("label", "str", allowed_values=CROP_LABELS),
    ],
)
