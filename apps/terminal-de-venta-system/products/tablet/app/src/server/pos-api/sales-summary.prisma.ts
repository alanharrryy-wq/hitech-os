import { prisma } from "../prisma/client";
import type { SalesHistoryInput, SalesTodayInput } from "./validators";

const MAX_HISTORY_DAYS = 60;

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

function startOfLocalDay(value: Date) {
  return new Date(value.getFullYear(), value.getMonth(), value.getDate());
}

function parseLocalDate(dateText: string, label: string) {
  const parsed = new Date(`${dateText}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) throw new Error(label);
  return startOfLocalDay(parsed);
}

function historyRange(input: SalesHistoryInput) {
  const today = startOfLocalDay(new Date());
  let from: Date;
  let toExclusive: Date;
  let label: string;

  if (input.preset === "custom") {
    if (!input.from || !input.to) throw new Error("MISSING_HISTORY_RANGE");
    from = parseLocalDate(input.from, "INVALID_HISTORY_FROM");
    const toInclusive = parseLocalDate(input.to, "INVALID_HISTORY_TO");
    toExclusive = new Date(toInclusive);
    toExclusive.setDate(toExclusive.getDate() + 1);
    label = `${input.from} a ${input.to}`;
  } else if (input.preset === "today") {
    from = today;
    toExclusive = new Date(today);
    toExclusive.setDate(toExclusive.getDate() + 1);
    label = "Hoy";
  } else if (input.preset === "yesterday") {
    from = new Date(today);
    from.setDate(from.getDate() - 1);
    toExclusive = new Date(today);
    label = "Ayer";
  } else {
    const days = input.preset === "30d" ? 30 : 7;
    from = new Date(today);
    from.setDate(from.getDate() - (days - 1));
    toExclusive = new Date(today);
    toExclusive.setDate(toExclusive.getDate() + 1);
    label = `Últimos ${days} días`;
  }

  if (toExclusive <= from) throw new Error("INVALID_HISTORY_RANGE");
  const days = Math.ceil((toExclusive.getTime() - from.getTime()) / 86_400_000);
  if (days > MAX_HISTORY_DAYS) throw new Error("HISTORY_RANGE_TOO_LARGE");
  return { from, to: toExclusive, days, label, maxDays: MAX_HISTORY_DAYS };
}

function ticketRows(sales: any[]) {
  return sales.map((sale: any) => ({
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
  }));
}

export async function getTodaySalesSummary(input: SalesTodayInput) {
  const { from, to, date } = localDayRange(input.date);
  const [sales, returns] = await Promise.all([
    prisma.sale.findMany({
      where: {
        businessId: input.businessId,
        status: "COMPLETED",
        createdAt: { gte: from, lt: to },
        ...(input.terminalId ? { terminalId: input.terminalId } : {})
      },
      include: { lines: true },
      orderBy: { createdAt: "desc" }
    }),
    prisma.saleReturn.findMany({
      where: {
        businessId: input.businessId,
        status: { not: "CANCELLED" },
        createdAt: { gte: from, lt: to }
      },
      orderBy: { createdAt: "desc" }
    })
  ]);

  const grossTotalCents = sales.reduce((sum: number, sale: any) => sum + sale.totalCents, 0);
  const returnsTotalCents = returns.reduce((sum: number, row: any) => sum + row.amountCents, 0);
  const netTotalCents = grossTotalCents - returnsTotalCents;
  const unitsSold = sales.flatMap((sale: any) => sale.lines).reduce((sum: number, line: any) => sum + line.qty, 0);
  const topProducts = Array.from(
    sales
      .flatMap((sale: any) => sale.lines)
      .reduce((map: Map<string, any>, line: any) => {
        const key = line.productId || line.sku || line.productName;
        const current = map.get(key) ?? { productId: line.productId, sku: line.sku, productName: line.productName, qty: 0, amountCents: 0 };
        current.qty += line.qty;
        current.amountCents += line.totalCents ?? line.qty * line.priceCents;
        map.set(key, current);
        return map;
      }, new Map<string, any>())
      .values()
  ).sort((a: any, b: any) => b.amountCents - a.amountCents).slice(0, 5);

  return {
    businessId: input.businessId,
    terminalId: input.terminalId ?? null,
    date,
    salesCount: sales.length,
    ticketsClosed: sales.length,
    returnCount: returns.length,
    returnsTotalCents,
    grossTotalCents,
    netTotalCents,
    totalCents: grossTotalCents,
    total: grossTotalCents / 100,
    netTotal: netTotalCents / 100,
    averageTicketCents: sales.length ? Math.round(grossTotalCents / sales.length) : 0,
    averageTicket: sales.length ? Math.round(grossTotalCents / sales.length) / 100 : 0,
    unitsSold,
    topProducts,
    tickets: ticketRows(sales)
  };
}

export async function getSalesHistorySummary(input: SalesHistoryInput) {
  const range = historyRange(input);
  const query = input.query?.trim().toLowerCase() ?? "";
  const where: any = {
    businessId: input.businessId,
    status: "COMPLETED",
    createdAt: { gte: range.from, lt: range.to },
    ...(input.terminalId ? { terminalId: input.terminalId } : {})
  };

  const sales = await prisma.sale.findMany({
    where,
    include: { lines: true },
    orderBy: { createdAt: "desc" },
    take: input.limit
  });

  const filtered = query
    ? sales.filter((sale: any) => {
        const haystack = [
          sale.id,
          sale.folio,
          sale.clientRequestId,
          sale.cashier,
          sale.terminalId,
          ...sale.lines.flatMap((line: any) => [line.sku, line.productName])
        ].filter(Boolean).join(" ").toLowerCase();
        return haystack.includes(query);
      })
    : sales;
  const tickets = ticketRows(filtered).filter((ticket) => ticket.saleId && ticket.saleId !== "undefined");
  const totalCents = tickets.reduce((sum: number, sale: any) => sum + sale.totalCents, 0);
  const returns = await prisma.saleReturn.findMany({
    where: {
      businessId: input.businessId,
      status: { not: "CANCELLED" },
      createdAt: { gte: range.from, lt: range.to }
    }
  });
  const returnsTotalCents = returns.reduce((sum: number, row: any) => sum + row.amountCents, 0);
  const netTotalCents = totalCents - returnsTotalCents;
  const unitsSold = tickets.reduce((sum: number, sale: any) => sum + sale.unitsSold, 0);

  return {
    businessId: input.businessId,
    terminalId: input.terminalId ?? null,
    preset: input.preset,
    range: {
      from: range.from.toISOString(),
      to: new Date(range.to.getTime() - 1).toISOString(),
      days: range.days,
      label: range.label,
      maxDays: range.maxDays
    },
    salesCount: tickets.length,
    ticketsClosed: tickets.length,
    totalCents,
    grossTotalCents: totalCents,
    returnsTotalCents,
    netTotalCents,
    total: totalCents / 100,
    netTotal: netTotalCents / 100,
    averageTicketCents: tickets.length ? Math.round(totalCents / tickets.length) : 0,
    averageTicket: tickets.length ? Math.round(totalCents / tickets.length) / 100 : 0,
    unitsSold,
    topProducts: [],
    tickets,
    meta: {
      source: "tablet_local_prisma",
      bounded: true,
      limit: input.limit,
      blockedOverDays: MAX_HISTORY_DAYS,
      localOnly: true,
      note: "Historial local de Tablet. PC no es requerido para consultar tickets locales."
    }
  };
}
