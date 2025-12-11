from fastapi import APIRouter, BackgroundTasks
from generator.data_generator_advanced import generate_data
from utils.progress import set_progress, get_progress, reset_progress

router = APIRouter()


@router.post("/create")
async def create_dataset(background: BackgroundTasks):
    """
    프론트가 호출하는 API
    - 즉시 응답
    - 백엔드에서 데이터 생성은 비동기로 실행
    """

    reset_progress()

    background.add_task(
        generate_data,
        save_to=("duckdb", "postgres", "mysql"),
        progress_callback=set_progress
    )

    return {"status": "started", "message": "데이터 생성 시작됨"}


@router.get("/progress")
async def progress():
    return get_progress()
