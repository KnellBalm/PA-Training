import { useEffect, useRef } from "react";
import Editor, { OnChange, OnMount } from "@monaco-editor/react";
import api from "@/lib/api";

type Engine = "duckdb" | "postgres" | "mysql";

type Props = {
  value: string;
  onChange: (v: string) => void;
  engine: Engine;
  onRun?: () => void;
};

type SchemaTables = Record<string, string[]>;

export default function MonacoEditor({ value, onChange, engine, onRun }: Props) {
  const monacoRef = useRef<any | null>(null);
  const editorRef = useRef<any | null>(null);
  const schemaRef = useRef<SchemaTables>({});
  const providerRegisteredRef = useRef(false);

  // -------------------------------
  // Ctrl/Cmd + Enter 실행 & 테마 정의
  // -------------------------------
  const handleMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Dracula Soft 기반 테마 정의
    monaco.editor.defineTheme("dracula-soft", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#1E1F29",
        "editor.foreground": "#F8F8F2",
        "editorLineNumber.foreground": "#6272A4",
        "editorCursor.foreground": "#FFCC00",
        "editor.selectionBackground": "#44475A",
        "editor.inactiveSelectionBackground": "#44475A99",
        "editor.lineHighlightBackground": "#282A36",
      },
    });
    monaco.editor.setTheme("dracula-soft");

    // Ctrl/Cmd + Enter 실행
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onRun) onRun();
    });

    // 스키마 기반 자동완성 등록 (mount 시 1회)
    registerCompletionProvider();
  };

  // -------------------------------
  // 스키마 로딩
  // -------------------------------
  const loadSchema = async () => {
    try {
      const res = await api.get("/schema/schema");
      schemaRef.current = res.data.tables || {};
    } catch (e) {
      console.warn("schema load failed", e);
    }
  };

  useEffect(() => {
    loadSchema();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // -------------------------------
  // 자동완성 Provider 등록
  // -------------------------------
  const registerCompletionProvider = () => {
    if (!monacoRef.current || providerRegisteredRef.current) return;

    const monaco = monacoRef.current;
    providerRegisteredRef.current = true;

    monaco.languages.registerCompletionItemProvider("sql", {
      triggerCharacters: [".", " ", "("],
      provideCompletionItems: (model: any, position: any) => {
        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn,
        };

        const suggestions: any[] = [];

        // 기본 SQL 키워드
        const baseKeywords = [
          "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY",
          "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
          "ON", "LIMIT", "OFFSET", "INSERT INTO", "VALUES",
          "UPDATE", "SET", "DELETE", "CREATE TABLE", "DROP TABLE",
        ];

        baseKeywords.forEach((kw) => {
          suggestions.push({
            label: kw,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: kw,
            range,
          });
        });

        // 엔진별 함수/키워드
        const engineSpecific: string[] = [];
        if (engine === "duckdb") {
          engineSpecific.push("DATE_TRUNC", "STRFTIME", "WINDOW", "FILTER");
        } else if (engine === "postgres") {
          engineSpecific.push("GENERATE_SERIES", "TO_CHAR", "DATE_TRUNC");
        } else if (engine === "mysql") {
          engineSpecific.push("DATE_FORMAT", "IFNULL", "GROUP_CONCAT");
        }

        engineSpecific.forEach((fn) => {
          suggestions.push({
            label: fn,
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: fn,
            range,
          });
        });

        // 스키마 기반 테이블/컬럼 자동완성
        const tables: SchemaTables = schemaRef.current || {};
        Object.keys(tables).forEach((table) => {
          suggestions.push({
            label: table,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: table,
            detail: "table",
            range,
          });

          tables[table].forEach((col) => {
            suggestions.push({
              label: col,
              kind: monaco.languages.CompletionItemKind.Field,
              insertText: col,
              detail: `${table}.${col}`,
              range,
            });
          });
        });

        return { suggestions };
      },
    });
  };

  // -------------------------------
  // 값 변경 핸들러
  // -------------------------------
  const handleChange: OnChange = (val) => {
    onChange(val || "");
  };

  return (
    <div className="h-full w-full border border-draculaBorder rounded-md overflow-hidden">
      <Editor
        value={value}
        defaultLanguage="sql"
        onChange={handleChange}
        onMount={handleMount}
        theme="vs-dark" // 실제 테마는 onMount에서 dracula-soft로 변경
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "JetBrains Mono, Menlo, monospace",
          automaticLayout: true,
          scrollBeyondLastLine: false,
          wordWrap: "on",
        }}
        height="100%"
      />
    </div>
  );
}
