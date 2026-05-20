import { prisma } from "../prisma/client";
import type { SalesTodayInput } from "./validators";

function toIso(value: unknown): string {
  if (value instanceof Date) return value.toISOString();
  if (typeof value === "number") return new Date(value).toISOString();
  if (typeof value === "string") {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toISOString();
  }
  return new Date(0).toISOString();
}

function localDayRange(dateText?: string) {
  const base = dateText ? new Date(`${dateText}T00:00:00`) : new Date();
  if (Number.isNaN(base.getTime())) throw new Error("INVALID_DATE");
  const from = new Date(base.getFullYear(), base.getMonth(), base.getDate());
  const to = new Date(base.getFullYear(), base.getMonth(), base.getDate() + 1);
  return {
    from,
    to,
    date: `${from.getFullYear()}-${String(from.getMonth() + 1).padStart(2, "0")}-${String(from.getDate()).padStart(2, "0")}`
  };
}

export async function getTodaySalesSummary(input: SalesTodayInput) {
  const { from, to, date } = localDayRange(input.date);
  const sales = await prisma.sale.findMany({
    where: {
      businessId: input.businessId,
      status: "COMPLETED",
      createdAt: { gte: from, lt: to },
      ...(input.terminalId ? { terminalId: input.terminalId } : {})
    },
    include: { lines: true },
    orderBy: { createdAt: "desc" }
  });

  const totalCents = sales.reduce((sum: number, sale: any) => sum + sale.totalCents, 0);
  const unitsSold = sales.flatMap((sale: any) => sale.lines).reduce((sum: number, line: any) => sum + line.qty, 0);
  const topProducts: any[] = [];

  return {
    businessId: input.businessId,
    terminalId: input.terminalId ?? null,
    date,
    salesCount: sales.length,
    ticketsClosed: sales.length,
    totalCents,
    total: totalCents / 100,
    averageTicketCents: sales.length ? Math.round(totalCents / sales.length) : 0,
    averageTicket: sales.length ? Math.round(totalCents / sales.length) / 100 : 0,
    unitsSold,
    topProducts,
    tickets: sales.map((sale: any) => ({
      saleId: sale.id,
      folio: sale.folio,
      businessId: sale.businessId,
      terminalId: sale.terminalId,
      cashSessionId: sale.cashSessionId ?? null,
      clientRequestId: sale.clientRequestId ?? null,
      cashier: sale.cashier,
      status: sale.status,
      createdAt: toIso(sale.createdAt),
      completedAt: sale.completedAt ? toIso(sale.completedAt) : null,
      paymentMethod: sale.paymentMethod ?? "cash",
      totalCents: sale.totalCents,
      lineCount: sale.lines.length,
      unitsSold: sale.lines.reduce((sum: number, line: any) => sum + line.qty, 0),
      lines: sale.lines.map((line: any) => ({
        id: line.id,
        productId: line.productId,
        sku: line.sku,
        productName: line.productName,
        qty: line.qty,
        priceCents: line.priceCents,
        totalCents: line.totalCents
      }))
    }))
  };
}
