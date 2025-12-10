import os
import sys
import duckdb
import streamlit as st

# web/style.py import
WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)
import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.config import DB_PATH

ui.page_header(
    title="SQL 콘솔",
    subtitle="DuckDB에 직접 SQL을 실행하면서 코호트 · 퍼널 · 세션 · RFM 쿼리를 연습할 수 있습니다.",
    icon="📝",
)

if not os.path.exists(DB_PATH):
    st.error("DB 파일이 없습니다. 메인 페이지에서 데이터셋을 먼저 생성하세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

# 상단: 테이블 개수, 이벤트 수, 유저 수 간단 요약
meta = con.execute(
    """
    SELECT 
        (SELECT COUNT(*) FROM information_schema.tables WHERE table_type='BASE TABLE') AS tables,
        (SELECT COUNT(*) FROM events) AS events,
        (SELECT COUNT(DISTINCT user_id) FROM users) AS users
"""
).df().iloc[0]

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("테이블 수", int(meta["tables"]))
with c2:
    st.metric("이벤트 수", f"{int(meta['events']):,}")
with c3:
    st.metric("사용자 수", f"{int(meta['users']):,}")

st.markdown("")

# 테이블 목록 버튼
with st.expander("📂 테이블 / 뷰 구조 보기", expanded=False):
    tables = con.execute("SHOW TABLES;").df()
    st.write("**테이블 및 뷰 목록**")
    st.dataframe(tables)

st.markdown('<div class="section-title">SQL 쿼리 실행</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">FROM 절에 `events`, `users`, `sessions`, `purchases`, `daily_metrics`, `fact_events`, `fact_purchases` 등을 활용해 보세요.</div>',
    unsafe_allow_html=True,
)

default_query = "SELECT * FROM events LIMIT 100;"

st.markdown('<div class="sql-label">SQL QUERY</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="sql-editor">', unsafe_allow_html=True)
    query = st.text_area(
        label="",
        value=default_query,
        height=220,
        key="sql_editor",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

run_col, _ = st.columns([1, 4])
with run_col:
    run = st.button("🚀 쿼리 실행", type="primary", use_container_width=True)

if run:
    try:
        df = con.execute(query).df()
        st.success(f"{len(df)} rows returned")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "결과 CSV 다운로드",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="query_result.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"쿼리 실행 중 오류가 발생했습니다:\n\n{e}")

con.close()
