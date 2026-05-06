import { prisma } from "@/server/prisma/client";
import { getTodaySalesSummary } from "@/server/pos-api/sales-summary.prisma";
import type { RuntimeSnapshotInput, RuntimeSnapshotQueryResult } from "./types";
import { buildEmptyRuntimeQueryResult } from "./build";

async function resolveBusinessAndTerminal(input: RuntimeSnapshotInput) {
  const terminal = await prisma.terminal.findFirst({
    where: { businessId: input.businessId, id: input.terminalId },
    include: { business: true, store: true }
  });

  if (terminal) {
    return {
      businessName: terminal.business?.name ?? null,
      storeName: terminal.store?.name ?? null,
      terminalName: terminal.name ?? null
    };
  }

  const business = await prisma.business.findFirst({ where: { id: input.businessId } });
  return {
    businessName: business?.name ?? null,
    storeName: null,
    terminalName: null
  };
}

async function resolveOpenShift(input: RuntimeSnapshotInput) {
  const session = await prisma.cashSession.findFirst({
    where: { businessId: input.businessId, terminalId: input.terminalId, status: "OPEN" },
    orderBy: { openedAt: "desc" },
    select: { id: true, openedAt: true, cashier: true }
  });
  return session ? { id: session.id, openedAt: session.openedAt, cashier: session.cashier } : null;
}

async function countOutbox(input: RuntimeSnapshotInput) {
  const [pendingEvents, failedEvents, conflictEvents] = await Promise.all([
    prisma.outboxEvent.count({ where: { businessId: input.businessId, status: "pending" } }),
    prisma.outboxEvent.count({ where: { businessId: input.businessId, status: "failed" } }),
    prisma.outboxEvent.count({ where: { businessId: input.businessId, status: "conflict" } })
  ]);
  return { pendingEvents, failedEvents, conflictEvents };
}

async function resolveCatalog(input: RuntimeSnapshotInput) {
  const [activeProducts, inactiveProducts, stockoutProducts, lastMovement] = await Promise.all([
    prisma.product.count({ where: { businessId: input.businessId, isActive: true } }),
    prisma.product.count({ where: { businessId: input.businessId, isActive: false } }),
    prisma.product.count({ where: { businessId: input.businessId, isActive: true, stockOnHand: { lte: 0 } } }),
    prisma.stockMovement.findFirst({
      where: { businessId: input.businessId },
      orderBy: { createdAt: "desc" },
      select: { createdAt: true }
    })
  ]);
  return {
    activeProducts,
    inactiveProducts,
    lowStockProducts: stockoutProducts,
    lastMovementAt: lastMovement?.createdAt ?? null
  };
}

async function resolveSales(input: RuntimeSnapshotInput) {
  const summary = await getTodaySalesSummary({
    businessId: input.businessId,
    terminalId: input.terminalId,
    date: input.date
  });
  return {
    date: summary.date,
    ticketsClosed: summary.ticketsClosed,
    totalCents: summary.totalCents,
    unitsSold: summary.unitsSold,
    averageTicketCents: summary.averageTicketCents
  };
}

export async function readRuntimeSnapshotFromPrisma(input: RuntimeSnapshotInput): Promise<RuntimeSnapshotQueryResult> {
  const empty = buildEmptyRuntimeQueryResult(input.date);
  const [identity, openShift, outbox, catalog, sales] = await Promise.allSettled([
    resolveBusinessAndTerminal(input),
    resolveOpenShift(input),
    countOutbox(input),
    resolveCatalog(input),
    resolveSales(input)
  ]);

  return {
    businessName: identity.status === "fulfilled" ? identity.value.businessName : empty.businessName,
    storeName: identity.status === "fulfilled" ? identity.value.storeName : empty.storeName,
    terminalName: identity.status === "fulfilled" ? identity.value.terminalName : empty.terminalName,
    openShift: openShift.status === "fulfilled" ? openShift.value : empty.openShift,
    pendingEvents: outbox.status === "fulfilled" ? outbox.value.pendingEvents : empty.pendingEvents,
    failedEvents: outbox.status === "fulfilled" ? outbox.value.failedEvents : empty.failedEvents,
    conflictEvents: outbox.status === "fulfilled" ? outbox.value.conflictEvents : empty.conflictEvents,
    activeProducts: catalog.status === "fulfilled" ? catalog.value.activeProducts : empty.activeProducts,
    inactiveProducts: catalog.status === "fulfilled" ? catalog.value.inactiveProducts : empty.inactiveProducts,
    lowStockProducts: catalog.status === "fulfilled" ? catalog.value.lowStockProducts : empty.lowStockProducts,
    lastMovementAt: catalog.status === "fulfilled" ? catalog.value.lastMovementAt : empty.lastMovementAt,
    sales: sales.status === "fulfilled" ? sales.value : empty.sales
  };
}
