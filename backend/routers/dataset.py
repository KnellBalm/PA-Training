from fastapi import APIRouter
import os
import duckdb

DB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")

router = APIRouter()

@router.get("/versions")
async def list_versions():
    con = duckdb.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS dataset_versions (
          version_id BIGINT,
          created_at TIMESTAMP,
          generator_type VARCHAR,
          start_date DATE,
          end_date DATE,
          n_users BIGINT,
          n_events BIGINT
        )
    """)
    df = con.execute(
        "SELECT * FROM dataset_versions ORDER BY created_at DESC"
    ).df()
    con.close()
    return {"versions": df.to_dict(orient="records")}
