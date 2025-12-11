from db.duckdb_engine import DuckDBEngine
from db.postgres_engine import PostgresEngine
from db.mysql_engine import MySQLEngine


def get_engine(name: str):
    """
    요청된 엔진 이름에 따라 적절한 Engine 클래스를 반환.
    FastAPI 라우터(sql.py)에서 호출.
    """
    name = name.lower()

    if name == "duckdb":   return DuckDBEngine()
    if name == "postgres": return PostgresEngine()
    if name == "mysql":    return MySQLEngine()

    raise ValueError(f"Unknown engine type: {name}")
