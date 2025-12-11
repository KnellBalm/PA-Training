import { useEffect, useState } from "react";
import api from "@/lib/api";
import Layout from "@/components/Layout";

type Summary = {
  total_users: number;
  total_events: number;
  start_date: string;
  end_date: string;
  recent_dau: number;
  recent_revenue: number;
};

export default function Home() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [errMsg, setErrMsg] = useState("");

  const loadSummary = async () => {
    try {
      const res = await api.get("/analytics/summary");
      setSummary(res.data);
    } catch (err: any) {
      setErrMsg("대시보드 데이터를 불러올 수 없습니다.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  return (
    <Layout>
      <div className="px-8 py-6">

        {/* Header */}
        <h1 className="text-2xl font-bold mb-2">Analytics Lab 홈</h1>
        <p className="text-sm text-slate-400 mb-6">
          SQL · Cohort · Funnel · RFM · 사용자 여정 분석을 연습할 수 있는 통합 플랫폼
        </p>

        {/* SUMMARY */}
        {loading && <div className="text-sm text-slate-400">불러오는 중...</div>}
        {errMsg && <div className="text-red-400 text-sm">{errMsg}</div>}

        {summary && (
          <>
            <div className="grid grid-cols-4 gap-4 mb-10">

              <div className="stat-card">
                <div className="text-xs text-slate-400">기간</div>
                <div className="font-semibold text-lg">
                  {summary.start_date} ~ {summary.end_date}
                </div>
              </div>

              <div className="stat-card">
                <div className="text-xs text-slate-400">총 사용자수</div>
                <div className="font-semibold text-lg">
                  {summary.total_users.toLocaleString()}
                </div>
              </div>

              <div className="stat-card">
                <div className="text-xs text-slate-400">총 이벤트 수</div>
                <div className="font-semibold text-lg">
                  {summary.total_events.toLocaleString()}
                </div>
              </div>

              <div className="stat-card">
                <div className="text-xs text-slate-400">최근 DAU</div>
                <div className="font-semibold text-lg">
                  {summary.recent_dau.toLocaleString()}
                </div>
              </div>
            </div>

            {/* Shortcut Menu */}
            <div className="grid grid-cols-3 gap-6">

              <a
                href="/sql-console"
                className="shortcut-btn"
              >
                <div className="text-lg font-semibold mb-1">SQL Console</div>
                <div className="text-sm text-slate-400">
                  실무형 SQL IDE · 히스토리 · 자동완성 · 문제 풀이
                </div>
              </a>

              <a
                href="/analytics"
                className="shortcut-btn"
              >
                <div className="text-lg font-semibold mb-1">Analysis Dashboard</div>
                <div className="text-sm text-slate-400">
                  Cohort · Funnel · RFM · User Journey 분석
                </div>
              </a>

              <a
                href="/generator"
                className="shortcut-btn"
              >
                <div className="text-lg font-semibold mb-1">데이터 생성기</div>
                <div className="text-sm text-slate-400">
                  3개월/6개월/고급형 이벤트 로그 자동 생성
                </div>
              </a>

            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
