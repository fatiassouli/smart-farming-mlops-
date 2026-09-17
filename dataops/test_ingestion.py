import duckdb

from dataops.dlt_pipeline import load_and_clean
from config.config import CROP_DATASET, YIELD_DATASET, CROP_TABLE, YIELD_TABLE

DB_PATH = "data/warehouse/smart_farming.duckdb"
SCHEMA = "sf_data"

conn = duckdb.connect(DB_PATH)

tables = conn.execute(
    f"""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = '{SCHEMA}'
"""
).fetchall()
table_names = [t[0] for t in tables]

print("Tables :", table_names)
assert len(table_names) >= 2, "❌ Tables manquantes dans le schéma sf_data"

# Vérification de la volumétrie : détecte toute duplication
# (ex. régression vers write_disposition="append")
checks = {
    CROP_TABLE: CROP_DATASET,
    YIELD_TABLE: YIELD_DATASET,
}

for table, source_path in checks.items():
    expected = len(load_and_clean(source_path))
    actual = conn.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{table}").fetchone()[0]
    print(f"{table} : source nettoyée={expected} | DuckDB={actual}")
    assert actual == expected, (
        f"❌ Volumétrie incohérente sur {table} : {actual} lignes en base "
        f"vs {expected} attendues (duplication possible)"
    )

print("✅ Ingestion OK — tables présentes et volumétrie conforme")
conn.close()