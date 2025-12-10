import json
from datetime import date
import duckdb
import os

from generator.config import DB_PATH
from .llm_client import get_gemini_client

PROBLEM_FILE = "sql_problems/today.json"


def collect_metadata():
    con = duckdb.connect(DB_PATH)

    summary = con.execute("""
        SELECT 
            MIN(event_time) AS start_time,
            MAX(event_time) AS end_time,
            COUNT(*) AS total_events,
            COUNT(DISTINCT user_id) AS users,
            COUNT(DISTINCT event_name) AS event_types
        FROM events;
    """).df().iloc[0]

    events_list = con.execute("""
        SELECT event_name, COUNT(*) AS cnt
        FROM events
        GROUP BY event_name
        ORDER BY cnt DESC;
    """).df()

    seg_list = con.execute("""
        SELECT segment, COUNT(DISTINCT user_id) AS users
        FROM events
        GROUP BY segment;
    """).df()

    con.close()

    return summary, events_list, seg_list


def build_prompt(summary, events_list, seg_list):
    return f"""
당신은 데이터 분석 팀 리더입니다. 아래는 오늘 생성된 이벤트 로그 스키마 요약입니다.

[데이터 요약]
- 기간: {summary['start_time']} ~ {summary['end_time']}
- 전체 이벤트 수: {summary['total_events']}
- 사용자 수: {summary['users']}
- 이벤트 타입 수: {summary['event_types']}

[이벤트 목록 상위]
{events_list.head(10).to_markdown(index=False)}

[세그먼트 목록]
{seg_list.to_markdown(index=False)}

요구사항:
1. DuckDB/표준 SQL로 풀 수 있는 실무형 문제를 생성하세요.
2. 난이도는 'easy', 'medium', 'hard' 3단계로 구분합니다.
3. hard 난이도 문제를 가장 많이 생성하세요.
4. 각 문제는 JSON 배열의 원소 형태로 표현합니다.
   - id: 정수
   - difficulty: 'easy' | 'medium' | 'hard'
   - question: 한국어로 작성된 문제 설명
   - hint: SQL 접근 힌트 (짧게)
   - tags: ['cohort', 'retention', 'funnel', 'rfm', 'session', 'segmentation', ...] 중 일부

5. 문제 유형 예시:
   - 코호트/리텐션 계산
   - 퍼널 분석(view → cart → purchase 등)
   - 세션 기반 분석
   - 세그먼트별 행동 차이
   - RFM 기반 유저 분석
   - 프로모션일/비프로모션일 비교

6. 출력은 **JSON 문자열만** 반환하세요.
7. 최소 5문제 이상, hard 비율은 전체의 50% 이상이 되도록 하세요.
"""


def generate_today_problems():
    summary, events_list, seg_list = collect_metadata()
    model = get_gemini_client()

    prompt = build_prompt(summary, events_list, seg_list)
    response = model.generate_content(prompt)
    text = response.text.strip()

    # 모델이 JSON 문자열만 반환한다고 가정
    problems = json.loads(text)

    today = date.today().isoformat()
    for p in problems:
        p["date"] = today

    with open(PROBLEM_FILE, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)


def load_today_problems():
    if not os.path.exists(PROBLEM_FILE):
        generate_today_problems()
    with open(PROBLEM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    generate_today_problems()
