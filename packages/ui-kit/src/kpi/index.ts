export type {
  ChartId,
  DataShapeId,
  Density,
  KpiBreakdownDatum,
  KpiCatalogEntry,
  KpiChartPropsBase,
  KpiHeatmapCell,
  KpiMiniTableRow,
  KpiSeries,
  KpiStyleId,
  KpiSurfaceId,
  KpiWidgetSnippet,
  Maturity,
  PerfCost,
  PerfProfile,
  SemanticIntent,
  SizeVariant,
  WidgetId,
  WidgetState
} from "./types.js";

export { useKpiTheme } from "./theme/useKpiTheme.js";
export type { KpiTheme, KpiThemeOptions } from "./theme/useKpiTheme.js";

export { useReducedMotion, prefersReducedMotion } from "./motion/useReducedMotion.js";
export type { ReducedMotionConfig, ReducedMotionState } from "./motion/useReducedMotion.js";

export {
  createAriaId,
  buildAriaDescribedBy,
  buildAriaLabel,
  summarizeSeries,
  summarizeBreakdown,
  summarizeMatrix
} from "./a11y/aria.js";

export { KpiWidgetFrame } from "./frame/KpiWidgetFrame.js";
export type { KpiWidgetFrameProps } from "./frame/KpiWidgetFrame.js";

export { KpiHeader } from "./frame/KpiHeader.js";
export type { KpiHeaderProps } from "./frame/KpiHeader.js";

export { KpiFooter } from "./frame/KpiFooter.js";
export type { KpiFooterProps } from "./frame/KpiFooter.js";

export {
  SparklineLine,
  SparklineArea,
  SPARKLINE_LINE_SAMPLE,
  SPARKLINE_LINE_USAGE_SNIPPET,
  SPARKLINE_AREA_SAMPLE,
  SPARKLINE_AREA_USAGE_SNIPPET
} from "./charts/sparklines.js";

export {
  LineChart,
  AreaChart,
  LINE_CHART_SAMPLE,
  LINE_CHART_USAGE_SNIPPET,
  AREA_CHART_SAMPLE,
  AREA_CHART_USAGE_SNIPPET
} from "./charts/line-area.js";

export {
  DonutBreakdown,
  RingGauge,
  RadialGauge,
  DONUT_BREAKDOWN_SAMPLE,
  DONUT_BREAKDOWN_USAGE_SNIPPET,
  RING_GAUGE_SAMPLE,
  RING_GAUGE_USAGE_SNIPPET,
  RADIAL_GAUGE_SAMPLE,
  RADIAL_GAUGE_USAGE_SNIPPET
} from "./charts/radial.js";

export {
  BulletChart,
  CompactBars,
  HeatmapGrid,
  BULLET_CHART_SAMPLE,
  BULLET_CHART_USAGE_SNIPPET,
  COMPACT_BARS_SAMPLE,
  COMPACT_BARS_USAGE_SNIPPET,
  HEATMAP_GRID_SAMPLE,
  HEATMAP_GRID_USAGE_SNIPPET
} from "./charts/bar-matrix.js";

export {
  WaterfallMini,
  MiniTableKpi,
  DistributionDots,
  WATERFALL_MINI_SAMPLE,
  WATERFALL_MINI_USAGE_SNIPPET,
  MINI_TABLE_KPI_SAMPLE,
  MINI_TABLE_KPI_USAGE_SNIPPET,
  DISTRIBUTION_DOTS_SAMPLE,
  DISTRIBUTION_DOTS_USAGE_SNIPPET
} from "./charts/finance.js";

export { KPI_WIDGET_SNIPPETS, getWidgetSnippet } from "./snippets.js";

export {
  KPI_WIDGET_CATALOG,
  getCatalogEntry,
  listCatalogWithSnippets
} from "./registry/catalog.js";

export {
  classifyMaturity,
  scoreCatalog,
  deriveCatalogMaturity
} from "./scoring/scoring.js";
export type { MaturityScore, MaturitySignal } from "./scoring/scoring.js";
