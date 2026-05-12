import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const mobileIncidentSparkCardsPassport = {
  chartId: "mobile.incident-spark-cards",
  displayName: "Incident Spark Cards",
  shortName: "Incident Sparks",
  family: "sparks",
  surface: "mobile",
  status: "partial_real",
  questionAnswered: "Which active incidents are moving and what is the next action?",
  primaryUser: "owner",
  routePreview: "/prisma-command?preview=charts",
  routeProduction: "/prisma-command",
  componentFile: "products/mobile/app/app/prisma-command/charts/MobileIncidentSparkCards.tsx",
  cardWrapperFile: "products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "incidentSparkOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "IncidentSparkCard[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildMobileIncidentSparkCardsViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockMobileCharts.incidentSparkCards",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "sparksRecipe",
  visualKnobs: [knob("sparklineWidth", "Controls microtrend strength.", "2-4", "lineStyle.width", "Too thick crowds cards"), knob("deltaBadge", "Shows action urgency.", "true-false", "card badge", "No badge can hide change")],
  states: supportedStates,
  interactions: ["tapSummary", "hoverTooltip"],
  accessibility: commonAccessibility,
  knownRisks: ["True multi-point incident history is limited; adapter derives sparse points from alerts/timeline."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "sparksRecipe", adapterName: "buildMobileIncidentSparkCardsViewModel", contractType: "IncidentSparkCard", componentFile: "products/mobile/app/app/prisma-command/charts/MobileIncidentSparkCards.tsx", deckFile: "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx" }),
  validation: validation("/prisma-command?preview=charts")
} satisfies PrismaChartPassport;

