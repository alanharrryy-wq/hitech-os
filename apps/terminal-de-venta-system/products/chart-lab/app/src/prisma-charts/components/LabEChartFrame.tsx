"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { prismaEchartsTheme } from "../../../../../../shared/prisma-charts/prismaChartTheme";
import type { LabChartDensity, LabChartEntry, LabChartSize } from "../chart-lab-types";

type LabEChartFrameProps = {
  entry: LabChartEntry;
  density: LabChartDensity;
  size: LabChartSize;
  optionOverride?: Record<string, unknown>;
};

function chartHeight(entry: LabChartEntry, size: LabChartSize, density: LabChartDensity) {
  const sizeBoost = size === "focus" ? 120 : size === "compact" ? -70 : 40;
  const densityTrim = density === "dense" ? -24 : 0;
  return Math.max(260, entry.defaultHeight + sizeBoost + densityTrim);
}

export function LabEChartFrame({ entry, density, size, optionOverride }: LabEChartFrameProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<import("echarts/core").ECharts | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const option = useMemo(() => optionOverride ?? entry.getOption?.() ?? {}, [entry, optionOverride]);
  const height = chartHeight(entry, size, density);

  if (!entry.getOption || !entry.renderer) {
    return (
      <div className="lab-empty-chart" style={{ minHeight: height }}>
        <span>{entry.readiness}</span>
        <strong>{entry.unavailableReason ?? "This chart is registered but does not expose an ECharts option yet."}</strong>
      </div>
    );
  }

  useEffect(() => {
    let disposed = false;
    let resizeObserver: ResizeObserver | null = null;

    async function boot() {
      if (!rootRef.current || !entry.renderer) return;
      if (!entry.getOption) {
        setState("empty");
        return;
      }

      try {
        const [echarts, charts, components, renderers] = await Promise.all([
          import("echarts/core"),
          import("echarts/charts"),
          import("echarts/components"),
          import("echarts/renderers")
        ]);

        echarts.use([
          charts.BarChart,
          charts.CustomChart,
          charts.GraphChart,
          charts.HeatmapChart,
          charts.LineChart,
          charts.PictorialBarChart,
          charts.RadarChart,
          charts.SankeyChart,
          charts.ScatterChart,
          charts.TreemapChart,
          components.AriaComponent,
          components.BrushComponent,
          components.DatasetComponent,
          components.DataZoomComponent,
          components.GridComponent,
          components.LegendComponent,
          components.TitleComponent,
          components.TooltipComponent,
          components.TransformComponent,
          components.VisualMapComponent,
          renderers.CanvasRenderer,
          renderers.SVGRenderer
        ]);

        if (disposed || !rootRef.current) return;
        const chart = echarts.init(rootRef.current, prismaEchartsTheme, { renderer: entry.renderer });
        chartRef.current = chart;
        chart.setOption(option as never, true);
        resizeObserver = new ResizeObserver(() => chart.resize());
        resizeObserver.observe(rootRef.current);
        setState("ready");
      } catch {
        if (!disposed) setState("error");
      }
    }

    void boot();

    return () => {
      disposed = true;
      resizeObserver?.disconnect();
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [entry, option]);

  useEffect(() => {
    if (chartRef.current) chartRef.current.setOption(option as never, true);
  }, [option]);

  return (
    <div className="lab-echart" aria-label={`${entry.title} preview`} role="img" style={{ minHeight: height }}>
      <p className="sr-only">{`${entry.title}: ${entry.operationalQuestion}`}</p>
      <div ref={rootRef} style={{ width: "100%", height }} />
      {state !== "ready" ? (
        <div className="lab-echart__state" aria-live="polite" style={{ minHeight: height, marginTop: -height }}>
          {state === "loading" ? "Loading chart..." : state === "empty" ? "No data available" : "Chart render failed"}
        </div>
      ) : null}
    </div>
  );
}
