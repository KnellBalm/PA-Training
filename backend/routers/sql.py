from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from db.base import get_engine
from app.settings import settings

router = APIRouter()

# 요청 모델
class SQLRequest(BaseModel):
    engine: Literal["duckdb", "postgres", "mysql"]
    query: str


@router.post("/run")
async def run_sql(req: SQLRequest):
    """
    SQL 실행 엔드포인트.
    엔진별 실행 방식을 통일하여, 항상 같은 형식으로 결과 반환.
    """
    engine = get_engine(req.engine)

    try:
        # DuckDB는 pandas dataframe을 반환
        if req.engine == "duckdb":
            df = engine.execute(req.query)

            return {
                "columns": list(df.columns),
                "rows": df.to_dict(orient="records")
            }

        # Postgres / MySQL 공통 처리
        else:
            conn = engine.connect()
            result = engine.execute(conn, req.query)
            conn.close()

            return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/test")
async def test():
    return {"status": "sql router ok"}
