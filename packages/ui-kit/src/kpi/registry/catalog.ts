import { KPI_WIDGET_SNIPPETS, getWidgetSnippet } from "../snippets.js";
import type { ChartId, KpiCatalogEntry, KpiWidgetSnippet } from "../types.js";

export interface CatalogEntry extends KpiCatalogEntry {
  readonly snippet?: KpiWidgetSnippet | undefined;
}

const BASE_STYLES = ["LIQUID_GLASS", "GOLD_NOIR_TERMINAL", "GRAPHITE_PRISM_ISO"] as const;
const BASE_SURFACES = ["glass", "matte", "graphite"] as const;

const BASE_CATALOG: readonly CatalogEntry[] = [
  {
    id: "kpi.sparkline-line",
    title: "Sparkline Line",
    description: "Micro trend line for compact KPI cards.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["timeSeries"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "outcome",
    wowNotes: ["Minimal footprint", "Hero-friendly line tension"]
  },
  {
    id: "kpi.sparkline-area",
    title: "Sparkline Area",
    description: "Micro area trend with restrained fill.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["timeSeries"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "cash",
    wowNotes: ["Subtle density read", "Premium low-noise shading"]
  },
  {
    id: "kpi.line-chart",
    title: "Line Chart",
    description: "Signature multi-series line chart with one hero series.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["timeSeries", "correlation"],
    perfCost: "med",
    maturity: "Mature",
    defaultIntent: "evidence",
    wowNotes: ["One hero, many supporters", "Readable in dense dashboards"]
  },
  {
    id: "kpi.area-chart",
    title: "Area Chart",
    description: "Area-over-line chart with conservative fill opacity.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["timeSeries"],
    perfCost: "med",
    maturity: "Mature",
    defaultIntent: "cash",
    wowNotes: ["No gamer gradients", "CFO-ready story density"]
  },
  {
    id: "kpi.donut-breakdown",
    title: "Donut Breakdown",
    description: "Segment mix visual with strict four-segment cap.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["breakdown"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "deal",
    wowNotes: ["Segment cap protects readability", "Center total stays calm"]
  },
  {
    id: "kpi.ring-gauge",
    title: "Ring Gauge",
    description: "Hero-capable ring progress gauge.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["gauge"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "outcome",
    wowNotes: ["One-hero budget aware", "Threshold tick discipline"]
  },
  {
    id: "kpi.radial-gauge",
    title: "Radial Gauge",
    description: "Semi-circular radial gauge for score telemetry.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["gauge"],
    perfCost: "med",
    maturity: "Mature",
    defaultIntent: "governance",
    wowNotes: ["Dashboard hero candidate", "Readable threshold overlays"]
  },
  {
    id: "kpi.bullet-chart",
    title: "Bullet Chart",
    description: "Target vs actual comparison with immediate benchmarking.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["gauge", "timeSeries"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "governance",
    wowNotes: ["Fast comparative cognition", "No decorative overhead"]
  },
  {
    id: "kpi.compact-bars",
    title: "Compact Bars",
    description: "Small-multiple bars for side-by-side operational units.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["breakdown", "timeSeries"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "evidence",
    wowNotes: ["Dense without becoming noisy", "Strong value-to-space ratio"]
  },
  {
    id: "kpi.heatmap-grid",
    title: "Heatmap Grid",
    description: "Matrix risk/load panel with explicit cell labeling.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["matrix"],
    perfCost: "med",
    maturity: "Mature",
    defaultIntent: "risk",
    wowNotes: ["Cell-level a11y labels", "Compact matrix storytelling"]
  },
  {
    id: "kpi.waterfall-mini",
    title: "Waterfall Mini",
    description: "Finance bridge chart for delta-by-delta narrative.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["timeSeries", "breakdown"],
    perfCost: "med",
    maturity: "Mature",
    defaultIntent: "cash",
    wowNotes: ["Ledger-friendly delta logic", "Compact bridge readability"]
  },
  {
    id: "kpi.mini-table",
    title: "Mini Table KPI",
    description: "Ledger-style mini table for numerically strict KPIs.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["tableMini"],
    perfCost: "low",
    maturity: "Mature",
    defaultIntent: "governance",
    wowNotes: ["No glow interior", "Tabular numeric discipline"]
  },
  {
    id: "kpi.distribution-dots",
    title: "Distribution Dots",
    description: "Optional dot distribution visual, gated as alien tech.",
    supportedStyles: BASE_STYLES,
    supportedSurfaces: BASE_SURFACES,
    supportedDataShapes: ["distribution", "correlation"],
    perfCost: "med",
    maturity: "AlienTech",
    defaultIntent: "risk",
    wowNotes: ["Gated by default", "High-variance exploratory chart"]
  }
];

export const KPI_WIDGET_CATALOG: readonly CatalogEntry[] = BASE_CATALOG.map((entry) => {
  const snippet = getWidgetSnippet(entry.id);
  if (snippet === undefined) {
    return entry;
  }

  return {
    ...entry,
    snippet
  };
});

export function getCatalogEntry(id: ChartId): CatalogEntry | undefined {
  return KPI_WIDGET_CATALOG.find((entry) => entry.id === id);
}

export function listCatalogWithSnippets(): readonly CatalogEntry[] {
  return KPI_WIDGET_CATALOG;
}

export { KPI_WIDGET_SNIPPETS };
