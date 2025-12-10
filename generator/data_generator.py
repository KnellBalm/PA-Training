import os
import sys
import duckdb
import psycopg2
import mysql.connector
import pandas as pd
import streamlit as st

# UI 모듈 로드
WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)
import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.config import DB_PATH

# =====================================
# VS Code 스타일 CSS
# =====================================
st.markdown(
    """
    <style>

    /* VS Code 스타일 다크 테마 전체 적용 */
    html, body, .block-container {
        background-color: #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* SQL Editor 박스 */
    .vscode-editor {
        background-color: #1e1e1e;
        border: 1px solid #3c3c3c;
        padding: 12px 14px;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        color: #d4d4d4;
        white-space: pre-wrap;
    }

    textarea {
        background: #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: none !important;
        font-size: 14px !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background-color: #0e639c;
        color: #ffffff;
        border-radius: 6px;
        padding: 8px 20px;
        border: 1px solid #0e639c;
        font-weight: 600;
        font-family: 'Noto Sans KR';
    }
    .stButton>button:hover {
        background-color: #1177bb;
        border-color: #1177bb;
    }

    /* 테이블 & 카드 배경 */
    .stDataFrame, .stTable {
        background: #252526 !important;
    }

    .sql-history-item {
        padding: 6px 10px;
        margin-bottom: 3px;
        background: #2a2d2e;
        border-radius: 6px;
        cursor: pointer;
        color: #9cdcfe;
        font-family: 'JetBrains Mono';
        font-size: 13px;
    }
    .sql-history-item:hover {
        background: #333333;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# 페이지 헤더
# =====================================
ui.page_header(
    title="SQL Console (VS Code 스타일)",
    subtitle="DuckDB / PostgreSQL / MySQL 엔진 선택 + EXPLAIN + 자동완성 + 히스토리",
    icon="📝",
)

# =====================================
# 엔진 선택
# =====================================
engine = st.selectbox(
    "SQL 엔진 선택",
    ["DuckDB", "PostgreSQL", "MySQL"],
    index=0
)

# =====================================
# DB 연결 함수
# =====================================
def get_connection(engine):
    if engine == "DuckDB":
        return duckdb.connect(DB_PATH)
    elif engine == "PostgreSQL":
        return psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASS"),
            database=os.getenv("PG_DB"),
            port=os.getenv("PG_PORT", 5432)
        )
    elif engine == "MySQL":
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASS"),
            database=os.getenv("MYSQL_DB"),
            port=os.getenv("MYSQL_PORT", 3306)
        )

# =====================================
# 자동완성(기본 SQL 키워드 + 테이블명 자동 로드)
# =====================================
BASE_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
    "GROUP BY", "ORDER BY", "LIMIT", "OFFSET", "COUNT", "SUM", "AVG",
    "DATE_TRUNC", "DATE_FORMAT", "EXTRACT", "CAST", "COALESCE"
]

def load_all_tables(engine):
    try:
        conn = get_connection(engine)
        cursor = conn.cursor()

        if engine == "DuckDB":
            q = "SHOW TABLES"
        elif engine == "PostgreSQL":
            q = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        else:
            q = "SHOW TABLES"

        cursor.execute(q)
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    except:
        return []

all_tables = load_all_tables(engine)
autocomplete_list = BASE_KEYWORDS + all_tables

# =====================================
# SQL 입력 박스 (VS Code 스타일)
# =====================================
st.markdown("### SQL 입력")

default_sql = "SELECT * FROM events LIMIT 100;"
sql = st.text_area(
    "SQL Editor",
    value=default_sql,
    height=220,
    key="sql_text",
)

# =====================================
# SQL 히스토리 기능
# =====================================
st.markdown("### SQL 히스토리")

st.session_state.setdefault("sql_history", [])

if sql not in st.session_state["sql_history"]:
    st.session_state["sql_history"].append(sql)

for item in reversed(st.session_state["sql_history"][-10:]):
    if st.button(item, key=item, help="Click to reuse", use_container_width=True):
        st.session_state["sql_text"] = item

# =====================================
# SQL 실행 버튼
# =====================================
col1, col2, col3 = st.columns(3)

run_btn = col1.button("🚀 실행")
explain_btn = col2.button("📘 EXPLAIN")
analyze_btn = col3.button("📗 EXPLAIN ANALYZE") if engine == "PostgreSQL" else None

# =====================================
# SQL 실행 함수
# =====================================
def run_sql(query):
    conn = get_connection(engine)
    cursor = conn.cursor()
    cursor.execute(query)

    if cursor.description:
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=cols)
        return df
    return pd.DataFrame()

# =====================================
# 실행 처리
# =====================================
if run_btn:
    try:
        df = run_sql(sql)
        st.success(f"쿼리 성공! {len(df)}행 반환")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(str(e))

if explain_btn:
    try:
        df = run_sql(f"EXPLAIN {sql}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(str(e))

if analyze_btn:
    try:
        df = run_sql(f"EXPLAIN ANALYZE {sql}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(str(e))
