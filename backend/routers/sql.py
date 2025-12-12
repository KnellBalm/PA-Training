from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from db.base import get_engine

router = APIRouter()

class SQLRequest(BaseModel):
    engine: Literal["duckdb", "postgres", "mysql"]
    query: str


@router.post("/run")
async def run_sql(req: SQLRequest):
    """
    엔진 종류에 상관없이 SQL 실행 결과를
    { columns: [...], rows: [...] } 형태로 통일하여 반환
    """

    try:
        engine = get_engine(req.engine)

        # DuckDB 엔진
        if req.engine == "duckdb":
            con = engine.connect()
            result = con.execute(req.query)
            print(f"{result=}")
            # DuckDB는 fetchdf가 가장 빠름
            df = result.fetchdf()

            return {
                "columns": list(df.columns),
                "rows": df.to_dict(orient="records")
            }
        else:
            # Postgres / MySQL 엔진
            conn = engine.connect()
            try:
                result = engine.execute(conn, req.query)
            finally:
                conn.close()
            print(f"{result=}")
            if isinstance(result, dict):
                cols = result.get("columns", [])
                rows = result.get("rows", [])
            else:
                cols, rows = result
                rows = [dict(zip(cols, r)) for r in rows]

            return {
                "columns": cols,
                "rows": rows
            }
        print(f"Query successful. Fetched {len(rows)} rows.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history/test")
async def test():
    return {"status": "sql router ok"}
