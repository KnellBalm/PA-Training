import Layout from "@/components/Layout";
import axios from "axios";
import { useEffect, useState } from "react";

export default function Datasets() {
  const [tables, setTables] = useState<string[]>([]);
  const [columns, setColumns] = useState<any>({});
  const [preview, setPreview] = useState<any[]>([]);
  const [selected, setSelected] = useState<string>("");

  useEffect(() => {
    axios.get("http://localhost:8100/schema/tables").then((res) => {
      setTables(res.data.tables);
    });
    axios.get("http://localhost:8100/schema/schema").then((res) => {
      setColumns(res.data.tables);
    });
  }, []);

  async function loadPreview(table: string) {
    setSelected(table);
    const res = await axios.get(`http://localhost:8100/schema/preview?table=${table}`);
    setPreview(res.data.rows);
  }

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">데이터셋 탐색</h1>

      <div className="grid grid-cols-4 gap-6">

        {/* 테이블 리스트 */}
        <div className="col-span-1 bg-draculaCurrent p-4 rounded-lg border border-draculaBorder">
          <h2 className="font-bold text-lg mb-3">📁 테이블 목록</h2>

          {tables.map((t) => (
            <div
              key={t}
              className={`p-2 rounded cursor-pointer hover:bg-draculaSelection ${
                selected === t ? "bg-draculaSelection" : ""
              }`}
              onClick={() => loadPreview(t)}
            >
              {t}
            </div>
          ))}
        </div>

        {/* 프리뷰 + 스키마 */}
        <div className="col-span-3">
          {selected ? (
            <>
              <h2 className="text-xl font-bold mb-2">{selected}</h2>

              {/* 스키마 */}
              <div className="mb-4">
                <h3 className="font-bold mb-1">Columns</h3>
                <div className="text-draculaComment">
                  {columns[selected].join(", ")}
                </div>
              </div>

              {/* 미리보기 */}
              <table className="w-full border-collapse bg-draculaCurrent border border-draculaBorder">
                <thead className="bg-draculaSelection">
                  <tr>
                    {Object.keys(preview[0] || {}).map((col) => (
                      <th key={col} className="px-3 py-2 border border-draculaBorder text-left">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, idx) => (
                    <tr key={idx} className="hover:bg-draculaSelection">
                      {Object.values(row).map((val, i) => (
                        <td key={i} className="px-3 py-2 border border-draculaBorder">
                          {String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : (
            <p className="text-draculaComment">왼쪽에서 테이블을 선택하세요.</p>
          )}
        </div>
      </div>
    </Layout>
  );
}
