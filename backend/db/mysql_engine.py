import mysql.connector
import settings


class MySQLEngine:
    """
    MySQL 실행 엔진
    - connect() : MySQL Connection 반환
    - execute(conn, query) : dict 형식 결과 반환
    """

    def connect(self):
        return mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            database=settings.MYSQL_DB,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASS,
        )

    def execute(self, conn, query: str):
        cur = conn.cursor()

        try:
            cur.execute(query)

            if cur.description:
                columns = [col[0] for col in cur.description]
                rows = cur.fetchall()

                rows_dict = [
                    {columns[i]: row[i] for i in range(len(columns))}
                    for row in rows
                ]

                return {
                    "columns": columns,
                    "rows": rows_dict,
                }

            conn.commit()
            return {"columns": [], "rows": []}

        finally:
            cur.close()
