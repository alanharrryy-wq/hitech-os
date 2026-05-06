import type { SalesTodayTicket } from "./types";

export type TicketFilterState = {
  query?: string;
  minTotalCents?: number;
  maxTotalCents?: number;
  cashier?: string;
  status?: string;
  onlyWithReturns?: boolean;
  returnedSaleIds?: string[];
};

export function filterSalesTodayTickets(tickets: SalesTodayTicket[], filters: TicketFilterState) {
  const q = (filters.query ?? "").trim().toLocaleLowerCase("es-MX");
  const returned = new Set(filters.returnedSaleIds ?? []);
  return tickets.filter(ticket => {
    if (q) {
      const haystack = [ticket.folio, ticket.cashier, ticket.status, ...ticket.lines.flatMap(line => [line.sku, line.productName])].join(" ").toLocaleLowerCase("es-MX");
      if (!haystack.includes(q)) return false;
    }
    if (filters.cashier && ticket.cashier !== filters.cashier) return false;
    if (filters.status && ticket.status !== filters.status) return false;
    if (typeof filters.minTotalCents === "number" && ticket.totalCents < filters.minTotalCents) return false;
    if (typeof filters.maxTotalCents === "number" && ticket.totalCents > filters.maxTotalCents) return false;
    if (filters.onlyWithReturns && !returned.has(ticket.saleId)) return false;
    return true;
  });
}

export function groupTicketsByCashier(tickets: SalesTodayTicket[]) {
  const groups = new Map<string, { cashier: string; tickets: number; totalCents: number }>();
  for (const ticket of tickets) {
    const key = ticket.cashier || "Sin operador";
    const group = groups.get(key) ?? { cashier: key, tickets: 0, totalCents: 0 };
    group.tickets += 1;
    group.totalCents += ticket.totalCents;
    groups.set(key, group);
  }
  return [...groups.values()].sort((a, b) => b.totalCents - a.totalCents);
}
