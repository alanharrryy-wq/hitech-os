"use client";

import { useMemo } from "react";
import { summarizeSeries } from "../a11y/aria.js";
import { useReducedMotion } from "../motion/useReducedMotion.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type { KpiChartPropsBase, KpiSeries } from "../types.js";
import {
  CHART_HEIGHT,
  CHART_PADDING,
  CHART_WIDTH,
  KpiChartSurface,
  areaPath,
  chartClassName,
  createRenderContext,
  dashedGrid,
  linePath
} from "./common.js";

export interface MultiSeriesChartProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly series: readonly KpiSeries[];
}

export const LINE_CHART_SAMPLE: readonly KpiSeries[] = [
  {
    id: "orders",
    label: "Orders",
    hero: true,
    values: [42, 45, 47, 50, 54, 58, 57, 62]
  },
  {
    id: "returns",
    label: "Returns",
    values: [6, 7, 6, 7, 8, 9, 8, 9]
  },
  {
    id: "sla",
    label: "SLA Breach",
    values: [4, 3, 2, 3, 2, 2, 1, 2]
  }
] as const;

export const LINE_CHART_USAGE_SNIPPET = `
<LineChart
  title="Fulfillment Signals"
  intent="outcome"
  series={LINE_CHART_SAMPLE}
  note="Hero series is auto-selected from hero=true"
/>
`.trim();

export function LineChart({ series, state, ...props }: MultiSeriesChartProps) {
  const resolvedState = state ?? (series.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });
  const motion = useReducedMotion({ perfProfile: props.perfProfile });
  const context = createRenderContext(props.perfProfile ?? "balanced", motion.reducedMotion);

  const heroIndex = Math.max(
    0,
    series.findIndex((entry) => entry.hero)
  );

  const summary = props.summary ?? summarizeSeries(series);
  const gradientId = `${props.title.replace(/\s+/g, "-").toLowerCase()}-line-hero-gradient`;

  return (
    <KpiChartSurface
      chartId="kpi.line-chart"
      state={resolvedState}
      summary={summary}
      emptyMessage="No series loaded for this line chart."
      loadingMessage="Loading multi-series line chart"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <defs>
          {theme.styleId === "GRAPHITE_PRISM_ISO" ? (
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="hsl(var(--ui-accent))" />
              <stop offset="44%" stopColor="hsl(var(--ui-warning))" />
              <stop offset="100%" stopColor="hsl(var(--ui-success))" />
            </linearGradient>
          ) : null}
        </defs>

        <g>{dashedGrid(4)}</g>

        {series.map((entry, index) => {
          const stroke =
            theme.styleId === "GRAPHITE_PRISM_ISO" && index === heroIndex
              ? `url(#${gradientId})`
              : theme.styleId === "GOLD_NOIR_TERMINAL" && index === heroIndex
                ? "hsl(var(--ui-warning))"
                : theme.chart.series[index % theme.chart.series.length];

          return (
            <path
              key={entry.id}
              d={linePath(entry.values, CHART_WIDTH, CHART_HEIGHT, CHART_PADDING)}
              fill="none"
              stroke={stroke}
              strokeWidth={index === heroIndex ? 2.9 : 1.7}
              strokeOpacity={index === heroIndex ? 1 : 0.74}
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{
                transition: context.canAnimate
                  ? `stroke-opacity ${theme.fx.motionDuration} ease-out`
                  : "none"
              }}
            />
          );
        })}
      </svg>
    </KpiChartSurface>
  );
}

export const AREA_CHART_SAMPLE: readonly KpiSeries[] = [
  {
    id: "gmv",
    label: "GMV",
    hero: true,
    values: [120, 124, 132, 128, 140, 148, 151, 160]
  },
  {
    id: "cost",
    label: "Cost",
    values: [84, 82, 86, 88, 92, 93, 94, 98]
  }
] as const;

export const AREA_CHART_USAGE_SNIPPET = `
<AreaChart
  title="Revenue vs Cost"
  intent="cash"
  series={AREA_CHART_SAMPLE}
  note="Subtle fill, no aggressive gaming gradients"
/>
`.trim();

export function AreaChart({ series, state, ...props }: MultiSeriesChartProps) {
  const resolvedState = state ?? (series.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const hero = useMemo(() => series.find((entry) => entry.hero) ?? series[0], [series]);
  const summary = props.summary ?? summarizeSeries(series);
  const fillId = `${props.title.replace(/\s+/g, "-").toLowerCase()}-area-fill`;

  return (
    <KpiChartSurface
      chartId="kpi.area-chart"
      state={resolvedState}
      summary={summary}
      emptyMessage="No area series loaded."
      loadingMessage="Loading area chart"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <defs>
          <linearGradient id={fillId} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={theme.chart.heroSeries} stopOpacity={0.28} />
            <stop offset="100%" stopColor={theme.chart.heroSeries} stopOpacity={0.06} />
          </linearGradient>
        </defs>

        <g>{dashedGrid(4)}</g>

        <path d={areaPath(hero?.values ?? [], CHART_WIDTH, CHART_HEIGHT, CHART_PADDING)} fill={`url(#${fillId})`} />

        <path
          d={linePath(hero?.values ?? [], CHART_WIDTH, CHART_HEIGHT, CHART_PADDING)}
          fill="none"
          stroke={theme.styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : theme.chart.heroSeries}
          strokeWidth={2.4}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </KpiChartSurface>
  );
}
