"use client";

import { summarizeMatrix } from "../a11y/aria.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type {
  KpiChartPropsBase,
  KpiHeatmapCell
} from "../types.js";
import {
  CHART_HEIGHT,
  CHART_PADDING,
  CHART_WIDTH,
  KpiChartSurface,
  chartClassName,
  clamp,
  extent,
  formatCompact
} from "./common.js";

export interface BulletChartProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly actual: number;
  readonly target: number;
  readonly min?: number;
  readonly max?: number;
}

export const BULLET_CHART_SAMPLE = {
  actual: 74,
  target: 82,
  min: 0,
  max: 100
} as const;

export const BULLET_CHART_USAGE_SNIPPET = `
<BulletChart
  title="Target vs Actual"
  intent="governance"
  actual={74}
  target={82}
  min={0}
  max={100}
/>
`.trim();

export function BulletChart({ actual, target, min = 0, max = 100, state, ...props }: BulletChartProps) {
  const resolvedState = state ?? "ready";
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const span = Math.max(max - min, 1e-9);
  const actualRatio = clamp((actual - min) / span, 0, 1);
  const targetRatio = clamp((target - min) / span, 0, 1);
  const baselineX = CHART_PADDING;
  const baselineWidth = CHART_WIDTH - CHART_PADDING * 2;

  return (
    <KpiChartSurface
      chartId="kpi.bullet-chart"
      state={resolvedState}
      value={actual.toFixed(0)}
      summary={props.summary ?? `Actual ${actual.toFixed(1)} against target ${target.toFixed(1)}.`}
      loadingMessage="Loading bullet chart"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        <rect
          x={baselineX}
          y={72}
          width={baselineWidth}
          height={28}
          rx={8}
          fill="hsl(var(--ui-surface-2))"
          stroke={theme.chart.grid}
        />

        <rect
          x={baselineX}
          y={78}
          width={baselineWidth * actualRatio}
          height={16}
          rx={6}
          fill={theme.styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : theme.chart.heroSeries}
        />

        <line
          x1={baselineX + baselineWidth * targetRatio}
          x2={baselineX + baselineWidth * targetRatio}
          y1={66}
          y2={106}
          stroke={theme.chart.caution}
          strokeWidth={3}
        />

        <text x={baselineX} y={126} style={{ fill: theme.text.muted, fontSize: "0.72rem" }}>
          min {min}
        </text>
        <text
          x={CHART_WIDTH - CHART_PADDING}
          y={126}
          textAnchor="end"
          style={{ fill: theme.text.muted, fontSize: "0.72rem" }}
        >
          max {max}
        </text>
      </svg>
    </KpiChartSurface>
  );
}

export interface CompactBarsProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly items: ReadonlyArray<{ id: string; label: string; value: number }>;
}

export const COMPACT_BARS_SAMPLE = [
  { id: "north", label: "North", value: 132 },
  { id: "south", label: "South", value: 108 },
  { id: "west", label: "West", value: 124 },
  { id: "east", label: "East", value: 97 }
] as const;

export const COMPACT_BARS_USAGE_SNIPPET = `
<CompactBars
  title="Regional Throughput"
  intent="evidence"
  items={COMPACT_BARS_SAMPLE}
/>
`.trim();

export function CompactBars({ items, state, ...props }: CompactBarsProps) {
  const resolvedState = state ?? (items.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const values = items.map((item) => item.value);
  const max = Math.max(...values, 1);
  const barHeight = (CHART_HEIGHT - CHART_PADDING * 2) / Math.max(items.length, 1);

  return (
    <KpiChartSurface
      chartId="kpi.compact-bars"
      state={resolvedState}
      summary={props.summary ?? `${items.length} compact bar multiples with top value ${formatCompact(max)}.`}
      emptyMessage="No bar groups available."
      loadingMessage="Loading compact bars"
      {...props}
    >
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-hidden="true" className={chartClassName()}>
        {items.map((item, index) => {
          const y = CHART_PADDING + index * barHeight + 4;
          const width = ((CHART_WIDTH - CHART_PADDING * 2) * item.value) / max;
          return (
            <g key={item.id}>
              <rect
                x={CHART_PADDING}
                y={y}
                width={width}
                height={Math.max(barHeight - 8, 8)}
                rx={4}
                fill={theme.chart.series[index % theme.chart.series.length]}
                opacity={0.82}
              />
              <text
                x={CHART_PADDING + 4}
                y={y + Math.max(barHeight - 8, 8) / 2 + 4}
                style={{ fill: theme.text.primary, fontSize: "0.65rem", fontWeight: 600 }}
              >
                {item.label}
              </text>
              <text
                x={CHART_WIDTH - CHART_PADDING}
                y={y + Math.max(barHeight - 8, 8) / 2 + 4}
                textAnchor="end"
                style={{ fill: theme.text.muted, fontSize: "0.65rem", fontVariantNumeric: "tabular-nums" }}
              >
                {item.value.toFixed(0)}
              </text>
            </g>
          );
        })}
      </svg>
    </KpiChartSurface>
  );
}

export interface HeatmapGridProps extends Omit<KpiChartPropsBase, "chartId"> {
  readonly rowLabels: readonly string[];
  readonly colLabels: readonly string[];
  readonly cells: readonly KpiHeatmapCell[];
}

export const HEATMAP_GRID_SAMPLE = {
  rowLabels: ["A", "B", "C"],
  colLabels: ["Mon", "Tue", "Wed", "Thu"],
  cells: [
    { rowId: "A", colId: "Mon", value: 12 },
    { rowId: "A", colId: "Tue", value: 16 },
    { rowId: "A", colId: "Wed", value: 9 },
    { rowId: "A", colId: "Thu", value: 22 },
    { rowId: "B", colId: "Mon", value: 8 },
    { rowId: "B", colId: "Tue", value: 14 },
    { rowId: "B", colId: "Wed", value: 11 },
    { rowId: "B", colId: "Thu", value: 18 },
    { rowId: "C", colId: "Mon", value: 10 },
    { rowId: "C", colId: "Tue", value: 13 },
    { rowId: "C", colId: "Wed", value: 7 },
    { rowId: "C", colId: "Thu", value: 15 }
  ]
} as const;

export const HEATMAP_GRID_USAGE_SNIPPET = `
<HeatmapGrid
  title="Matrix Load"
  intent="risk"
  rowLabels={HEATMAP_GRID_SAMPLE.rowLabels}
  colLabels={HEATMAP_GRID_SAMPLE.colLabels}
  cells={HEATMAP_GRID_SAMPLE.cells}
/>
`.trim();

export function HeatmapGrid({ rowLabels, colLabels, cells, state, ...props }: HeatmapGridProps) {
  const resolvedState = state ?? (cells.length > 0 ? "ready" : "empty");
  const theme = useKpiTheme({
    styleId: props.styleId,
    surface: props.surface,
    intent: props.intent,
    perfProfile: props.perfProfile,
    size: props.size,
    density: props.density
  });

  const values = cells.map((cell) => cell.value);
  const { min, max } = extent(values);

  const contentWidth = CHART_WIDTH - CHART_PADDING * 2;
  const contentHeight = CHART_HEIGHT - CHART_PADDING * 2;
  const cellWidth = contentWidth / Math.max(colLabels.length, 1);
  const cellHeight = contentHeight / Math.max(rowLabels.length, 1);

  const summary =
    props.summary ??
    summarizeMatrix({
      cells,
      rowLabels,
      colLabels
    });

  return (
    <KpiChartSurface
      chartId="kpi.heatmap-grid"
      state={resolvedState}
      summary={summary}
      emptyMessage="No matrix entries to visualize."
      loadingMessage="Loading heatmap grid"
      {...props}
    >
      <svg
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        role="img"
        aria-hidden="true"
        className={chartClassName()}
      >
        {rowLabels.map((rowLabel, rowIndex) =>
          colLabels.map((colLabel, colIndex) => {
            const cell = cells.find((entry) => entry.rowId === rowLabel && entry.colId === colLabel);
            const value = cell?.value ?? 0;
            const ratio = clamp((value - min) / Math.max(max - min, 1e-9), 0, 1);
            const x = CHART_PADDING + colIndex * cellWidth;
            const y = CHART_PADDING + rowIndex * cellHeight;

            return (
              <rect
                key={`${rowLabel}:${colLabel}`}
                x={x + 1}
                y={y + 1}
                width={Math.max(cellWidth - 2, 2)}
                height={Math.max(cellHeight - 2, 2)}
                rx={3}
                fill={theme.styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : theme.chart.heroSeries}
                opacity={0.16 + ratio * 0.74}
              >
                <title>{`${rowLabel} / ${colLabel}: ${value.toFixed(2)}`}</title>
              </rect>
            );
          })
        )}

        {rowLabels.map((rowLabel, rowIndex) => (
          <text
            key={`row-${rowLabel}`}
            x={4}
            y={CHART_PADDING + rowIndex * cellHeight + cellHeight / 2 + 4}
            style={{ fill: theme.text.muted, fontSize: "0.62rem" }}
          >
            {rowLabel}
          </text>
        ))}

        {colLabels.map((colLabel, colIndex) => (
          <text
            key={`col-${colLabel}`}
            x={CHART_PADDING + colIndex * cellWidth + cellWidth / 2}
            y={CHART_HEIGHT - 4}
            textAnchor="middle"
            style={{ fill: theme.text.muted, fontSize: "0.62rem" }}
          >
            {colLabel}
          </text>
        ))}
      </svg>
    </KpiChartSurface>
  );
}
