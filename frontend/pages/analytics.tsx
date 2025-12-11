import { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import PlotlyChart from "@/components/PlotlyChart";
import axios from "axios";

export default function Analytics() {
  const [revenueFig, setRevenueFig] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get("http://localhost:8100/dashboard/sample-revenue");
        setRevenueFig(res.data);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <Layout>
      <div className="mb-4">
        <h1 className="text-xl font-semibold">Analytics Dashboard</h1>
        <p className="text-xs text-slate-300">
          Python Plotly → React Plotly.js 변환 예시입니다.
        </p>
      </div>

      <div className="rounded-lg border border-draculaBorder bg-draculaCard p-3">
        <h2 className="mb-2 text-sm font-semibold">Daily Revenue</h2>

        {loading && <div className="text-slate-400 text-sm">불러오는 중...</div>}

        {!loading && revenueFig && (
          <div className="h-[420px]">
            <PlotlyChart figure={revenueFig} />
          </div>
        )}
      </div>
    </Layout>
  );
}
