from fastapi import APIRouter, HTTPException

from schemas.yield_request import YieldRequest
from schemas.yield_response import YieldResponse
from services.ml_service import ml_service

router = APIRouter(tags=["Prediction"])


@router.post(
    "/predict_yield",
    response_model=YieldResponse,
    summary="Prédit le rendement attendu (t/ha) pour une culture, une région et une année données",
)
def predict_yield(payload: YieldRequest):
    if not ml_service.regression_ready:
        raise HTTPException(
            status_code=503, detail="Modèle de régression indisponible."
        )

    try:
        yield_tha = ml_service.predict_yield(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la prédiction : {exc}"
        )

    return YieldResponse(
        predicted_yield_tha=yield_tha, predicted_yield_kgha=yield_tha * 1000
    )
