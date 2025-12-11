import os
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
import duckdb
import psycopg2
import mysql.connector

DB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")

router = APIRouter()

class SQLRequest(BaseModel):
    engine: Literal["duckdb", "postgres", "mysql"]
    query: str


def run_duckdb(query: str):
    con = duckdb.connect(DB_PATH)
    df = con.execute(query).df()
    con.close()
    return df


def run_postgres(query: str):
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "postgres"),
        port=int(os.getenv("PG_PORT", 5432)),
        user=os.getenv("PG_USER", "analytics"),
        password=os.getenv("PG_PASS", "analytics123"),
        database=os.getenv("PG_DB", "analytics"),
    )
    cur = conn.cursor()
    cur.execute(query)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall() if cur.description else []
    cur.close()
    conn.close()
    return cols, rows


def run_mysql(query: str):
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "analytics"),
        password=os.getenv("MYSQL_PASS", "analytics123"),
        database=os.getenv("MYSQL_DB", "analytics"),
    )
    cur = conn.cursor()
    cur.execute(query)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall() if cur.description else []
    cur.close()
    conn.close()
    return cols, rows


@router.post("/run")
async def run_sql(req: SQLRequest):
    if req.engine == "duckdb":
        df = run_duckdb(req.query)
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records")}
    elif req.engine == "postgres":
        cols, rows = run_postgres(req.query)
        return {"columns": cols, "rows": [dict(zip(cols, r)) for r in rows]}
    else:
        cols, rows = run_mysql(req.query)
        return {"columns": cols, "rows": [dict(zip(cols, r)) for r in rows]}
