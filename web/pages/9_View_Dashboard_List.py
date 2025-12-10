# web/pages/9_View_Dashboard_List.py

import os, json, sys
import streamlit as st

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)

import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DASHBOARD_FILE = os.path.join(ROOT, "dashboard", "dashboards.json")

ui.page_header(
    title="나의 대시보드",
    subtitle="직접 생성한 SQL 기반 분석 카드 목록",
    icon="📚",
)

if not os.path.exists(DASHBOARD_FILE):
    st.info("아직 저장된 대시보드가 없습니다.")
    st.stop()

with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
    boards = json.load(f)

for d in boards:
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown(f"### {d['title']}")
    st.caption(f"생성: {d['created_at']}")
    if d.get("tags"):
        st.caption("Tags: " + ", ".join(d["tags"]))
    if st.button(f"열기 ({d['title']})", key=d["id"]):
        st.session_state["view_dashboard_id"] = d["id"]
        st.switch_page("pages/10_View_Dashboard.py")
    st.markdown("</div>", unsafe_allow_html=True)
