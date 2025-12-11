from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    sql,
    analytics,
    dashboard,
    generator,
    schema,
    history,
    problems,
    dataset,
    sql_eval
)

app = FastAPI(title="Analytics Training Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 라우터
app.include_router(sql.router, prefix="/sql", tags=["sql"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(generator.router, prefix="/generator", tags=["generator"])

# 새 라우터
app.include_router(schema.router, prefix="/schema", tags=["schema"])
app.include_router(history.router, prefix="/sql/history", tags=["history"])
app.include_router(problems.router, prefix="/problems", tags=["problems"])
app.include_router(dataset.router, prefix="/datasets", tags=["datasets"])
app.include_router(sql_eval.router, prefix="/sql/eval", tags=["sql-eval"])

@app.get("/health")
async def health():
    return {"status": "ok"}
