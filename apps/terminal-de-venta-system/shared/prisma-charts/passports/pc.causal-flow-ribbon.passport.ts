import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcCausalFlowRibbonPassport = {
  chartId: "pc.causal-flow-ribbon",
  displayName: "Causal Flow Ribbon",
  shortName: "Causal Flow",
  family: "flow",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "Which source modules create operational effects and what action should governance take?",
  primaryUser: "manager",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/pc/app/app/prisma-insights/charts/PcCausalFlowRibbon.tsx",
  cardWrapperFile: "products/pc/app/app/prisma-insights/charts/PcChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "causalFlowRibbonOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "CausalFlowRibbonDatum[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcCausalFlowRibbonViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.causalFlowRibbon",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "flowRecipe",
  visualKnobs: [knob("ribbonWidth", "Controls sankey ribbon weight.", "8-18", "series.nodeWidth / link width", "Too wide hides labels"), knob("ribbonOpacity", "Controls visual pressure.", "0.22-0.62", "link.lineStyle.opacity", "Too high looks noisy")],
  states: supportedStates,
  interactions: ["hoverTooltip", "clickFocus", "legendFilter"],
  accessibility: commonAccessibility,
  knownRisks: ["No canonical causality table exists yet; adapter uses safe sync/dashboard signals."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "flowRecipe", adapterName: "buildPcCausalFlowRibbonViewModel", contractType: "CausalFlowRibbonDatum", componentFile: "products/pc/app/app/prisma-insights/charts/PcCausalFlowRibbon.tsx", deckFile: "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx" }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;

