# web/app.py
import os
import sys
import duckdb
import streamlit as st

# 루트 경로 추가 (generator, sql_problems import용)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.data_generator import generate_data
from generator.config import DB_PATH
import web.style as ui

st.set_page_config(
    page_title="Analytics Lab",
    page_icon="📊",
    layout="wide",
)

ui.inject_global_css()

with st.sidebar:
    st.markdown('<div class="sidebar-title">Analytics Lab</div>', unsafe_allow_html=True)
    st.caption("코호트 · 리텐션 · 퍼널 · RFM · 여정 분석 연습 환경")
    if st.button("🔁 새 데이터셋 생성 (랜덤 기간)", use_container_width=True):
        with st.spinner("데이터 생성 중..."):
            generate_data(mode="full", seed=42)
        st.success("새 데이터셋 생성이 완료되었습니다. 페이지를 새로고침 해 주세요.")

ui.page_header(
    title="Analytics Lab 홈",
    subtitle="가상의 서비스 로그 데이터를 기반으로 SQL · 코호트 · 퍼널 · RFM · 사용자 여정을 연습할 수 있는 통합 환경입니다.",
    icon="📊",
)

if not os.path.exists(DB_PATH):
    st.warning("DuckDB 데이터 파일이 아직 없습니다. 좌측 사이드바에서 **새 데이터셋 생성**을 먼저 실행해 주세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

summary = con.execute(
    """
    SELECT 
        MIN(event_time) AS start_time,
        MAX(event_time) AS end_time,
        COUNT(*) AS total_events,
        COUNT(DISTINCT user_id) AS users
    FROM events
"""
).df().iloc[0]

daily = con.execute(
    """
    SELECT 
        MAX(date) AS last_date,
        MAX(dau) AS last_dau,
        MAX(revenue) AS last_revenue,
        MAX(purchases) AS last_purchases
    FROM daily_metrics
"""
).df().iloc[0]

con.close()

# 상단 KPI 카드
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("기간", f"{summary['start_time'].date()} ~ {summary['end_time'].date()}")
with col2:
    st.metric("전체 이벤트 수", f"{int(summary['total_events']):,}")
with col3:
    st.metric("전체 사용자 수", f"{int(summary['users']):,}")
with col4:
    st.metric("최근 DAU", f"{int(daily['last_dau']):,}")

st.markdown("")

# 카드 레이아웃
col_l, col_r = st.columns([2, 1])

with col_l:
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📚 연습 흐름 가이드</div>', unsafe_allow_html=True)
    st.markdown(
        """
        1. **SQL Console** 탭에서 스키마를 확인하고, 자유롭게 쿼리 연습을 합니다.  
        2. **Cohort / Retention** 페이지에서 가입 Cohort와 잔존율을 분석합니다.  
        3. **Funnel Analysis**에서 view → cart → purchase 퍼널을 확인합니다.  
        4. **User Journey**에서 세션 내 이벤트 흐름(Sankey)을 분석합니다.  
        5. **RFM Segmentation**에서 유저 가치를 RFM 점수로 나눠 봅니다.  
        6. 마지막으로 **Today’s SQL Problems**에서 난이도 높은 문제를 풀어봅니다.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ 데이터셋 정보</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        - 최근 데이터 기준일: **{daily['last_date']}**  
        - 최근 매출(Revenue): **{int(daily['last_revenue']):,}**  
        - 최근 구매 건수: **{int(daily['last_purchases']):,}**  
        - DuckDB 파일: `{DB_PATH}`
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
