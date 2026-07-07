# DataOps - Smart Farming Pipeline

## 🎯 Scope
This module handles ONLY data ingestion.

## 📌 Responsibilities
- Load raw CSV files
- Clean basic data (strip, duplicates)
- Load into DuckDB using dlt

## 🚫 Not included
- Feature engineering (dbt team)
- Machine learning (ML team)
- API deployment (Dev team)

## 🚀 Pipeline
CSV → Pandas → dlt → DuckDB (raw layer)

## ▶ Run
```bash
python dlt_pipeline.py