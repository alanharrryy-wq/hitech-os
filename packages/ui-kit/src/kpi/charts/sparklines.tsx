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
  chartClassName,
  createRenderContext,
  extent,
  linePath,
  xScale,
  yScale
} from "./common.js";

export interface SparklineProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly data: readonly number[];
}

export const SPARKLINE_LINE_SAMPLE = [23, 24, 22, 27, 29, 33, 31, 36] as const;

export const SPARKLINE_LINE_USAGE_SNIPPET = `
<SparklineLine
  title="Fulfillment Rate"
  value="96.3"
  unit="%"
  intent="outcome"
  data={[23, 24, 22, 27, 29, 33, 31, 36]}
/>
`.trim();

export function SparklineLine({ data, state, className, ...props }: SparklineProps) {
  const resolvedState = state ?? (data.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });
  const motion = useReducedMotion({ perfProfile: props.perfProfile });
  const ctx = createRenderContext(props.perfProfile ?? "balanced", motion.reducedMotion);

  const path = useMemo(() => linePath(data, CHART_WIDTH, CHART_HEIGHT, CHART_PADDING), [data]);
  const points = data.filter((value) => Number.isFinite(value));
  const { min, max } = extent(points);
  const lastIndex = Math.max(points.length - 1, 0);
  const lastPoint = points[lastIndex];

  const summary =
    props.summary ??
    summarizeSeries([
      {
        id: "sparkline-line",
        label: props.title,
        values: data,
        hero: true
      }
    ] satisfies readonly KpiSeries[]);

  const gradientId = `${props.title.replace(/\s+/g, "-").toLowerCase()}-sparkline-gradient`;

  return (
    <KpiChartSurface
      chartId="kpi.sparkline-line"
      state={resolvedState}
      summary={summary}
      emptyMessage="No trend samples for this sparkline."
      loadingMessage="Loading sparkline"
      {...props}
      className={className ?? ""}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <defs>
          {theme.styleId === "GRAPHITE_PRISM_ISO" ? (
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="hsl(var(--ui-accent))" />
              <stop offset="45%" stopColor="hsl(var(--ui-warning))" />
              <stop offset="100%" stopColor="hsl(var(--ui-success))" />
            </linearGradient>
          ) : null}
        </defs>

        <line
          x1={CHART_PADDING}
          x2={CHART_WIDTH - CHART_PADDING}
          y1={CHART_HEIGHT - CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke={theme.chart.grid}
          strokeWidth={1}
        />

        <path
          d={path}
          fill="none"
          stroke={theme.styleId === "GRAPHITE_PRISM_ISO" ? `url(#${gradientId})` : theme.chart.heroSeries}
          strokeWidth={theme.styleId === "GOLD_NOIR_TERMINAL" ? 2 : 2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            transition: ctx.canAnimate ? `stroke-dashoffset ${theme.fx.motionDuration} ease-out` : "none"
          }}
        />

        {points.length > 0 && lastPoint !== undefined ? (
          <circle
            cx={xScale(lastIndex, points.length, CHART_WIDTH, CHART_PADDING)}
            cy={yScale(lastPoint, min, max, CHART_HEIGHT, CHART_PADDING)}
            r={3}
            fill={theme.styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : theme.chart.heroSeries}
          />
        ) : null}
      </svg>
    </KpiChartSurface>
  );
}

export const SPARKLINE_AREA_SAMPLE = [18, 19, 21, 20, 25, 26, 24, 28] as const;

export const SPARKLINE_AREA_USAGE_SNIPPET = `
<SparklineArea
  title="Cash Velocity"
  value="1.24"
  unit="x"
  intent="cash"
  data={[18, 19, 21, 20, 25, 26, 24, 28]}
/>
`.trim();

export function SparklineArea({ data, state, className, ...props }: SparklineProps) {
  const resolvedState = state ?? (data.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const line = useMemo(() => linePath(data, CHART_WIDTH, CHART_HEIGHT, CHART_PADDING), [data]);
  const area = useMemo(() => {
    const values = data.filter((value) => Number.isFinite(value));
    if (values.length === 0) {
      return "";
    }

    const { min, max } = extent(values);
    const topPath = values
      .map((value, index) => {
        const x = xScale(index, values.length, CHART_WIDTH, CHART_PADDING);
        const y = yScale(value, min, max, CHART_HEIGHT, CHART_PADDING);
        return `${index === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`;
      })
      .join(" ");

    const lastX = xScale(values.length - 1, values.length, CHART_WIDTH, CHART_PADDING);
    const firstX = xScale(0, values.length, CHART_WIDTH, CHART_PADDING);
    const baseline = CHART_HEIGHT - CHART_PADDING;

    return `${topPath} L ${lastX.toFixed(2)} ${baseline.toFixed(2)} L ${firstX.toFixed(2)} ${baseline.toFixed(2)} Z`;
  }, [data]);

  const summary =
    props.summary ??
    summarizeSeries([
      {
        id: "sparkline-area",
        label: props.title,
        values: data,
        hero: true
      }
    ] satisfies readonly KpiSeries[]);

  const gradientId = `${props.title.replace(/\s+/g, "-").toLowerCase()}-spark-area-fill`;

  return (
    <KpiChartSurface
      chartId="kpi.sparkline-area"
      state={resolvedState}
      summary={summary}
      emptyMessage="No area trend samples for this widget."
      loadingMessage="Loading area sparkline"
      {...props}
      className={className ?? ""}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={theme.chart.heroSeries} stopOpacity={0.34} />
            <stop offset="100%" stopColor={theme.chart.heroSeries} stopOpacity={0.06} />
          </linearGradient>
        </defs>

        <line
          x1={CHART_PADDING}
          x2={CHART_WIDTH - CHART_PADDING}
          y1={CHART_HEIGHT - CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke={theme.chart.grid}
          strokeWidth={1}
        />

        <path d={area} fill={`url(#${gradientId})`} />
        <path d={line} fill="none" stroke={theme.chart.heroSeries} strokeWidth={2.2} strokeLinecap="round" />
      </svg>
    </KpiChartSurface>
  );
}
