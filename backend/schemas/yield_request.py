from pydantic import BaseModel, ConfigDict, Field


class YieldRequest(BaseModel):
    """
    Paramètres nécessaires à la prédiction du rendement (module Régression).
    Confirmé via transform/models/marts/mart_yield.sql (Personne 3) :
    le modèle utilise Area (région/pays), Item (culture) et Year — PAS les
    données sol/climat.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"area": "Morocco", "item": "Wheat", "year": 2020}}
    )

    area: str = Field(..., description="Région / pays", examples=["Morocco"])
    item: str = Field(..., description="Culture concernée", examples=["Wheat"])
    year: int = Field(..., description="Année de la prédiction", ge=1961, le=2030, examples=[2020])
