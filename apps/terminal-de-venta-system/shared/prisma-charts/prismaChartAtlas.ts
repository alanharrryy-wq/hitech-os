import type { PrismaChartId, PrismaChartSurface } from "./prismaChartContracts";
import { pcCausalFlowRibbonPassport } from "./passports/pc.causal-flow-ribbon.passport";
import { pcDecisionLedgerTimelinePassport } from "./passports/pc.decision-ledger-timeline.passport";
import { pcFinancialOperationalWaterfallPassport } from "./passports/pc.financial-operational-waterfall.passport";
import { pcInventoryRiskTreemapPassport } from "./passports/pc.inventory-risk-treemap.passport";
import { pcOperationalDensityFieldPassport } from "./passports/pc.operational-density-field.passport";
import { opsOperationalDensityHeatmapPassport } from "./passports/ops.operational-density-heatmap.passport";
import { pcServiceDependencyGraphPassport } from "./passports/pc.service-dependency-graph.passport";
import { tabletShiftPulseStripPassport } from "./passports/tablet.shift-pulse-strip.passport";
import { tabletSyncOutboxStatusMatrixPassport } from "./passports/tablet.sync-outbox-status-matrix.passport";
import { mobileActionInboxPriorityStackPassport } from "./passports/mobile.action-inbox-priority-stack.passport";
import { mobileConfidenceMeterBandsPassport } from "./passports/mobile.confidence-meter-bands.passport";
import { mobileFreshnessBeaconGridPassport } from "./passports/mobile.freshness-beacon-grid.passport";
import { mobileHealthRadarCompactPassport } from "./passports/mobile.health-radar-compact.passport";
import { mobileIncidentSparkCardsPassport } from "./passports/mobile.incident-spark-cards.passport";
import { mobileOwnerPulseTimelinePassport } from "./passports/mobile.owner-pulse-timeline.passport";

export type PrismaChartFamily =
  | "flow"
  | "density"
  | "network"
  | "treemap"
  | "timeline"
  | "waterfall"
  | "strip"
  | "matrix"
  | "stack"
  | "radar"
  | "rings"
  | "sparks"
  | "bands";

export type PrismaChartPassportStatus = "preview_mock" | "partial_real" | "real_data" | "production_ready" | "deprecated";
export type PrismaChartPrimaryUser = "owner" | "operator" | "manager" | "auditor" | "admin" | "system";

export type PrismaChartVisualKnob = {
  name: string;
  purpose: string;
  safeRange: string;
  whereApplied: string;
  risk: string;
};

export type PrismaChartPassport = {
  chartId: PrismaChartId;
  displayName: string;
  shortName: string;
  family: PrismaChartFamily;
  surface: PrismaChartSurface;
  status: PrismaChartPassportStatus;
  questionAnswered: string;
  primaryUser: PrismaChartPrimaryUser;
  routePreview: string;
  routeProduction: string;
  componentFile: string;
  cardWrapperFile: string;
  optionBuilderFile: string;
  optionBuilderName: string;
  contractFile: string;
  contractType: string;
  adapterFile: string;
  adapterName: string;
  mockFile: string;
  mockName: string;
  registryFile: string;
  qualityModel: string;
  visualRecipe: string;
  visualKnobs: PrismaChartVisualKnob[];
  states: string[];
  interactions: string[];
  accessibility: {
    ariaLabel: string;
    textDescription: string;
    nonColorSignal: string;
    keyboardFocus: string;
  };
  knownRisks: string[];
  doNotTouch: string[];
  editPlaybook: {
    visualEdit: string[];
    dataEdit: string[];
    contractEdit: string[];
    layoutEdit: string[];
  };
  validation: {
    previewRoute: string;
    expectedSelectors: string[];
    verifier: string;
    manualChecks: string[];
  };
};

export const prismaChartAtlas = [
  pcCausalFlowRibbonPassport,
  pcOperationalDensityFieldPassport,
  opsOperationalDensityHeatmapPassport,
  pcServiceDependencyGraphPassport,
  pcInventoryRiskTreemapPassport,
  pcDecisionLedgerTimelinePassport,
  pcFinancialOperationalWaterfallPassport,
  tabletShiftPulseStripPassport,
  tabletSyncOutboxStatusMatrixPassport,
  mobileOwnerPulseTimelinePassport,
  mobileActionInboxPriorityStackPassport,
  mobileHealthRadarCompactPassport,
  mobileFreshnessBeaconGridPassport,
  mobileIncidentSparkCardsPassport,
  mobileConfidenceMeterBandsPassport
] satisfies PrismaChartPassport[];

export function getChartPassport(chartId: PrismaChartId) {
  return prismaChartAtlas.find((passport) => passport.chartId === chartId) ?? null;
}

export function findChartsByFamily(family: PrismaChartFamily) {
  return prismaChartAtlas.filter((passport) => passport.family === family);
}

export function findChartsBySurface(surface: PrismaChartSurface) {
  return prismaChartAtlas.filter((passport) => passport.surface === surface);
}

export function findChartsByRoute(route: string) {
  return prismaChartAtlas.filter((passport) => passport.routePreview.startsWith(route) || passport.routeProduction === route);
}

export function findChartsByContract(contractType: string) {
  return prismaChartAtlas.filter((passport) => passport.contractType.includes(contractType));
}
