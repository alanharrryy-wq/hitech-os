import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { PrismaMobileSnapshotPayload } from "../prisma-mobile-snapshot-contract";
import { formatMxnFromCents, formatSignedMxnFromCents } from "../prisma-mobile-formatters";
import { evaluateDataQuality } from "./data-quality-engine";
import { buildIntelligenceAlerts } from "./alert-engine";
import { buildIntelligenceActionInbox } from "./action-inbox-engine";
import { buildIntelligenceHealthRadar } from "./health-radar-engine";
import { buildSyncStatus, buildChartViewModels } from "./chart-series-engine";
import { buildIntelligenceTimeline } from "./timeline-engine";
import { buildIntelligenceDailyBrief } from "./daily-brief-engine";
import { PrismaMobileIntelligenceSnapshotSchema, PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID, type PrismaMobileIntelligenceSnapshot } from "./contracts";
import { evidence } from "./evidence";

function valueStatus(sourceOk: boolean, hasValue: boolean) {
  if (!sourceOk) return "unavailable" as const;
  return hasValue ? "ok" as const : "null" as const;
}

export function buildPrismaMobileIntelligenceSnapshot(state: MobileDataPlaneState, legacy: Omit<PrismaMobileSnapshotPayload, keyof PrismaMobileIntelligenceSnapshot>): PrismaMobileIntelligenceSnapshot {
  const dataQuality = evaluateDataQuality(state);
  const generatedAt = dataQuality.generatedAt;
  const tabletOk = dataQuality.sources.some((source) => source.id === "tablet" && source.status === "ok");
  const salesHasValue = tabletOk && state.salesToday.tickets > 0;
  const inventoryHasValue = tabletOk && state.inventory.items.length > 0;
  const cashHasCount = state.cash.countedCents !== null;

  const alertCenter = buildIntelligenceAlerts(state, dataQuality);
  const actionInbox = buildIntelligenceActionInbox(alertCenter);
  const healthRadar = buildIntelligenceHealthRadar(state, dataQuality, alertCenter);
  const sync = buildSyncStatus(state, dataQuality);
  const chartViewModels = buildChartViewModels(state, dataQuality, alertCenter, healthRadar, sync);
  const timeline = buildIntelligenceTimeline(state, alertCenter, actionInbox, dataQuality);
  const reports = buildIntelligenceDailyBrief({
    businessName: state.config.businessName,
    generatedAt,
    alertCenter,
    actionInbox,
    dataQuality,
    healthRadar
  });

  const inventoryTopRisk = state.inventory.items.find((item) => item.stockQty <= item.lowStockThreshold);
  const healthScoreLabel = healthRadar.globalScore === null ? "sin score" : `${healthRadar.globalScore}/100`;
  const primaryAction = actionInbox.primaryAction?.recommendedAction ?? alertCenter.primaryRecommendedAction;

  return PrismaMobileIntelligenceSnapshotSchema.parse({
    meta: {
      contractId: PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID,
      generatedAt,
      runtimeMode: dataQuality.runtimeMode,
      confidence: dataQuality.confidence,
      freshnessSeconds: dataQuality.freshnessSeconds
    },
    today: {
      businessName: state.config.businessName,
      generatedAt,
      openingLine: `PRISMA está en modo ${dataQuality.runtimeMode} con salud ${healthScoreLabel}.`,
      healthLabel: healthScoreLabel,
      recommendedAction: primaryAction,
      status: dataQuality.runtimeMode === "live" ? "ok" : dataQuality.runtimeMode === "unknown" ? "unknown" : "partial"
    },
    money: {
      expectedCashCents: tabletOk ? state.cash.expectedCents : null,
      countedCashCents: cashHasCount ? state.cash.countedCents : null,
      varianceCents: cashHasCount ? state.cash.differenceCents : null,
      varianceStatus: cashHasCount ? "ok" : tabletOk ? "unknown" : "unavailable",
      label: cashHasCount ? formatSignedMxnFromCents(state.cash.differenceCents) : "sin conteo real",
      evidence: [evidence("money-summary", "Caja", "Tablet POS", cashHasCount ? state.cash.differenceCents : "sin conteo")]
    },
    sales: {
      totalSalesCents: tabletOk ? state.salesToday.totalSalesCents : null,
      tickets: tabletOk ? state.salesToday.tickets : null,
      averageTicketCents: tabletOk ? state.salesToday.averageTicketCents : null,
      paceStatus: valueStatus(tabletOk, salesHasValue),
      summary: salesHasValue ? `${legacy.salesToday.totalSalesLabel} en ${state.salesToday.tickets} tickets.` : tabletOk ? "Tablet respondió sin tickets cerrados hoy." : "Ventas no disponibles.",
      evidence: [evidence("sales-summary", "Ventas hoy", "Tablet POS", `${state.salesToday.tickets} tickets, ${formatMxnFromCents(state.salesToday.totalSalesCents)}`)]
    },
    inventory: {
      criticalCount: tabletOk ? state.inventory.critical : null,
      reorderCount: tabletOk ? state.inventory.reorder : null,
      topRiskSku: inventoryTopRisk?.sku ?? null,
      riskStatus: valueStatus(tabletOk, inventoryHasValue),
      summary: inventoryHasValue ? `${state.inventory.critical} críticos y ${state.inventory.reorder} para reponer.` : tabletOk ? "Watchlist sin SKUs de riesgo recibidos." : "Inventario no disponible.",
      evidence: [evidence("inventory-summary", "Inventario", "Tablet POS", `${state.inventory.items.length} SKUs`)]
    },
    alertCenter,
    actionInbox,
    timeline,
    healthRadar,
    sync,
    reports,
    dataQuality,
    chartViewModels
  });
}

