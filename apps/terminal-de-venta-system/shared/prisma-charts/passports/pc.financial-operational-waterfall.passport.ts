import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcFinancialOperationalWaterfallPassport = {
  chartId: "pc.financial-operational-waterfall",
  displayName: "Financial / Operational Waterfall",
  shortName: "Waterfall",
  family: "waterfall",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "How do visible operations explain money movement?",
  primaryUser: "manager",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/pc/app/app/prisma-insights/charts/PcFinancialOperationalWaterfall.tsx",
  cardWrapperFile: "products/pc/app/app/prisma-insights/charts/PcChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "financialOperationalWaterfallOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "OperationalWaterfallStep[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcFinancialOperationalWaterfallViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.financialOperationalWaterfall",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "waterfallRecipe",
  visualKnobs: [knob("connectorStyle", "Controls executive connector subtlety.", "none-subtle-strong", "series/bar connector", "Strong connectors look busy"), knob("totalBarEmphasis", "Emphasizes final subtotal.", "true-false", "series.itemStyle", "No emphasis weakens decision")],
  states: supportedStates,
  interactions: ["hoverTooltip", "clickFocus"],
  accessibility: commonAccessibility,
  knownRisks: ["Refunds, discounts, shrink, and cost are not fully canonical in this chart adapter yet."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "waterfallRecipe", adapterName: "buildPcFinancialOperationalWaterfallViewModel", contractType: "OperationalWaterfallStep", componentFile: "products/pc/app/app/prisma-insights/charts/PcFinancialOperationalWaterfall.tsx", deckFile: "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx" }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;

