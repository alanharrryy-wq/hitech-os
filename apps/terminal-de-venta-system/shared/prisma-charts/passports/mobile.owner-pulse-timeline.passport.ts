import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const mobileOwnerPulseTimelinePassport = {
  chartId: "mobile.owner-pulse-timeline",
  displayName: "Owner Pulse Timeline",
  shortName: "Owner Pulse",
  family: "timeline",
  surface: "mobile",
  status: "partial_real",
  questionAnswered: "Is the owner view improving, degrading, stale, or partial?",
  primaryUser: "owner",
  routePreview: "/prisma-command?preview=charts",
  routeProduction: "/prisma-command",
  componentFile: "products/mobile/app/app/prisma-command/charts/MobileOwnerPulseTimeline.tsx",
  cardWrapperFile: "products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "ownerPulseTimelineOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "OwnerPulsePoint[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildMobileOwnerPulseTimelineViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockMobileCharts.ownerPulseTimeline",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "timelineRecipe",
  visualKnobs: [knob("markerSize", "Controls tap target weight.", "6-14", "scatter.symbolSize", "Too large crowds mobile"), knob("eventDensity", "Controls compact owner scan.", "compact-standard", "axis/series labels", "Too dense becomes mini-PC")],
  states: supportedStates,
  interactions: ["tapSummary", "hoverTooltip"],
  accessibility: commonAccessibility,
  knownRisks: ["Historical owner timeline is limited by current snapshot depth."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "timelineRecipe", adapterName: "buildMobileOwnerPulseTimelineViewModel", contractType: "OwnerPulsePoint", componentFile: "products/mobile/app/app/prisma-command/charts/MobileOwnerPulseTimeline.tsx", deckFile: "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx" }),
  validation: validation("/prisma-command?preview=charts")
} satisfies PrismaChartPassport;

