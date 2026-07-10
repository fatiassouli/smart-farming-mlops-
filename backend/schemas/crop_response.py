from pydantic import BaseModel, Field


class CropResponse(BaseModel):
    recommended_crop: str = Field(..., description="Culture recommandée par le modèle")
    confidence: float = Field(
        ..., description="Confiance de la prédiction, en % (0-100)"
    )
