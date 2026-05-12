import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcInventoryRiskTreemapPassport = {
  chartId: "pc.inventory-risk-treemap",
  displayName: "Inventory Risk Treemap",
  shortName: "Inventory Risk",
  family: "treemap",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "Which inventory groups create continuity or revenue risk?",
  primaryUser: "manager",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/pc/app/app/prisma-insights/charts/PcInventoryRiskTreemap.tsx",
  cardWrapperFile: "products/pc/app/app/prisma-insights/charts/PcChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "inventoryRiskTreemapOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "InventoryRiskNode[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcInventoryRiskTreemapViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.inventoryRiskTreemap",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "treemapRecipe",
  visualKnobs: [knob("tilePadding", "Controls premium tile breathing room.", "2-8", "series.itemStyle.gapWidth", "Too high wastes space"), knob("labelDensity", "Controls SKU label amount.", "compact-standard-rich", "series.label", "Too dense reduces governance clarity")],
  states: supportedStates,
  interactions: ["hoverTooltip", "breadcrumb", "clickFocus"],
  accessibility: commonAccessibility,
  knownRisks: ["Uses top SKU and low-stock summaries until per-SKU risk source is expanded."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "treemapRecipe", adapterName: "buildPcInventoryRiskTreemapViewModel", contractType: "InventoryRiskNode", componentFile: "products/pc/app/app/prisma-insights/charts/PcInventoryRiskTreemap.tsx", deckFile: "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx" }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;

