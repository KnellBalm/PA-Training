import os
import sys
import duckdb
import pandas as pd
import streamlit as st

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)
import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.config import DB_PATH

ui.page_header(
    title="RFM Segmentation",
    subtitle="Recency · Frequency · Monetary 점수를 기반으로 유저 가치를 세그먼트합니다.",
    icon="💎",
)

if not os.path.exists(DB_PATH):
    st.error("DB 파일이 없습니다. 메인 페이지에서 데이터셋을 먼저 생성하세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

rfm_df = con.execute(
    """
    WITH purchases AS (
        SELECT
            user_id,
            MAX(purchase_time) AS last_purchase,
            COUNT(*) AS freq,
            SUM(amount) AS monetary
        FROM purchases
        GROUP BY user_id
    ),
    now_ AS (
        SELECT MAX(event_time) AS max_time FROM events
    ),
    base AS (
        SELECT
            p.user_id,
            DATE_DIFF('day', p.last_purchase, n.max_time) AS recency,
            p.freq,
            COALESCE(p.monetary, 0) AS monetary
        FROM purchases p
        CROSS JOIN now_ n
    )
    SELECT * FROM base;
"""
).df()

con.close()

if rfm_df.empty:
    st.warning("RFM을 계산할 구매 데이터가 없습니다.")
    st.stop()

rfm_df["R_score"] = pd.qcut(rfm_df["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm_df["F_score"] = pd.qcut(
    rfm_df["freq"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
)
rfm_df["M_score"] = pd.qcut(
    rfm_df["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
)

rfm_df["RFM"] = (
    rfm_df["R_score"].astype(int)
    + rfm_df["F_score"].astype(int)
    + rfm_df["M_score"].astype(int)
)

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">RFM 샘플</div>', unsafe_allow_html=True)
st.dataframe(rfm_df.head(50), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">RFM Score 분포</div>', unsafe_allow_html=True)
st.bar_chart(rfm_df["RFM"].value_counts().sort_index())
st.markdown("</div>", unsafe_allow_html=True)
