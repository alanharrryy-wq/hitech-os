import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcOperationalDensityFieldPassport = {
  chartId: "pc.operational-density-field",
  displayName: "Operational Density Field",
  shortName: "Density Field",
  family: "density",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "Where is operational pressure concentrated by module and time?",
  primaryUser: "manager",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/pc/app/app/prisma-insights/charts/PcOperationalDensityField.tsx",
  cardWrapperFile: "products/pc/app/app/prisma-insights/charts/PcChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "operationalDensityFieldOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "OperationalDensityCell[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcOperationalDensityFieldViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.operationalDensityField",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "densityRecipe",
  visualKnobs: [knob("heatIntensity", "Controls pressure color ramp.", "0.65-1.25", "visualMap.inRange", "Too hot exaggerates medium states"), knob("timeLabelDensity", "Controls x-axis labels.", "compact-standard", "xAxis.axisLabel", "Too dense hurts scanability")],
  states: supportedStates,
  interactions: ["hoverTooltip", "brushWindow", "clickFocus"],
  accessibility: commonAccessibility,
  knownRisks: ["Current adapter has safe module pressure, not a full historical event-density table."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "densityRecipe", adapterName: "buildPcOperationalDensityFieldViewModel", contractType: "OperationalDensityCell", componentFile: "products/pc/app/app/prisma-insights/charts/PcOperationalDensityField.tsx", deckFile: "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx" }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;

