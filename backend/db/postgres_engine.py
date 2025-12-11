import psycopg2
from psycopg2.extras import RealDictCursor
import settings


class PostgresEngine:
    """
    PostgreSQL 실행 엔진
    - connect() : connection 반환
    - execute(conn, query) : dict 형식 결과 반환
    """

    def connect(self):
        return psycopg2.connect(
            host=settings.PG_HOST,
            port=settings.PG_PORT,
            dbname=settings.PG_DB,
            user=settings.PG_USER,
            password=settings.PG_PASS,
        )

    def execute(self, conn, query: str):
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cur.execute(query)

            # SELECT 쿼리
            if cur.description:
                rows = cur.fetchall()
                columns = [col.name for col in cur.description]

                return {
                    "columns": columns,
                    "rows": rows,
                }

            # UPDATE, INSERT, DELETE
            conn.commit()
            return {
                "columns": [],
                "rows": [],
            }

        finally:
            cur.close()
