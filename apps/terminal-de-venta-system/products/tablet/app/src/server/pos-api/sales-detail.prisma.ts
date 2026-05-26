import { prisma } from "../prisma/client";

export type GetSaleDetailInput = { businessId: string; saleIdOrFolio: string };

function toIso(value: unknown): string {
  if (value instanceof Date) return value.toISOString();
  if (typeof value === "number") return new Date(value).toISOString();
  if (typeof value === "string") {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toISOString();
  }
  return new Date(0).toISOString();
}

function normalizeTicketNeedle(value: string) {
  return value.trim();
}

function ticketNeedleWhere(needle: string) {
  return [
    { id: needle },
    { folio: needle },
    { clientRequestId: needle },
  ];
}

function ticketNeedleContainsWhere(needle: string) {
  return [
    { id: { contains: needle } },
    { folio: { contains: needle } },
    { clientRequestId: { contains: needle } },
  ];
}

function syntheticPaymentTender(sale: any) {
  return {
    id: `sale-payment-${sale.id}`,
    tenderType: sale.paymentMethod ?? "cash",
    amountCents: sale.totalCents,
    reference: sale.clientRequestId ?? null,
    recordedAt: toIso(sale.completedAt ?? sale.createdAt),
    source: "sale.paymentFields"
  };
}

function mapPaymentTenders(sale: any) {
  const rows = Array.isArray(sale.paymentTenders) ? sale.paymentTenders : [];
  const tenders = rows
    .filter((tender: any) => Number(tender?.amountCents ?? 0) > 0)
    .map((tender: any) => ({
      id: tender.id,
      tenderType: tender.tenderType ?? sale.paymentMethod ?? "cash",
      amountCents: tender.amountCents,
      reference: tender.reference ?? null,
      recordedAt: toIso(tender.recordedAt ?? sale.completedAt ?? sale.createdAt),
      source: "salePaymentTender"
    }));
  return tenders.length ? tenders : [syntheticPaymentTender(sale)];
}

async function outboxEvidenceForSale(sale: any) {
  const rows = await prisma.outboxEvent.findMany({
    where: { businessId: sale.businessId, aggregateId: sale.id },
    orderBy: { createdAt: "asc" },
    select: {
      id: true,
      topic: true,
      status: true,
      idempotencyKey: true,
      terminalId: true,
      createdAt: true,
      sentAt: true,
      syncedAt: true,
      lastError: true
    }
  });

  return rows.map((row: any) => ({
    id: row.id,
    topic: row.topic,
    status: row.status,
    idempotencyKey: row.idempotencyKey,
    terminalId: row.terminalId,
    createdAt: toIso(row.createdAt),
    sentAt: row.sentAt ? toIso(row.sentAt) : null,
    syncedAt: row.syncedAt ? toIso(row.syncedAt) : null,
    lastError: row.lastError ?? null
  }));
}

async function mapSaleDetail(sale: any, resolvedBy: "scoped" | "local_alias_fallback") {
  const outboxEvents = await outboxEvidenceForSale(sale);
  const store = sale.terminal?.store ?? sale.cashSession?.store ?? null;
  const business = sale.terminal?.business ?? sale.business ?? null;
  const paymentTenders = mapPaymentTenders(sale);

  return {
    saleId: sale.id,
    folio: sale.folio,
    canonicalTicketId: sale.id,
    lookupAliases: [sale.id, sale.folio, sale.clientRequestId].filter(Boolean),
    resolvedBy,
    businessId: sale.businessId,
    businessName: business?.name ?? null,
    storeId: store?.id ?? sale.cashSession?.storeId ?? null,
    storeName: store?.name ?? null,
    terminalId: sale.terminalId,
    terminalName: sale.terminal?.name ?? null,
    cashSessionId: sale.cashSessionId ?? null,
    cashSession: sale.cashSession
      ? {
          id: sale.cashSession.id,
          storeId: sale.cashSession.storeId,
          cashierId: sale.cashSession.cashierId,
          cashier: sale.cashSession.cashier,
          status: sale.cashSession.status,
          openedAt: toIso(sale.cashSession.openedAt),
          closedAt: sale.cashSession.closedAt ? toIso(sale.cashSession.closedAt) : null
        }
      : null,
    clientRequestId: sale.clientRequestId ?? null,
    cashier: sale.cashier,
    status: sale.status,
    createdAt: toIso(sale.createdAt),
    completedAt: sale.completedAt ? toIso(sale.completedAt) : null,
    subtotalCents: sale.subtotalCents,
    discountCents: sale.discountCents,
    totalCents: sale.totalCents,
    paymentMethod: sale.paymentMethod ?? "cash",
    cashReceivedCents: sale.cashReceivedCents ?? null,
    changeCents: sale.changeCents ?? 0,
    paymentTenders,
    evidence: {
      contract: "SALE_AS_TICKET_EVIDENCE_V1",
      local: true,
      outboxEvents,
      auditEvents: [],
      evidenceEventIds: outboxEvents.map((event: any) => event.id),
      evidenceTopics: outboxEvents.map((event: any) => event.topic)
    },
    lines: sale.lines.map((line: any) => ({
      id: line.id,
      productId: line.productId,
      sku: line.sku,
      productName: line.productName,
      qty: line.qty,
      priceCents: line.priceCents,
      totalCents: line.totalCents,
    })),
  };
}

export async function getSaleDetail(input: GetSaleDetailInput) {
  const needle = normalizeTicketNeedle(input.saleIdOrFolio);
  if (!needle) return null;

  const or = ticketNeedleWhere(needle);

  const scopedSale = await prisma.sale.findFirst({
    where: { businessId: input.businessId, OR: or },
    include: { lines: true, paymentTenders: true, terminal: { include: { store: true, business: true } }, business: true, cashSession: { include: { store: true } } },
    orderBy: { createdAt: "desc" },
  });

  if (scopedSale) return mapSaleDetail(scopedSale, "scoped");

  // PRISMA_TABLET_TICKET_DETAIL_NOT_FOUND_FIX_01:
  // Fallback local: algunos flujos visuales llegan con businessId omitido, cacheado o
  // diferente al usado al cerrar la venta. El ticket ya vive en la DB local, así que
  // intentamos recuperar por identificadores únicos visibles antes de mostrar 404.
  const localFallbackSale = await prisma.sale.findFirst({
    where: { OR: or },
    include: { lines: true, paymentTenders: true, terminal: { include: { store: true, business: true } }, business: true, cashSession: { include: { store: true } } },
    orderBy: { createdAt: "desc" },
  });

  if (!localFallbackSale) return null;
  return mapSaleDetail(localFallbackSale, "local_alias_fallback");
}

export async function getSaleLookupDiagnostic(input: GetSaleDetailInput) {
  const needle = normalizeTicketNeedle(input.saleIdOrFolio);
  const attemptedFields = ["saleId", "folio", "clientRequestId", "local alias fallback"];
  const containsWhere = needle ? ticketNeedleContainsWhere(needle) : [];

  const [scopedTickets, latestTickets, matchedOutboxEvents, latestOutboxEvents, scopedTicketCount, totalTicketCount] = await Promise.all([
    needle
      ? prisma.sale.findMany({
          where: { businessId: input.businessId, OR: containsWhere },
          orderBy: { createdAt: "desc" },
          take: 5,
          select: {
            id: true,
            folio: true,
            businessId: true,
            terminalId: true,
            clientRequestId: true,
            status: true,
            createdAt: true,
            totalCents: true,
          },
        })
      : Promise.resolve([]),
    prisma.sale.findMany({
      orderBy: { createdAt: "desc" },
      take: 5,
      select: {
        id: true,
        folio: true,
        businessId: true,
        terminalId: true,
        clientRequestId: true,
        status: true,
        createdAt: true,
        totalCents: true,
      },
    }),
    needle
      ? prisma.outboxEvent.findMany({
          where: {
            OR: [
              { id: { contains: needle } },
              { aggregateId: { contains: needle } },
              { idempotencyKey: { contains: needle } },
              { payloadJson: { contains: needle } },
            ],
          },
          orderBy: { createdAt: "desc" },
          take: 8,
          select: {
            id: true,
            topic: true,
            aggregateId: true,
            businessId: true,
            terminalId: true,
            status: true,
            createdAt: true,
            lastError: true,
          },
        })
      : Promise.resolve([]),
    prisma.outboxEvent.findMany({
      orderBy: { createdAt: "desc" },
      take: 8,
      select: {
        id: true,
        topic: true,
        aggregateId: true,
        businessId: true,
        terminalId: true,
        status: true,
        createdAt: true,
        lastError: true,
      },
    }),
    prisma.sale.count({ where: { businessId: input.businessId } }),
    prisma.sale.count(),
  ]);

  const mapTicket = (sale: any) => ({
    saleId: sale.id,
    folio: sale.folio,
    businessId: sale.businessId,
    terminalId: sale.terminalId,
    clientRequestId: sale.clientRequestId ?? null,
    status: sale.status,
    createdAt: toIso(sale.createdAt),
    totalCents: sale.totalCents,
  });

  const mapEvent = (event: any) => ({
    id: event.id,
    topic: event.topic,
    aggregateId: event.aggregateId,
    businessId: event.businessId,
    terminalId: event.terminalId,
    status: event.status,
    createdAt: toIso(event.createdAt),
    lastError: event.lastError ?? null,
  });

  return {
    requestedId: needle,
    businessId: input.businessId,
    attemptedFields,
    scopedTicketCount,
    totalTicketCount,
    scopedPartialMatches: scopedTickets.map(mapTicket),
    latestTickets: latestTickets.map(mapTicket),
    matchedOutboxEvents: matchedOutboxEvents.map(mapEvent),
    latestOutboxEvents: latestOutboxEvents.map(mapEvent),
    serverAdapters: [
      "products/tablet/app/app/api/pos/sales/detail/route.ts",
      "products/tablet/app/src/server/pos-api/sales-detail.prisma.ts",
      "products/tablet/app/src/server/prisma/client.ts",
    ],
    nextActions: [
      "Revisar si el folio pertenece a otro negocio o terminal local.",
      "Buscar por clientRequestId desde el recibo o evidencia outbox.",
      "Exportar diagnostico desde License Ops si soporte necesita evidencia.",
    ],
  };
}
