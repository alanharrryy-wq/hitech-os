import { SaleRepositoryPrisma } from "@/server/repositories/sale-repository.prisma";

const saleRepository = new SaleRepositoryPrisma();

function pesos(cents: number) {
  return cents / 100;
}

function saleTone(status: string) {
  return status === "closed" ? ("ok" as const) : ("warn" as const);
}

export async function getRecentTickets() {
  const sales = await saleRepository.listRecent(6);
  return sales.map((sale) => ({
    folio: sale.folio,
    total: pesos(sale.totalCents),
    items: sale.lines.reduce((acc: number, line: { qty: number }) => acc + line.qty, 0),
    cashier: sale.cashier,
    status: sale.status,
    tone: saleTone(sale.status)
  }));
}

export async function getSalesConsole() {
  const sales = await saleRepository.listRecent(25);
  const recentTickets = sales.slice(0, 6).map((sale) => ({
    folio: sale.folio,
    total: pesos(sale.totalCents),
    items: sale.lines.reduce((acc: number, line: { qty: number }) => acc + line.qty, 0),
    cashier: sale.cashier,
    status: sale.status,
    tone: saleTone(sale.status)
  }));
  const totals = sales.reduce(
    (acc, sale) => ({
      totalCents: acc.totalCents + sale.totalCents,
      lineQty: acc.lineQty + sale.lines.reduce((lineAcc: number, line: { qty: number }) => lineAcc + line.qty, 0)
    }),
    { totalCents: 0, lineQty: 0 }
  );
  const topProductMap = new Map<string, { sku: string; name: string; qty: number; revenue: number }>();
  for (const sale of sales) {
    for (const line of sale.lines) {
      const current = topProductMap.get(line.sku) ?? {
        sku: line.sku,
        name: line.productName,
        qty: 0,
        revenue: 0
      };
      current.qty += line.qty;
      current.revenue += pesos(line.totalCents);
      topProductMap.set(line.sku, current);
    }
  }

  return {
    shift: {
      cashier: sales[0]?.cashier ?? "sin turno",
      openedAt: "ver turno"
    },
    queue: {
      waitingTickets: sales.filter((sale) => sale.status !== "closed").length,
      waitingItems: totals.lineQty
    },
    kpis: {
      netSales: pesos(totals.totalCents),
      tickets: sales.length,
      avgTicket: sales.length ? pesos(totals.totalCents) / sales.length : 0,
      unitsPerTicket: sales.length ? totals.lineQty / sales.length : 0
    },
    recentTickets,
    topProducts: Array.from(topProductMap.values()).sort((a, b) => b.revenue - a.revenue).slice(0, 5),
    alerts: [
      {
        title: "Ventas Prisma activas",
        level: "ok",
        tone: "ok" as const,
        description: "Los tickets recientes se leen desde Sale y SaleLine canónicos.",
        action: "Mantener venta sobre el repositorio Prisma."
      }
    ],
    stockSignals: [],
    replenishment: []
  };
}
