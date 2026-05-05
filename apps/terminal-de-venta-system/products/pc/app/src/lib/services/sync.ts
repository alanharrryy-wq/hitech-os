import { OutboxRepositoryPrisma } from "@/server/repositories/outbox-repository.prisma";
import { StockRepositoryPrisma } from "@/server/repositories/stock-repository.prisma";

const outbox = new OutboxRepositoryPrisma();
const stock = new StockRepositoryPrisma();

function ageLabel(value: Date | string) {
  const created = new Date(value).getTime();
  const fixedNow = new Date("2026-04-18T18:05:00.000Z").getTime();
  const seconds = Math.max(0, Math.round((fixedNow - created) / 1000));
  return `${seconds}s`;
}

export async function getOutboxConsole() {
  const pending = await outbox.listPending(50);
  const statusSummary = new Map<string, number>();
  for (const row of pending) {
    statusSummary.set(row.status, (statusSummary.get(row.status) ?? 0) + 1);
  }
  return {
    outboxStatusSummary: Array.from(statusSummary.entries()).map(([status, total]) => ({ status, total })),
    outboxPending: pending.map((row) => ({
      id: row.id,
      topic: row.topic,
      aggregateId: row.aggregateId,
      status: row.status,
      age: ageLabel(row.createdAt)
    }))
  };
}

export async function getReplenishmentConsole() {
  const signals = await stock.listReplenishmentSignals(25);
  const summary = new Map<string, { total: number; qty: number }>();
  for (const signal of signals) {
    const current = summary.get(signal.priority) ?? { total: 0, qty: 0 };
    current.total += 1;
    current.qty += signal.suggestedQty;
    summary.set(signal.priority, current);
  }
  return {
    replenishmentSummary: Array.from(summary.entries()).map(([priority, row]) => ({
      priority,
      total: row.total,
      qty: row.qty
    })),
    topSignals: signals.map((signal) => ({
      id: signal.id,
      sku: signal.product.sku,
      name: signal.product.name,
      category: signal.product.category,
      location: signal.location,
      suggestedQty: signal.suggestedQty,
      priority: signal.priority,
      createdAt: new Date(signal.createdAt).toISOString()
    }))
  };
}
