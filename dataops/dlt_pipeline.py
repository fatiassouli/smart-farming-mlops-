import pandas as pd
import duckdb
import dlt
import os
from pathlib import Path

from config.config import (
    CROP_DATASET,
    YIELD_DATASET,
    CROP_TABLE,
    YIELD_TABLE,
)

# =========================
# PATH UNIQUE (DATA WAREHOUSE)
# =========================
WAREHOUSE_DB = Path("data/warehouse/smart_farming.duckdb")


# =========================
# LOAD + CLEAN
# =========================
def load_and_clean(path):
    df = pd.read_csv(path)

    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()

    df = df.drop_duplicates()
    df = df.dropna(how="all")

    return df


# =========================
# PIPELINE (encapsulé pour être importable sans effet de bord)
# =========================
def run_pipeline():
    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)
    os.environ["DESTINATION__DUCKDB__CREDENTIALS"] = str(WAREHOUSE_DB)

    crop_df = load_and_clean(CROP_DATASET)
    yield_df = load_and_clean(YIELD_DATASET)

    print("Crop shape:", crop_df.shape)
    print("Yield shape:", yield_df.shape)

    pipeline = dlt.pipeline(
        pipeline_name="smart_farming_pipeline",
        destination="duckdb",
        dataset_name="sf_data",
    )

    # write_disposition="replace" : chaque run remplace la table au lieu
    # de l'empiler (corrige la duplication ×12 constatée en mode append par défaut)
    crop_resource = dlt.resource(
        crop_df.to_dict(orient="records"),
        name=CROP_TABLE,
        write_disposition="replace",
    )
    yield_resource = dlt.resource(
        yield_df.to_dict(orient="records"),
        name=YIELD_TABLE,
        write_disposition="replace",
    )

    info = pipeline.run([crop_resource, yield_resource])

    print("\nPipeline info:")
    print(info)
    print("\n✔ Data stored in:", WAREHOUSE_DB)

    return info


if __name__ == "__main__":
    run_pipeline()

    conn = duckdb.connect(str(WAREHOUSE_DB))

    print("\n📌 Tables disponibles :")
    print(conn.execute("SHOW TABLES").fetchall())

    print("\n📌 Tables avec schema :")
    print(
        conn.execute(
            """
        SELECT table_schema, table_name
        FROM information_schema.tables
    """
        ).fetchall()
    )

    print("\n📌 Sample crop :")
    print(conn.execute("SELECT * FROM sf_data.crop_recommendation LIMIT 5").fetchdf())

    conn.close()