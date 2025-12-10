# web/style.py
import streamlit as st

def inject_global_css():
    """앱 전체에 공통으로 적용할 CSS 및 한글 폰트 설정"""
    st.markdown(
        """
        <style>
        /* 한글 폰트 (Nanum Gothic + Noto Sans KR) */
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Nanum Gothic','Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* 메인 컨테이너 여백 & 최대폭 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
        }

        /* metric 카드 스타일 */
        .stMetric {
            background: #ffffff;
            border-radius: 16px;
            padding: 12px 16px !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            border: 1px solid rgba(148, 163, 184, 0.2);
        }

        /* SQL 에디터 영역 */
        .sql-editor {
            background-color: #020617;
            color: #e5e7eb;
            border-radius: 12px;
            padding: 12px 14px;
            font-family: 'JetBrains Mono','SF Mono','Menlo',monospace;
            font-size: 13px;
            border: 1px solid #1e293b;
        }
        .sql-editor textarea {
            background: transparent !important;
            color: #e5e7eb !important;
        }

        .sql-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: .12em;
            margin-bottom: 0.25rem;
        }

        /* 주요 버튼 스타일 */
        .primary-button button {
            border-radius: 999px;
            padding: 0.45rem 1.3rem;
            font-weight: 600;
        }

        /* 카드 레이아웃 */
        .analytics-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 18px 18px 16px 18px;
            box-shadow: 0 10px 30px rgba(15,23,42,0.06);
            border: 1px solid rgba(148, 163, 184, 0.18);
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
            color: #0f172a;
        }
        .section-subtitle {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 0.9rem;
        }

        /* 사이드바 헤더 정리 */
        [data-testid="stSidebar"] .sidebar-title {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str | None = None, icon: str = "📊"):
    """페이지 공통 헤더"""
    inject_global_css()
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1.4rem;">
            <div>
                <div style="font-size:0.8rem;font-weight:600;color:#64748b;letter-spacing:.18em;text-transform:uppercase;margin-bottom:0.15rem;">
                    ANALYTICS LAB
                </div>
                <h1 style="font-weight:700;font-size:1.6rem;margin:0;display:flex;align-items:center;gap:.4rem;">
                    <span>{icon}</span> <span>{title}</span>
                </h1>
                {"<p style='color:#64748b;margin-top:.25rem;font-size:0.9rem;'>" + subtitle + "</p>" if subtitle else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
