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

@router.get("/summary")
def analytics_summary():
    con = duckdb.connect(DB_PATH)

    # 데이터가 있다고 가정하는 기본 쿼리들
    try:
        total_users = con.execute("SELECT COUNT(DISTINCT user_id) FROM events").fetchone()[0]
        total_events = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    except:
        {
        "total_users": 0,
        "total_events": 0,
        "start_date": None,
        "end_date": None,
        "recent_dau": 0,
        "recent_revenue": 0  # 추후 확장
    }    

    dates = con.execute("""
        SELECT MIN(event_time), MAX(event_time) FROM events
    """).fetchone()

    start_date = str(dates[0]) if dates[0] else None
    end_date = str(dates[1]) if dates[1] else None

    recent_dau = con.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM events
        WHERE event_time >= NOW() - INTERVAL 1 DAY
    """).fetchone()[0]

    con.close()

    return {
        "total_users": total_users,
        "total_events": total_events,
        "start_date": start_date,
        "end_date": end_date,
        "recent_dau": recent_dau,
        "recent_revenue": 0  # 추후 확장
    }