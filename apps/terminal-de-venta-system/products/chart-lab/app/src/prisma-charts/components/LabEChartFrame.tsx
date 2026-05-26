// PRISMA_CHART_LAB_POWER_STUDIO_V3_FINAL_INFRASTRUCTURE
// PRISMA_CHART_LAB_POWER_STUDIO_ECHART_FRAME_V1
"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { prismaEchartsTheme } from "../../../../../../shared/prisma-charts/prismaChartTheme";
import type { LabChartDensity, LabChartEntry, LabChartSize } from "../chart-lab-types";

type LabEChartFrameProps = {
  entry: LabChartEntry;
  density: LabChartDensity;
  size: LabChartSize;
  optionOverride?: Record<string, unknown>;
  tourSignal?: number;
};

export type VisibleSeriesSummary = {
  seriesCount: number;
  visibleSeriesCount: number;
  hasSeriesData: boolean;
  hasDatasetData: boolean;
  suspectedBlankChart: boolean;
};

function chartHeight(entry: LabChartEntry, size: LabChartSize, density: LabChartDensity) {
  const base = size === "focus" ? 640 : size === "wide" ? 560 : 430;
  const densityTrim = density === "dense" ? -18 : 0;
  return Math.max(360, Math.max(entry.defaultHeight, base) + densityTrim);
}

function chartClassName(state: "loading" | "ready" | "error" | "empty") {
  return ["lab-echart", "lab-echart--power-studio", `lab-echart--${state}`].join(" ");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function normalizeSeries(option: Record<string, unknown>): Record<string, unknown>[] {
  const series = option.series;
  if (Array.isArray(series)) return series.filter(isRecord);
  return isRecord(series) ? [series] : [];
}

function hasArrayData(value: unknown): boolean {
  return Array.isArray(value) && value.length > 0;
}

function hasRecordSourceData(value: Record<string, unknown>): boolean {
  return Object.values(value).some((item) => (Array.isArray(item) ? item.length > 0 : item !== undefined && item !== null));
}

function hasSeriesRecordData(series: Record<string, unknown>): boolean {
  return (
    hasArrayData(series.data) ||
    hasArrayData(series.nodes) ||
    hasArrayData(series.links) ||
    hasArrayData(series.edges) ||
    hasArrayData(series.children)
  );
}

export function hasSeriesData(series: unknown): boolean {
  const items = Array.isArray(series) ? series : [series];
  return items.some((item) => isRecord(item) && hasSeriesRecordData(item));
}

function hasDatasetSourceData(source: unknown): boolean {
  if (Array.isArray(source)) return source.length > 0;
  if (isRecord(source)) return hasRecordSourceData(source);
  return typeof source === "string" && source.trim().length > 0;
}

export function hasDatasetData(option: Record<string, unknown>): boolean {
  const dataset = option.dataset;
  const datasets = Array.isArray(dataset) ? dataset : isRecord(dataset) ? [dataset] : [];
  return datasets.some((item) => isRecord(item) && hasDatasetSourceData(item.source));
}

function numericOpacity(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function seriesLooksVisible(series: Record<string, unknown>): boolean {
  if (series.show === false) return false;
  const opacityCandidates = [
    numericOpacity(series.opacity),
    numericOpacity(isRecord(series.itemStyle) ? series.itemStyle.opacity : undefined),
    numericOpacity(isRecord(series.lineStyle) ? series.lineStyle.opacity : undefined),
    numericOpacity(isRecord(series.areaStyle) ? series.areaStyle.opacity : undefined)
  ].filter((value): value is number => value !== null);
  return opacityCandidates.length === 0 || opacityCandidates.some((value) => value > 0.05);
}

function hasRenderedSurface(root: HTMLDivElement) {
  return Boolean(root.querySelector("canvas, svg"));
}

export function getVisibleSeriesSummary(option: Record<string, unknown>): VisibleSeriesSummary {
  const series = normalizeSeries(option);
  const seriesCount = series.length;
  const visibleSeriesCount = series.filter(seriesLooksVisible).length;
  const hasDirectSeriesData = hasSeriesData(series);
  const hasDirectDatasetData = hasDatasetData(option);
  return {
    seriesCount,
    visibleSeriesCount,
    hasSeriesData: hasDirectSeriesData,
    hasDatasetData: hasDirectDatasetData,
    suspectedBlankChart: !hasDirectDatasetData && (seriesCount === 0 || visibleSeriesCount === 0 || !hasDirectSeriesData)
  };
}

export function LabEChartFrame({ entry, density, size, optionOverride, tourSignal = 0 }: LabEChartFrameProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<import("echarts/core").ECharts | null>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);
  const resizeFrameRef = useRef<number | null>(null);
  const resizeTimerRef = useRef<number | null>(null);
  const tourTimerRef = useRef<number | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const option = useMemo(() => optionOverride ?? entry.getOption?.() ?? {}, [entry, optionOverride]);
  const visibleSeriesSummary = useMemo(() => getVisibleSeriesSummary(option), [option]);
  const height = chartHeight(entry, size, density);

  function clearScheduledResize() {
    if (resizeFrameRef.current) window.cancelAnimationFrame(resizeFrameRef.current);
    if (resizeTimerRef.current) window.clearTimeout(resizeTimerRef.current);
    resizeFrameRef.current = null;
    resizeTimerRef.current = null;
  }

  function scheduleChartResize(chart: import("echarts/core").ECharts) {
    clearScheduledResize();
    resizeFrameRef.current = window.requestAnimationFrame(() => {
      chart.resize();
      resizeFrameRef.current = null;
    });
    resizeTimerRef.current = window.setTimeout(() => {
      chart.resize();
      resizeTimerRef.current = null;
    }, 120);
  }

  useEffect(() => {
    if (!entry.getOption || !entry.renderer) {
      setState("empty");
      return;
    }

    let disposed = false;

    async function boot() {
      if (!rootRef.current || !entry.renderer) return;
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
          components.ToolboxComponent,
          components.MarkLineComponent,
          components.MarkPointComponent,
          components.TransformComponent,
          components.VisualMapComponent,
          components.GraphicComponent,
          renderers.CanvasRenderer,
          renderers.SVGRenderer
        ]);

        if (disposed || !rootRef.current) return;
        chartRef.current?.dispose();
        let chart = echarts.init(rootRef.current, prismaEchartsTheme, { renderer: entry.renderer });
        chart.setOption(option as never, true);
        chart.resize();
        if (!hasRenderedSurface(rootRef.current)) {
          chart.dispose();
          const fullEcharts = await import("echarts");
          if (disposed || !rootRef.current) return;
          chart = fullEcharts.init(rootRef.current, prismaEchartsTheme, { renderer: entry.renderer }) as unknown as import("echarts/core").ECharts;
          chart.setOption(option as never, true);
          chart.resize();
        }
        chartRef.current = chart;
        scheduleChartResize(chart);
        resizeObserverRef.current?.disconnect();
        resizeObserverRef.current = new ResizeObserver(() => scheduleChartResize(chart));
        resizeObserverRef.current.observe(rootRef.current);
        setState("ready");
      } catch {
        if (!disposed) setState("error");
      }
    }

    setState("loading");
    void boot();

    return () => {
      disposed = true;
      if (tourTimerRef.current) window.clearInterval(tourTimerRef.current);
      clearScheduledResize();
      resizeObserverRef.current?.disconnect();
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [entry.id, entry.renderer]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    try {
      chart.setOption(option as never, true);
      scheduleChartResize(chart);
      setState("ready");
    } catch {
      setState("error");
    }
  }, [option]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || tourSignal <= 0) return;
    if (tourTimerRef.current) window.clearInterval(tourTimerRef.current);
    let index = 0;
    const steps = [0, 1, 2, 3, 4];
    chart.dispatchAction({ type: "downplay" });
    tourTimerRef.current = window.setInterval(() => {
      try {
        const dataIndex = steps[index % steps.length];
        chart.dispatchAction({ type: "downplay" });
        chart.dispatchAction({ type: "highlight", seriesIndex: 0, dataIndex });
        chart.dispatchAction({ type: "showTip", seriesIndex: 0, dataIndex });
        index += 1;
        if (index > steps.length) {
          if (tourTimerRef.current) window.clearInterval(tourTimerRef.current);
          chart.dispatchAction({ type: "downplay" });
        }
      } catch {
        if (tourTimerRef.current) window.clearInterval(tourTimerRef.current);
      }
    }, 850);
  }, [tourSignal]);

  function restoreChartView() {
    const chart = chartRef.current;
    if (!chart) return;
    chart.dispatchAction({ type: "restore" });
    chart.dispatchAction({ type: "brush", areas: [] });
    chart.dispatchAction({ type: "downplay" });
    chart.dispatchAction({ type: "hideTip" });
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const chart = chartRef.current;
    if (!chart) return;
    if (event.key.toLowerCase() === "r") {
      restoreChartView();
      event.preventDefault();
    }
    if (event.key.toLowerCase() === "s") {
      chart.dispatchAction({ type: "takeGlobalCursor", key: "brush", brushOption: { brushType: "rect", brushMode: "single" } });
      event.preventDefault();
    }
    if (event.key === "Escape") {
      chart.dispatchAction({ type: "brush", areas: [] });
      chart.dispatchAction({ type: "downplay" });
      chart.dispatchAction({ type: "hideTip" });
      event.preventDefault();
    }
  }

  if (!entry.getOption || !entry.renderer) {
    return (
      <div className="lab-empty-chart lab-empty-chart--power-studio" style={{ minHeight: height }}>
        <span>{entry.readiness}</span>
        <strong>{entry.unavailableReason ?? "This chart is registered but does not expose an ECharts option yet."}</strong>
      </div>
    );
  }

  return (
    <div
      className={chartClassName(state)}
      aria-busy={state === "loading"}
      aria-label={`${entry.title} preview`}
      data-chart-density={density}
      data-chart-family={entry.family}
      data-chart-id={entry.id}
      data-chart-has-dataset-data={visibleSeriesSummary.hasDatasetData}
      data-chart-has-series-data={visibleSeriesSummary.hasSeriesData}
      data-chart-series-count={visibleSeriesSummary.seriesCount}
      data-chart-size={size}
      data-chart-suspected-blank={visibleSeriesSummary.suspectedBlankChart}
      data-chart-visible-series-count={visibleSeriesSummary.visibleSeriesCount}
      data-polish="power-studio-v1"
      data-render-state={state}
      aria-keyshortcuts="R S Escape"
      role="img"
      style={{ minHeight: height }}
      tabIndex={0}
      onDoubleClick={restoreChartView}
      onKeyDown={handleKeyDown}
    >
      <p className="sr-only">{`${entry.title}: ${entry.operationalQuestion}`}</p>
      <div ref={rootRef} className="lab-echart__canvas" style={{ width: "100%", height }} />
      {visibleSeriesSummary.suspectedBlankChart ? (
        <div className="lab-echart__visibility-warning" aria-live="polite">
          <strong>Chart rendered, but visible data looks too faint or empty.</strong>
          <span>Check series opacity, data, or visual preset.</span>
        </div>
      ) : null}
      <div className="lab-echart__luxury-rail" aria-hidden="true"><span /><span /><span /></div>
      <div className="lab-echart__command-hints" aria-hidden="true"><span>R restore</span><span>S select</span><span>Esc clear</span></div>
      {state !== "ready" ? (
        <div className="lab-echart__state" aria-live="polite" style={{ minHeight: height, marginTop: -height }}>
          {state === "loading" ? "Loading chart..." : state === "empty" ? "No data available" : "Chart render failed"}
        </div>
      ) : null}
    </div>
  );
}
