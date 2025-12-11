import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # DuckDB
    DUCKDB_PATH: str = os.getenv("DUCKDB_PATH", "/app/db/event_log.duckdb")

    # PostgreSQL
    PG_HOST: str = os.getenv("PG_HOST", "postgres")
    PG_PORT: int = int(os.getenv("PG_PORT", 5432))
    PG_USER: str = os.getenv("PG_USER", "analytics")
    PG_PASS: str = os.getenv("PG_PASS", "analytics123")
    PG_DB: str = os.getenv("PG_DB", "analytics")

    # MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "mysql")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "analytics")
    MYSQL_PASS: str = os.getenv("MYSQL_PASS", "analytics123")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "analytics")


settings = Settings()
