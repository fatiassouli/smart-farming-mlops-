# 📊 Data Ingestion - Smart Farming MLOps

## 🎯 Objectif

Ce module est responsable de l’ingestion des données brutes du projet Smart Farming.

Il permet de charger les datasets CSV, de les nettoyer légèrement et de les stocker dans une base de données DuckDB via DLT (Data Load Tool).

---

## 📁 Sources de données

Deux datasets sont utilisés :

- Crop Recommendation Dataset  
  `data/raw/Crop_recommendation.csv`

- Yield Dataset  
  `data/raw/yield.csv`

---

## ⚙️ Pipeline d’ingestion

Le pipeline suit les étapes suivantes :

1. Lecture des fichiers CSV avec Pandas
2. Nettoyage léger :
   - suppression des espaces inutiles
   - suppression des doublons
   - suppression des lignes vides
3. Conversion en format dictionnaire
4. Chargement dans DuckDB via DLT
5. Stockage dans une base locale

---

## 🗄️ Base de données (DuckDB)

Les données sont stockées dans une base DuckDB contenant :

### Tables créées :

- `crop_recommendation`
- `yield`

### Tables système DLT :

- `_dlt_loads`
- `_dlt_pipeline_state`
- `_dlt_version`

---

## 📦 Sortie du pipeline

Après exécution, les données sont disponibles dans : smart_farming_pipeline.DuckDB



Et copiées dans :

---

## ▶️ Comment exécuter le pipeline

Depuis la racine du projet : data/warehouse/smart_farming.DuckDB

```bash
python -m dataops.dlt_pipeline


import duckdb

conn = duckdb.connect("data/warehouse/smart_farming.duckdb")

print(conn.execute("SHOW TABLES").fetchall())