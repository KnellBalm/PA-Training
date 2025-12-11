import { useState } from "react";
import api from "@/lib/api";
import Layout from "@/components/Layout";

export default function Generator() {
  const [status, setStatus] = useState<string>("");
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  async function pollProgress() {
      const timer = setInterval(async () => {
        try {
          const progressRes = await api.get("/generator/progress");
          setProgress(progressRes.data.progress);

          if (progressRes.data.progress >= 100) {
            clearInterval(timer);
            setStatus("데이터 생성 완료!");
          }

          if (progressRes.data.progress < 0) {
            clearInterval(timer);
            setStatus("에러 발생");
            setError("데이터 생성 실패");
          }
        } catch (err) {
          clearInterval(timer);
          setError("프로그레스 조회 실패");
        }
      }, 1000);
    }

  async function generate() {
    setError(null);
    setStatus("데이터 생성 중...");
    setProgress(10);

    try {
      const res = await api.post("/generator/create");
      if (res.data.status === "started") {
        pollProgress();
      }
      // 실제로는 백엔드에서 progress API를 붙이면 여기서 폴링 가능
      setProgress(100);
      setStatus("완료: " + res.data.message);
    } catch (e: any) {
      setStatus("데이터 생성 실패");
      setError(e?.response?.data?.detail || e.message);
      setProgress(0);
    }
  }

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-2">데이터 생성</h1>
      <p className="text-sm text-draculaComment mb-6">
        고급형 랜덤 로그 데이터를 생성하여 SQL 연습용 데이터셋을 준비합니다.
        생성이 완료되면 SQL Console과 대시보드에서 바로 조회할 수 있습니다.
      </p>

      <button
        onClick={generate}
        className="bg-draculaAccent text-black font-semibold px-4 py-2 rounded-lg hover:bg-draculaAccent2 transition"
      >
        새 데이터 생성
      </button>

      <div className="mt-6">
        <p className="text-sm">상태: {status || "대기 중"}</p>

        <div className="w-full bg-draculaBorder rounded h-3 mt-2">
          <div
            className="bg-draculaAccent h-3 rounded"
            style={{ width: `${progress}%`, transition: "width 0.3s ease" }}
          />
        </div>
        <p className="mt-1 text-xs text-draculaComment">{progress}%</p>

        {error && (
          <p className="mt-2 text-xs text-red-400">에러: {error}</p>
        )}
      </div>
    </Layout>
  );
}
