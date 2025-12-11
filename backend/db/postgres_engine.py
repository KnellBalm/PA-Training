import psycopg2
from settings import settings


class PostgresEngine:
    def connect(self):
        return psycopg2.connect(
            host=settings.PG_HOST,
            port=settings.PG_PORT,
            dbname=settings.PG_DB,
            user=settings.PG_USER,
            password=settings.PG_PASS,
        )
