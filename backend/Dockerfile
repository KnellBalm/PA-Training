FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# DuckDB 파일을 /data/event_log.duckdb 로 사용
ENV DUCKDB_PATH=/data/event_log.duckdb

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
