import { prisma } from "../prisma/client";
import { getTabletRuntimeMeta } from "../pos-runtime";
import { countOutboxByState, listOutboxEvents, listRecentEvents } from "../pos-outbox";
import { getTodaySalesSummary } from "../pos-api/sales-summary.prisma";
import type { PosListInput } from "../pos-api/validators";

function localDayRange(dateText?: string) {
  const base = dateText ? new Date(`${dateText}T00:00:00`) : new Date();
  if (Number.isNaN(base.getTime())) {
    throw new Error("INVALID_DATE");
  }
  const from = new Date(base.getFullYear(), base.getMonth(), base.getDate(), 0, 0, 0, 0);
  const to = new Date(base.getFullYear(), base.getMonth(), base.getDate() + 1, 0, 0, 0, 0);
  const yyyy = String(from.getFullYear());
  const mm = String(from.getMonth() + 1).padStart(2, "0");
  const dd = String(from.getDate()).padStart(2, "0");
  return { from, to, date: `${yyyy}-${mm}-${dd}` };
}

export function getOperationalDayRange(dateText?: string) {
  return localDayRange(dateText);
}

export async function getRecentEvents(input: PosListInput) {
  return listRecentEvents(input);
}

export async function getOutboxEvents(input: PosListInput) {
  return listOutboxEvents(input);
}

export async function getLowStockProducts(input: PosListInput) {
  const rows = await prisma.product.findMany({
    where: {
      businessId: input.businessId,
      isActive: true,
      stockOnHand: { lte: input.threshold }
    },
    include: { barcodes: true },
    orderBy: [{ stockOnHand: "asc" }, { name: "asc" }],
    take: input.limit
  });

  return rows.map((row: any) => ({
    id: row.id,
    businessId: row.businessId,
    sku: row.sku,
    name: row.name,
    category: row.category,
    barcode: row.barcodes[0]?.code ?? null,
    barcodes: row.barcodes.map((barcode: any) => barcode.code),
    priceCents: row.priceCents,
    stockOnHand: row.stockOnHand,
    lowStockThreshold: input.threshold,
    isActive: row.isActive,
    updatedAt: row.updatedAt.toISOString()
  }));
}

export async function getRecentInventoryMovements(input: PosListInput) {
  const rows = await prisma.stockMovement.findMany({
    where: { businessId: input.businessId },
    include: { product: true },
    orderBy: { createdAt: "desc" },
    take: input.limit
  });

  return rows.map((row: any) => ({
    id: row.id,
    businessId: row.businessId,
    productId: row.productId,
    sku: row.product.sku,
    productName: row.product.name,
    movement: row.movement,
    quantityDelta: row.qty,
    reason: row.reason,
    location: row.location,
    createdAt: row.createdAt.toISOString()
  }));
}

export async function getOperationalTodayReport(input: PosListInput) {
  const range = localDayRange(input.date);
  const [summary, lowStockCount, outboxCounts, recentMovementsCount] = await Promise.all([
    getTodaySalesSummary({
      businessId: input.businessId,
      terminalId: input.terminalId,
      date: input.date
    }),
    prisma.product.count({
      where: {
        businessId: input.businessId,
        isActive: true,
        stockOnHand: { lte: input.threshold }
      }
    }),
    countOutboxByState(input.businessId),
    prisma.stockMovement.count({
      where: {
        businessId: input.businessId,
        createdAt: { gte: range.from, lt: range.to }
      }
    })
  ]);

  return {
    businessId: input.businessId,
    terminalId: input.terminalId ?? null,
    date: range.date,
    range: { from: range.from.toISOString(), to: range.to.toISOString() },
    runtime: getTabletRuntimeMeta(),
    salesCount: summary.salesCount,
    completedSalesCount: summary.ticketsClosed,
    grossTotalCents: summary.totalCents,
    netTotalCents: summary.totalCents,
    totalUnitsSold: summary.unitsSold,
    averageTicketCents: summary.averageTicketCents,
    lowStockCount,
    pendingOutboxCount: outboxCounts.pending,
    failedOutboxCount: outboxCounts.failed,
    outboxCounts,
    recentMovementsCount,
    topProducts: summary.topProducts
  };
}
