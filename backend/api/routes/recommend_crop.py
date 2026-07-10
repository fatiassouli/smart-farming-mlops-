from fastapi import APIRouter, HTTPException

from schemas.features_schema import SoilClimateFeatures
from schemas.crop_response import CropResponse
from services.ml_service import ml_service

router = APIRouter(tags=["Recommendation"])


@router.post(
    "/recommend_crop",
    response_model=CropResponse,
    summary="Recommande la culture la plus adaptée à des conditions pédoclimatiques données",
)
def recommend_crop(payload: SoilClimateFeatures):
    if not ml_service.classification_ready:
        raise HTTPException(
            status_code=503, detail="Modèle de classification indisponible."
        )

    try:
        crop_name, confidence = ml_service.recommend_crop(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la prédiction : {exc}"
        )

    return CropResponse(recommended_crop=crop_name, confidence=confidence)
