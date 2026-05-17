import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const mobileHealthRadarCompactPassport = {
  chartId: "mobile.health-radar-compact",
  displayName: "Health Radar Compact",
  shortName: "Health Radar",
  family: "radar",
  surface: "mobile",
  status: "partial_real",
  questionAnswered: "Which health dimension is weak: data quality, sync, alerts, inventory, uptime, or cashflow?",
  primaryUser: "owner",
  routePreview: "/prisma-command?preview=charts",
  routeProduction: "/prisma-command",
  componentFile: "products/mobile/app/app/prisma-command/charts/MobileHealthRadarCompact.tsx",
  cardWrapperFile: "products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "healthRadarCompactOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "HealthRadarAxis[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildMobileHealthRadarCompactViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockMobileCharts.healthRadarCompact",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "radarRecipe",
  visualKnobs: [
    knob("radius", "Controls radar size inside the card.", "52%-72%", "radar.radius", "Too large cuts labels"),
    knob("axisNameWeight", "Controls axis hierarchy.", "600-850", "radar.axisName.fontWeight", "Too heavy looks noisy"),
    knob("splitLineOpacity", "Controls internal grid presence.", "0.08-0.28", "radar.splitLine.lineStyle.color", "Too visible adds clutter"),
    knob("areaFillOpacity", "Controls crystalline fill.", "0.10-0.32", "series.data.areaStyle.color", "Too high hides grid"),
    knob("lineWidth", "Controls premium silhouette.", "2-4", "series.data.lineStyle.width", "Too thick looks toy-like"),
    knob("pointGlow", "Controls node emphasis.", "off-controlled", "series.itemStyle", "Too much glow becomes decorative")
  ],
  states: supportedStates,
  interactions: ["tapSummary", "hoverTooltip"],
  accessibility: commonAccessibility,
  knownRisks: ["The compact contract maps the richer Mobile health radar into six axes; unknown sources must stay UNKNOWN."],
  doNotTouch: [...commonDoNotTouch, "Do not put this radar around the main score text."],
  editPlaybook: editPlaybook({ visualRecipe: "radarRecipe", adapterName: "buildMobileHealthRadarCompactViewModel", contractType: "HealthRadarAxis", componentFile: "products/mobile/app/app/prisma-command/charts/MobileHealthRadarCompact.tsx", deckFile: "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx" }),
  validation: validation("/prisma-command?preview=charts")
} satisfies PrismaChartPassport;

