import React, { useEffect, useRef } from 'react';
// Blueprint: in production, import echarts from the app dependency and render option safely.
export function PrismoEChartsMiniPreview({ option, title }: { option?: unknown; title?: string }) {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    // Codex: replace this placeholder with echarts.init(ref.current), setOption(option), ResizeObserver, dispose.
  }, [option]);
  return <section className="prismo-chart-preview" data-prismo-fx="echarts-ready"><h3>{title ?? 'Vista de datos'}</h3><div ref={ref} className="prismo-chart-preview__canvas" /><pre className="prismo-chart-preview__fallback">{JSON.stringify(option ?? {}, null, 2)}</pre></section>;
}
