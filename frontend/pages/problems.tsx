import { useEffect, useState } from "react";
import axios from "axios";
import Layout from "@/components/Layout";

export default function Problems() {
  const [problem, setProblem] = useState("");

  useEffect(() => {
    const load = async () => {
      const res = await axios.get("http://localhost:8100/problems/daily");
      setProblem(res.data.problem);
    };
    load();
  }, []);

  return (
    <Layout>
      <h1 className="text-xl font-bold mb-4">Today’s SQL Problem</h1>
      <div className="bg-draculaCard border border-draculaBorder p-4 rounded">
        {problem}
      </div>
    </Layout>
  );
}
