import type { MobileDataPlaneState } from "./types";
import type { PrismaMobileAlertsPayload, PrismaMobileBranchesPayload, PrismaMobileCashCurrentPayload, PrismaMobileHealthPayload, PrismaMobileInventoryItem, PrismaMobileInventoryWatchlistPayload, PrismaMobileReportsDailyPayload, PrismaMobileSalesPoint, PrismaMobileSalesTodayPayload, PrismaMobileSummaryPayload } from "../prisma-app-api-contracts";
import type { PrismaMobileSnapshotPayload } from "../prisma-mobile-snapshot-contract";
import { buildPrismaMobileIntelligenceSnapshot } from "../mobile-intelligence/snapshot-engine";
import { classifyInventoryState } from "./inventory-adapter";
import { buildOperationalAlerts, countAlerts } from "./alerts-policy";
import { cashStatus } from "./cash-policy";
import { minutesAgoLabel, moneyLabel, nowLabel, percentHeight, signedMoneyLabel } from "./money";
import { deriveMobileDataReadiness } from "./data-readiness";

function salesTimeline(state: MobileDataPlaneState): PrismaMobileSalesPoint[] {
  const max = Math.max(0, ...state.salesToday.hourlyBuckets.map((bucket) => bucket.amountCents));
  return state.salesToday.hourlyBuckets.map((bucket) => ({ hour: bucket.hour, label: bucket.hour, amount: moneyLabel(bucket.amountCents), amountCents: bucket.amountCents, height: percentHeight(bucket.amountCents, max) }));
}

function inventoryItems(state: MobileDataPlaneState): PrismaMobileInventoryItem[] {
  return state.inventory.items.map((item) => ({ sku: item.sku, name: item.name, category: item.category, stock: `${item.stockQty} pzas`, stockQty: item.stockQty, movement: item.lastMovementLabel, weeklyUnitsSold: item.weeklyUnitsSold, state: classifyInventoryState(item) }));
}

export function buildSalesTodayPayload(state: MobileDataPlaneState): PrismaMobileSalesTodayPayload {
  return {
    totalSalesCents: state.salesToday.totalSalesCents,
    totalSalesLabel: moneyLabel(state.salesToday.totalSalesCents),
    tickets: state.salesToday.tickets,
    averageTicketCents: state.salesToday.averageTicketCents,
    averageTicketLabel: moneyLabel(state.salesToday.averageTicketCents),
    deltaAgainstYesterday: state.pc.consolidatedSalesCents === null ? "esperando consolidado PC" : signedMoneyLabel(state.salesToday.totalSalesCents - state.pc.consolidatedSalesCents),
    strongCategory: state.salesToday.topCategory,
    timeline: salesTimeline(state)
  };
}

export function buildCashCurrentPayload(state: MobileDataPlaneState): PrismaMobileCashCurrentPayload {
  return {
    status: cashStatus(state.cash, state.config),
    expectedCents: state.cash.expectedCents,
    expectedLabel: moneyLabel(state.cash.expectedCents),
    countedCents: state.cash.countedCents ?? state.cash.expectedCents,
    countedLabel: state.cash.countedCents === null ? "sin conteo" : moneyLabel(state.cash.countedCents),
    differenceCents: state.cash.differenceCents,
    lastCut: state.cash.lastCutAt ? minutesAgoLabel(state.cash.lastCutAt) : "sin corte registrado",
    movements: [
      { label: "Efectivo", value: moneyLabel(state.cash.cashInCents), amountCents: state.cash.cashInCents, detail: "Ventas pagadas en efectivo" },
      { label: "Tarjeta", value: moneyLabel(state.cash.cardCents), amountCents: state.cash.cardCents, detail: "Ventas con tarjeta" },
      { label: "Transferencia", value: moneyLabel(state.cash.transferCents), amountCents: state.cash.transferCents, detail: "Ventas por transferencia" },
      { label: "Salida", value: moneyLabel(state.cash.cashOutCents), amountCents: -state.cash.cashOutCents, detail: "Retiros o salidas registradas" }
    ]
  };
}

export function buildInventoryWatchlistPayload(state: MobileDataPlaneState): PrismaMobileInventoryWatchlistPayload {
  return { items: inventoryItems(state), counts: { critical: state.inventory.critical, reorder: state.inventory.reorder, normal: state.inventory.normal, overstock: state.inventory.overstock } };
}

export function buildAlertsPayload(state: MobileDataPlaneState): PrismaMobileAlertsPayload {
  const alerts = buildOperationalAlerts(state);
  return { alerts, counts: countAlerts(alerts) };
}

export function buildBranchesPayload(state: MobileDataPlaneState): PrismaMobileBranchesPayload {
  const status = state.pc.ok ? state.pc.branchStatus : state.runtimeMode === "offline" ? "offline" : "revisar";
  const branch = {
    name: state.pc.branchName,
    status,
    salesToday: moneyLabel(state.salesToday.totalSalesCents),
    salesTodayCents: state.salesToday.totalSalesCents,
    salesDelta: state.pc.consolidatedSalesCents === null ? "esperando consolidado PC" : signedMoneyLabel(state.salesToday.totalSalesCents - state.pc.consolidatedSalesCents),
    cashState: cashStatus(state.cash, state.config),
    alerts: buildAlertsPayload(state).counts.total,
    syncLag: state.pc.syncLagMs === null ? minutesAgoLabel(state.outbox.lastSyncedAt) : `${Math.round(state.pc.syncLagMs / 1000)}s`,
    tickets: state.salesToday.tickets
  };
  return { branches: [branch], counts: { total: 1, healthy: status === "sano" ? 1 : 0, review: status === "revisar" ? 1 : 0, urgent: status === "urgente" ? 1 : 0, offline: status === "offline" ? 1 : 0 } };
}

export function buildReportsDailyPayload(state: MobileDataPlaneState): PrismaMobileReportsDailyPayload {
  return {
    reportDate: new Intl.DateTimeFormat("es-MX", { dateStyle: "full" }).format(new Date()),
    nextReportAt: "al cierre operativo",
    cards: [
      { title: "Ventas netas", value: moneyLabel(state.salesToday.totalSalesCents), detail: `${state.salesToday.tickets} tickets`, footnote: "Leído desde Tablet POS" },
      { title: "Ticket promedio", value: moneyLabel(state.salesToday.averageTicketCents), detail: state.salesToday.tickets > 0 ? "promedio operativo" : "sin tickets", footnote: "Datos de fuentes conectadas" },
      { title: "Stock crítico", value: String(state.inventory.critical), detail: `${state.inventory.reorder} por reponer`, footnote: "Watchlist calculada" },
      { title: "Sync", value: state.outbox.pending === 0 ? "sin pendientes" : `${state.outbox.pending} pendientes`, detail: `${state.outbox.failed} fallidos`, footnote: minutesAgoLabel(state.outbox.lastSyncedAt) }
    ]
  };
}

export function buildSummaryPayload(state: MobileDataPlaneState): PrismaMobileSummaryPayload {
  const alerts = buildAlertsPayload(state);
  const branches = buildBranchesPayload(state);
  const dataReadiness = deriveMobileDataReadiness(state);
  const health: PrismaMobileSummaryPayload["health"] = dataReadiness.level === "offline" || dataReadiness.level === "blocked"
    ? "offline"
    : alerts.counts.critical > 0
      ? "urgente"
      : alerts.counts.high > 0 || branches.counts.review > 0 || dataReadiness.level === "partial" || dataReadiness.level === "empty"
        ? "revisar"
        : "sano";
  const salesNote = state.salesToday.tickets > 0 ? `${state.salesToday.tickets} tickets cerrados` : "sin tickets cerrados hoy";
  const ticketNote = state.salesToday.tickets > 0 ? "promedio desde ventas reales" : "esperando primer ticket real";
  return {
    businessName: state.config.businessName,
    screen: "hoy" as const,
    mode: "owner_mobile" as const,
    generatedLabel: nowLabel(),
    health,
    urgentAlerts: alerts.counts.critical + alerts.counts.high,
    branchesToReview: branches.counts.review + branches.counts.urgent + branches.counts.offline,
    dataReadiness,
    account: {
      customerName: state.config.businessName,
      customerId: state.config.customerId,
      tenantId: state.config.tenantId,
      licenseId: state.config.licenseId,
      planLabel: state.config.planLabel,
      activationMode: state.config.activationMode,
      activationModeLabel: state.config.activationModeLabel,
      licenseStateLabel: state.config.licenseStateLabel,
      authorizationLabel: state.config.authorizationLabel,
      mobileDeviceLabel: "Mobile vinculado",
      tabletDeviceLabel: "Tablet vinculada",
      pcDeviceLabel: "PC vinculada",
      customerSetupLabel: "Prisma Customer Setup",
      setupSlotLabel: "Mobile Companion Slot"
    },
    kpis: [
      { key: "ventas", label: "Ventas hoy", value: moneyLabel(state.salesToday.totalSalesCents), note: salesNote, tone: "gold" as const, numericValue: state.salesToday.totalSalesCents, unit: "MXN" },
      { key: "ticket_promedio", label: "Ticket promedio", value: moneyLabel(state.salesToday.averageTicketCents), note: ticketNote, tone: "green" as const, numericValue: state.salesToday.averageTicketCents, unit: "MXN" },
      { key: "stock", label: "Stock crítico", value: String(state.inventory.critical), note: state.inventory.items.length > 0 ? `${state.inventory.reorder} SKUs por reponer` : "watchlist sin SKUs recibidos", tone: state.inventory.critical > 0 ? "red" as const : "blue" as const, numericValue: state.inventory.critical, unit: "SKUs" },
      { key: "sync", label: "Sync pendiente", value: String(state.outbox.pending), note: state.outbox.failed > 0 ? `${state.outbox.failed} fallidos` : dataReadiness.syncState === "unknown" ? "sin confirmación reciente" : "sin fallos visibles", tone: state.outbox.failed > 0 ? "red" as const : "neutral" as const, numericValue: state.outbox.pending, unit: "eventos" }
    ],
    quickActions: dataReadiness.actions
  };
}

export function buildHealthPayload(state: MobileDataPlaneState): PrismaMobileHealthPayload {
  return { ok: true as const, product: "PRISMA App Mobile" as const, surface: "prisma.mobile.app" as const, contract: "PRISMA_APP_MOBILE_17_DATA_PLANE" as const, endpoints: ["summary", "sales_today", "cash_current", "inventory_watchlist", "alerts", "reports_daily", "branches", "health"] as const, upstreams: state.probes.map((p) => ({ id: p.id, ok: p.ok, latencyMs: p.latencyMs, error: p.error })) };
}

export function buildSnapshotPayload(state: MobileDataPlaneState): PrismaMobileSnapshotPayload {
  const legacy = {
    summary: buildSummaryPayload(state),
    salesToday: buildSalesTodayPayload(state),
    cashCurrent: buildCashCurrentPayload(state),
    inventoryWatchlist: buildInventoryWatchlistPayload(state),
    alerts: buildAlertsPayload(state),
    reportsDaily: buildReportsDailyPayload(state),
    branches: buildBranchesPayload(state),
    health: buildHealthPayload(state)
  };
  return { ...legacy, ...buildPrismaMobileIntelligenceSnapshot(state, legacy) };
}
