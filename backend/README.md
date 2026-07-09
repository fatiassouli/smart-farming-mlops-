# Smart Farming API — Backend & Déploiement

API REST FastAPI exposant les modules de Machine Learning du projet
**Smart Farming: Crop Recommendation and Yield Prediction**, servis
depuis le **registry MLflow** via `mlops/model_loader.py` (Personne 6).

## Architecture

```
SMART-FARMING-MLOPS/
├── backend/     <-- ce dossier (Personne 7)
│   ├── main.py
│   ├── api/routes/{health,recommend_crop,predict_yield}.py
│   ├── schemas/
│   ├── services/ml_service.py   <-- wrappe mlops.model_loader.get_model_loader()
│   └── tests/
├── mlops/       <-- Personne 6 (model_loader.py, mlflow_setup.py, ...)
└── mlruns/      <-- store MLflow local (généré automatiquement)
```

Le service `ml_service.py` ne réimplémente aucune logique de chargement ou
de prétraitement : il délègue entièrement à `mlops/model_loader.py`
(singleton `ModelLoader`), qui charge :
- `models:/ModeleClassification/Production` (fallback `Staging`)
- `models:/ModeleRegression/Production` (fallback `Staging`)

**Important** : les deux modèles utilisent les mêmes 7 features en entrée
(`N, P, K, temperature, humidity, ph, rainfall`) — le modèle de régression
prédit le rendement à partir des conditions du sol/climat, pas à partir de
culture/région/année.

## Lancement local

Depuis la **racine du projet** (important : `mlops/model_loader.py` utilise
un chemin MLflow relatif `./mlruns`, donc le cwd doit être la racine) :

```bash
pip install -r backend/requirements.txt
uvicorn main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

Documentation interactive : http://localhost:8000/docs (Swagger) ou
http://localhost:8000/redoc (Redoc).

## Lancement avec Docker

Le build doit se faire avec la **racine du repo comme contexte** (car le
service importe `mlops/`) :

```bash
docker build -f backend/Dockerfile -t smart-farming-api .
docker run -p 8000:8000 -v $(pwd)/mlruns:/app/mlruns smart-farming-api
```

## Endpoints

### `GET /health`
```json
{
  "status": "ok",
  "classification_model_loaded": true,
  "regression_model_loaded": true
}
```

### `POST /recommend_crop`
Recommande la culture la plus adaptée (module Classification).

**Requête**
```json
{
  "N": 90, "P": 42, "K": 43,
  "temperature": 20.87, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9
}
```

**Réponse 200**
```json
{ "recommended_crop": "rice", "confidence": 98.2 }
```

### `POST /predict_yield`
Prédit le rendement (module Régression), mêmes features en entrée que
`/recommend_crop`.

**Réponse 200**
```json
{ "predicted_yield_tha": 2.85, "predicted_yield_kgha": 2850.0 }
```

**Erreurs communes aux deux endpoints**
- `422` — champ manquant ou hors bornes (validation Pydantic)
- `503` — modèle non chargé côté MLflow registry (vérifier `/health`)
- `500` — erreur interne lors de la prédiction

## Tests

```bash
cd backend
pytest tests/ -v
```
8 tests couvrant `/health`, validation des payloads, et cas d'erreur
(les tests passent même sans registry MLflow peuplé : l'API répond alors
`503` proprement plutôt que de planter).

## Checklist d'intégration avec la Personne 6 (MLOps)

- [ ] Confirmer que les modèles sont bien enregistrés sous les noms
      `ModeleClassification` et `ModeleRegression` dans MLflow, avec un
      stage `Production` (ou `Staging`) assigné
- [ ] Confirmer que le modèle de régression est un pipeline complet
      (prétraitement inclus), puisque `model_loader.py` appelle
      `model.predict(X)` directement sur les features brutes
- [ ] S'assurer que `mlruns/` est accessible (volume partagé en Docker,
      ou tracking server MLflow distant si vous en utilisez un)
