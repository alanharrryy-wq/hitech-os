import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const tabletSyncOutboxStatusMatrixPassport = {
  chartId: "tablet.sync-outbox-status-matrix",
  displayName: "Sync Outbox Status Matrix",
  shortName: "Outbox Matrix",
  family: "matrix",
  surface: "tablet",
  status: "partial_real",
  questionAnswered: "What local outbox work needs attention before/after sync?",
  primaryUser: "operator",
  routePreview: "/prisma-pulse?preview=charts",
  routeProduction: "/prisma-pulse",
  componentFile: "products/tablet/app/app/prisma-pulse/charts/TabletSyncOutboxStatusMatrix.tsx",
  cardWrapperFile: "products/tablet/app/app/prisma-pulse/charts/TabletChartCard.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "syncOutboxMatrixOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "SyncOutboxMatrixCell[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildTabletSyncOutboxStatusMatrixViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockTabletCharts.syncOutboxStatusMatrix",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "matrixRecipe",
  visualKnobs: [knob("cellSize", "Controls touch cell size.", "28-44", "heatmap grid", "Too small hurts Tablet"), knob("offlineEmphasis", "Highlights blocked/offline states.", "true-false", "status palette", "Too strong can imply false criticality")],
  states: supportedStates,
  interactions: ["tapTooltip", "tapFocus", "reset"],
  accessibility: commonAccessibility,
  knownRisks: ["Item-type breakdown depends on outbox topics; unknown events remain itemType=event."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "matrixRecipe", adapterName: "buildTabletSyncOutboxStatusMatrixViewModel", contractType: "SyncOutboxMatrixCell", componentFile: "products/tablet/app/app/prisma-pulse/charts/TabletSyncOutboxStatusMatrix.tsx", deckFile: "products/tablet/app/app/prisma-pulse/PrismaTabletPulsePanel.tsx" }),
  validation: validation("/prisma-pulse?preview=charts")
} satisfies PrismaChartPassport;

