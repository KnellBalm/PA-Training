import os
import duckdb
from fastapi import APIRouter

DB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")

router = APIRouter()


def _con():
    return duckdb.connect(DB_PATH)


@router.get("/daily-metrics")
async def daily_metrics():
    con = _con()
    df = con.execute("SELECT * FROM daily_metrics ORDER BY date").df()
    con.close()
    return {
        "columns": list(df.columns),
        "rows": df.to_dict(orient="records")
    }
