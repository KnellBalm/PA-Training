import os
import sys
import duckdb
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
    title="Funnel Analysis",
    subtitle="view_product → add_to_cart → purchase 흐름을 사용자가 어디에서 이탈하는지 분석합니다.",
    icon="🔻",
)

if not os.path.exists(DB_PATH):
    st.error("DB 파일이 없습니다. 메인 페이지에서 데이터셋을 먼저 생성하세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">전체 퍼널</div>', unsafe_allow_html=True)

df = con.execute(
    """
    SELECT
        COUNT(DISTINCT CASE WHEN event_name = 'view_product' THEN user_id END) AS view_users,
        COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN event_name = 'purchase' THEN user_id END) AS purchase_users
    FROM events;
"""
).df().iloc[0]

view_users = df["view_users"]
cart_users = df["cart_users"]
purchase_users = df["purchase_users"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("상품 조회 사용자", int(view_users))
with col2:
    st.metric("장바구니 사용자", int(cart_users))
with col3:
    st.metric("구매 사용자", int(purchase_users))

if view_users > 0 and cart_users > 0:
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("View → Cart 전환율", f"{cart_users / view_users * 100:.2f} %")
    with c2:
        st.metric("Cart → Purchase 전환율", f"{purchase_users / cart_users * 100:.2f} %")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">세그먼트별 퍼널</div>', unsafe_allow_html=True)

seg_df = con.execute(
    """
    SELECT
        segment,
        COUNT(DISTINCT CASE WHEN event_name = 'view_product' THEN user_id END) AS view_users,
        COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN event_name = 'purchase' THEN user_id END) AS purchase_users
    FROM events
    GROUP BY segment;
"""
).df()

con.close()

st.dataframe(seg_df, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
