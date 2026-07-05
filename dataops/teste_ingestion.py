import duckdb

DB_PATH = "smart_farming_pipeline.duckdb"

conn = duckdb.connect(DB_PATH)

tables = conn.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'smart_farming'
""").fetchall()

print("Tables :", tables)

assert len(tables) >= 2, "❌ Ingestion failed"

print("✅ Ingestion OK")

conn.close()