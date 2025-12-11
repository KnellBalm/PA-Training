"use client";

import { useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import axios from "axios";

type Props = {
  value: string;
  onChange: (v: string) => void;
  engine: "duckdb" | "postgres" | "mysql";
  onRun: () => void;
};

export default function MonacoEditor({ value, onChange, engine, onRun }: Props) {
  const editorRef = useRef<any>(null);

  // 에디터 로딩 완료 시 호출
  function handleEditorDidMount(editor: any) {
    editorRef.current = editor;

    // Ctrl(Cmd) + Enter 실행 단축키
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onRun();
    });
  }

  /** SQL 자동완성 로드 */
  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get("http://localhost:8100/schema/schema");
        const schema: Record<string, string[]> = res.data.tables;

        const suggestions: monaco.languages.CompletionItem[] = [];

        /** 테이블 자동완성 */
        Object.keys(schema).forEach((table) => {
          suggestions.push({
            label: table,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: table,
            range: undefined,
          });

          /** 컬럼 자동완성 */
          schema[table].forEach((col) => {
            suggestions.push({
              label: col,
              kind: monaco.languages.CompletionItemKind.Field,
              insertText: col,
              range: undefined,
            });
          });
        });

        /** SQL 키워드 자동완성 */
        const KEYWORDS = [
          "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "LIMIT",
          "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
          "COUNT", "SUM", "AVG", "MIN", "MAX"
        ];

        KEYWORDS.forEach((kw) =>
          suggestions.push({
            label: kw,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: kw,
            range: undefined,
          })
        );

        monaco.languages.registerCompletionItemProvider("sql", {
          provideCompletionItems: () => ({ suggestions }),
        });
      } catch (e) {
        console.warn("schema load failed", e);
      }
    };

    load();
  }, [engine]);

  return (
    <div className="border border-draculaBorder rounded-md overflow-hidden h-full">
      <Editor
        height="100%"
        defaultLanguage="sql"
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange(v || "")}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "JetBrains Mono, monospace",
          automaticLayout: true,
        }}
      />
    </div>
  );
}
