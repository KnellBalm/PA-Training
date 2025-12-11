from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    DUCKDB_PATH: str = "/app/db/event_log.duckdb"

    PG_HOST: str = "postgres"
    PG_PORT: int = 5432
    PG_USER: str = "analytics"
    PG_PASS: str = "analytics123"
    PG_DB: str = "analytics"

    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "analytics"
    MYSQL_PASS: str = "analytics123"
    MYSQL_DB: str = "analytics"

    GEMINI_API_KEY: str = ""

    class Config:
        env_file = "/app/.env"
        extra = "ignore"

settings = Settings()  # ← 반드시 이 라인 있어야 함
