import os
from fastapi import APIRouter
import duckdb
from pydantic import BaseModel
import pandas as pd

DB_PATH = os.getenv("DB_PATH", "db/event_log.duckdb")
router = APIRouter()

con = duckdb.connect(DB_PATH)
class EvalRequest(BaseModel):
    expected: str
    user: str

def run_sql(q):
    # con = duckdb.connect("db/event_log.duckdb")
    df = con.execute(q).df()
    con.close()
    return df

@router.post("/eval")
async def evaluate_sql(req: EvalRequest):
    try:
        expected_df = run_sql(req.expected)
    except Exception as e:
        return {"error": f"Expected SQL Error: {str(e)}"}

    try:
        user_df = run_sql(req.user)
    except Exception as e:
        return {"correct": False, "error": f"User SQL Error: {str(e)}"}

    # 정답 여부 판단
    correct = user_df.equals(expected_df)

    # 상세 diff
    missing = expected_df.merge(user_df, how="left", indicator=True)
    missing_rows = missing[missing["_merge"] == "left_only"]

    extra = user_df.merge(expected_df, how="left", indicator=True)
    extra_rows = extra[extra["_merge"] == "left_only"]

    return {
        "correct": correct,
        "expected_rows": len(expected_df),
        "user_rows": len(user_df),
        "missing_rows": missing_rows.to_dict(orient="records"),
        "extra_rows": extra_rows.to_dict(orient="records"),
    }
