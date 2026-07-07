# Data Lineage — Module Data Quality

## 1. Objectif

Documenter le flux des données depuis les sources brutes jusqu'au rapport
de validation final, limite du périmètre Data Quality (Personne 4).

## 2. Sources de données

| Source | Fichier | Origine | Volume |
|---|---|---|---|
| FAOSTAT | `yield.csv` | Rendements agricoles 1961-2016 | 56 717 lignes |
| Kaggle | `Crop_recommendation.csv` | Recommandation de culture | 2 200 lignes |

## 3. Flux de données (pipeline Data Quality)
┌──────────────────┐     ┌──────────────────┐
│   yield.csv      │     │ Crop_recommend.  │
│   (FAOSTAT)      │     │   csv (Kaggle)    │
└────────┬─────────┘     └────────┬─────────┘
│                        │
▼                        ▼
┌─────────────────────────────────────┐
│        RAW ZONE (data/raw/*.csv)    │
└────────────────┬────────────────────┘
│
▼
┌─────────────────────────────────────┐
│   GATE 1 — Data Quality Tests        │◄── test_completeness.py
│   (pytest : completeness, validity,  │◄── test_validity.py
│    consistency)                      │◄── test_consistency.py
└────────────────┬────────────────────┘
│ (si échec → pipeline bloqué)
▼
┌─────────────────────────────────────┐
│   GATE 2 — Data Contract Validation  │◄── contracts/data_contracts.yml
│   (contract_validator.py)            │◄── tests/schemas.py (Pandera)
└────────────────┬────────────────────┘
│
▼
┌─────────────────────────────────────┐
│   RAPPORT CONSOLIDÉ                  │◄── pipeline_validator.py
│   (pipeline_report.json)             │◄── Livrable final Personne 4
└─────────────────────────────────────┘

## 4. Points de contrôle (Quality Gates)

| Gate | Fichier | Bloquant ? |
|---|---|---|
| 1. Completeness | `tests/test_completeness.py` | Oui |
| 2. Validity | `tests/test_validity.py` | Oui |
| 3. Consistency | `tests/test_consistency.py` | Oui |
| 4. Contract Validation | `validators/contract_validator.py` | Oui |
| 5. Rapport consolidé | `validators/pipeline_validator.py` | Non (informatif) |

## 5. Traçabilité

- Modifications des règles : `tests/schemas.py` (Pandera) + `contracts/data_contracts.yml`
- Gouvernance (volume, propriétaire) : `metadata/dataset_metadata.yml`
- Rapport d'audit : `reports/pipeline_report.json` (généré par CI/CD