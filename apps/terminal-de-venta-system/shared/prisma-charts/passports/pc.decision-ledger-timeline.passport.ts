import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcDecisionLedgerTimelinePassport = {
  chartId: "pc.decision-ledger-timeline",
  displayName: "Decision Ledger Timeline",
  shortName: "Decision Ledger",
  family: "timeline",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "What evidence and governance decisions changed operational state over time?",
  primaryUser: "auditor",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/pc/app/app/prisma-insights/charts/PcDecisionLedgerTimeline.tsx",
  cardWrapperFile: "products/pc/app/app/prisma-insights/charts/PcChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "decisionLedgerTimelineOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "DecisionLedgerPoint[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcDecisionLedgerTimelineViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.decisionLedgerTimeline",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "timelineRecipe",
  visualKnobs: [knob("markerSize", "Controls evidence marker weight.", "6-22", "scatter.symbolSize", "Too large obscures time"), knob("dateLabelDensity", "Controls timeline labels.", "compact-standard", "xAxis.axisLabel", "Too dense hurts audit scanning")],
  states: supportedStates,
  interactions: ["hoverTooltip", "clickFocus", "brushWindow"],
  accessibility: commonAccessibility,
  knownRisks: ["No durable decision ledger table is exposed yet; bridge/dashboard events are partial evidence."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "timelineRecipe", adapterName: "buildPcDecisionLedgerTimelineViewModel", contractType: "DecisionLedgerPoint", componentFile: "products/pc/app/app/prisma-insights/charts/PcDecisionLedgerTimeline.tsx", deckFile: "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx" }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;

