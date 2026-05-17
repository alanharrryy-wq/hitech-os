import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const mobileFreshnessBeaconGridPassport = {
  chartId: "mobile.freshness-beacon-grid",
  displayName: "Freshness Rings",
  shortName: "Freshness",
  family: "rings",
  surface: "mobile",
  status: "partial_real",
  questionAnswered: "Which source is fresh, aging, stale, offline, or unknown?",
  primaryUser: "owner",
  routePreview: "/prisma-command?preview=charts",
  routeProduction: "/prisma-command",
  componentFile: "products/mobile/app/app/prisma-command/charts/MobileFreshnessRings.tsx",
  cardWrapperFile: "products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "freshnessBeaconGridOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "FreshnessBeacon[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildMobileFreshnessRingsViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockMobileCharts.freshnessBeaconGrid",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "ringsRecipe",
  visualKnobs: [knob("ringThickness", "Controls freshness mark weight.", "6-14", "pictorial/ring profile", "Too thick looks like score meter"), knob("staleEmphasis", "Highlights stale sources.", "true-false", "status palette", "Must not imply critical without evidence")],
  states: supportedStates,
  interactions: ["tapSummary", "hoverTooltip"],
  accessibility: commonAccessibility,
  knownRisks: ["TTL is inferred from snapshot freshness where source-specific TTL is not explicit."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "ringsRecipe", adapterName: "buildMobileFreshnessRingsViewModel", contractType: "FreshnessBeacon", componentFile: "products/mobile/app/app/prisma-command/charts/MobileFreshnessRings.tsx", deckFile: "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx" }),
  validation: validation("/prisma-command?preview=charts")
} satisfies PrismaChartPassport;

