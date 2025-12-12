import { useEffect, useState, useCallback } from "react";
import Layout from "@/components/Layout";
import MonacoEditor from "@/components/MonacoEditor";
import api from "@/lib/api";

import {
  Panel,
  PanelGroup,
  PanelResizeHandle,
} from "react-resizable-panels";

type Engine = "duckdb" | "postgres" | "mysql";

type HistoryItem = {
  id: number;
  created_at: string;
  engine: string;
  query: string;
  problem?: string | null;
  correct?: boolean | null;
};

type SqlResult = {
  columns: string[];
  rows: Record<string, any>[];
};

export default function SqlConsole() {
  const [engine, setEngine] = useState<Engine>("duckdb");
  const [sql, setSql] = useState<string>("SELECT * FROM events LIMIT 100;");
  const [result, setResult] = useState<SqlResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [activeLeftTab, setActiveLeftTab] = useState<"problem" | "schema" | "history">("problem");
  const [problem, setProblem] = useState<string>("");
  const [schema, setSchema] = useState<Record<string, string[]>>({});
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const loadProblem = async () => {
    try {
      const res = await api.post('/problems/generate', {
        difficulty: "hard",
        engine,
      });
      setProblem(res.data.problem);
    } catch (e: any) {
      setProblem("문제를 불러오지 못했습니다. 백엔드 문제 API를 확인하세요.");
    }
  };

  const loadSchema = async () => {
    try {
      const res = await api.get('/schema/schema');
      setSchema(res.data.tables);
    } catch (e) {
      console.warn("Schema load failed", e);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await api.get('/sql/history/list');
      setHistory(res.data.items);
    } catch (e) {
      console.warn("History load failed", e);
    }
  };

  useEffect(() => {
    Promise.all([
      loadProblem(),
      loadSchema(),
      loadHistory(),
    ]);
  }, []);

  const runSql = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<SqlResult>('/sql/run', {
        engine,
        query: sql,
      });
      console.log("SQL Result:")
      console.log(res);
      setResult(res.data);

      const newHistoryItemRes = await api.post<HistoryItem>('/sql/history/add', {
        engine,
        query: sql,
        problem,
      });
      setHistory(prev => [newHistoryItemRes.data, ...prev]);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [engine, sql, problem, loading]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runSql();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [runSql]);

  return (
    <Layout>
      <div className="flex flex-col h-full w-full px-6 pt-4 pb-2 overflow-hidden">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-xl font-semibold">SQL Console</h1>
            <p className="text-xs text-slate-400">
              VS Code 스타일 실무용 SQL IDE — 자동완성·문제풀이·히스토리 포함
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select
              className="rounded-md border border-draculaBorder bg-draculaCard px-2 py-1 text-sm"
              value={engine}
              onChange={(e) => setEngine(e.target.value as Engine)}
            >
              <option value="duckdb">DuckDB</option>
              <option value="postgres">PostgreSQL</option>
              <option value="mysql">MySQL</option>
            </select>

            <button
              onClick={runSql}
              className="rounded-md bg-draculaAccent px-3 py-1 text-sm font-semibold text-black"
              disabled={loading}
            >
              {loading ? "실행 중..." : "실행 (Ctrl+Enter)"}
            </button>
          </div>
        </div>

      <PanelGroup direction="horizontal" className="h-full">
        <Panel defaultSize={30} minSize={20}>
          <div className="h-full w-full rounded-lg border border-draculaBorder bg-draculaCard flex flex-col overflow-hidden">
            <div className="flex border-b border-draculaBorder text-xs flex-shrink-0">
              <button
                className={`px-3 py-2 ${activeLeftTab === "problem" ? "bg-draculaBg" : ""}`}
                onClick={() => setActiveLeftTab("problem")}
              >
                오늘의 문제
              </button>
              <button
                className={`px-3 py-2 ${activeLeftTab === "schema" ? "bg-draculaBg" : ""}`}
                onClick={() => setActiveLeftTab("schema")}
              >
                스키마
              </button>
              <button
                className={`px-3 py-2 ${activeLeftTab === "history" ? "bg-draculaBg" : ""}`}
                onClick={() => setActiveLeftTab("history")}
              >
                히스토리
              </button>
            </div>

            <div className="flex-1 overflow-auto p-3 text-xs min-h-0">
              {activeLeftTab === "problem" && (
                <div>
                  <div className="mb-2 flex justify-between items-center">
                    <span className="font-semibold text-sm">Today&apos;s Problem</span>
                    <button
                      onClick={loadProblem}
                      className="text-[11px] underline text-draculaAccent"
                    >
                      새 문제 받기
                    </button>
                  </div>
                  <pre className="whitespace-pre-wrap">{problem}</pre>
                </div>
              )}

              {activeLeftTab === "schema" && (
                <div>
                  {Object.keys(schema).map((t) => (
                    <div key={t} className="mb-2">
                      <div className="font-semibold">{t}</div>
                      <ul className="ml-3 list-disc">
                        {schema[t].map((c) => (
                          <li key={c}>{c}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}

              {activeLeftTab === "history" && (
                <div>
                  {history.length === 0 && (
                    <div className="text-slate-400">
                      아직 저장된 기록이 없습니다.
                    </div>
                  )}
                  {history.map((h) => (
                    <div
                      key={h.id}
                      className="mb-2 border-b border-draculaBorder pb-2"
                    >
                      <div className="text-[11px] text-slate-400">
                        {h.created_at} · {h.engine}
                      </div>
                      {h.problem && (
                        <div className="text-[11px] text-slate-300 mb-1">
                          문제: {h.problem.slice(0, 60)}...
                        </div>
                      )}
                      <pre className="whitespace-pre-wrap text-[11px]">
                        {h.query}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-draculaBorder" />

        <Panel defaultSize={70} minSize={30}>
          <PanelGroup direction="vertical" className="h-full">
            <Panel defaultSize={55} minSize={30}>
              <MonacoEditor value={sql} onChange={setSql} engine={engine} onRun={runSql}/>
            </Panel>
            <PanelResizeHandle className="h-1 bg-draculaBorder" />
            <Panel defaultSize={45} minSize={20}>
              <div className="h-full rounded-lg border border-draculaBorder bg-draculaCard p-3 text-sm flex flex-col overflow-hidden">
                <h2 className="mb-2 text-sm font-semibold">결과</h2>
                {error && (
                  <div className="mb-2 text-red-400 text-xs">에러: {error}</div>
                )}
                {result ? (
                  <div className="overflow-auto flex-1">
                    <table className="min-w-full border-collapse text-xs">
                      <thead>
                        <tr>
                          {result.columns.map((c: string) => (
                            <th
                              key={c}
                              className="border-b border-draculaBorder px-2 py-1 text-left"
                            >
                              {c}
                            </th>
                          ))}
                        </tr>
                      </thead>

                      <tbody>
                        {result.rows.map((row, idx: number) => (
                          <tr key={idx}>
                            {result.columns.map((c: string) => (
                              <td
                                key={c}
                                className="border-b border-draculaBorder px-2 py-1"
                              >
                                {String(row[c])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : !error && (
                  <div className="text-slate-400 text-xs">
                    아직 실행 결과가 없습니다.
                  </div>
                )}
              </div>
            </Panel>
          </PanelGroup>
        </Panel>
      </PanelGroup>
      </div>
    </Layout>
  );
}
