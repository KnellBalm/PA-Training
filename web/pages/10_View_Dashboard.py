# web/pages/10_View_Dashboard.py

import os, sys, json
import duckdb
import altair as alt
import streamlit as st

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)

import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DASHBOARD_FILE = os.path.join(ROOT, "dashboard", "dashboards.json")

from generator.config import DB_PATH

ui.page_header(
    title="대시보드 상세보기",
    subtitle="저장된 SQL + 시각화 + 설명",
    icon="📑",
)

if "view_dashboard_id" not in st.session_state:
    st.error("대시보드가 선택되지 않았습니다.")
    st.stop()

if not os.path.exists(DASHBOARD_FILE):
    st.error("대시보드 데이터 파일이 없습니다.")
    st.stop()

with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
    boards = json.load(f)

target = next((b for b in boards if b["id"] == st.session_state["view_dashboard_id"]), None)

if not target:
    st.error("대시보드를 찾을 수 없습니다.")
    st.stop()

st.subheader(target["title"])
st.caption(f"생성: {target['created_at']}")

if target.get("description"):
    st.write(target["description"])

st.markdown("### SQL")
st.code(target["sql"], language="sql")

# 쿼리 실행
con = duckdb.connect(DB_PATH)
df = con.execute(target["sql"]).df()
con.close()

st.dataframe(df, use_container_width=True)

# 차트가 있을 경우
if target.get("chart_type"):
    chart_type = target["chart_type"]
    cols = df.columns.tolist()

    if len(cols) >= 2:
        x = cols[0]
        y = cols[1]

        base = alt.Chart(df).encode(x=x, y=y)

        if chart_type == "line":
            fig = base.mark_line(point=True)
        elif chart_type == "bar":
            fig = base.mark_bar()
        elif chart_type == "area":
            fig = base.mark_area()
        else:
            fig = base.mark_circle()

        st.altair_chart(fig, use_container_width=True)
