import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { AlertCenter, ChartPoint, ChartViewModel, DataQualityReport, HealthRadar, SyncStatus } from "./contracts";
import { ChartViewModelSchema } from "./contracts";
import { classifyInventoryState } from "../mobile-data-plane/inventory-adapter";
import { evidence } from "./evidence";

function chart(input: ChartViewModel): ChartViewModel {
  return ChartViewModelSchema.parse(input);
}

function cumulative(points: Array<{ hour: string; amountCents: number }>): ChartPoint[] {
  let running = 0;
  return points.map((point) => {
    running += point.amountCents;
    return { x: point.hour, y: running, label: point.hour, status: "ok", meta: { amountCents: point.amountCents } };
  });
}

export function buildSyncStatus(state: MobileDataPlaneState, report: DataQualityReport): SyncStatus {
  const tablet = report.sources.find((source) => source.id === "tablet");
  const status = tablet?.status !== "ok" ? "offline" : state.outbox.failed > 0 ? "blocked" : state.outbox.pending > 0 ? "delayed" : "ok";
  return {
    status,
    pendingCount: tablet?.status === "ok" ? state.outbox.pending : null,
    failedCount: tablet?.status === "ok" ? state.outbox.failed : null,
    oldestPendingAt: state.outbox.oldestPendingAt,
    freshnessSeconds: tablet?.freshnessSeconds ?? null,
    evidence: [evidence("sync-outbox", "Outbox", "Tablet POS", `${state.outbox.pending} pendientes, ${state.outbox.failed} fallidos`)]
  };
}

export function buildChartViewModels(state: MobileDataPlaneState, report: DataQualityReport, alerts: AlertCenter, radar: HealthRadar, sync: SyncStatus): ChartViewModel[] {
  const salesPoints: ChartPoint[] = state.salesToday.hourlyBuckets.map((bucket) => ({
    x: bucket.hour,
    y: bucket.amountCents,
    label: bucket.hour,
    status: "ok",
    meta: { tickets: bucket.tickets }
  }));
  const salesEvidence = [evidence("chart-sales-rhythm", "Ventas por hora", "Tablet POS", `${state.salesToday.hourlyBuckets.length} buckets`)];

  const inventoryPoints: ChartPoint[] = state.inventory.items.slice(0, 8).map((item) => {
    const stateName = classifyInventoryState(item);
    const dailyVelocity = item.weeklyUnitsSold > 0 ? item.weeklyUnitsSold / 7 : null;
    const daysToStockOut = dailyVelocity ? Math.max(0, Math.round((item.stockQty / dailyVelocity) * 10) / 10) : null;
    const risk = stateName === "critico" ? 100 : stateName === "reponer" ? 76 : stateName === "sobrestock" ? 34 : 12;
    return {
      x: item.sku,
      y: risk,
      label: item.name,
      status: stateName === "critico" ? "partial" : "ok",
      meta: {
        stockQty: item.stockQty,
        daysToStockOut,
        weeklyUnitsSold: item.weeklyUnitsSold,
        state: stateName
      }
    };
  });

  const alertPoints: ChartPoint[] = [
    { x: "critical", y: alerts.counts.critical, label: "Críticas", status: alerts.counts.critical > 0 ? "partial" : "ok", meta: {} },
    { x: "high", y: alerts.counts.high, label: "Altas", status: alerts.counts.high > 0 ? "partial" : "ok", meta: {} },
    { x: "medium", y: alerts.counts.medium, label: "Medias", status: alerts.counts.medium > 0 ? "partial" : "ok", meta: {} },
    { x: "low", y: alerts.counts.low, label: "Bajas", status: "ok", meta: {} },
    { x: "info", y: alerts.counts.info, label: "Info", status: "ok", meta: {} }
  ];

  const syncPoints: ChartPoint[] = [
    { x: "pending", y: sync.pendingCount, label: "Pendientes", status: sync.status === "offline" ? "offline" : "ok", meta: {} },
    { x: "failed", y: sync.failedCount, label: "Fallidos", status: sync.status === "blocked" ? "partial" : "ok", meta: {} },
    { x: "freshness", y: sync.freshnessSeconds === null ? null : Math.round(sync.freshnessSeconds / 60), label: "Minutos frescura", status: sync.freshnessSeconds === null ? "unknown" : "ok", meta: { oldestPendingAt: sync.oldestPendingAt } }
  ];

  const cashVariancePoint: ChartPoint = {
    x: "cash-variance",
    y: state.cash.countedCents === null ? null : state.cash.differenceCents,
    label: "Diferencia",
    status: state.cash.countedCents === null ? "unknown" : "ok",
    meta: { expectedCents: state.cash.expectedCents, countedCents: state.cash.countedCents }
  };

  const radarPoints: ChartPoint[] = radar.dimensions.map((dimension) => ({
    x: dimension.key,
    y: dimension.score,
    label: dimension.label,
    status: dimension.score === null ? "unknown" : "ok",
    meta: { status: dimension.status, confidence: dimension.confidence }
  }));

  const topProducts = state.salesToday.sales
    .flatMap((sale) => sale.lines)
    .reduce((map, line) => {
      const current = map.get(line.sku) ?? { sku: line.sku, name: line.name, qty: 0, totalCents: 0 };
      current.qty += line.qty;
      current.totalCents += line.totalCents;
      map.set(line.sku, current);
      return map;
    }, new Map<string, { sku: string; name: string; qty: number; totalCents: number }>())
    .values();

  const topProductPoints = Array.from(topProducts)
    .sort((a, b) => b.totalCents - a.totalCents)
    .slice(0, 6)
    .map((item) => ({ x: item.sku, y: item.totalCents, label: item.name, status: "ok" as const, meta: { qty: item.qty } }));

  return [
    chart({
      chartKey: "operational-health-gauge",
      title: "Salud operativa",
      rangeKey: "today",
      points: [{ x: "health", y: radar.globalScore, label: "Salud", status: radar.globalScore === null ? "unknown" : "ok", meta: { status: radar.status } }],
      unit: "percent",
      summary: radar.globalScore === null ? "Salud sin fuentes suficientes." : `Salud ${radar.globalScore}/100 con modo ${report.runtimeMode}.`,
      emptyState: "Sin fuentes suficientes para calcular salud.",
      source: "HealthRadarEngine",
      confidence: radar.confidence,
      evidence: radar.dimensions.flatMap((dimension) => dimension.evidence).slice(0, 4)
    }),
    chart({
      chartKey: "sales-rhythm-hourly",
      title: "Ritmo de ventas",
      rangeKey: "today",
      points: salesPoints,
      unit: "currency",
      summary: salesPoints.length > 0 ? "Venta real agrupada por hora desde Tablet." : "Sin tickets horarios reales.",
      emptyState: "Cuando Tablet cierre tickets, aparecerá el ritmo por hora.",
      source: "Tablet POS",
      confidence: report.confidence,
      evidence: salesEvidence
    }),
    chart({
      chartKey: "revenue-momentum",
      title: "Momentum de ingresos",
      rangeKey: "today",
      points: cumulative(state.salesToday.hourlyBuckets),
      unit: "currency",
      summary: state.salesToday.hourlyBuckets.length > 0 ? "Tendencia acumulada de venta real del día." : "Sin histórico suficiente para comparar contra 7 días.",
      emptyState: "Sin ventas reales o histórico de 7 días disponible.",
      source: "Tablet POS",
      confidence: report.confidence,
      evidence: salesEvidence
    }),
    chart({
      chartKey: "inventory-risk-ranking",
      title: "Ranking de riesgo de inventario",
      rangeKey: "today",
      points: inventoryPoints,
      unit: "percent",
      summary: inventoryPoints.length > 0 ? "Productos ordenados por riesgo de quiebre operativo." : "No se recibió watchlist de inventario.",
      emptyState: "Inventario no disponible o sin SKUs de riesgo.",
      source: "Tablet POS",
      confidence: report.confidence,
      evidence: [evidence("chart-inventory", "Watchlist", "Tablet POS", `${state.inventory.items.length} SKUs`)]
    }),
    chart({
      chartKey: "alert-severity-donut",
      title: "Severidad de alertas",
      rangeKey: "today",
      points: alertPoints,
      unit: "count",
      summary: alerts.counts.total > 0 ? `${alerts.counts.total} alertas con prioridad y evidencia.` : "Sin alertas activas relevantes.",
      emptyState: "Sin alertas activas.",
      source: "AlertEngine",
      confidence: report.confidence,
      evidence: alerts.alerts.flatMap((alert) => alert.evidence).slice(0, 4)
    }),
    chart({
      chartKey: "sync-freshness-outbox",
      title: "Frescura de sync",
      rangeKey: "today",
      points: syncPoints,
      unit: "count",
      summary: `Sync ${sync.status}; ${sync.pendingCount ?? "?"} pendientes y ${sync.failedCount ?? "?"} fallidos.`,
      emptyState: "Sync no disponible.",
      source: "Tablet POS",
      confidence: report.confidence,
      evidence: sync.evidence
    }),
    chart({
      chartKey: "cash-variance-bullet",
      title: "Variación de caja",
      rangeKey: "today",
      points: [cashVariancePoint],
      unit: "currency",
      summary: state.cash.countedCents === null ? "Sin conteo real de caja; no se calcula variación." : "Esperado contra contado.",
      emptyState: "Caja no cuenta con conteo real.",
      source: "Tablet POS",
      confidence: state.cash.countedCents === null ? 0.4 : report.confidence,
      evidence: [evidence("chart-cash", "Caja", "Tablet POS", state.cash.countedCents === null ? "sin conteo" : state.cash.differenceCents)]
    }),
    chart({
      chartKey: "health-radar-dimensions",
      title: "Radar por dimensión",
      rangeKey: "today",
      points: radarPoints,
      unit: "percent",
      summary: "Dimensiones Tablet, PC, Mobile, Sync, Inventario, Ventas, Caja, Alertas, Core y Control.",
      emptyState: "No hay dimensiones suficientes.",
      source: "HealthRadarEngine",
      confidence: radar.confidence,
      evidence: radar.dimensions.flatMap((dimension) => dimension.evidence).slice(0, 5)
    }),
    chart({
      chartKey: "top-products-ranking",
      title: "Top productos",
      rangeKey: "today",
      points: topProductPoints,
      unit: "currency",
      summary: topProductPoints.length > 0 ? "Productos con mayor venta del día." : "Sin líneas de venta reales para ranking.",
      emptyState: "No hay líneas de venta reales.",
      source: "Tablet POS",
      confidence: report.confidence,
      evidence: [evidence("chart-top-products", "Líneas de venta", "Tablet POS", `${topProductPoints.length} productos`)]
    })
  ];
}
