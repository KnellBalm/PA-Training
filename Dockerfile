FROM python:3.12-slim

WORKDIR /app

# OS 기본 패키지
RUN apt-get update && apt-get install -y \
    curl build-essential && \
    apt-get clean

# Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app 전체 복사
COPY . .

EXPOSE 8501

# 환경변수 (DuckDB 파일 경로 등)
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "web/app.py"]
