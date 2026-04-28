import { prisma } from "../prisma/client";
import type { SalesTodayInput } from "./validators";

export type PosTodayTopProduct = {
  productId: string;
  sku: string;
  name: string;
  qty: number;
  totalCents: number;
  total: number;
};

export type PosTodaySummary = {
  businessId: string;
  terminalId: string | null;
  date: string;
  range: { from: string; to: string };
  salesCount: number;
  ticketsClosed: number;
  totalCents: number;
  total: number;
  averageTicketCents: number;
  averageTicket: number;
  unitsSold: number;
  topProducts: PosTodayTopProduct[];
};

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

export async function getTodaySalesSummary(input: SalesTodayInput): Promise<PosTodaySummary> {
  const { from, to, date } = localDayRange(input.date);
  const where = {
    businessId: input.businessId,
    status: "COMPLETED",
    createdAt: { gte: from, lt: to },
    ...(input.terminalId ? { terminalId: input.terminalId } : {})
  };

  const sales = await prisma.sale.findMany({
    where,
    include: { lines: true },
    orderBy: { createdAt: "asc" }
  });

  const totalCents = sales.reduce((sum: number, sale: any) => sum + sale.totalCents, 0);
  const unitsSold = sales.flatMap((sale: any) => sale.lines).reduce((sum: number, line: any) => sum + line.qty, 0);
  const topMap = new Map<string, PosTodayTopProduct>();

  for (const sale of sales as any[]) {
    for (const line of sale.lines ?? []) {
      const current = topMap.get(line.productId) ?? {
        productId: line.productId,
        sku: line.sku,
        name: line.productName,
        qty: 0,
        totalCents: 0,
        total: 0
      };
      current.qty += line.qty;
      current.totalCents += line.totalCents;
      current.total = current.totalCents / 100;
      topMap.set(line.productId, current);
    }
  }

  const salesCount = sales.length;
  const averageTicketCents = salesCount ? Math.round(totalCents / salesCount) : 0;

  return {
    businessId: input.businessId,
    terminalId: input.terminalId ?? null,
    date,
    range: { from: from.toISOString(), to: to.toISOString() },
    salesCount,
    ticketsClosed: salesCount,
    totalCents,
    total: totalCents / 100,
    averageTicketCents,
    averageTicket: averageTicketCents / 100,
    unitsSold,
    topProducts: [...topMap.values()].sort((a, b) => b.qty - a.qty || b.totalCents - a.totalCents).slice(0, 10)
  };
}
