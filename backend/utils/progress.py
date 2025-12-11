import json
import os
from typing import Dict

PROGRESS_FILE = "/app/generator_progress.json"


def set_progress(progress: int, status: str = "running") -> None:
    """
    진행률 기록
    """
    data = {"progress": progress, "status": status}
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)


def get_progress() -> Dict:
    """
    진행률 조회 (없으면 기본값 0 반환)
    """
    if not os.path.exists(PROGRESS_FILE):
        return {"progress": 0, "status": "idle"}

    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            return {
                "progress": data.get("progress", 0),
                "status": data.get("status", "running")
            }
    except Exception:
        return {"progress": -1, "status": "error"}


def reset_progress() -> None:
    """
    초기화: 호출 시 0%로 리셋.
    """
    set_progress(0, status="idle")
