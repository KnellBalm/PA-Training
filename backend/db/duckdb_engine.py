import duckdb
from settings import settings


class DuckDBEngine:
    def connect(self):
        return duckdb.connect(settings.DUCKDB_PATH)
