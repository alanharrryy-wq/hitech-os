import type { OperationMode, OperationWorkspace, PurchaseRow, ReceiptRow, ReplenishmentRow, KpiRow } from "@/modules/operations/types";
import { OperationRepository } from "@/server/repositories/operation.repository";
import { buildOperationAlerts, classifyPurchaseRisk, classifyReceiptDiscrepancy, suggestedReplenishment, validateReplenishmentSignal } from "@/server/validators/procurement-integrity";
import { fillRate, formatKpiMoney, formatKpiNumber, netSales, safeAverage } from "@/server/services/kpi-formulas";

const repository = new OperationRepository();

function dateLabel(value: Date | string | null | undefined) {
  if (!value) return "No disponible";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function sum(values: number[]) {
  return values.reduce((acc, value) => acc + value, 0);
}

function modeText(mode: OperationMode) {
  if (mode === "purchasing") return { title: "Compras", kicker: "compras", description: "Órdenes, proveedores, estatus, pendientes y riesgo operativo." };
  if (mode === "receiving") return { title: "Recepción", kicker: "recepción", description: "Recepciones contra orden, diferencias y evidencia de entrada." };
  if (mode === "replenishment") return { title: "Reabasto", kicker: "reabasto", description: "Señales, prioridad, stock actual, min/max y sugerido." };
  return { title: "Dashboard KPI", kicker: "decisión ejecutiva", description: "KPIs con fórmula, fuente, confianza y rango, sin NaN ni números inventados." };
}

function purchaseRows(orders: any[]): PurchaseRow[] {
  return orders.map((order) => {
    const orderedQty = sum((order.lines ?? []).map((line: any) => Number(line.qtyOrdered ?? 0)));
    const receivedQty = sum((order.goodsReceipts ?? []).flatMap((receipt: any) => receipt.lines ?? []).map((line: any) => Number(line.qtyReceived ?? 0)));
    const pendingQty = Math.max(0, orderedQty - receivedQty);
    const row: PurchaseRow = {
      folio: order.folio ?? order.id,
      supplier: order.supplier?.name ?? "Proveedor no disponible",
      status: order.status ?? "sin estado",
      createdAt: dateLabel(order.createdAt),
      expectedAt: dateLabel(order.expectedAt),
      totalCents: Number(order.totalCents ?? 0),
      linesCount: (order.lines ?? []).length,
      orderedQty,
      receivedQty,
      pendingQty,
      risk: "OK"
    };
    row.risk = classifyPurchaseRisk(row);
    return row;
  });
}

function receiptRows(receipts: any[]): ReceiptRow[] {
  return receipts.map((receipt) => {
    const purchaseLines = new Map<string, any>();
    for (const line of receipt.purchaseOrder?.lines ?? []) {
      if (line.id) purchaseLines.set(line.id, line);
      if (line.sku) purchaseLines.set(line.sku, line);
    }
    let expectedQty = 0;
    let receivedQty = 0;
    let discrepancyCount = 0;
    for (const line of receipt.lines ?? []) {
      const expected = purchaseLines.get(line.purchaseOrderLineId) ?? purchaseLines.get(line.sku);
      const expectedLineQty = Number(expected?.qtyOrdered ?? 0);
      const receivedLineQty = Number(line.qtyReceived ?? 0);
      expectedQty += expectedLineQty;
      receivedQty += receivedLineQty;
      if (expectedLineQty !== receivedLineQty) discrepancyCount += 1;
    }
    const discrepancy = classifyReceiptDiscrepancy(expectedQty, receivedQty);
    return {
      folio: receipt.folio ?? receipt.id,
      purchaseFolio: receipt.purchaseOrder?.folio ?? receipt.purchaseOrderId ?? "sin orden",
      supplier: receipt.supplier?.name ?? "Proveedor no disponible",
      status: receipt.status ?? "sin estado",
      receivedAt: dateLabel(receipt.receivedAt),
      totalCents: Number(receipt.totalCents ?? 0),
      linesCount: (receipt.lines ?? []).length,
      expectedQty,
      receivedQty,
      discrepancyQty: discrepancy.delta,
      discrepancyCount,
      discrepancyLabel: discrepancy.label
    } satisfies ReceiptRow;
  });
}

function replenishmentRows(signals: any[], snapshots: any[]): ReplenishmentRow[] {
  const snapshotByProduct = new Map<string, any>();
  for (const snapshot of snapshots) {
    if (!snapshotByProduct.has(snapshot.productId)) snapshotByProduct.set(snapshot.productId, snapshot);
  }
  return signals.map((signal) => {
    const snapshot = snapshotByProduct.get(signal.productId) ?? signal.product?.stockSnapshots?.[0];
    const currentStock = Number(snapshot?.available ?? snapshot?.onHand ?? signal.product?.stockOnHand ?? 0);
    const minStock = Math.max(1, Math.ceil(currentStock * 0.5));
    const maxStock = Math.max(minStock * 2, currentStock + Number(signal.suggestedQty ?? 0));
    const suggestedQty = Math.max(0, Number(signal.suggestedQty ?? suggestedReplenishment(currentStock, minStock, maxStock)));
    const row: ReplenishmentRow = {
      sku: signal.product?.sku ?? signal.productId,
      name: signal.product?.name ?? "Producto no disponible",
      location: signal.location ?? snapshot?.location ?? "general",
      priority: signal.priority ?? "media",
      currentStock,
      suggestedQty,
      minStock,
      maxStock,
      reason: suggestedQty > 0 ? "Cobertura baja o señal activa." : "Sin sugerido pendiente."
    };
    const findings = validateReplenishmentSignal(row);
    return findings.length ? { ...row, reason: `${row.reason} Validar: ${findings.join(", ")}.` } : row;
  });
}

function kpis(input: { purchases: PurchaseRow[]; receipts: ReceiptRow[]; replenishment: ReplenishmentRow[]; sales: any[]; returns: any[]; snapshots: any[]; }): KpiRow[] {
  const grossSales = sum(input.sales.map((sale) => Number(sale.totalCents ?? 0)));
  const returnsCents = sum(input.returns.map((row) => Number(row.amountCents ?? 0)));
  const netSalesCents = netSales(grossSales, returnsCents, 0, 0);
  const tickets = input.sales.length;
  const averageTicket = safeAverage(netSalesCents, tickets);
  const completedReceipts = input.receipts.filter((row) => ["posted", "received", "cerrada", "recibida"].includes(row.status.toLowerCase())).length;
  const rate = fillRate(completedReceipts, Math.max(input.purchases.length, 0));
  const stockouts = input.snapshots.filter((row) => Number(row.available ?? row.onHand ?? 0) <= 0).length;
  const discrepantReceipts = input.receipts.filter((row) => row.discrepancyCount > 0).length;

  return [
    { key: "net_sales", label: "Ventas netas", value: formatKpiMoney(netSalesCents), formula: "ventas brutas - devoluciones - cancelaciones - descuentos", source: "Sale + SaleReturn", confidence: tickets ? "real" : "missing", range: "últimos registros canónicos", href: "/dashboard", note: "No inventa ventas si no hay persistencia.", status: tickets ? "ok" : "empty" },
    { key: "tickets", label: "Tickets", value: formatKpiNumber(tickets), formula: "conteo de Sale", source: "Sale", confidence: tickets ? "real" : "missing", range: "últimos registros canónicos", href: "/dashboard", note: "Mide volumen operativo consolidado.", status: tickets ? "ok" : "empty" },
    { key: "avg_ticket", label: "Ticket promedio", value: formatKpiMoney(averageTicket), formula: "ventas netas / tickets", source: "Sale + SaleReturn", confidence: averageTicket === null ? "missing" : "real", range: "últimos registros canónicos", href: "/dashboard", note: "Protegido contra división entre cero.", status: averageTicket === null ? "empty" : "ok" },
    { key: "open_orders", label: "Órdenes abiertas", value: formatKpiNumber(input.purchases.length), formula: "conteo de PurchaseOrder", source: "PurchaseOrder", confidence: "real", range: "top 50 por fecha esperada", href: "/purchasing", note: "Pulso de compras pendientes.", status: input.purchases.length ? "warning" : "ok" },
    { key: "receipt_discrepancy", label: "Recepciones con diferencia", value: formatKpiNumber(discrepantReceipts), formula: "recepciones con qty recibida distinta a ordenada", source: "GoodsReceipt + PurchaseOrderLine", confidence: input.receipts.length ? "real" : "missing", range: "top 50 recientes", href: "/receiving", note: "Diferencias contra orden visibles.", status: discrepantReceipts ? "critical" : "ok" },
    { key: "fill_rate", label: "Fill rate", value: rate === null ? "sin datos" : formatKpiNumber(rate * 100, "%"), formula: "recepciones completadas / órdenes", source: "PurchaseOrder + GoodsReceipt", confidence: rate === null ? "missing" : "partial", range: "top 50", href: "/receiving", note: "Proxy operativo hasta cerrar posting completo.", status: rate === null ? "empty" : rate < 0.8 ? "warning" : "ok" },
    { key: "replenishment", label: "Señales de reabasto", value: formatKpiNumber(input.replenishment.length), formula: "conteo de ReplenishmentSignal", source: "ReplenishmentSignal", confidence: "real", range: "top 50 recientes", href: "/replenishment", note: "Prioriza productos con cobertura baja.", status: input.replenishment.length ? "warning" : "ok" },
    { key: "stockouts", label: "Quiebres visibles", value: formatKpiNumber(stockouts), formula: "snapshots con available <= 0", source: "StockSnapshot", confidence: input.snapshots.length ? "real" : "missing", range: "top 250 snapshots", href: "/stock", note: "Conecta tablero con inventario.", status: stockouts ? "critical" : "ok" }
  ];
}

export async function getOperationWorkspace(mode: OperationMode): Promise<OperationWorkspace> {
  const labels = modeText(mode);
  const generatedAt = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date());
  try {
    const [orders, receiptsRaw, signalsRaw, sales, returns, snapshots] = await Promise.all([
      repository.listPurchaseOrders(50),
      repository.listGoodsReceipts(50),
      repository.listReplenishmentSignals(50),
      repository.listSales(250),
      repository.listReturns(250),
      repository.listStockSnapshots(250)
    ]);
    const purchases = purchaseRows(orders);
    const receipts = receiptRows(receiptsRaw);
    const replenishment = replenishmentRows(signalsRaw, snapshots);
    const kpiRows = kpis({ purchases, receipts, replenishment, sales, returns, snapshots });
    const alerts = buildOperationAlerts({ purchases, receipts, replenishment });
    const netSalesCents = netSales(sum(sales.map((sale: any) => Number(sale.totalCents ?? 0))), sum(returns.map((row: any) => Number(row.amountCents ?? 0))), 0, 0);
    const completedReceipts = receipts.filter((row) => ["posted", "received", "cerrada", "recibida"].includes(row.status.toLowerCase())).length;
    return {
      mode,
      ...labels,
      summary: {
        openOrders: purchases.length,
        overdueOrders: purchases.filter((row) => row.risk === "VENCIDA").length,
        receiptsWithDiscrepancy: receipts.filter((row) => row.discrepancyCount > 0).length,
        replenishmentSignals: replenishment.length,
        highPrioritySignals: replenishment.filter((row) => row.priority.toLowerCase().includes("high") || row.priority.toLowerCase().includes("alta")).length,
        netSalesCents,
        tickets: sales.length,
        fillRate: fillRate(completedReceipts, purchases.length)
      },
      purchases,
      receipts,
      replenishment,
      kpis: kpiRows,
      alerts,
      meta: { source: "canonical_prisma", persistence: "available", confidence: "real", generatedAt, warnings: [] }
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Error desconocido leyendo operación.";
    return {
      mode,
      ...labels,
      summary: { openOrders: 0, overdueOrders: 0, receiptsWithDiscrepancy: 0, replenishmentSignals: 0, highPrioritySignals: 0, netSalesCents: 0, tickets: 0, fillRate: null },
      purchases: [],
      receipts: [],
      replenishment: [],
      kpis: [],
      alerts: [],
      meta: { source: "fallback_empty", persistence: "unavailable", confidence: "blocked", generatedAt, warnings: ["No se pudo cargar la información. Revisa la sincronización o la base local."] }
    };
  }
}
