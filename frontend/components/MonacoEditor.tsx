"use client";

import { useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";

type Props = {
  value: string;
  onChange: (v: string) => void;
  engine: "duckdb" | "postgres" | "mysql";
  onRun: () => void;
};

export default function MonacoEditor({ value, onChange, engine, onRun }: Props) {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);

  /** 에디터 마운트 후 호출 */
  function handleEditorDidMount(editor: any, monaco: any) {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Ctrl / Cmd + Enter 실행
    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
      () => {
        onRun();
      }
    );

    // 최초 한번 자동완성 로딩
    loadSchemaAndRegisterCompletion(monaco);
  }

  /** 스키마 기반 자동완성 등록 */
  async function loadSchemaAndRegisterCompletion(monaco: any) {
    try {
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/schema/schema`);
      const schema: Record<string, string[]> = res.data.tables;

      const suggestions: any[] = [];

      // 테이블명 자동완성
      Object.keys(schema).forEach((table) => {
        suggestions.push({
          label: table,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: table,
        });

        // 컬럼명 자동완성
        schema[table].forEach((col) => {
          suggestions.push({
            label: col,
            kind: monaco.languages.CompletionItemKind.Field,
            insertText: col,
          });
        });
      });

      // 기본 SQL 키워드
      const KEYWORDS = [
        "SELECT",
        "FROM",
        "WHERE",
        "GROUP BY",
        "ORDER BY",
        "LIMIT",
        "JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "INNER JOIN",
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
      ];

      KEYWORDS.forEach((kw) =>
        suggestions.push({
          label: kw,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: kw,
        })
      );

      monaco.languages.registerCompletionItemProvider("sql", {
        provideCompletionItems: (model: any, position: any) => {
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          return {
            suggestions: suggestions.map((s) => ({
              ...s,
              range,
            })),
          };
        },
      });
    } catch (e) {
      console.warn("schema load failed", e);
    }
  }

  // 엔진 변경 시에도 스키마 다시 로딩
  useEffect(() => {
    if (!monacoRef.current) return;
    loadSchemaAndRegisterCompletion(monacoRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
          fontFamily: "JetBrains Mono, Menlo, monospace",
          automaticLayout: true,
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
}
