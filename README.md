# README.md

1) Python 데이터 생성기
현실적인 대규모 이벤트 로그 생성
주기적(매일/명령 실행 시) 재생성 가능
DuckDB 파일(.duckdb)로 저장
데이터 생성 스펙 (6개월 · 약 2천만 이벤트)
📅 기간
180일(6개월)

👤 사용자 규모 모델링
총 사용자 약 200k ~ 350k
일 신규 유저 300~800명
일 활성 유저 5k~20k명

사용자 세그먼트
low_engaged (50%)
mid_engaged (30%)
high_engaged (20%)

🎯 이벤트 수
6개월 총 18M ~ 25M 이벤트 목표
이벤트 종류 15개 이상

🧩 이벤트 종류(고급 분석용)
session_start, session_end
view_home, view_category, view_product
search, search_result_click
wishlist_add, wishlist_remove
add_to_cart, remove_from_cart
purchase, refund
review_write
coupon_apply, login, signup

2) DuckDB
매우 빠르고 가볍고, 파일 기반 DB라 설치 부담 거의 없음
SQL 인터페이스 제공
Web UI / Streamlit / Jupyter 어디서든 접근 가능

3) SQL Web UI
웹 브라우저에서 SQL 작성 → 즉시 실행 결과 출력
쿼리 히스토리 저장
자동 문제 생성 + 문제 풀이 제출 가능

가능한 기술 스택
SQLPad (가장 가볍고 설치 쉽고 DuckDB 연동 가능)
Datasette + DuckDB (웹에서 SQL 실행)
Streamlit + DuckDB SQL Editor (가볍고 개발 자유도 높음)
Apache Superset (강력하지만 무거움 — 행정망 계열 환경 아니면 굳이 X)
학습 용도로는 Streamlit 또는 SQLPad가 가장 최적.

4) 대시보드(UI)
Streamlit 기반 대시보드 구현 추천

아래와 같은 시각화 가능
DAU/WAU/MAU
Cohort retention heatmap
Funnel conversion chart

이벤트 타임라인
User segmentation

📌 ① SQL Console
SQL 직접 실행
DuckDB와 연동
자동완성 지원
결과 다운로드(csv/xlsx)
"문제 자동 입력" 기능

📌 ② Cohort & Retention Dashboard
월별 Cohort
Day1 / Day3 / Day7 / Day14 / Day30 / Day60
Heatmap
세그먼트별 Cohort 비교
코호트 수 대비 잔존율 자동 계산

📌 ③ Funnel Analysis Dashboard (고급)
다음과 같은 분석 가능:
view → product → cart → purchase
search → click → purchase
segment별 funnel
A/B 테스트 퍼널(랜덤 분배 가능)

시각화:
단계별 전환율 waterfall chart
세그먼트별 bar chart

📌 ④ User Behavior Dashboard
Daily/Weekly 이벤트 추세
Active Users / New Users / Returning Users
세션 당 이벤트 수 분포(histogram)
이벤트 카테고리별 참여도

📌 ⑤ User Journey / Path Analysis (선택)
Sankey chart: view → search → product → cart → purchase
유저 동선 기반 분석
전환 실패 지점 파악
(이 Sankey는 Streamlit + Plotly로 구현)

📌 ⑥ RFM / Segmentation Dashboard (고급형)
Recency / Frequency / Monetary scoring
User clustering (KMeans optional)
세그먼트별 전환 / 잔존율 비교

📌 ⑦ Today’s SQL Problems (자동 생성)
매일 다음과 같은 문제들이 생성됨:
Cohort retention 분석 문제
Funnel transformation SQL 문제
Segment별 행동 차이 분석 문제
세션 기반 분석 문제
특정 이벤트 기반 날짜 필터 문제
구매 기여도 분석 문제
문제는 JSON 파일로 저장해 Web UI에 호출.
또한 "SQL 템플릿 자동 입력" 기능 포함.

📌 ⑧ Data Management
“새로운 6개월 데이터 생성” 버튼
“랜덤 1일치 데이터 추가” 기능
→ 더 길게 늘릴 수 있음
현 데이터셋 요약 정보(레코드 수/용량/범위)

✅ 3. 실행/배포 방식
두 가지 방식 모두 지원합니다.
📦 A) 로컬 실행(추천)
개발 머신 + Jupyter 있는 워크스테이션에서 실행:
```bash
streamlit run app.py
```
브라우저에서 접속:
```bash
http://localhost:8501
```
🐳 B) Docker 방식
1) 이미지 빌드
```bash
docker build -t analytics-app .
```
2) 실행
```bash
docker run -p 8501:8501 analytics-app
```

✅ 4. 최종 폴더 구조 (확정안)
``` bash
analytics-lab/
├── generator/
│   ├── data_generator.py
│   └── config.py
├── db/
│   └── (처음엔 비어있음) event_log.duckdb
├── web/
│   ├── app.py
│   └── pages/
│       ├── 1_SQL_Console.py
│       ├── 2_Cohort_Dashboard.py
│       ├── 3_Funnel_Analysis.py
│       ├── 4_User_Behavior.py
│       ├── 5_User_Journey.py
│       ├── 6_RFM_Segmentation.py
│       └── 7_Today_Problems.py
├── sql_problems/
│   └── problem_generator.py
├── requirements.txt
└── Dockerfile
```
