import os
import sys
import duckdb
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WEB_ROOT not in sys.path:
    sys.path.append(WEB_ROOT)
import style as ui  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator.config import DB_PATH

ui.page_header(
    title="User Journey",
    subtitle="세션 내 이벤트 흐름을 Sankey 다이어그램으로 시각화합니다.",
    icon="🛤️",
)

if not os.path.exists(DB_PATH):
    st.error("DB 파일이 없습니다. 메인 페이지에서 데이터셋을 먼저 생성하세요.")
    st.stop()

con = duckdb.connect(DB_PATH)

N_SESSIONS = 5000

paths_df = con.execute(
    f"""
    WITH ordered AS (
        SELECT
            session_id,
            event_time,
            event_name,
            ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY event_time) AS rn
        FROM events
    )
    SELECT
        o1.event_name AS src,
        o2.event_name AS dst,
        COUNT(*) AS cnt
    FROM ordered o1
    JOIN ordered o2
      ON o1.session_id = o2.session_id
     AND o1.rn + 1 = o2.rn
    WHERE o1.session_id IN (
        SELECT DISTINCT session_id FROM events LIMIT {N_SESSIONS}
    )
    GROUP BY 1, 2
    HAVING cnt > 50
    ORDER BY cnt DESC;
"""
).df()

con.close()

if paths_df.empty:
    st.warning("Sankey를 그릴 충분한 데이터가 없습니다.")
    st.stop()

st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">세션 내 이벤트 흐름 (상위 전이)</div>', unsafe_allow_html=True)

nodes = sorted(list(set(paths_df["src"]).union(set(paths_df["dst"]))))
node_index = {name: i for i, name in enumerate(nodes)}

source = [node_index[s] for s in paths_df["src"]]
target = [node_index[d] for d in paths_df["dst"]]
value = paths_df["cnt"].tolist()

fig = go.Figure(
    data=[
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=nodes,
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
            ),
        )
    ]
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
