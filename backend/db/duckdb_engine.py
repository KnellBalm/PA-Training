import duckdb
from settings import settings

duck_con = duckdb.connect(settings.DUCKDB_PATH, read_only=False)
class DuckDBEngine:
    """
    DuckDB는 connection.execute() 로 바로 pandas DataFrame 반환이 가능하므로
    Postgres/MySQL 과 달리 conn/cursor 개념이 필요 없다.
    """

    def connect(self):
        return duckdb.connect(settings.DUCKDB_PATH)

    def execute(self, query: str):
        con = self.connect()
        df = con.execute(query).df()
        con.close()

        return df
