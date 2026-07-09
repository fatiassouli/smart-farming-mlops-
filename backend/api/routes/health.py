from fastapi import APIRouter

from services.ml_service import ml_service

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Vérifie l'état de l'API et des modèles")
def health_check():
    return {
        "status": "ok",
        "classification_model_loaded": ml_service.classification_ready,
        "regression_model_loaded": ml_service.regression_ready,
    }
