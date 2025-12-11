import mysql.connector
from settings import settings


class MySQLEngine:
    def connect(self):
        return mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASS,
            database=settings.MYSQL_DB,
        )
