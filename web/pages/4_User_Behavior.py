import os
import sys
import duckdb
import streamlit as st
import altair as alt

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)
import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.config import DB_PATH

ui.page_header(
    title="User Behavior",
    subtitle="일별 DAU, 이벤트 수, 세션 수 등의 트렌드를 확인합니다.",
    icon="📈",
)

if not os.path.exists(DB_PATH):
    st.error("DB 파일이 없습니다. 메인 페이지에서 데이터셋을 먼저 생성하세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

df = con.execute(
    """
    SELECT
        date,
        dau,
        sessions,
        revenue
    FROM daily_metrics
    ORDER BY date;
"""
).df()

con.close()

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">DAU 추이</div>', unsafe_allow_html=True)

c1 = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x="date:T",
        y="dau:Q",
        tooltip=["date", "dau"],
    )
    .properties(height=260)
)

st.altair_chart(c1, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">이벤트 / 세션 / 매출</div>', unsafe_allow_html=True)

c2 = (
    alt.Chart(df.melt("date", ["sessions", "revenue"]))
    .mark_line(point=True)
    .encode(
        x="date:T",
        y="value:Q",
        color="variable:N",
        tooltip=["date", "variable", "value"],
    )
    .properties(height=260)
)
st.altair_chart(c2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
