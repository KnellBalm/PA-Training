import dynamic from "next/dynamic";
import { CSSProperties, useEffect, useRef } from "react";

// react-plotly.js 타입 정의
export interface PlotlyFigure {
  data: any[];
  layout: any;
}

type Props = {
  figure: PlotlyFigure;
};

// dynamic import + 타입 강제 선언 (Next.js 빌드 오류 방지)
const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
}) as React.ComponentType<{
  data: any[];
  layout: any;
  style?: CSSProperties;
  useResizeHandler?: boolean;
  config?: any;
}>;

export default function PlotlyChart({ figure }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  // ResizeObserver로 부모 DIV 크기 변화 감지 → Plotly autosize 유도
  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver(() => {
      // Plotly는 useResizeHandler가 true면 자동 재렌더링
    });

    observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "100%",
        minHeight: "350px", // 모바일 대응 위한 최소 높이
        display: "flex",
      }}
    >
      <Plot
        data={figure.data}
        layout={{
          ...figure.layout,
          autosize: true,       // 화면 크기 변화 자동 적용
          margin: { t: 40, l: 40, r: 10, b: 40 },
        }}
        useResizeHandler={true}
        style={{
          width: "100%",
          height: "100%",
        }}
        config={{
          responsive: true,     // Plotly 공식 반응형 옵션
          displaylogo: false,
        }}
      />
    </div>
  );
}
