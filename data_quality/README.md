
# data_quality

Module de qualité des données du projet **smart-farming-mlops**.
Il garantit que les jeux de données `yield.csv` (FAOSTAT) et
`Crop_recommendation.csv` (Kaggle) respectent des règles de complétude, de
validité et de cohérence avant d'entrer dans les pipelines de feature
engineering et d'entraînement des modèles.

## Structure

```
data_quality/
├── contracts/
│   └── data_contracts.yml     # Data Contracts formels (schéma + SLA + gouvernance)
├── tests/
│   ├── conftest.py            # Fixtures pytest (DataFrames, schémas)
│   ├── schemas.py             # Schémas Pandera (source de vérité technique)
│   ├── test_completeness.py   # Critère 1 : complétude
│   ├── test_validity.py       # Critère 2 : validité
│   └── test_consistency.py    # Critère 3 : cohérence
├── validators/
│   ├── contract_validator.py  # Valide les datasets contre data_contracts.yml
│   └── pipeline_validator.py  # Orchestrateur : pytest + contrats -> rapport
├── lineage/
│   ├── data_lineage.md        # Documentation du flux de données
│   └── lineage_visual.py      # Génère data_lineage.png
├── metadata/
│   └── dataset_metadata.yml   # Métadonnées de gouvernance par dataset
└── reports/
    └── pipeline_report.json   # Rapport généré par pipeline_validator.py
```

Les fichiers sources (`yield.csv`, `Crop_recommendation.csv`) se trouvent à
la racine du repo, dans `data/raw/`, et sont référencés par leur chemin
relatif dans `contracts/data_contracts.yml`.

## Installation

```bash

#dans le venv du projet :
pip install pandas pandera pyyaml pytest matplotlib
```

## Utilisation

### Lancer la suite de tests

```bash
cd data_quality
pytest tests/ -v
```

### Valider les Data Contracts

```bash
cd data_quality
python -m validators.contract_validator --all
```

### Lancer le pipeline complet (tests + contrats + rapport)

```bash
cd data_quality
python -m validators.pipeline_validator --report ../reports/pipeline_report.json
# -> écrit reports/pipeline_report.json à la racine du repo
```

### Régénérer le diagramme de lineage

```bash
cd data_quality
python lineage/lineage_visual.py
# -> écrit lineage/data_lineage.png
```

