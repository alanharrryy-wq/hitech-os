"use client";

import { useMemo } from "react";
import { summarizeBreakdown } from "../a11y/aria.js";
import { useReducedMotion } from "../motion/useReducedMotion.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type { KpiBreakdownDatum, KpiChartPropsBase } from "../types.js";
import {
  CHART_HEIGHT,
  CHART_WIDTH,
  KpiChartSurface,
  arcPath,
  chartClassName,
  clamp,
  createRenderContext,
  formatCompact,
  sum
} from "./common.js";

export interface DonutBreakdownProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly segments: readonly KpiBreakdownDatum[];
}

export const DONUT_BREAKDOWN_SAMPLE: readonly KpiBreakdownDatum[] = [
  { id: "prime", label: "Prime", value: 42, intent: "deal" },
  { id: "enterprise", label: "Enterprise", value: 30, intent: "cash" },
  { id: "pilot", label: "Pilot", value: 16, intent: "evidence" },
  { id: "longtail", label: "Long Tail", value: 12, intent: "outcome" }
] as const;

export const DONUT_BREAKDOWN_USAGE_SNIPPET = `
<DonutBreakdown
  title="Segment Mix"
  intent="deal"
  segments={DONUT_BREAKDOWN_SAMPLE}
  note="Donut enforces max 4 segments"
/>
`.trim();

export function DonutBreakdown({ segments, state, ...props }: DonutBreakdownProps) {
  const limited = useMemo(() => segments.slice(0, 4), [segments]);
  const resolvedState = state ?? (limited.length > 0 ? "ready" : "empty");
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

  const total = sum(limited.map((segment) => segment.value));
  const summary = props.summary ?? summarizeBreakdown(limited);

  let cursor = -Math.PI / 2;
  const radius = 56;
  const centerX = CHART_WIDTH / 2;
  const centerY = CHART_HEIGHT / 2;

  return (
    <KpiChartSurface
      chartId="kpi.donut-breakdown"
      state={resolvedState}
      summary={summary}
      emptyMessage="No segment values to render."
      loadingMessage="Loading donut breakdown"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <circle cx={centerX} cy={centerY} r={radius} fill="none" stroke={theme.chart.grid} strokeWidth={18} />

        {limited.map((segment, index) => {
          const ratio = total > 0 ? segment.value / total : 0;
          const angle = ratio * Math.PI * 2;
          const start = cursor;
          const end = cursor + angle;
          cursor += angle;

          const path = arcPath(centerX, centerY, radius, start, end);
          const stroke =
            theme.styleId === "GOLD_NOIR_TERMINAL" && index === 0
              ? "hsl(var(--ui-warning))"
              : theme.chart.series[index % theme.chart.series.length];

          return <path key={segment.id} d={path} fill="none" stroke={stroke} strokeWidth={18} strokeLinecap="round" />;
        })}

        <text
          x={centerX}
          y={centerY - 2}
          textAnchor="middle"
          style={{ fill: theme.text.primary, fontSize: "1.05rem", fontWeight: 650, fontVariantNumeric: "tabular-nums" }}
        >
          {formatCompact(total)}
        </text>
        <text x={centerX} y={centerY + 15} textAnchor="middle" style={{ fill: theme.text.muted, fontSize: "0.68rem" }}>
          total
        </text>
      </svg>

      <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
        {limited.map((segment, index) => (
          <div key={segment.id} className="flex items-center gap-2" style={{ color: theme.text.secondary }}>
            <span
              aria-hidden="true"
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: theme.chart.series[index % theme.chart.series.length] }}
            />
            <span className="truncate">{segment.label}</span>
          </div>
        ))}
      </div>

      {context.canAnimate ? null : null}
    </KpiChartSurface>
  );
}

export interface GaugeProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly value: number;
  readonly min?: number;
  readonly max?: number;
  readonly threshold?: number;
}

export const RING_GAUGE_SAMPLE = {
  value: 78,
  min: 0,
  max: 100,
  threshold: 82
} as const;

export const RING_GAUGE_USAGE_SNIPPET = `
<RingGauge
  title="Conversion Goal"
  intent="outcome"
  density="hero"
  hero
  heroSlot="primary"
  value={78}
  min={0}
  max={100}
  threshold={82}
/>
`.trim();

export function RingGauge({ value, min = 0, max = 100, threshold, state, ...props }: GaugeProps) {
  const resolvedState = state ?? "ready";
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const normalized = clamp((value - min) / Math.max(max - min, 1e-9), 0, 1);
  const circumference = 2 * Math.PI * 58;
  const dashOffset = circumference * (1 - normalized);

  return (
    <KpiChartSurface
      chartId="kpi.ring-gauge"
      state={resolvedState}
      value={value.toFixed(0)}
      unit="%"
      summary={props.summary ?? `Gauge value ${value.toFixed(1)} between ${min} and ${max}.`}
      loadingMessage="Loading ring gauge"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <circle cx="180" cy="90" r="58" fill="none" stroke={theme.chart.grid} strokeWidth="14" />
        <circle
          cx="180"
          cy="90"
          r="58"
          fill="none"
          stroke={theme.styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : theme.chart.heroSeries}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          transform="rotate(-90 180 90)"
        />

        {threshold !== undefined ? (
          <line
            x1="180"
            y1="27"
            x2="180"
            y2="41"
            stroke={theme.chart.caution}
            strokeWidth={2}
            transform={`rotate(${((threshold - min) / Math.max(max - min, 1e-9)) * 360 - 90} 180 90)`}
          />
        ) : null}
      </svg>
    </KpiChartSurface>
  );
}

export const RADIAL_GAUGE_SAMPLE = {
  value: 64,
  min: 0,
  max: 100,
  threshold: 70
} as const;

export const RADIAL_GAUGE_USAGE_SNIPPET = `
<RadialGauge
  title="Governance Score"
  intent="governance"
  value={64}
  min={0}
  max={100}
  threshold={70}
/>
`.trim();

export function RadialGauge({ value, min = 0, max = 100, threshold, state, ...props }: GaugeProps) {
  const resolvedState = state ?? "ready";
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const ratio = clamp((value - min) / Math.max(max - min, 1e-9), 0, 1);
  const start = Math.PI * 0.75;
  const end = Math.PI * 2.25;
  const current = start + (end - start) * ratio;

  const baseArc = arcPath(CHART_WIDTH / 2, CHART_HEIGHT * 0.74, 72, start, end);
  const valueArc = arcPath(CHART_WIDTH / 2, CHART_HEIGHT * 0.74, 72, start, current);

  const thresholdRatio = threshold === undefined ? null : clamp((threshold - min) / Math.max(max - min, 1e-9), 0, 1);
  const thresholdAngle = thresholdRatio === null ? null : start + (end - start) * thresholdRatio;

  return (
    <KpiChartSurface
      chartId="kpi.radial-gauge"
      state={resolvedState}
      value={value.toFixed(0)}
      unit="pts"
      summary={props.summary ?? `Radial gauge value ${value.toFixed(0)} of ${max}.`}
      loadingMessage="Loading radial gauge"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <path d={baseArc} fill="none" stroke={theme.chart.grid} strokeWidth={16} strokeLinecap="round" />
        <path
          d={valueArc}
          fill="none"
          stroke={theme.styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : theme.chart.heroSeries}
          strokeWidth={16}
          strokeLinecap="round"
        />

        {thresholdAngle !== null ? (
          <line
            x1={CHART_WIDTH / 2}
            y1={CHART_HEIGHT * 0.74}
            x2={CHART_WIDTH / 2 + Math.cos(thresholdAngle) * 84}
            y2={CHART_HEIGHT * 0.74 + Math.sin(thresholdAngle) * 84}
            stroke={theme.chart.caution}
            strokeWidth={2}
            strokeDasharray="3 4"
          />
        ) : null}
      </svg>
    </KpiChartSurface>
  );
}
