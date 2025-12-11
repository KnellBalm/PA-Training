import os
from datetime import date, timedelta
import random

DATASET_DIR = os.getenv("DATASET_DIR", "db")
DATASET_META_PATH = os.path.join(DATASET_DIR, "datasets.json")

# ------------------------------
# 자동 기간 설정
# ------------------------------
TOTAL_DAYS = random.randint(180, 220)   # 약 6~7개월
TODAY = date.today()
START_DATE = TODAY - timedelta(days=TOTAL_DAYS)
END_DATE = TODAY

# ------------------------------
# User 설정
# ------------------------------
N_USERS = 50000               # 사용자 수
NEW_USERS_DAILY = (50, 300)   # 하루 신규 가입자 범위

# ------------------------------
# 이벤트 확률
# ------------------------------
PROB_VISIT = 1.0
PROB_VIEW = 0.9
PROB_CART = 0.3
PROB_CHECKOUT = 0.18
PROB_PURCHASE = 0.12

# ------------------------------
# 디바이스/채널 설정
# ------------------------------
DEVICES = ["web", "android", "ios"]
CHANNELS = ["organic", "ads", "email", "push"]

# ------------------------------
# 프로모션 일자 자동 생성
# ------------------------------
PROMOTION_DAYS = random.sample(
    [START_DATE + timedelta(days=i) for i in range(TOTAL_DAYS)],
    k=random.randint(8, 15)
)

PROMOTION_BOOST = 3.0  # 구매율 × 3 증가

# ------------------------------
# DB 정보
# ------------------------------
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")

PG_CONFIG = {
    "host": os.getenv("PG_HOST", "postgres"),
    "port": int(os.getenv("PG_PORT", 5432)),
    "user": os.getenv("PG_USER", "analytics"),
    "password": os.getenv("PG_PASS", "analytics123"),
    "database": os.getenv("PG_DB", "analytics"),
}

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "analytics"),
    "password": os.getenv("MYSQL_PASS", "analytics123"),
    "database": os.getenv("MYSQL_DB", "analytics"),
}
