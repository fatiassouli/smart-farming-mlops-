# API Documentation — Smart Farming Backend

Documentation de l'API REST du backend Smart Farming MLOps, construite avec **FastAPI**.

## Sommaire

- [Lancer l'API](#lancer-lapi)
- [Endpoints](#endpoints)
  - [`GET /health`](#get-health)
  - [`POST /recommend_crop`](#post-recommend_crop)
  - [`POST /predict_yield`](#post-predict_yield)
- [Codes d'erreur](#codes-derreur)
- [Documentation interactive (Swagger)](#documentation-interactive-swagger)

---

## Lancer l'API

### En local (sans Docker)

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Avec Docker

Depuis la **racine du projet** (le contexte de build doit être la racine, car le service importe `mlops/` et `models/`) :

```powershell
docker build -f backend/Dockerfile -t smart-farming-api .
docker run -p 8000:8000 -v ${PWD}/mlruns:/app/mlruns smart-farming-api
```

L'API est ensuite accessible sur `http://localhost:8000`.

---

## Endpoints

### `GET /health`

Vérifie que l'API est démarrée et que les modèles ML sont bien chargés en mémoire.

**Réponse `200 OK`**

```json
{
  "status": "ok",
  "classification_model_loaded": true,
  "regression_model_loaded": true
}
```

| Champ | Type | Description |
|---|---|---|
| `status` | string | `"ok"` si le serveur répond |
| `classification_model_loaded` | boolean | `true` si le modèle de classification (recommandation de culture) est chargé |
| `regression_model_loaded` | boolean | `true` si le modèle de régression (prédiction de rendement) est chargé |

---

### `POST /recommend_crop`

Recommande une culture adaptée à partir de paramètres agronomiques (modèle de classification, chargé via MLflow).

**Corps de la requête**

```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "temperature": 20.87,
  "humidity": 82.0,
  "ph": 6.5,
  "rainfall": 202.9
}
```

| Champ | Type | Bornes | Description |
|---|---|---|---|
| `N` | int | — | Teneur en azote du sol |
| `P` | int | — | Teneur en phosphore du sol |
| `K` | int | — | Teneur en potassium du sol |
| `temperature` | float | — | Température (°C) |
| `humidity` | float | — | Humidité relative (%) |
| `ph` | float | 0–14 | pH du sol |
| `rainfall` | float | — | Précipitations (mm) |

**Réponse `200 OK`**

```json
{
  "recommended_crop": "rice",
  "confidence": 90.0
}
```

**Réponse `503 Service Unavailable`** — si le modèle de classification n'est pas chargé (ex. registry MLflow vide en local).

**Réponse `422 Unprocessable Entity`** — si un champ est manquant ou hors bornes (ex. `ph` > 14).

---

### `POST /predict_yield`

Prédit le rendement agricole (t/ha) pour une zone, une culture et une année données (modèle de régression).

**Corps de la requête**

```json
{
  "area": "Morocco",
  "item": "Wheat",
  "year": 2020
}
```

| Champ | Type | Bornes | Description |
|---|---|---|---|
| `area` | string | — | Pays / région |
| `item` | string | — | Culture concernée |
| `year` | int | 1961–2030 | Année de la prédiction |

**Réponse `200 OK`**

```json
{
  "predicted_yield_tha": 1.7457,
  "predicted_yield_kgha": 1745.7
}
```

| Champ | Type | Description |
|---|---|---|
| `predicted_yield_tha` | float | Rendement prédit en tonnes par hectare |
| `predicted_yield_kgha` | float | Rendement prédit en kilogrammes par hectare |

**Réponse `422 Unprocessable Entity`** — si un champ est manquant, ou si `year` est hors des bornes 1961–2030.

---

## Codes d'erreur

| Code | Signification | Cas d'usage |
|---|---|---|
| `200` | OK | Requête traitée avec succès |
| `422` | Unprocessable Entity | Payload invalide (champ manquant, valeur hors bornes) — validation Pydantic |
| `503` | Service Unavailable | Modèle ML non chargé (ex. MLflow registry inaccessible ou vide) |

---

## Documentation interactive (Swagger)

FastAPI génère automatiquement une documentation interactive, accessible une fois le serveur lancé :

- **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

Ces interfaces permettent de tester chaque endpoint directement depuis le navigateur, avec les schémas de requête/réponse générés à partir des modèles Pydantic.