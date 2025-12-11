from settings import settings
from db.duckdb_engine import DuckDBEngine
from db.postgres_engine import PostgresEngine
from db.mysql_engine import MySQLEngine

def get_engine(engine: str):
    if engine == "duckdb": return DuckDBEngine()
    if engine == "postgres": return PostgresEngine()
    if engine == "mysql": return MySQLEngine()

    else:
        raise ValueError(f"Unknown DB engine: {engine}")
