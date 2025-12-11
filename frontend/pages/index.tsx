import Layout from "@/components/Layout";
import Link from "next/link";
import axios from "axios";
import { useEffect, useState } from "react";

export default function Home() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    axios.get("http://localhost:8100/analytics/summary").then((res) => {
      setSummary(res.data);
    });
  }, []);

  return (
    <Layout>
      {/* 메인 Hero Section */}
      <section className="mb-16">
        <h1 className="text-4xl font-bold mb-3 text-draculaPink">
          Analytics Lab
        </h1>
        <p className="text-lg text-draculaComment max-w-3xl">
          SQL, Cohort, Funnel, RFM, User Journey 등을 실제 서비스 환경처럼 연습할 수 있는
          통합 분석 실험 플랫폼입니다. 데이터 생성 → SQL → 분석 → 시각화까지 모두 지원합니다.
        </p>
      </section>

      {/* 데이터셋 정보 */}
      {summary && (
        <section className="grid grid-cols-4 gap-6 mb-16">
          <div className="stat-card">
            <div className="stat-title">데이터 기간</div>
            <div className="stat-value">{summary.start} ~ {summary.end}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">전체 이벤트</div>
            <div className="stat-value">{summary.events.toLocaleString()}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">전체 사용자</div>
            <div className="stat-value">{summary.users.toLocaleString()}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">최근 업데이트</div>
            <div className="stat-value">{summary.updated_at}</div>
          </div>
        </section>
      )}

      {/* 메뉴 섹션 */}
      <section className="mb-20">
        <h2 className="section-title">🧠 SQL 분석 & 시각화 기능</h2>

        <div className="grid grid-cols-3 gap-8 mt-6">

          <Link href="/sql-console" className="menu-card">
            <div className="menu-icon">💻</div>
            <div className="menu-title">SQL Console</div>
            <div className="menu-desc">
              DuckDB · MySQL · PostgreSQL 엔진에서 직접 SQL을 실행하고 결과를 시각화합니다.
            </div>
          </Link>

          <Link href="/analytics" className="menu-card">
            <div className="menu-icon">📊</div>
            <div className="menu-title">Analytics Dashboard</div>
            <div className="menu-desc">
              Cohort, Funnel, RFM, User Journey 등 다양한 분석을 확인할 수 있습니다.
            </div>
          </Link>

          <Link href="/problems" className="menu-card">
            <div className="menu-icon">🧩</div>
            <div className="menu-title">AI SQL 문제</div>
            <div className="menu-desc">
              Gemini API 기반 오늘의 실무형 SQL 문제 자동 생성 기능을 제공합니다.
            </div>
          </Link>

        </div>
      </section>

      {/* 데이터 관리 섹션 */}
      <section>
        <h2 className="section-title">📁 데이터 관리</h2>

        <div className="grid grid-cols-2 gap-8 mt-6">
          <Link href="/generator" className="menu-card">
            <div className="menu-icon">⚙️</div>
            <div className="menu-title">데이터 생성</div>
            <div className="menu-desc">
              고급형 랜덤 데이터셋 생성 (6개월, 20M events) 포함.
            </div>
          </Link>

          <Link href="/datasets" className="menu-card">
            <div className="menu-icon">📂</div>
            <div className="menu-title">데이터셋 탐색</div>
            <div className="menu-desc">
              테이블 목록 및 스키마 확인, 상위 데이터 미리보기 기능 제공.
            </div>
          </Link>
        </div>
      </section>
    </Layout>
  );
}
