"""
Smart Farming API — Backend & Déploiement (Personne 7)

Expose les modules de Machine Learning (classification + régression, cf.
Personne 5 / Personne 6) via une API REST FastAPI.

Endpoints :
    GET  /health          -> statut de l'API et des modèles
    POST /recommend_crop  -> recommandation de culture (classification)
    POST /predict_yield   -> prédiction de rendement (régression)

Lancement local :
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Documentation interactive générée automatiquement :
    http://localhost:8000/docs   (Swagger)
    http://localhost:8000/redoc  (Redoc)
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monitoring import setup_monitoring

# Le dossier mlops/ (Personne 6) vit à la racine du repo, un niveau au-dessus
# de backend/. On l'ajoute au sys.path pour pouvoir faire
# `from mlops.model_loader import get_model_loader` quel que soit le cwd
# depuis lequel uvicorn est lancé.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import APP_NAME, APP_VERSION
from api.routes import health, recommend_crop, predict_yield
from services.ml_service import ml_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_farming_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ml_service.load()
        logger.info(
            "Modèles chargés — classification: %s, régression: %s",
            ml_service.classification_ready,
            ml_service.regression_ready,
        )
    except Exception as exc:
        logger.error("Échec du chargement des modèles : %s", exc)

    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "API REST du projet Smart Farming : recommandation de culture "
        "(classification) et prédiction de rendement agricole (régression), "
        "modèles servis depuis le registry MLflow."
    ),
    lifespan=lifespan,
)
setup_monitoring(app)

# CORS ouvert pour permettre l'accès depuis le frontend / les démos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommend_crop.router)
app.include_router(predict_yield.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": f"{APP_NAME} v{APP_VERSION} — voir /docs pour la documentation."}
