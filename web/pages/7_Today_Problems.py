import os
import sys
import streamlit as st

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)
import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from sql_problems.problem_generator import load_today_problems

ui.page_header(
    title="Today's SQL Problems",
    subtitle="오늘 생성된 데이터에 기반한 실무형 SQL 문제를 난이도별로 연습합니다.",
    icon="🧩",
)

problems = load_today_problems()

difficulty = st.radio("난이도 필터", ["all", "easy", "medium", "hard"], index=3, horizontal=True)

for p in problems:
    if difficulty != "all" and p.get("difficulty") != difficulty:
        continue

    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown(
        f"<div class='section-title'>[{p.get('difficulty','?').upper()}] 문제 {p.get('id')}</div>",
        unsafe_allow_html=True,
    )
    st.write(p["question"])
    if p.get("tags"):
        st.caption("Tags: " + ", ".join(p["tags"]))
    if st.button(f"힌트 보기 (문제 {p['id']})"):
        st.info(p["hint"])
    st.markdown("</div>", unsafe_allow_html=True)
