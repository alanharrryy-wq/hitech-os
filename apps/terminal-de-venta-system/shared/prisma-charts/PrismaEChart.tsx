"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
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

function chartClassName(state: "loading" | "ready" | "error" | "empty") {
  return ["prisma-echart", "lab-echart", "lab-echart--executive-observatory", `lab-echart--${state}`].join(" ");
}

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
    setState(empty ? "empty" : "loading");
    void boot().then((result) => {
      cleanup = result;
    });
    return () => {
      disposed = true;
      if (typeof cleanup === "function") cleanup();
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [empty, onFocusLabel, renderer, stableOption]);

  useEffect(() => {
    if (chartRef.current && !empty) chartRef.current.setOption(stableOption as never, true);
  }, [empty, stableOption]);

  function restoreChartView() {
    const chart = chartRef.current;
    if (!chart) return;
    chart.dispatchAction({ type: "restore" });
    chart.dispatchAction({ type: "brush", areas: [] });
    chart.dispatchAction({ type: "downplay" });
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const chart = chartRef.current;
    if (!chart) return;
    if (event.key.toLowerCase() === "r") {
      restoreChartView();
      event.preventDefault();
    }
    if (event.key === "Escape") {
      chart.dispatchAction({ type: "brush", areas: [] });
      chart.dispatchAction({ type: "downplay" });
      event.preventDefault();
    }
  }

  return (
    <div
      aria-busy={state === "loading"}
      aria-label={label}
      className={chartClassName(state)}
      data-polish="luxury-observatory-v1"
      data-command-center-chart="phase4-pro"
      data-render-state={state}
      aria-keyshortcuts="R Escape"
      role="img"
      style={{ minHeight: height }}
      tabIndex={0}
      onDoubleClick={restoreChartView}
      onKeyDown={handleKeyDown}
    >
      <p style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" }}>{description}</p>
      <div ref={rootRef} style={{ width: "100%", height }} />
      <div className="prisma-echart__luxury-rail" aria-hidden="true"><span /><span /><span /></div>
      <div className="prisma-echart__command-hints" aria-hidden="true"><span>R restore</span><span>Esc clear</span><span>dbl-click reset</span></div>
      {state !== "ready" ? (
        <div className="lab-echart__state" aria-live="polite" style={{ display: "grid", placeItems: "center", minHeight: height, marginTop: -height }}>
          {state === "loading" ? "Cargando grafica..." : state === "empty" ? "No hay datos suficientes" : "No se pudo renderizar la grafica"}
        </div>
      ) : null}
    </div>
  );
}
