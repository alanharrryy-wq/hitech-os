"use client";

import { summarizeSeries } from "../a11y/aria.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type {
  KpiChartPropsBase,
  KpiMiniTableRow,
  KpiSeries
} from "../types.js";
import {
  CHART_HEIGHT,
  CHART_PADDING,
  CHART_WIDTH,
  KpiChartSurface,
  chartClassName,
  extent,
  xScale,
  yScale
} from "./common.js";

export interface WaterfallStep {
  readonly id: string;
  readonly label: string;
  readonly delta: number;
}

export interface WaterfallMiniProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly steps: readonly WaterfallStep[];
  readonly openingValue?: number;
}

export const WATERFALL_MINI_SAMPLE = {
  openingValue: 420,
  steps: [
    { id: "rev", label: "Revenue", delta: 240 },
    { id: "cost", label: "Cost", delta: -154 },
    { id: "rebate", label: "Rebates", delta: -18 },
    { id: "upsell", label: "Upsell", delta: 46 }
  ]
} as const;

export const WATERFALL_MINI_USAGE_SNIPPET = `
<WaterfallMini
  title="Margin Bridge"
  intent="cash"
  openingValue={420}
  steps={WATERFALL_MINI_SAMPLE.steps}
/>
`.trim();

export function WaterfallMini({ steps, openingValue = 0, state, className, ...props }: WaterfallMiniProps) {
  const resolvedState = state ?? (steps.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  let running = openingValue;
  const cumulative = [openingValue, ...steps.map((step) => {
    running += step.delta;
    return running;
  })];

  const values = [...cumulative, openingValue];
  const { min, max } = extent(values);
  const closingValue = cumulative[cumulative.length - 1] ?? openingValue;

  return (
    <KpiChartSurface
      chartId="kpi.waterfall-mini"
      state={resolvedState}
      summary={
        props.summary ??
        `Waterfall with ${steps.length} steps. Opening ${openingValue.toFixed(0)}, closing ${closingValue.toFixed(0)}.`
      }
      emptyMessage="No waterfall steps available."
      loadingMessage="Loading waterfall chart"
      {...props}
      className={className ?? ""}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        {steps.map((step, index) => {
          const prior = cumulative[index] ?? openingValue;
          const next = cumulative[index + 1] ?? prior;
          const x = CHART_PADDING + index * ((CHART_WIDTH - CHART_PADDING * 2) / Math.max(steps.length, 1));
          const width = Math.max((CHART_WIDTH - CHART_PADDING * 2) / Math.max(steps.length, 1) - 10, 8);
          const yTop = yScale(Math.max(prior, next), min, max, CHART_HEIGHT, CHART_PADDING);
          const yBottom = yScale(Math.min(prior, next), min, max, CHART_HEIGHT, CHART_PADDING);

          return (
            <g key={step.id}>
              <rect
                x={x + 4}
                y={yTop}
                width={width}
                height={Math.max(yBottom - yTop, 3)}
                rx={4}
                fill={
                  step.delta >= 0
                    ? theme.styleId === "GOLD_NOIR_TERMINAL"
                      ? "hsl(var(--ui-warning))"
                      : theme.chart.positive
                    : theme.chart.negative
                }
                opacity={0.84}
              />
              <text
                x={x + width / 2 + 4}
                y={CHART_HEIGHT - 6}
                textAnchor="middle"
                style={{ fill: theme.text.muted, fontSize: "0.6rem" }}
              >
                {step.label}
              </text>
            </g>
          );
        })}
      </svg>
    </KpiChartSurface>
  );
}

export interface MiniTableKpiProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly rows: readonly KpiMiniTableRow[];
}

export const MINI_TABLE_KPI_SAMPLE: readonly KpiMiniTableRow[] = [
  { id: "ap", label: "Accounts Payable", value: "$142k", delta: "+4.2%" },
  { id: "ar", label: "Accounts Receivable", value: "$188k", delta: "-1.1%" },
  { id: "cash", label: "Cash Buffer", value: "$96k", delta: "+2.8%" }
] as const;

export const MINI_TABLE_KPI_USAGE_SNIPPET = `
<MiniTableKpi
  title="Ledger Snapshot"
  intent="governance"
  rows={MINI_TABLE_KPI_SAMPLE}
/>
`.trim();

export function MiniTableKpi({ rows, state, className, ...props }: MiniTableKpiProps) {
  const resolvedState = state ?? (rows.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  return (
    <KpiChartSurface
      chartId="kpi.mini-table"
      state={resolvedState}
      summary={props.summary ?? `Mini ledger with ${rows.length} rows.`}
      emptyMessage="No ledger rows available."
      loadingMessage="Loading mini ledger table"
      {...props}
      className={className ?? ""}
    >
      <table className="w-full border-collapse text-sm" role="table" aria-label={`${props.title} ledger`}>
        <thead>
          <tr>
            <th
              className="pb-2 text-left text-[0.67rem] uppercase"
              style={{ color: theme.text.muted, letterSpacing: "0.08em" }}
            >
              Account
            </th>
            <th
              className="pb-2 text-right text-[0.67rem] uppercase"
              style={{ color: theme.text.muted, letterSpacing: "0.08em" }}
            >
              Value
            </th>
            <th
              className="pb-2 text-right text-[0.67rem] uppercase"
              style={{ color: theme.text.muted, letterSpacing: "0.08em" }}
            >
              Delta
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td className="py-1.5" style={{ color: theme.text.secondary }}>
                {row.label}
              </td>
              <td
                className="py-1.5 text-right"
                style={{ color: theme.text.primary, fontVariantNumeric: "tabular-nums" }}
              >
                {row.value}
              </td>
              <td
                className="py-1.5 text-right"
                style={{
                  color: row.delta?.startsWith("-") ? theme.chart.negative : theme.chart.positive,
                  fontVariantNumeric: "tabular-nums"
                }}
              >
                {row.delta ?? "--"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </KpiChartSurface>
  );
}

export interface DistributionDotsProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly points: ReadonlyArray<{ id: string; x: number; y: number }>;
  readonly enabled?: boolean;
}

export const DISTRIBUTION_DOTS_SAMPLE = [
  { id: "d1", x: 1.2, y: 12 },
  { id: "d2", x: 1.8, y: 16 },
  { id: "d3", x: 2.1, y: 15 },
  { id: "d4", x: 2.8, y: 19 },
  { id: "d5", x: 3.2, y: 21 }
] as const;

export const DISTRIBUTION_DOTS_USAGE_SNIPPET = `
<DistributionDots
  title="Latency Distribution"
  intent="risk"
  enabled={false}
  points={DISTRIBUTION_DOTS_SAMPLE}
/>
`.trim();

export function DistributionDots({ points, enabled = false, state, className, ...props }: DistributionDotsProps) {
  const resolvedState = state ?? (enabled && points.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  if (!enabled) {
    return (
      <KpiChartSurface
        chartId="kpi.distribution-dots"
        state="empty"
        summary={props.summary ?? "Distribution Dots is intentionally gated off by default."}
        emptyMessage="Alien Tech mode is off. Enable explicitly to render this widget."
        {...props}
        className={className ?? ""}
      />
    );
  }

  const yExtent = extent(points.map((point) => point.y));

  return (
    <KpiChartSurface
      chartId="kpi.distribution-dots"
      state={resolvedState}
      summary={
        props.summary ??
        summarizeSeries([
          {
            id: "distribution",
            label: props.title,
            values: points.map((point) => point.y),
            hero: true
          }
        ] satisfies readonly KpiSeries[])
      }
      loadingMessage="Loading distribution dots"
      emptyMessage="No distribution samples available."
      {...props}
      className={className ?? ""}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <line
          x1={CHART_PADDING}
          x2={CHART_WIDTH - CHART_PADDING}
          y1={CHART_HEIGHT - CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke={theme.chart.grid}
          strokeWidth={1}
        />
        <line
          x1={CHART_PADDING}
          x2={CHART_PADDING}
          y1={CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke={theme.chart.grid}
          strokeWidth={1}
        />

        {points.map((point, index) => (
          <circle
            key={point.id}
            cx={xScale(index, points.length, CHART_WIDTH, CHART_PADDING)}
            cy={yScale(point.y, yExtent.min, yExtent.max, CHART_HEIGHT, CHART_PADDING)}
            r={3.2}
            fill={theme.chart.series[index % theme.chart.series.length]}
          />
        ))}
      </svg>
    </KpiChartSurface>
  );
}
