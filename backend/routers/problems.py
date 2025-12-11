from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from settings import settings

router = APIRouter()

class ProblemRequest(BaseModel):
    difficulty: str = "hard"
    engine: str = "duckdb"


genai.configure(api_key=settings.GEMINI_API_KEY)


@router.post("/generate")
async def generate_problem(req: ProblemRequest):

    prompt = f"""
    Generate a realistic SQL problem for a data analyst.
    Difficulty: {req.difficulty}
    Engine: {req.engine}

    Requirements:
    - Use the dataset fields typical for event logs: user_id, event_name, event_time, value, revenue.
    - Should require JOIN, WINDOW, GROUPING or filtering logic.
    - Must output only the problem, no explanation.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)

        return {"problem": response.text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
