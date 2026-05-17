import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const mobileConfidenceMeterBandsPassport = {
  chartId: "mobile.confidence-meter-bands",
  displayName: "Confidence Meter Bands",
  shortName: "Confidence Bands",
  family: "bands",
  surface: "mobile",
  status: "partial_real",
  questionAnswered: "Why can or cannot the owner trust the current snapshot?",
  primaryUser: "owner",
  routePreview: "/prisma-command?preview=charts",
  routeProduction: "/prisma-command",
  componentFile: "products/mobile/app/app/prisma-command/charts/MobileConfidenceMeterBands.tsx",
  cardWrapperFile: "products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "confidenceMeterBandsOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "ConfidenceBand[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildMobileConfidenceMeterBandsViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockMobileCharts.confidenceMeterBands",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "bandsRecipe",
  visualKnobs: [knob("bandHeight", "Controls one-handed readability.", "10-18", "bar width/profile", "Too tall reduces glanceability"), knob("percentagePillStyle", "Controls confidence labels.", "inline-pill-none", "series.label/card", "No label weakens non-color signal")],
  states: supportedStates,
  interactions: ["tapSummary", "hoverTooltip"],
  accessibility: commonAccessibility,
  knownRisks: ["Evidence band is a proxy until evidence coverage has a first-class score."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "bandsRecipe", adapterName: "buildMobileConfidenceMeterBandsViewModel", contractType: "ConfidenceBand", componentFile: "products/mobile/app/app/prisma-command/charts/MobileConfidenceMeterBands.tsx", deckFile: "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx" }),
  validation: validation("/prisma-command?preview=charts")
} satisfies PrismaChartPassport;

