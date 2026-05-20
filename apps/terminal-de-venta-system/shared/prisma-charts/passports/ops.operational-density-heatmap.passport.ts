import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const opsOperationalDensityHeatmapPassport = {
  chartId: "ops.operational-density-heatmap",
  displayName: "Operational Density Heatmap",
  shortName: "Ops Heatmap",
  family: "density",
  surface: "pc",
  status: "preview_mock",
  questionAnswered: "Which module is overloaded, when did it happen, and what evidence should governance inspect first?",
  primaryUser: "manager",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/chart-lab/app/src/prisma-charts/components/LabEChartFrame.tsx",
  cardWrapperFile: "products/chart-lab/app/src/components/PrismaChartLabShell.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "operationalDensityHeatmapOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "OperationalDensityCell[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcOperationalDensityHeatmapViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.operationalDensityHeatmap",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "densityRecipe",
  visualKnobs: [
    knob("heatPalette", "Switches the governed color ramp.", "control-spectrum|thermal|aurora|critical", "visualMap.inRange.color", "Palette cannot imply real data freshness."),
    knob("heatZoneMode", "Moves deterministic lab heat to known operational zones.", "balanced|gateway-noon|payments-night|ops-wave|stress-demo", "series[0].data.value[2]", "Heat zones are preview-only until an adapter is real."),
    knob("heatIntensity", "Scales pressure values for visual stress tests.", "70-150", "series[0].data.value[2]", "High values can overstate mock severity."),
    knob("showCallouts", "Shows or hides executive annotations.", "true|false", "graphic[].invisible", "Callouts must stay evidence-labeled.")
  ],
  states: supportedStates,
  interactions: ["hoverTooltip", "paletteSwitch", "heatZonePreview", "reset", "copyConfig"],
  accessibility: commonAccessibility,
  knownRisks: ["Current heatmap is deterministic mock/demo; promotion to live use requires a real operational density adapter."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({
    visualRecipe: "densityRecipe",
    adapterName: "buildPcOperationalDensityHeatmapViewModel",
    contractType: "OperationalDensityCell",
    componentFile: "products/chart-lab/app/src/prisma-charts/components/LabEChartFrame.tsx",
    deckFile: "products/chart-lab/app/src/components/PrismaChartLabShell.tsx"
  }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;
