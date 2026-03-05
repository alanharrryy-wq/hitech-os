export type KpiStyleId = "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO";

export type KpiSurfaceId = "glass" | "matte" | "graphite";

export type WidgetId =
  | "kpi.sparkline-line"
  | "kpi.sparkline-area"
  | "kpi.line-chart"
  | "kpi.area-chart"
  | "kpi.donut-breakdown"
  | "kpi.ring-gauge"
  | "kpi.radial-gauge"
  | "kpi.bullet-chart"
  | "kpi.compact-bars"
  | "kpi.heatmap-grid"
  | "kpi.waterfall-mini"
  | "kpi.mini-table"
  | "kpi.distribution-dots";

export type ChartId = WidgetId;

export type SizeVariant = "xs" | "s" | "m" | "l";

export type Density = "dense" | "normal" | "hero";

export type SemanticIntent =
  | "deal"
  | "cash"
  | "evidence"
  | "outcome"
  | "governance"
  | "risk"
  | "neutral";

export type DataShapeId =
  | "timeSeries"
  | "breakdown"
  | "matrix"
  | "gauge"
  | "tableMini"
  | "distribution"
  | "correlation";

export type PerfProfile = "quality" | "balanced" | "performance";

export type WidgetState = "ready" | "loading" | "empty";

export type Maturity = "Mature" | "NeedsLove" | "AlienTech";

export type PerfCost = "low" | "med" | "high";

export interface KpiSeries {
  readonly id: string;
  readonly label: string;
  readonly values: readonly number[];
  readonly hero?: boolean | undefined;
}

export interface KpiBreakdownDatum {
  readonly id: string;
  readonly label: string;
  readonly value: number;
  readonly intent?: SemanticIntent | undefined;
}

export interface KpiHeatmapCell {
  readonly rowId: string;
  readonly colId: string;
  readonly value: number;
}

export interface KpiMiniTableRow {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly delta?: string | undefined;
}

export interface KpiWidgetSnippet {
  readonly id: WidgetId;
  readonly usageSnippet: string;
  readonly sampleData: unknown;
}

export interface KpiChartPropsBase {
  readonly chartId: ChartId;
  readonly title: string;
  readonly subtitle?: string | undefined;
  readonly value?: string | number | undefined;
  readonly unit?: string | undefined;
  readonly note?: string | undefined;
  readonly styleId?: KpiStyleId | undefined;
  readonly surface?: KpiSurfaceId | undefined;
  readonly size?: SizeVariant | undefined;
  readonly density?: Density | undefined;
  readonly intent?: SemanticIntent | undefined;
  readonly perfProfile?: PerfProfile | undefined;
  readonly state?: WidgetState | undefined;
  readonly hero?: boolean | undefined;
  readonly heroSlot?: "primary" | "support" | undefined;
  readonly className?: string | undefined;
  readonly ariaLabel?: string | undefined;
  readonly summary?: string | undefined;
}

export interface KpiCatalogEntry {
  readonly id: WidgetId;
  readonly title: string;
  readonly description: string;
  readonly supportedStyles: readonly KpiStyleId[];
  readonly supportedSurfaces: readonly KpiSurfaceId[];
  readonly supportedDataShapes: readonly DataShapeId[];
  readonly perfCost: PerfCost;
  readonly maturity: Maturity;
  readonly defaultIntent: SemanticIntent;
  readonly wowNotes: readonly string[];
}
