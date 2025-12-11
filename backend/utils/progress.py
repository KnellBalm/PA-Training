import json
import os

PROGRESS_FILE = "generator_progress.json"

def set_progress(status: str, progress: int):
    data = {"status": status, "progress": progress}
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

def get_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"status": "idle", "progress": 0}
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)
