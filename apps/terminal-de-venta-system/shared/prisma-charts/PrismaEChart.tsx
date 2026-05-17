"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { prismaEchartsTheme } from "./prismaChartTheme";
import { loadPrismaEcharts } from "./prismaEchartsLoader";
import type { PrismaChartRenderer } from "./prismaChartContracts";

type PrismaEChartProps = {
  option: Record<string, unknown>;
  renderer: PrismaChartRenderer;
  height: number;
  label: string;
  description: string;
  empty?: boolean;
  onFocusLabel?: (label: string) => void;
};

export function PrismaEChart({ option, renderer, height, label, description, empty, onFocusLabel }: PrismaEChartProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<import("echarts/core").ECharts | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const stableOption = useMemo(() => option, [option]);

  useEffect(() => {
    let disposed = false;
    async function boot() {
      if (!rootRef.current) return;
      if (empty) {
        setState("empty");
        return;
      }
      try {
        const echarts = await loadPrismaEcharts();
        if (disposed || !rootRef.current) return;
        const chart = echarts.init(rootRef.current, prismaEchartsTheme, { renderer });
        chartRef.current = chart;
        chart.setOption(stableOption as never, true);
        chart.on("click", (params: { name?: string; data?: unknown }) => {
          const dataLabel = typeof params.name === "string" ? params.name : JSON.stringify(params.data ?? "item");
          onFocusLabel?.(dataLabel);
        });
        const resizeObserver = new ResizeObserver(() => chart.resize());
        resizeObserver.observe(rootRef.current);
        setState("ready");
        return () => resizeObserver.disconnect();
      } catch {
        if (!disposed) setState("error");
      }
    }
    let cleanup: void | (() => void);
    void boot().then((result) => {
      cleanup = result;
    });
    return () => {
      disposed = true;
      cleanup?.();
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [empty, onFocusLabel, renderer, stableOption]);

  useEffect(() => {
    if (chartRef.current && !empty) chartRef.current.setOption(stableOption as never, true);
  }, [empty, stableOption]);

  return (
    <div aria-label={label} role="img" style={{ minHeight: height }}>
      <p style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" }}>{description}</p>
      <div ref={rootRef} style={{ width: "100%", height }} />
      {state !== "ready" ? (
        <div aria-live="polite" style={{ display: "grid", placeItems: "center", minHeight: height, marginTop: -height }}>
          {state === "loading" ? "Cargando grafica..." : state === "empty" ? "No hay datos suficientes" : "No se pudo renderizar la grafica"}
        </div>
      ) : null}
    </div>
  );
}

