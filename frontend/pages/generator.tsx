import { useEffect, useState } from "react";
import axios from "axios";
import Layout from "@/components/Layout";

export default function Generator() {
  const [status, setStatus] = useState("");

  async function generate() {
    setStatus("데이터 생성 중...");
    const res = await axios.post("http://localhost:8100/generator/create");
    setStatus("완료: " + res.data.message);
  }

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">데이터 생성</h1>
      <button
        onClick={generate}
        className="bg-draculaPurple px-4 py-2 rounded hover:bg-draculaPink"
      >
        새 데이터 생성
      </button>
      <p className="mt-4">{status}</p>
    </Layout>
  );
}

export default function GeneratorPage() {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle");

  const startAdvanced = async () => {
    await axios.post("http://localhost:8100/generator/advanced");
  };

  useEffect(() => {
    const timer = setInterval(async () => {
      const res = await axios.get("http://localhost:8100/generator/progress");
      setProgress(res.data.progress);
      setStatus(res.data.status);
    }, 2000);

    return () => clearInterval(timer);
  }, []);

  return (
    <Layout>
      <h1 className="text-xl font-bold mb-3">고급 데이터 생성기</h1>

      <button
        onClick={startAdvanced}
        className="bg-draculaAccent text-black px-4 py-2 rounded-md"
      >
        고급형 데이터 생성 시작
      </button>

      <div className="mt-6">
        <p>상태: {status}</p>
        <div className="w-full bg-draculaBorder rounded h-4 mt-2">
          <div
            className="bg-draculaAccent h-4 rounded"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-1">{progress}%</p>
      </div>
    </Layout>
  );
}
