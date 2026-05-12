import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const mobileActionInboxPriorityStackPassport = {
  chartId: "mobile.action-inbox-priority-stack",
  displayName: "Action Inbox Priority Stack",
  shortName: "Action Stack",
  family: "stack",
  surface: "mobile",
  status: "partial_real",
  questionAnswered: "Who owns open actions and which priorities need attention first?",
  primaryUser: "owner",
  routePreview: "/prisma-command?preview=charts",
  routeProduction: "/prisma-command",
  componentFile: "products/mobile/app/app/prisma-command/charts/MobileActionInboxPriorityStack.tsx",
  cardWrapperFile: "products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "actionInboxPriorityStackOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "ActionPriorityStackDatum[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildMobileActionInboxPriorityStackViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockMobileCharts.actionInboxPriorityStack",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "stackRecipe",
  visualKnobs: [knob("barThickness", "Controls mobile readability.", "10-18", "series.barWidth", "Too thick reduces rows"), knob("legendDensity", "Controls compact legend.", "minimal-standard", "legend", "Too much legend becomes dashboard")],
  states: supportedStates,
  interactions: ["tapSummary", "legendToggle"],
  accessibility: commonAccessibility,
  knownRisks: ["No mutations are allowed from Mobile; actions are supervisory only."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "stackRecipe", adapterName: "buildMobileActionInboxPriorityStackViewModel", contractType: "ActionPriorityStackDatum", componentFile: "products/mobile/app/app/prisma-command/charts/MobileActionInboxPriorityStack.tsx", deckFile: "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx" }),
  validation: validation("/prisma-command?preview=charts")
} satisfies PrismaChartPassport;

