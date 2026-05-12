import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const tabletShiftPulseStripPassport = {
  chartId: "tablet.shift-pulse-strip",
  displayName: "Shift Pulse Strip",
  shortName: "Shift Pulse",
  family: "strip",
  surface: "tablet",
  status: "partial_real",
  questionAnswered: "Can the Tablet keep operating right now?",
  primaryUser: "operator",
  routePreview: "/prisma-pulse?preview=charts",
  routeProduction: "/prisma-pulse",
  componentFile: "products/tablet/app/app/prisma-pulse/charts/TabletShiftPulseStrip.tsx",
  cardWrapperFile: "products/tablet/app/app/prisma-pulse/charts/TabletChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "shiftPulseStripOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "ShiftPulseBucket[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildTabletShiftPulseStripViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockTabletCharts.shiftPulseStrip",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "stripRecipe",
  visualKnobs: [knob("segmentHeight", "Controls touch strip readability.", "22-42", "bar/line profile", "Too small hurts touch"), knob("touchTargetSize", "Keeps Tablet operational.", "44-56", "card/control layout", "Too small breaks operator flow")],
  states: supportedStates,
  interactions: ["tapFocus", "reset"],
  accessibility: commonAccessibility,
  knownRisks: ["Current safe source is current runtime snapshot, not full shift history."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "stripRecipe", adapterName: "buildTabletShiftPulseStripViewModel", contractType: "ShiftPulseBucket", componentFile: "products/tablet/app/app/prisma-pulse/charts/TabletShiftPulseStrip.tsx", deckFile: "products/tablet/app/app/prisma-pulse/PrismaTabletPulsePanel.tsx" }),
  validation: validation("/prisma-pulse?preview=charts")
} satisfies PrismaChartPassport;

