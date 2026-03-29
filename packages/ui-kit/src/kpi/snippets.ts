import {
  AREA_CHART_SAMPLE,
  AREA_CHART_USAGE_SNIPPET,
  LINE_CHART_SAMPLE,
  LINE_CHART_USAGE_SNIPPET
} from "./charts/line-area.js";
import {
  BULLET_CHART_SAMPLE,
  BULLET_CHART_USAGE_SNIPPET,
  COMPACT_BARS_SAMPLE,
  COMPACT_BARS_USAGE_SNIPPET,
  HEATMAP_GRID_SAMPLE,
  HEATMAP_GRID_USAGE_SNIPPET
} from "./charts/bar-matrix.js";
import {
  DISTRIBUTION_DOTS_SAMPLE,
  DISTRIBUTION_DOTS_USAGE_SNIPPET,
  MINI_TABLE_KPI_SAMPLE,
  MINI_TABLE_KPI_USAGE_SNIPPET,
  WATERFALL_MINI_SAMPLE,
  WATERFALL_MINI_USAGE_SNIPPET
} from "./charts/finance.js";
import {
  DONUT_BREAKDOWN_SAMPLE,
  DONUT_BREAKDOWN_USAGE_SNIPPET,
  RADIAL_GAUGE_SAMPLE,
  RADIAL_GAUGE_USAGE_SNIPPET,
  RING_GAUGE_SAMPLE,
  RING_GAUGE_USAGE_SNIPPET
} from "./charts/radial.js";
import {
  SPARKLINE_AREA_SAMPLE,
  SPARKLINE_AREA_USAGE_SNIPPET,
  SPARKLINE_LINE_SAMPLE,
  SPARKLINE_LINE_USAGE_SNIPPET
} from "./charts/sparklines.js";
import type { ChartId, KpiWidgetSnippet } from "./types.js";

export const KPI_WIDGET_SNIPPETS: readonly KpiWidgetSnippet[] = [
  {
    id: "kpi.sparkline-line",
    usageSnippet: SPARKLINE_LINE_USAGE_SNIPPET,
    sampleData: SPARKLINE_LINE_SAMPLE
  },
  {
    id: "kpi.sparkline-area",
    usageSnippet: SPARKLINE_AREA_USAGE_SNIPPET,
    sampleData: SPARKLINE_AREA_SAMPLE
  },
  {
    id: "kpi.line-chart",
    usageSnippet: LINE_CHART_USAGE_SNIPPET,
    sampleData: LINE_CHART_SAMPLE
  },
  {
    id: "kpi.area-chart",
    usageSnippet: AREA_CHART_USAGE_SNIPPET,
    sampleData: AREA_CHART_SAMPLE
  },
  {
    id: "kpi.donut-breakdown",
    usageSnippet: DONUT_BREAKDOWN_USAGE_SNIPPET,
    sampleData: DONUT_BREAKDOWN_SAMPLE
  },
  {
    id: "kpi.ring-gauge",
    usageSnippet: RING_GAUGE_USAGE_SNIPPET,
    sampleData: RING_GAUGE_SAMPLE
  },
  {
    id: "kpi.radial-gauge",
    usageSnippet: RADIAL_GAUGE_USAGE_SNIPPET,
    sampleData: RADIAL_GAUGE_SAMPLE
  },
  {
    id: "kpi.bullet-chart",
    usageSnippet: BULLET_CHART_USAGE_SNIPPET,
    sampleData: BULLET_CHART_SAMPLE
  },
  {
    id: "kpi.compact-bars",
    usageSnippet: COMPACT_BARS_USAGE_SNIPPET,
    sampleData: COMPACT_BARS_SAMPLE
  },
  {
    id: "kpi.heatmap-grid",
    usageSnippet: HEATMAP_GRID_USAGE_SNIPPET,
    sampleData: HEATMAP_GRID_SAMPLE
  },
  {
    id: "kpi.waterfall-mini",
    usageSnippet: WATERFALL_MINI_USAGE_SNIPPET,
    sampleData: WATERFALL_MINI_SAMPLE
  },
  {
    id: "kpi.mini-table",
    usageSnippet: MINI_TABLE_KPI_USAGE_SNIPPET,
    sampleData: MINI_TABLE_KPI_SAMPLE
  },
  {
    id: "kpi.distribution-dots",
    usageSnippet: DISTRIBUTION_DOTS_USAGE_SNIPPET,
    sampleData: DISTRIBUTION_DOTS_SAMPLE
  }
] as const;

export function getWidgetSnippet(id: ChartId): KpiWidgetSnippet | undefined {
  return KPI_WIDGET_SNIPPETS.find((entry) => entry.id === id);
}
