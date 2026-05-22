import type { PrismaChartPassport } from "../prismaChartAtlas";
import { commonAccessibility, commonDoNotTouch, editPlaybook, knob, supportedStates, validation } from "./passportShared";

export const pcSyncCommandLifecycleTimelinePassport = {
  chartId: "pc.sync-command-lifecycle-timeline",
  displayName: "Sync Command Lifecycle Timeline",
  shortName: "Sync Lifecycle",
  family: "timeline",
  surface: "pc",
  status: "partial_real",
  questionAnswered: "Where did a catalog sync command get created, exported, pulled, applied, rejected, conflicted, or duplicated?",
  primaryUser: "operator",
  routePreview: "/sync?preview=charts",
  routeProduction: "/sync",
  componentFile: "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx",
  cardWrapperFile: "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx",
  optionBuilderFile: "shared/prisma-charts/prismaChartOptions.ts",
  optionBuilderName: "syncCommandLifecycleTimelineOption",
  contractFile: "shared/prisma-charts/prismaChartContracts.ts",
  contractType: "SyncCommandLifecycleEvent[]",
  adapterFile: "shared/prisma-charts/prismaChartAdapters.ts",
  adapterName: "buildPcSyncCommandLifecycleTimelineViewModel",
  mockFile: "shared/prisma-charts/prismaChartMocks.ts",
  mockName: "mockPcCharts.syncCommandLifecycleTimeline",
  registryFile: "shared/prisma-charts/prismaChartRegistry.ts",
  qualityModel: "PrismaChartQuality",
  visualRecipe: "timelineRecipe",
  visualKnobs: [
    knob("statusLane", "Maps lifecycle state to event lane.", "created-applied-failed", "yAxis.category", "Missing status text can obscure failure reasons."),
    knob("eventWeight", "Maps entity/result volume to marker size.", "12-30", "series.scatter.symbolSize", "Too large hides adjacent events.")
  ],
  states: supportedStates,
  interactions: ["hoverTooltip", "refresh", "eventScan"],
  accessibility: commonAccessibility,
  knownRisks: ["PC export ledger is real; pulled/applied states require Tablet checkpoint evidence reported back to PC."],
  doNotTouch: commonDoNotTouch,
  editPlaybook: editPlaybook({ visualRecipe: "timelineRecipe", adapterName: "buildPcSyncCommandLifecycleTimelineViewModel", contractType: "SyncCommandLifecycleEvent", componentFile: "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx", deckFile: "products/pc/app/app/sync/page.tsx" }),
  validation: validation("/sync?preview=charts")
} satisfies PrismaChartPassport;
