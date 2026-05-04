import type { SalesTodayTicket } from "./types";

export type SalesKpiInput = { tickets: SalesTodayTicket[]; returnedSaleIds?: string[] };
export type SalesKpiResult = {
  ticketsClosed: number;
  grossCents: number;
  netCents: number;
  averageTicketCents: number;
  unitsSold: number;
  returnedTickets: number;
  topSkus: Array<{ sku: string; name: string; qty: number; totalCents: number }>;
  hourlyBuckets: Array<{ hour: number; tickets: number; totalCents: number }>;
};

export function buildSalesTodayKpis(input: SalesKpiInput): SalesKpiResult {
  const returned = new Set(input.returnedSaleIds ?? []);
  const top = new Map<string, { sku: string; name: string; qty: number; totalCents: number }>();
  const hourly = new Map<number, { hour: number; tickets: number; totalCents: number }>();
  let grossCents = 0;
  let netCents = 0;
  let unitsSold = 0;
  let returnedTickets = 0;
  for (const ticket of input.tickets) {
    const isReturned = returned.has(ticket.saleId);
    grossCents += ticket.totalCents;
    netCents += isReturned ? 0 : ticket.totalCents;
    returnedTickets += isReturned ? 1 : 0;
    const hour = Number.isNaN(Date.parse(ticket.createdAt)) ? 0 : new Date(ticket.createdAt).getHours();
    const bucket = hourly.get(hour) ?? { hour, tickets: 0, totalCents: 0 };
    bucket.tickets += 1;
    bucket.totalCents += ticket.totalCents;
    hourly.set(hour, bucket);
    for (const line of ticket.lines) {
      unitsSold += line.qty;
      const current = top.get(line.sku) ?? { sku: line.sku, name: line.productName, qty: 0, totalCents: 0 };
      current.qty += line.qty;
      current.totalCents += line.totalCents;
      top.set(line.sku, current);
    }
  }
  return {
    ticketsClosed: input.tickets.length,
    grossCents,
    netCents,
    averageTicketCents: input.tickets.length ? Math.round(netCents / input.tickets.length) : 0,
    unitsSold,
    returnedTickets,
    topSkus: [...top.values()].sort((a, b) => b.qty - a.qty || b.totalCents - a.totalCents).slice(0, 10),
    hourlyBuckets: [...hourly.values()].sort((a, b) => a.hour - b.hour),
  };
}
