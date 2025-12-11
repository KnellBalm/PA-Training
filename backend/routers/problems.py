import os
from fastapi import APIRouter
from backend.settings import settings
from pydantic import BaseModel
import google.generativeai as genai
import duckdb

DB_PATH = os.getenv("DB_PATH", "db/event_log.duckdb")
router = APIRouter()
con = duckdb.connect(DB_PATH)
class ProblemRequest(BaseModel):
    difficulty: str = "hard"
    engine: str = "duckdb"

genai.configure(api_key=settings.GEMINI_API_KEY)


def load_schema(engine):
    # if engine == "duckdb":
    #     con = duckdb.connect("db/event_log.duckdb")
    # else:
    #     raise NotImplementedError("Postgres/MySQL schema load later")

    tables = con.execute("SELECT table_name FROM information_schema.tables").fetchall()
    
    schema_text = "Available tables:\n"
    for (t,) in tables:
        cols = con.execute(f"DESCRIBE {t}").fetchall()
        schema_text += f"\n**{t}**:\n"
        for col in cols:
            schema_text += f" - {col[0]} ({col[1]})\n"

    con.close()

    return schema_text


@router.post("/generate")
async def generate_problem(req: ProblemRequest):
    schema = load_schema(req.engine)

    prompt = f"""
You are an expert SQL instructor.
Generate **one SQL analytical problem** based on the schema below.

Difficulty level: {req.difficulty}

Schema:
{schema}

The problem must require real analytical thinking, similar to real-world BI/DA challenges.
Do NOT provide the answer. Question only.
"""

    response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    return {"problem": response.text}
