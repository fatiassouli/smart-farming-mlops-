# Transformation dbt — Smart Farming MLOps

Pipeline de transformation des données (dbt + DuckDB) pour le projet Smart Farming MLOps.

**Responsable :** Layla Ouarrak — Personne 3 (Analytics & Transformation)

## Comment lancer

```bash
cd transform
dbt run      # construit les tables
dbt test     # vérifie la qualité des données
dbt docs generate && dbt docs serve --port 8085   # documentation
```

## Tables produites

**`mart_crop_recommendation`** (2200 lignes) — données sol/climat pour recommander une culture.
Colonnes : `nitrogen`, `phosphorus`, `potassium`, `temperature`, `humidity`, `ph`, `rainfall`, `crop_label`, `npk_total`, `np_ratio`, `nk_ratio`, `heat_humidity`, `rain_temp`

**`mart_yield`** (56 717 lignes) — rendement agricole par pays/culture/année.
Colonnes : `country`, `crop`, `year`, `year_norm`, `yield_hg_ha`, `yield_tonnes_per_ha`, `log_yield`

## Qualité des données

12/12 tests dbt passés · 0 valeur manquante · 0 doublon

## ⚠️ Pour le ML

Les noms de colonnes sont en minuscules (snake_case). Le modèle ML attend des noms différents (`N`, `P`, `K`, `label`, `NPK_total`...). Le renommage doit se faire côté script Python d'inférence, pas dans dbt.

## Analyse exploratoire

Voir `notebooks/01_eda_crop_yield.ipynb`
