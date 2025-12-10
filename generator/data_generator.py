# generator/data_generator.py
import os
import random
from datetime import timedelta
import numpy as np
import pandas as pd
import duckdb
from dateutil import rrule
from dotenv import load_dotenv

from .config import (
    GLOBAL_START_BOUND, GLOBAL_END_BOUND,
    MIN_MONTHS, MAX_MONTHS,
    DAILY_NEW_USERS_RANGE,
    SEGMENT_WEIGHTS,
    EVENTS_PER_SESSION,
    PROMOTION_DAYS_PER_MONTH,
    DB_PATH
)

load_dotenv()

np.random.seed(42)
random.seed(42)

MARKETING_CHANNELS = ["organic", "paid_search", "display", "email", "affiliate"]
DEVICE_TYPES = ["web", "android", "ios"]

# ---------------- 기간 랜덤 ----------------
def pick_random_period(mode="full"):
    if mode == "test":
        n_days = random.randint(7, 14)
    else:
        n_months = random.randint(MIN_MONTHS, MAX_MONTHS)
        n_days = n_months * 30

    max_start = GLOBAL_END_BOUND - timedelta(days=n_days)
    start_dt = GLOBAL_START_BOUND + timedelta(
        days=random.randint(0, (max_start - GLOBAL_START_BOUND).days)
    )
    end_dt = start_dt + timedelta(days=n_days - 1)
    return start_dt, end_dt

# ---------------- 프로모션일 랜덤 ----------------
def pick_promotion_days(start_dt, end_dt):
    all_dates = pd.date_range(start_dt, end_dt, freq="D")
    promo_set = set()

    for month, sub_df in all_dates.to_series().groupby(all_dates.month):
        month_dates = list(sub_df.dt.date)
        if not month_dates:
            continue

        n_promo = random.randint(*PROMOTION_DAYS_PER_MONTH)
        weekend = [d for d in month_dates if d.weekday() >= 4]
        weekday = [d for d in month_dates if d.weekday() < 4]

        chosen = []
        for _ in range(n_promo):
            if weekend and random.random() < 0.7:
                d = random.choice(weekend)
                weekend.remove(d)
            elif weekday:
                d = random.choice(weekday)
                weekday.remove(d)
            else:
                break
            chosen.append(d)

        promo_set.update(chosen)

    return promo_set

# ---------------- 시간 샘플링 ----------------
def sample_time_in_day(date):
    if random.random() < 0.7:
        hour = random.choice([11, 12, 13, 20, 21, 22, 23])
    else:
        hour = random.randint(0, 23)

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return pd.Timestamp(
        year=date.year, month=date.month, day=date.day,
        hour=hour, minute=minute, second=second
    )

# ---------------- 세그먼트/리텐션 ----------------
def choose_segment():
    segs = list(SEGMENT_WEIGHTS.keys())
    weights = np.array(list(SEGMENT_WEIGHTS.values()))
    weights = weights / weights.sum()
    return np.random.choice(segs, p=weights)

def retention_prob(days_since_signup):
    if days_since_signup == 0: return 1.0
    if days_since_signup == 1: return 0.45
    if days_since_signup <= 7: return 0.20
    if days_since_signup <= 30: return 0.08
    if days_since_signup <= 90: return 0.03
    return 0.01

# ---------------- 세션 이벤트 생성 ----------------
def generate_session_events(user_id, date, segment, session_idx, is_promo=False):
    from datetime import timedelta as td

    EVENT_WEIGHTS = {
        "view_home":    0.9,
        "view_product": 0.6,
        "search":       0.15,
        "add_to_cart":  0.1,
        "purchase":     0.03
    }
    if is_promo:
        EVENT_WEIGHTS["purchase"] *= 2
        EVENT_WEIGHTS["add_to_cart"] *= 1.3

    keys = list(EVENT_WEIGHTS.keys())
    vals = np.array(list(EVENT_WEIGHTS.values()))
    vals = vals / vals.sum()

    events = []
    session_id = f"{user_id}-{date.strftime('%Y%m%d')}-{session_idx}"
    current_time = sample_time_in_day(date)

    # session_start
    events.append([user_id, "session_start", current_time, session_id, None, segment])

    for _ in range(np.random.randint(EVENTS_PER_SESSION[0], EVENTS_PER_SESSION[1] + 1)):
        ev = np.random.choice(keys, p=vals)
        current_time += td(seconds=random.randint(5, 300))
        amount = None
        if ev == "purchase":
            amount = float(np.round(np.random.lognormal(mean=11, sigma=0.5), -2))
        events.append([user_id, ev, current_time, session_id, amount, segment])

    current_time += td(seconds=random.randint(5, 300))
    events.append([user_id, "session_end", current_time, session_id, None, segment])

    return events

# ---------------- 메인 생성 ----------------
def generate_data(mode="full", seed=None):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    start_dt, end_dt = pick_random_period(mode)
    print(f"기간: {start_dt.date()} ~ {end_dt.date()} (mode={mode})")

    promo_days = pick_promotion_days(start_dt, end_dt)
    print(f"프로모션일 {len(promo_days)}일 자동 선택됨")

    users_dict = {}      # user_id -> {signup_time, segment, channel, device}
    users_rows = []
    sessions_rows = []
    events_rows = []
    purchases_rows = []

    date_list = pd.date_range(start_dt, end_dt, freq="D")
    current_user_id = 1
    event_id = 1
    purchase_id = 1

    for dt in date_list:
        date = dt.date()
        is_promo = date in promo_days

        # 신규 유저
        n_new = random.randint(*DAILY_NEW_USERS_RANGE)
        new_ids = range(current_user_id, current_user_id + n_new)
        current_user_id += n_new

        for uid in new_ids:
            seg = choose_segment()
            signup_time = sample_time_in_day(dt)
            channel = random.choice(MARKETING_CHANNELS)
            device = random.choice(DEVICE_TYPES)

            users_dict[uid] = {
                "signup_time": signup_time,
                "segment": seg,
                "marketing_channel": channel,
                "device_type": device,
            }
            users_rows.append([
                uid, signup_time, seg, channel, device
            ])

        # 활성 유저 선정
        active_users = []
        for uid, info in users_dict.items():
            diff = (date - info["signup_time"].date()).days
            if np.random.rand() < retention_prob(diff):
                active_users.append(uid)

        # 세션/이벤트 생성
        for uid in active_users:
            seg = users_dict[uid]["segment"]
            n_session = random.randint(1, 3)
            for s_idx in range(n_session):
                evs = generate_session_events(uid, date, seg, s_idx, is_promo)
                session_id = evs[0][3]
                times = [e[2] for e in evs]
                session_start = min(times)
                session_end = max(times)
                session_length = (session_end - session_start).total_seconds()

                sessions_rows.append([
                    session_id, uid, session_start, session_end,
                    is_promo, session_length
                ])

                for e in evs:
                    _, ev_name, ev_time, sess_id, amount, seg_ = e
                    events_rows.append([
                        event_id, sess_id, uid, ev_name, ev_time, amount, seg_, ev_time.date()
                    ])
                    if ev_name == "purchase" and amount is not None:
                        product_id = random.randint(1, 5000)
                        coupon_used = random.random() < 0.3
                        purchases_rows.append([
                            purchase_id, uid, sess_id, ev_time, amount, product_id, coupon_used
                        ])
                        purchase_id += 1
                    event_id += 1

    # DataFrame 변환
    users_df = pd.DataFrame(users_rows, columns=[
        "user_id", "signup_time", "segment", "marketing_channel", "device_type"
    ])
    sessions_df = pd.DataFrame(sessions_rows, columns=[
        "session_id", "user_id", "session_start", "session_end",
        "is_promotion_day", "session_length_sec"
    ])
    events_df = pd.DataFrame(events_rows, columns=[
        "event_id", "session_id", "user_id", "event_name",
        "event_time", "amount", "segment", "event_date"
    ])
    purchases_df = pd.DataFrame(purchases_rows, columns=[
        "purchase_id", "user_id", "session_id", "purchase_time",
        "amount", "product_id", "coupon_used"
    ])

    # daily_metrics 집계
    daily_metrics_df = build_daily_metrics(users_df, sessions_df, events_df, purchases_df)

    save_to_duckdb(users_df, sessions_df, events_df, purchases_df, daily_metrics_df)
    print("데이터 생성 및 DuckDB 저장 완료.")


def build_daily_metrics(users_df, sessions_df, events_df, purchases_df):
    # date 컬럼 준비
    events_df["event_date"] = pd.to_datetime(events_df["event_date"])
    sessions_df["session_date"] = sessions_df["session_start"].dt.date
    purchases_df["purchase_date"] = purchases_df["purchase_time"].dt.date

    dau = (events_df.groupby("event_date")["user_id"]
           .nunique()
           .rename("dau"))
    new_users = (users_df.groupby(users_df["signup_time"].dt.date)["user_id"]
                 .nunique()
                 .rename("new_users"))
    sess = (sessions_df.groupby("session_date")["session_id"]
            .nunique()
            .rename("sessions"))
    purch = (purchases_df.groupby("purchase_date")["purchase_id"]
             .nunique()
             .rename("purchases"))
    rev = (purchases_df.groupby("purchase_date")["amount"]
           .sum()
           .rename("revenue"))

    daily = (pd.concat([dau, new_users, sess, purch, rev], axis=1)
             .fillna(0)
             .reset_index()
             .rename(columns={"index": "date", "event_date": "date"}))

    daily["date"] = pd.to_datetime(daily["date"]).dt.date
    return daily


def save_to_duckdb(users_df, sessions_df, events_df, purchases_df, daily_metrics_df):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = duckdb.connect(DB_PATH)

    con.execute("DROP TABLE IF EXISTS users;")
    con.execute("DROP TABLE IF EXISTS sessions;")
    con.execute("DROP TABLE IF EXISTS events;")
    con.execute("DROP TABLE IF EXISTS purchases;")
    con.execute("DROP TABLE IF EXISTS daily_metrics;")

    con.execute("CREATE TABLE users AS SELECT * FROM users_df")
    con.execute("CREATE TABLE sessions AS SELECT * FROM sessions_df")
    con.execute("CREATE TABLE events AS SELECT * FROM events_df")
    con.execute("CREATE TABLE purchases AS SELECT * FROM purchases_df")
    con.execute("CREATE TABLE daily_metrics AS SELECT * FROM daily_metrics_df")

    # 모델링 뷰 생성
    con.execute("DROP VIEW IF EXISTS fact_events;")
    con.execute("DROP VIEW IF EXISTS fact_purchases;")

    con.execute("""
    CREATE VIEW fact_events AS
    SELECT
        e.*,
        u.marketing_channel,
        u.device_type,
        s.is_promotion_day,
        s.session_length_sec
    FROM events e
    JOIN users u ON e.user_id = u.user_id
    JOIN sessions s ON e.session_id = s.session_id;
    """)

    con.execute("""
    CREATE VIEW fact_purchases AS
    SELECT
        p.*,
        u.segment,
        u.marketing_channel,
        s.is_promotion_day
    FROM purchases p
    JOIN users u ON p.user_id = u.user_id
    JOIN sessions s ON p.session_id = s.session_id;
    """)

    con.close()

def sync_to_postgres(df_dict):
    import psycopg2

    conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASS"),
        database=os.getenv("PG_DB"),
        port=os.getenv("PG_PORT", 5432)
    )
    cur = conn.cursor()

    for table, df in df_dict.items():
        cur.execute(f"DELETE FROM {table}")
        for _, row in df.iterrows():
            cols = ", ".join(row.index)
            vals = ", ".join(["%s"] * len(row))
            cur.execute(f"INSERT INTO {table} ({cols}) VALUES ({vals})", tuple(row))

    conn.commit()
    cur.close()
    conn.close()

def sync_to_mysql(df_dict):
    import mysql.connector

    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASS"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )
    cur = conn.cursor()

    for table, df in df_dict.items():
        cur.execute(f"DELETE FROM {table}")
        for _, row in df.iterrows():
            cols = ", ".join(row.index)
            vals = ", ".join(["%s"] * len(row))
            cur.execute(f"INSERT INTO {table} ({cols}) VALUES ({vals})", tuple(row))

    conn.commit()
    cur.close()
    conn.close()

df_dict = {
    "users": users_df,
    "sessions": sessions_df,
    "events": events_df,
    "purchases": purchases_df,
    "daily_metrics": daily_metrics_df
}

sync_to_postgres(df_dict)
sync_to_mysql(df_dict)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["test", "full"], default="test")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    generate_data(mode=args.mode, seed=args.seed)
