from fastapi import APIRouter
import os
import duckdb

router = APIRouter()
DB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")

@router.get("/schema")
async def get_schema():
    con = duckdb.connect(DB_PATH)
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    ).fetchall()

    schema = {}

    for (t,) in tables:
        cols = con.execute(f"DESCRIBE {t}").fetchall()
        schema[t] = [c[0] for c in cols]

    con.close()
    return {"tables": schema}

@router.get("/tables")
def get_tables():
    tables = get_table_names()
    return {"tables": tables}

@router.get("/preview")
def preview(table: str):
    con = get_connection()
    q = f"SELECT * FROM {table} LIMIT 20"
    rows = con.execute(q).fetchall()
    cols = [c[0] for c in con.description]
    con.close()
    return {"rows": [dict(zip(cols, r)) for r in rows]}
