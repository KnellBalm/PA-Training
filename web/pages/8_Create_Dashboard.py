# web/pages/8_Create_Dashboard.py

import os, sys, json, uuid
import duckdb
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)

import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.config import DB_PATH

DASHBOARD_FILE = os.path.join(ROOT, "dashboard", "dashboards.json")
os.makedirs(os.path.dirname(DASHBOARD_FILE), exist_ok=True)

ui.page_header(
    title="대시보드 생성",
    subtitle="SQL 실행 → 차트 생성 → 설명 입력 → 나만의 대시보드로 저장",
    icon="🛠",
)

if not os.path.exists(DB_PATH):
    st.error("DB 파일이 없습니다. 메인 페이지에서 데이터셋을 먼저 생성하세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

# SQL 입력
st.markdown('<div class="section-title">SQL 입력</div>', unsafe_allow_html=True)

default_sql = "SELECT date, revenue FROM daily_metrics ORDER BY date;"

sql = st.text_area("SQL", value=default_sql, height=200)

# 실행 버튼
if st.button("🚀 SQL 실행", type="primary"):
    try:
        result_df = con.execute(sql).df()
        st.success("SQL 실행 완료!")
        st.dataframe(result_df, use_container_width=True)

        st.session_state["last_sql"] = sql
        st.session_state["last_df"] = result_df

    except Exception as e:
        st.error(f"SQL 오류: {e}")

con.close()

# SQL 실행 후 → 차트 생성
if "last_df" in st.session_state:
    df = st.session_state["last_df"]

    st.markdown('<div class="section-title">차트 생성</div>', unsafe_allow_html=True)

    numeric_cols = df.select_dtypes(include=["int", "float"]).columns.tolist()
    time_cols = df.select_dtypes(include=["datetime", "date"]).columns.tolist()
    all_cols = df.columns.tolist()

    chart_type = st.selectbox(
        "차트 타입 선택",
        ["line", "bar", "area", "scatter"],
        index=0,
    )

    x_col = st.selectbox("X축 컬럼", all_cols)
    y_col = st.selectbox("Y축 컬럼", numeric_cols)

    if st.button("📊 차트 미리보기"):
        chart = (
            alt.Chart(df)
            .mark_line() if chart_type == "line"
            else alt.Chart(df).mark_bar()
            if chart_type == "bar"
            else alt.Chart(df).mark_area()
            if chart_type == "area"
            else alt.Chart(df).mark_circle()
        )

        fig = chart.encode(x=x_col, y=y_col, tooltip=list(df.columns))
        st.altair_chart(fig, use_container_width=True)

        st.session_state["last_chart_type"] = chart_type

# 대시보드 저장
if "last_df" in st.session_state:
    st.markdown('<div class="section-title">대시보드 정보 입력</div>', unsafe_allow_html=True)

    title = st.text_input("대시보드 제목")
    description = st.text_area("설명 (선택)", height=100)
    tags = st.text_input("태그 (comma-separated, optional)")

    if st.button("💾 대시보드 저장", type="primary"):
        entry = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "sql": st.session_state["last_sql"],
            "chart_type": st.session_state.get("last_chart_type", None),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tags": [t.strip() for t in tags.split(",")] if tags else [],
        }

        # 기존 파일 로드
        if os.path.exists(DASHBOARD_FILE):
            with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
                dashboards = json.load(f)
        else:
            dashboards = []

        dashboards.append(entry)

        with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(dashboards, f, ensure_ascii=False, indent=4)

        st.success("대시보드가 저장되었습니다!")
