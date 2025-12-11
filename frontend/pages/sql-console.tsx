import { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import MonacoEditor from "@/components/MonacoEditor";
import axios from "axios";
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

export default function SqlConsole() {
  const [engine, setEngine] = useState<Engine>("duckdb");
  const [sql, setSql] = useState<string>("SELECT * FROM events LIMIT 100;");
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [activeLeftTab, setActiveLeftTab] = useState<"problem" | "schema" | "history">("problem");
  const [problem, setProblem] = useState<string>("");
  const [schema, setSchema] = useState<Record<string, string[]>>({});
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // 오늘의 문제 로드 (Gemini 기반 API와 연결 예정)
  const loadProblem = async () => {
    try {
      const res = await axios.post("http://localhost:8100/problems/generate", {
        difficulty: "hard",
        engine: "duckdb",
      });
      setProblem(res.data.problem);
    } catch (e: any) {
      setProblem("문제를 불러오지 못했습니다. 백엔드 문제 API를 확인하세요.");
    }
  };

  const loadSchema = async () => {
    try {
      const res = await axios.get("http://localhost:8100/schema/schema");
      setSchema(res.data.tables);
    } catch (e) {
      console.warn(e);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await axios.get("http://localhost:8100/sql/history/list");
      setHistory(res.data.items);
    } catch (e) {
      console.warn(e);
    }
  };

  useEffect(() => {
    loadProblem();
    loadSchema();
    loadHistory();
  }, []);

  const runSql = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post("http://localhost:8100/sql/run", {
        engine,
        query: sql,
      });
      setResult(res.data);

      // 자동 히스토리 저장
      await axios.post("http://localhost:8100/sql/history/add", {
        engine,
        query: sql,
        problem,
      });

      // 히스토리 갱신
      loadHistory();
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">SQL Console</h1>
          <p className="text-xs text-slate-300">
            VS Code 스타일 레이아웃 · 자동완성 · 히스토리 기능이 포함된 SQL IDE입니다.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={engine}
            onChange={(e) => setEngine(e.target.value as Engine)}
            className="rounded-md border border-draculaBorder bg-draculaCard px-2 py-1 text-sm"
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
            {loading ? "실행 중..." : "실행 (Ctrl+Enter 느낌)"}
          </button>
        </div>
      </div>

      <PanelGroup direction="horizontal" className="h-[70vh]">
        {/* LEFT */}
        <Panel defaultSize={30} minSize={20}>
          <div className="h-full rounded-lg border border-draculaBorder bg-draculaCard flex flex-col">
            <div className="flex border-b border-draculaBorder text-xs">
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

            <div className="flex-1 overflow-auto p-3 text-xs">
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

        {/* RIGHT */}
        <Panel defaultSize={70} minSize={30}>
          <PanelGroup direction="vertical">
            <Panel defaultSize={55} minSize={30}>
              <MonacoEditor value={sql} onChange={setSql} engine={engine} onRun={runSql}/>
            </Panel>
            <PanelResizeHandle className="h-1 bg-draculaBorder" />
            <Panel defaultSize={45} minSize={20}>
              <div className="h-full rounded-lg border border-draculaBorder bg-draculaCard p-3 text-sm">
                <h2 className="mb-2 text-sm font-semibold">결과</h2>
                {error && (
                  <div className="mb-2 text-red-400 text-xs">에러: {error}</div>
                )}
                {result ? (
                  <div className="overflow-auto">
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
                        {result.rows.map((row: any, idx: number) => (
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
                ) : (
                  <div className="text-slate-400 text-xs">
                    아직 실행 결과가 없습니다.
                  </div>
                )}
              </div>
            </Panel>
          </PanelGroup>
        </Panel>
      </PanelGroup>
    </Layout>
  );
}
