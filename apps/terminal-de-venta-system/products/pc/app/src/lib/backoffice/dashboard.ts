import { prisma } from "@/server/prisma/client";

export type BackofficeKpi = {
  key: string;
  label: string;
  value: string;
  note: string;
  status: "supported" | "partial" | "unavailable";
  source: string;
  tone: "ok" | "warn" | "danger" | "neutral";
};

export type BackofficeDashboard = {
  kpis: BackofficeKpi[];
  topSkus: Array<{ sku: string; productName: string; qty: number; totalCents: number }>;
  sync: {
    pendingEvents: number;
    failedEvents: number;
    conflictCount: number;
    lastIngestAt: string | null;
    lastOutboxEventAt: string | null;
    healthLabel: string;
    dataSourceFreshness: Array<Record<string, unknown>>;
    outboxStatusBuckets: Array<Record<string, unknown>>;
  };
  meta: {
    source: "canonical_prisma";
    persistence: "available" | "unavailable";
    hasConsolidatedEvents: boolean;
    generatedAt: string;
    warnings: string[];
  };
};

const EMPTY_DASHBOARD: BackofficeDashboard = {
  kpis: [
    { key: "netSalesTodayCents", label: "Ventas netas del día", value: "$0", note: "Aún no hay eventos consolidados.", status: "supported", source: "Sale", tone: "neutral" },
    { key: "ticketCountToday", label: "Tickets", value: "0", note: "Sin tickets consolidados para hoy.", status: "supported", source: "Sale", tone: "neutral" },
    { key: "averageTicketCents", label: "Ticket promedio", value: "No disponible", note: "Se calcula cuando existan ventas reales.", status: "supported", source: "Sale", tone: "neutral" },
    { key: "topSkus", label: "Top SKUs", value: "0", note: "Sin líneas de venta para ranking.", status: "supported", source: "SaleLine", tone: "neutral" },
    { key: "lowStockCount", label: "Quiebres de existencias", value: "0", note: "Sin cortes críticos disponibles.", status: "supported", source: "StockSnapshot", tone: "neutral" },
    { key: "inventoryAccuracy", label: "Exactitud de inventario", value: "Parcial", note: "Proxy por conteos/variaciones; requiere ciclo completo de conteo para exactitud real.", status: "partial", source: "AuditCount", tone: "warn" },
    { key: "shrinkage", label: "Merma", value: "No disponible", note: "No existe modelo durable de merma/costo perdido todavía.", status: "unavailable", source: "Sin fuente canónica", tone: "neutral" },
    { key: "cancellationsReturns", label: "Cancelaciones/devoluciones", value: "0", note: "Proxy por SaleReturn y Sale cancelada.", status: "partial", source: "SaleReturn + Sale", tone: "neutral" },
    { key: "fillRate", label: "Fill rate", value: "Parcial", note: "Proxy por cantidades ordenadas/recibidas; no sustituye cumplimiento por línea.", status: "partial", source: "PurchaseOrderLine + GoodsReceiptLine", tone: "warn" },
    { key: "offlineModeUsage", label: "Uso de modo offline", value: "No disponible", note: "Tablet aún no persiste una marca durable de modo offline por venta.", status: "unavailable", source: "Sin fuente canónica", tone: "neutral" },
    { key: "syncLatency", label: "Latencia de sincronización", value: "Parcial", note: "Derivada de OutboxEvent cuando hay sentAt/createdAt.", status: "partial", source: "OutboxEvent", tone: "warn" },
    { key: "pendingEvents", label: "Eventos pendientes", value: "0", note: "Outbox canónico sin pendientes leídos.", status: "supported", source: "OutboxEvent", tone: "neutral" },
    { key: "conflictCount", label: "Conflictos", value: "0", note: "OutboxEvent marcado como conflict.", status: "supported", source: "OutboxEvent", tone: "neutral" }
  ],
  topSkus: [],
  sync: {
    pendingEvents: 0,
    failedEvents: 0,
    conflictCount: 0,
    lastIngestAt: null,
    lastOutboxEventAt: null,
    healthLabel: "sin eventos consolidados",
    dataSourceFreshness: [],
    outboxStatusBuckets: []
  },
  meta: {
    source: "canonical_prisma",
    persistence: "available",
    hasConsolidatedEvents: false,
    generatedAt: "",
    warnings: []
  }
};

function moneyFromCents(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

function dayRange() {
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setDate(end.getDate() + 1);
  return { start, end };
}

function normalizeStatus(status: string) {
  return [status, status.toLowerCase(), status.toUpperCase()];
}

function buildHealthLabel(pending: number, failed: number, conflicts: number, totalEvents: number) {
  if (conflicts > 0) return "conflictos por revisar";
  if (failed > 0) return "requiere atención";
  if (pending > 0) return "pendiente de consolidación";
  if (totalEvents > 0) return "sin pendientes visibles";
  return "sin eventos consolidados";
}

function kpi(input: BackofficeKpi): BackofficeKpi {
  return input;
}

async function readManyIfAvailable(modelName: string, args: Record<string, unknown>) {
  const model = (prisma as any)[modelName];
  if (!model?.findMany) return [];
  try {
    return await model.findMany(args);
  } catch {
    return [];
  }
}

export async function getBackofficeDashboard(): Promise<BackofficeDashboard> {
  const generatedAt = new Date().toISOString();
  const { start, end } = dayRange();

  try {
    const [
      salesAggregate,
      ticketCount,
      todayLines,
      lowStockCount,
      pendingEvents,
      failedEvents,
      conflictCount,
      lastOutbox,
      returnCount,
      cancelledSalesCount,
      auditCounts,
      purchaseLineAggregate,
      receiptLineAggregate,
      latencyRows,
      dataSourceFreshness,
      outboxStatusBuckets
    ] = await Promise.all([
      prisma.sale.aggregate({
        where: { status: { in: normalizeStatus("COMPLETED") }, createdAt: { gte: start, lt: end } },
        _sum: { totalCents: true }
      }),
      prisma.sale.count({
        where: { status: { in: normalizeStatus("COMPLETED") }, createdAt: { gte: start, lt: end } }
      }),
      prisma.saleLine.findMany({
        where: { createdAt: { gte: start, lt: end } },
        orderBy: { createdAt: "desc" },
        take: 500
      }),
      prisma.stockSnapshot.count({ where: { daysCover: { lt: 2 } } }),
      prisma.outboxEvent.count({ where: { status: { in: normalizeStatus("pending") } } }),
      prisma.outboxEvent.count({ where: { status: { in: normalizeStatus("failed") } } }),
      prisma.outboxEvent.count({ where: { status: { in: normalizeStatus("conflict") } } }),
      prisma.outboxEvent.findFirst({ orderBy: { createdAt: "desc" } }),
      prisma.saleReturn.count({ where: { createdAt: { gte: start, lt: end } } }),
      prisma.sale.count({ where: { status: { in: normalizeStatus("CANCELLED") }, createdAt: { gte: start, lt: end } } }),
      prisma.auditCount.findMany({ orderBy: { countedAt: "desc" }, take: 100 }),
      prisma.purchaseOrderLine.aggregate({ _sum: { qtyOrdered: true } }),
      prisma.goodsReceiptLine.aggregate({ _sum: { qtyReceived: true } }),
      prisma.outboxEvent.findMany({ where: { sentAt: { not: null } }, orderBy: { sentAt: "desc" }, take: 100 }),
      readManyIfAvailable("dataSourceFreshness", { orderBy: { updatedAt: "desc" }, take: 10 }),
      readManyIfAvailable("syncOutboxStatusBucket", { orderBy: { bucketStartAt: "desc" }, take: 20 })
    ]);

    const skuMap = new Map<string, { sku: string; productName: string; qty: number; totalCents: number }>();
    for (const line of todayLines) {
      const current = skuMap.get(line.sku) ?? { sku: line.sku, productName: line.productName, qty: 0, totalCents: 0 };
      current.qty += line.qty;
      current.totalCents += line.totalCents;
      skuMap.set(line.sku, current);
    }

    const netSalesTodayCents = salesAggregate._sum.totalCents ?? 0;
    const averageTicketCents = ticketCount > 0 ? Math.round(netSalesTodayCents / ticketCount) : 0;
    const totalEvents = pendingEvents + failedEvents + conflictCount;
    const topSkus = Array.from(skuMap.values()).sort((a, b) => b.totalCents - a.totalCents).slice(0, 5);
    const auditCountRows = auditCounts as Array<{ variance: number }>;
    const outboxLatencyRows = latencyRows as Array<{ sentAt: Date | null; createdAt: Date }>;
    const varianceCount = auditCountRows.filter((row) => row.variance !== 0).length;
    const inventoryAccuracyValue = auditCountRows.length
      ? `${Math.round(((auditCountRows.length - varianceCount) / auditCountRows.length) * 100)}%`
      : "Sin conteos";
    const cancellationsReturns = returnCount + cancelledSalesCount;
    const qtyOrdered = purchaseLineAggregate._sum.qtyOrdered ?? 0;
    const qtyReceived = receiptLineAggregate._sum.qtyReceived ?? 0;
    const fillRateValue = qtyOrdered > 0 ? `${Math.round((qtyReceived / qtyOrdered) * 100)}%` : "Sin órdenes";
    const latencySamples = outboxLatencyRows
      .filter((row) => row.sentAt)
      .map((row) => Math.max(0, row.sentAt!.getTime() - row.createdAt.getTime()));
    const averageSyncLatencyMs = latencySamples.length
      ? Math.round(latencySamples.reduce((sum, value) => sum + value, 0) / latencySamples.length)
      : null;
    const warnings: string[] = [];

    if (ticketCount === 0 && totalEvents === 0) {
      warnings.push("Aún no hay eventos consolidados.");
    }
    if (lastOutbox?.createdAt) {
      warnings.push("La última recepción usa la bandeja operativa como registro durable mínimo.");
    }

    return {
      kpis: [
        kpi({
          key: "netSalesTodayCents",
          label: "Ventas netas del día",
          value: moneyFromCents(netSalesTodayCents),
          note: ticketCount > 0 ? "Calculado desde Sale canónico." : "Aún no hay eventos consolidados.",
          status: "supported",
          source: "Sale.aggregate(totalCents)",
          tone: ticketCount > 0 ? "ok" : "neutral"
        }),
        kpi({
          key: "ticketCountToday",
          label: "Tickets",
          value: String(ticketCount),
          note: "Conteo de ventas COMPLETED del día.",
          status: "supported",
          source: "Sale.count(COMPLETED)",
          tone: ticketCount > 0 ? "ok" : "neutral"
        }),
        kpi({
          key: "averageTicketCents",
          label: "Ticket promedio",
          value: ticketCount > 0 ? moneyFromCents(averageTicketCents) : "No disponible",
          note: ticketCount > 0 ? "Ventas netas / tickets." : "Se calcula cuando existan ventas reales.",
          status: "supported",
          source: "Sale.aggregate / Sale.count",
          tone: ticketCount > 0 ? "ok" : "neutral"
        }),
        kpi({
          key: "topSkus",
          label: "Top SKUs",
          value: String(topSkus.length),
          note: topSkus.length ? "Ranking calculado desde SaleLine del día." : "Sin líneas de venta para ranking.",
          status: "supported",
          source: "SaleLine",
          tone: topSkus.length ? "ok" : "neutral"
        }),
        kpi({
          key: "lowStockCount",
          label: "Quiebres de existencias",
          value: String(lowStockCount),
          note: "Cortes de inventario con cobertura menor a dos días.",
          status: "supported",
          source: "StockSnapshot(daysCover < 2)",
          tone: lowStockCount > 0 ? "warn" : "ok"
        }),
        kpi({
          key: "inventoryAccuracy",
          label: "Exactitud de inventario",
          value: inventoryAccuracyValue,
          note: auditCounts.length ? "Proxy: conteos sin variación / conteos recientes." : "Parcial: requiere conteos físicos para medir exactitud real.",
          status: "partial",
          source: "AuditCount",
          tone: auditCounts.length && varianceCount === 0 ? "ok" : "warn"
        }),
        kpi({
          key: "shrinkage",
          label: "Merma",
          value: "No disponible",
          note: "Sin modelo durable de merma o costo perdido en el schema actual.",
          status: "unavailable",
          source: "Sin fuente canónica",
          tone: "neutral"
        }),
        kpi({
          key: "cancellationsReturns",
          label: "Cancelaciones/devoluciones",
          value: String(cancellationsReturns),
          note: "Parcial: suma SaleReturn y Sale CANCELLED del día.",
          status: "partial",
          source: "SaleReturn + Sale(CANCELLED)",
          tone: cancellationsReturns > 0 ? "warn" : "neutral"
        }),
        kpi({
          key: "fillRate",
          label: "Fill rate",
          value: fillRateValue,
          note: "Parcial: qtyReceived / qtyOrdered; no sustituye conciliación por línea.",
          status: "partial",
          source: "PurchaseOrderLine + GoodsReceiptLine",
          tone: qtyOrdered > 0 && qtyReceived < qtyOrdered ? "warn" : "neutral"
        }),
        kpi({
          key: "offlineModeUsage",
          label: "Uso de modo offline",
          value: "No disponible",
          note: "Tablet aún no persiste marca de modo offline por venta/evento.",
          status: "unavailable",
          source: "Sin fuente canónica",
          tone: "neutral"
        }),
        kpi({
          key: "syncLatency",
          label: "Latencia de sincronización",
          value: averageSyncLatencyMs === null ? "Parcial" : `${Math.round(averageSyncLatencyMs / 1000)}s`,
          note: averageSyncLatencyMs === null ? "Parcial: faltan marcas de envío suficientes." : "Promedio entre creación y envío en la bandeja operativa.",
          status: "partial",
          source: "OutboxEvent(sentAt, createdAt)",
          tone: averageSyncLatencyMs === null ? "warn" : "ok"
        }),
        kpi({
          key: "pendingEvents",
          label: "Eventos pendientes",
          value: String(pendingEvents),
          note: "Evento pendiente de envío o consolidación.",
          status: "supported",
          source: "OutboxEvent(status=pending)",
          tone: pendingEvents > 0 ? "warn" : "ok"
        }),
        kpi({
          key: "conflictCount",
          label: "Conflictos",
          value: String(conflictCount),
          note: "Evento marcado como conflicto.",
          status: "supported",
          source: "OutboxEvent(status=conflict)",
          tone: conflictCount > 0 ? "danger" : "ok"
        })
      ],
      topSkus,
      sync: {
        pendingEvents,
        failedEvents,
        conflictCount,
        lastIngestAt: lastOutbox?.createdAt ? lastOutbox.createdAt.toISOString() : null,
        lastOutboxEventAt: lastOutbox?.createdAt ? lastOutbox.createdAt.toISOString() : null,
        healthLabel: buildHealthLabel(pendingEvents, failedEvents, conflictCount, totalEvents),
        dataSourceFreshness: dataSourceFreshness as Array<Record<string, unknown>>,
        outboxStatusBuckets: outboxStatusBuckets as Array<Record<string, unknown>>
      },
      meta: {
        source: "canonical_prisma",
        persistence: "available",
        hasConsolidatedEvents: ticketCount > 0 || totalEvents > 0,
        generatedAt,
        warnings
      }
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Error desconocido al leer Prisma.";
    return {
      ...EMPTY_DASHBOARD,
      meta: {
        source: "canonical_prisma",
        persistence: "unavailable",
        hasConsolidatedEvents: false,
        generatedAt,
        warnings: ["Aún no hay eventos consolidados.", `No fue posible leer persistencia canónica: ${message}`]
      }
    };
  }
}
