from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

from db.base import get_engine


router = APIRouter()


class SQLRequest(BaseModel):
    engine: Literal["duckdb", "postgres", "mysql"]
    query: str


@router.post("/run")
async def run_sql(req: SQLRequest):
    engine = get_engine(req.engine)
    conn = engine.connect()
    cur = conn.cursor()

    cur.execute(req.query)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall() if cur.description else []

    cur.close()
    conn.close()

    return {
        "columns": cols,
        "rows": [dict(zip(cols, r)) for r in rows],
    }
