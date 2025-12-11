import os
import duckdb
from fastapi import APIRouter
from fastapi import BackgroundTasks
from generator.data_generator_advanced import generate_data as generate_advanced
from generator.utils.progress import get_progress

router = APIRouter()


@router.post("/initialize")
async def initialize_duckdb():
    db_path = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)

    # 간단한 스키마: events / daily_metrics
    con.execute("""
        CREATE TABLE IF NOT EXISTS events (
            user_id INTEGER,
            event_name VARCHAR,
            event_time TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date DATE,
            revenue DOUBLE
        )
    """)

    con.close()
    return {"status": "initialized", "db": db_path}

@router.post("/advanced")
async def generate_advanced_data(background_tasks: BackgroundTasks):
    """
    고급형(20M+) 데이터 생성 작업을 백그라운드로 실행.
    """
    def task():
        generate_advanced(("duckdb",))  # 필요하면 postgres/mysql도 추가 가능

    background_tasks.add_task(task)
    return {"status": "started", "message": "Advanced data generation started."}

@router.get("/progress")
async def generator_progress():
    return get_progress()