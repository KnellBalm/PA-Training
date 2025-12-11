from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import os
import duckdb

DB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")

router = APIRouter()

class HistoryIn(BaseModel):
  engine: str
  query: str
  problem: str | None = None
  correct: bool | None = None


def ensure_table():
  con = duckdb.connect(DB_PATH)
  con.execute("""
    CREATE TABLE IF NOT EXISTS query_history (
      id BIGINT,
      created_at TIMESTAMP,
      engine VARCHAR,
      query VARCHAR,
      problem VARCHAR,
      correct BOOLEAN
    )
  """)
  con.close()


@router.post("/add")
async def add_history(item: HistoryIn):
  ensure_table()
  con = duckdb.connect(DB_PATH)
  # id는 max+1 방식
  cur_max = con.execute("SELECT COALESCE(MAX(id), 0) FROM query_history").fetchone()[0]
  new_id = cur_max + 1

  con.execute(
    "INSERT INTO query_history VALUES (?, ?, ?, ?, ?, ?)",
    (
      new_id,
      datetime.utcnow(),
      item.engine,
      item.query,
      item.problem,
      item.correct,
    ),
  )
  con.close()
  return {"status": "ok", "id": new_id}


@router.get("/list")
async def list_history(limit: int = 30):
  ensure_table()
  con = duckdb.connect(DB_PATH)
  df = con.execute(
    "SELECT * FROM query_history ORDER BY created_at DESC LIMIT ?", [limit]
  ).df()
  con.close()
  return {"items": df.to_dict(orient="records")}
