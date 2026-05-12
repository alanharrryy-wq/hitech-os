import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcServiceDependencyGraphPassport = {
  chartId: "pc.service-dependency-graph",
  displayName: "Service Dependency Graph",
  shortName: "Dependency Graph",
  family: "network",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "Which apps, services, and databases form the current operational dependency path?",
  primaryUser: "admin",
  routePreview: "/prisma-insights?preview=charts",
  routeProduction: "/prisma-insights",
  componentFile: "products/pc/app/app/prisma-insights/charts/PcServiceDependencyGraph.tsx",
  cardWrapperFile: "products/pc/app/app/prisma-insights/charts/PcChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "serviceDependencyGraphOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "{ nodes: ServiceDependencyNode[]; edges: ServiceDependencyEdge[] }",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcServiceDependencyGraphViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.serviceDependencyGraph",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "networkRecipe",
  visualKnobs: [knob("nodeSize", "Controls node hierarchy.", "30-64", "series.data.symbolSize", "Oversized nodes collide"), knob("edgeOpacity", "Controls dependency subtlety.", "0.35-0.9", "series.links.lineStyle", "Low opacity hides failure paths")],
  states: supportedStates,
  interactions: ["hoverTooltip", "clickFocus", "roam"],
  accessibility: commonAccessibility,
  knownRisks: ["Does not perform live probes; it uses safe status summaries only."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "networkRecipe", adapterName: "buildPcServiceDependencyGraphViewModel", contractType: "ServiceDependencyNode/ServiceDependencyEdge", componentFile: "products/pc/app/app/prisma-insights/charts/PcServiceDependencyGraph.tsx", deckFile: "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx" }),
  validation: validation("/prisma-insights?preview=charts")
} satisfies PrismaChartPassport;

