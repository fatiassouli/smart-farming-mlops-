from pydantic import BaseModel, Field


class YieldResponse(BaseModel):
    predicted_yield_tha: float = Field(
        ..., description="Rendement estimé en tonnes/hectare (sortie brute du modèle)"
    )
    predicted_yield_kgha: float = Field(
        ..., description="Rendement estimé en kilogrammes/hectare (t/ha x 1000)"
    )
