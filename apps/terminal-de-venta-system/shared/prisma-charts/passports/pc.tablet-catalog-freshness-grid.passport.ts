import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcTabletCatalogFreshnessGridPassport = {
  chartId: "pc.tablet-catalog-freshness-grid",
  displayName: "Tablet Catalog Freshness Grid",
  shortName: "Catalog Freshness",
  family: "matrix",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "Which Tablets are fresh, stale, conflicted, or missing PC catalog checkpoints by entity?",
  primaryUser: "operator",
  routePreview: "/sync?preview=charts",
  routeProduction: "/sync",
  componentFile: "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx",
  cardWrapperFile: "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "tabletCatalogFreshnessGridOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "TabletCatalogFreshnessGridRow[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcTabletCatalogFreshnessGridViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.tabletCatalogFreshnessGrid",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "matrixRecipe",
  visualKnobs: [
    knob("cellStatus", "Maps entity freshness to matrix color and text.", "fresh-warning-stale-error", "series.heatmap.data", "Color alone must never be the only signal."),
    knob("rowDensity", "Controls Tablet row density inside /sync.", "compact-standard", "PC product wrapper", "Too dense hides checkpoint text.")
  ],
  states: supportedStates,
  interactions: ["hoverTooltip", "refresh", "rowScan"],
  accessibility: commonAccessibility,
  knownRisks: ["PC can only report Tablet-side checkpoint details when they are present in PC heartbeat/checkpoint evidence."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "matrixRecipe", adapterName: "buildPcTabletCatalogFreshnessGridViewModel", contractType: "TabletCatalogFreshnessGridRow", componentFile: "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx", deckFile: "products/pc/app/app/sync/page.tsx" }),
  validation: validation("/sync?preview=charts")
} satisfies PrismaChartPassport;
