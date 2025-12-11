import os
import random
from datetime import timedelta, datetime

import duckdb
import psycopg2
import mysql.connector
from tqdm import tqdm

from generator.config import (
    START_DATE,
    END_DATE,
    N_USERS,
    NEW_USERS_DAILY,
    PROB_VISIT,
    PROB_VIEW,
    PROB_CART,
    PROB_CHECKOUT,
    PROB_PURCHASE,
    DEVICES,
    CHANNELS,
    PROMOTION_DAYS,
    PROMOTION_BOOST,
    DUCKDB_PATH,
    PG_CONFIG,
    MYSQL_CONFIG,
)

from generator.utils import generate_session_id, generate_ts

# progress 파일은 backend/utils/progress.py에서 관리
try:
    from backend.utils.progress import set_progress
except ImportError:
    # 백엔드 컨텍스트가 아닐 때는 더미 함수
    def set_progress(status: str, progress: int) -> None:  # type: ignore
        pass


# ----------------------------------------
# 사용자 생성
# ----------------------------------------


def generate_users():
    """
    일자별로 신규 유저를 생성해 전체 유저 딕셔너리를 반환.
    {user_id: {"signup_date": date, "device": ..., "channel": ...}}
    """
    users = {}
    cur_user_id = 1
    total_days = (END_DATE - START_DATE).days

    for d in range(total_days):
        day = START_DATE + timedelta(days=d)
        new_users = random.randint(*NEW_USERS_DAILY)

        for _ in range(new_users):
            users[cur_user_id] = {
                "signup_date": day,
                "device": random.choice(DEVICES),
                "channel": random.choice(CHANNELS),
            }
            cur_user_id += 1

        # 안전장치: 최대 유저 수를 초과하지 않도록
        if cur_user_id > N_USERS:
            break

    return users


# ----------------------------------------
# Event 생성 (streaming)
# ----------------------------------------


def generate_events(users):
    """
    (events_batch, daily_batch)를 yield 하는 제너레이터.
    events_batch: [(user_id, session_id, event_name, event_time, device, channel), ...]
    daily_batch:  [(date, revenue, purchases), ...]
    """
    total_days = (END_DATE - START_DATE).days
    events_batch = []
    daily_batch = []
    BATCH_THRESHOLD = 200_000

    user_ids = list(users.keys())

    for d in tqdm(range(total_days), desc="Generating events"):
        day = START_DATE + timedelta(days=d)
        day_str = str(day)

        # 프로그레스 업데이트
        progress = int((d / max(total_days, 1)) * 100)
        set_progress("running", progress)

        # 오늘 활성 유저
        if not user_ids:
            continue
        k = min(len(user_ids), random.randint(3000, 12000))
        if k <= 0:
            continue
        active_users = random.sample(user_ids, k=k)

        revenue_today = 0
        purchase_count = 0

        boost = PROMOTION_BOOST if day in PROMOTION_DAYS else 1.0

        for user in active_users:
            base = users.get(user, {})
            device = base.get("device", random.choice(DEVICES))
            channel = base.get("channel", random.choice(CHANNELS))

            session_id = generate_session_id()

            # VISIT (무조건 1개)
            events_batch.append(
                (
                    user,
                    session_id,
                    "visit",
                    generate_ts(day_str),
                    device,
                    channel,
                )
            )

            # VIEW
            if random.random() < PROB_VIEW:
                events_batch.append(
                    (
                        user,
                        session_id,
                        "view_product",
                        generate_ts(day_str),
                        device,
                        channel,
                    )
                )

            # CART
            if random.random() < PROB_CART:
                events_batch.append(
                    (
                        user,
                        session_id,
                        "add_to_cart",
                        generate_ts(day_str),
                        device,
                        channel,
                    )
                )

            # CHECKOUT
            if random.random() < PROB_CHECKOUT:
                events_batch.append(
                    (
                        user,
                        session_id,
                        "checkout",
                        generate_ts(day_str),
                        device,
                        channel,
                    )
                )

            # PURCHASE
            if random.random() < PROB_PURCHASE * boost:
                amount = random.randint(5, 200)
                revenue_today += amount
                purchase_count += 1

                events_batch.append(
                    (
                        user,
                        session_id,
                        "purchase",
                        generate_ts(day_str),
                        device,
                        channel,
                    )
                )

        daily_batch.append((day_str, float(revenue_today), int(purchase_count)))

        # 배치 기준량을 넘으면 yield
        if len(events_batch) >= BATCH_THRESHOLD:
            yield events_batch, daily_batch
            events_batch = []
            daily_batch = []

    # 마지막 남은 배치
    if events_batch or daily_batch:
        yield events_batch, daily_batch


# ----------------------------------------
# DB 저장 함수들 (스트리밍 대응)
# ----------------------------------------


def init_duckdb(conn: duckdb.DuckDBPyConnection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            user_id INTEGER,
            session_id VARCHAR,
            event_name VARCHAR,
            event_time TIMESTAMP,
            device VARCHAR,
            channel VARCHAR
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date DATE,
            revenue DOUBLE,
            purchases INTEGER
        )
        """
    )
    conn.execute("DELETE FROM events")
    conn.execute("DELETE FROM daily_metrics")


def init_postgres(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            user_id INT,
            session_id TEXT,
            event_name TEXT,
            event_time TIMESTAMP,
            device TEXT,
            channel TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date DATE,
            revenue FLOAT,
            purchases INT
        )
        """
    )
    cur.execute("DELETE FROM events")
    cur.execute("DELETE FROM daily_metrics")


def init_mysql(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            user_id INT,
            session_id VARCHAR(64),
            event_name VARCHAR(50),
            event_time DATETIME,
            device VARCHAR(20),
            channel VARCHAR(20)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date DATE,
            revenue DOUBLE,
            purchases INT
        )
        """
    )
    cur.execute("DELETE FROM events")
    cur.execute("DELETE FROM daily_metrics")


# ----------------------------------------
# Dataset 버전 기록 (DuckDB 내부 메타)
# ----------------------------------------


def register_dataset_version(generator_type: str = "advanced") -> None:
    """
    DuckDB 내부에 dataset_versions 테이블로 버전 메타를 기록.
    """
    con = duckdb.connect(DUCKDB_PATH)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS dataset_versions (
          version_id BIGINT,
          created_at TIMESTAMP,
          generator_type VARCHAR,
          start_date DATE,
          end_date DATE,
          n_users BIGINT,
          n_events BIGINT
        )
        """
    )
    cur_max = con.execute(
        "SELECT COALESCE(MAX(version_id), 0) FROM dataset_versions"
    ).fetchone()[0]
    new_id = int(cur_max) + 1

    n_users = con.execute(
        "SELECT COUNT(DISTINCT user_id) FROM events"
    ).fetchone()[0]
    n_events = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    con.execute(
        "INSERT INTO dataset_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            new_id,
            datetime.utcnow(),
            generator_type,
            START_DATE,
            END_DATE,
            int(n_users),
            int(n_events),
        ),
    )
    con.close()


# ----------------------------------------
# MAIN orchestration
# ----------------------------------------


def generate_data(
    save_to=("duckdb", "postgres", "mysql"),
) -> None:
    """
    고급형 데이터 생성기.
    - save_to: ("duckdb", "postgres", "mysql") 중 하나 또는 여러 개 선택 가능
    """
    print("📌 사용자 생성 중...")
    users = generate_users()

    print("📌 이벤트 생성 및 저장 시작 (streaming)...")

    # DuckDB 준비
    duck_con = None
    if "duckdb" in save_to:
        os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)
        duck_con = duckdb.connect(DUCKDB_PATH)
        init_duckdb(duck_con)

    # Postgres 준비
    pg_con = pg_cur = None
    if "postgres" in save_to:
        pg_con = psycopg2.connect(**PG_CONFIG)
        pg_cur = pg_con.cursor()
        init_postgres(pg_cur)

    # MySQL 준비
    my_con = my_cur = None
    if "mysql" in save_to:
        my_con = mysql.connector.connect(**MYSQL_CONFIG)
        my_cur = my_con.cursor()
        init_mysql(my_cur)

    # 스트리밍으로 배치 삽입
    for events_batch, daily_batch in generate_events(users):
        if duck_con is not None:
            duck_con.executemany(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)", events_batch
            )
            duck_con.executemany(
                "INSERT INTO daily_metrics VALUES (?, ?, ?)", daily_batch
            )

        if pg_cur is not None:
            pg_cur.executemany(
                "INSERT INTO events VALUES (%s, %s, %s, %s, %s, %s)", events_batch
            )
            pg_cur.executemany(
                "INSERT INTO daily_metrics VALUES (%s, %s, %s)", daily_batch
            )

        if my_cur is not None:
            my_cur.executemany(
                "INSERT INTO events VALUES (%s, %s, %s, %s, %s, %s)", events_batch
            )
            my_cur.executemany(
                "INSERT INTO daily_metrics VALUES (%s, %s, %s)", daily_batch
            )

    # 커밋 및 연결 종료
    if duck_con is not None:
        duck_con.close()

    if pg_con is not None:
        pg_con.commit()
        pg_cur.close()
        pg_con.close()

    if my_con is not None:
        my_con.commit()
        my_cur.close()
        my_con.close()

    # 버전 메타 기록 (DuckDB 기준)
    if "duckdb" in save_to:
        register_dataset_version(generator_type="advanced")

    set_progress("completed", 100)
    print("✨ 고급형 데이터 생성 완료!")


if __name__ == "__main__":
    # 로컬 테스트 시: DuckDB만 생성
    generate_data(save_to=("duckdb",))
