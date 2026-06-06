import { prisma } from "../prisma/client";

export type GetSaleDetailInput = { businessId: string; saleIdOrFolio: string };
type SaleDetailResolvedBy = "scoped" | "local_alias_fallback" | "legacy_date_fallback";
type RawRow = Record<string, unknown>;

function isPrismaDateCoercionError(error: unknown) {
  const maybe = error as { code?: string; message?: string };
  return maybe?.code === "P2023" && /Inconsistent column data|Conversion failed/i.test(String(maybe.message ?? ""));
}

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value : value == null ? fallback : String(value);
}

function asNullableString(value: unknown) {
  const text = asString(value).trim();
  return text ? text : null;
}

function asNumber(value: unknown, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

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


type ReturnLineStatus = "available" | "partial_returned" | "fully_returned";

function clampPositiveInt(value: unknown) {
  const numeric = Number(value ?? 0);
  if (!Number.isFinite(numeric)) return 0;
  return Math.max(0, Math.trunc(numeric));
}

function returnStatusFor(lineQty: number, returnedQty: number): ReturnLineStatus {
  if (returnedQty >= lineQty && lineQty > 0) return "fully_returned";
  if (returnedQty > 0) return "partial_returned";
  return "available";
}

function applyReturnAvailability(lines: any[], rows: RawRow[]) {
  const bySaleLine = new Map<string, number>();
  const byProductFallback = new Map<string, number>();

  for (const row of rows) {
    const qty = clampPositiveInt(row.qty);
    if (!qty) continue;
    const saleLineId = asNullableString(row.saleLineId);
    const productId = asString(row.productId);
    if (saleLineId) {
      bySaleLine.set(saleLineId, (bySaleLine.get(saleLineId) ?? 0) + qty);
    } else if (productId) {
      byProductFallback.set(productId, (byProductFallback.get(productId) ?? 0) + qty);
    }
  }

  return lines.map((line) => {
    const soldQty = clampPositiveInt(line.qty);
    const preciseReturned = clampPositiveInt(bySaleLine.get(line.id));
    const remainingForFallback = Math.max(0, soldQty - preciseReturned);
    const fallbackPool = clampPositiveInt(byProductFallback.get(line.productId));
    const fallbackReturned = Math.min(remainingForFallback, fallbackPool);
    if (fallbackReturned > 0) {
      byProductFallback.set(line.productId, Math.max(0, fallbackPool - fallbackReturned));
    }
    const returnedQty = Math.min(soldQty, preciseReturned + fallbackReturned);
    const returnAvailableQty = Math.max(0, soldQty - returnedQty);
    return {
      ...line,
      returnedQty,
      returnAvailableQty,
      returnedCents: returnedQty * clampPositiveInt(line.priceCents),
      returnStatus: returnStatusFor(soldQty, returnedQty),
    };
  });
}

async function returnedRowsForSale(sale: any) {
  if (!sale?.businessId || !sale?.id) return [];
  return rawRows(
    `SELECT srl.saleLineId, srl.productId, srl.qty
     FROM SaleReturnLine srl
     LEFT JOIN SaleReturn sr ON sr.id = srl.saleReturnId AND sr.businessId = srl.businessId
     WHERE srl.businessId = ?
       AND srl.saleId = ?
       AND COALESCE(sr.status, 'CREATED') <> 'CANCELLED'
     ORDER BY srl.rowid ASC`,
    [sale.businessId, sale.id]
  );
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

async function rawRows<T extends RawRow>(sql: string, params: unknown[] = []) {
  return prisma.$queryRawUnsafe(sql, ...params) as Promise<T[]>;
}

function mapRawOutboxEvent(row: RawRow) {
  return {
    id: asString(row.id),
    topic: asString(row.topic),
    status: asString(row.status),
    idempotencyKey: asNullableString(row.idempotencyKey),
    terminalId: asNullableString(row.terminalId),
    aggregateId: asString(row.aggregateId),
    businessId: asString(row.businessId),
    createdAt: toIso(row.createdAt),
    sentAt: row.sentAt ? toIso(row.sentAt) : null,
    syncedAt: row.syncedAt ? toIso(row.syncedAt) : null,
    lastError: asNullableString(row.lastError)
  };
}

async function outboxEvidenceForSaleRaw(sale: any) {
  const rows = await rawRows(
    `SELECT id, topic, status, idempotencyKey, terminalId, aggregateId, businessId, createdAt, sentAt, syncedAt, lastError
     FROM OutboxEvent
     WHERE businessId = ? AND aggregateId = ?
     ORDER BY rowid ASC`,
    [sale.businessId, sale.id]
  );
  return rows.map(mapRawOutboxEvent);
}

async function outboxEvidenceForSale(sale: any) {
  if (Array.isArray(sale.__rawOutboxEvents)) return sale.__rawOutboxEvents;

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

  return rows.map(mapRawOutboxEvent);
}

async function mapSaleDetail(sale: any, resolvedBy: SaleDetailResolvedBy) {
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
    lines: applyReturnAvailability(
      sale.lines.map((line: any) => ({
        id: line.id,
        productId: line.productId,
        sku: line.sku,
        productName: line.productName,
        qty: line.qty,
        priceCents: line.priceCents,
        totalCents: line.totalCents,
      })),
      await returnedRowsForSale(sale)
    ),
  };
}

function hydrateRawSale(row: RawRow, lines: RawRow[], paymentTenders: RawRow[], outboxEvents: ReturnType<typeof mapRawOutboxEvent>[]) {
  const storeId = asNullableString(row.storeId);
  const store = storeId ? { id: storeId, name: asNullableString(row.storeName) } : null;
  const business = { id: asString(row.businessId), name: asNullableString(row.businessName) };
  const cashSessionId = asNullableString(row.cashSessionId);

  return {
    id: asString(row.id),
    businessId: asString(row.businessId),
    terminalId: asString(row.terminalId),
    cashSessionId,
    clientRequestId: asNullableString(row.clientRequestId),
    folio: asString(row.folio),
    cashier: asString(row.cashier, "tablet-cashier"),
    subtotalCents: asNumber(row.subtotalCents),
    discountCents: asNumber(row.discountCents),
    totalCents: asNumber(row.totalCents),
    completedAt: row.completedAt ?? null,
    paymentMethod: asString(row.paymentMethod, "cash"),
    cashReceivedCents: row.cashReceivedCents == null ? null : asNumber(row.cashReceivedCents),
    changeCents: asNumber(row.changeCents),
    status: asString(row.status),
    createdAt: row.createdAt,
    business,
    terminal: {
      id: asString(row.terminalId),
      name: asNullableString(row.terminalName),
      store,
      business
    },
    cashSession: cashSessionId
      ? {
          id: cashSessionId,
          storeId: asString(row.cashSessionStoreId, storeId ?? ""),
          cashierId: asString(row.cashSessionCashierId),
          cashier: asString(row.cashSessionCashier, asString(row.cashier, "tablet-cashier")),
          status: asString(row.cashSessionStatus),
          openedAt: row.cashSessionOpenedAt ?? row.createdAt,
          closedAt: row.cashSessionClosedAt ?? null,
          store
        }
      : null,
    lines: lines.map((line) => ({
      id: asString(line.id),
      productId: asString(line.productId),
      sku: asString(line.sku),
      productName: asString(line.productName),
      qty: asNumber(line.qty),
      priceCents: asNumber(line.priceCents),
      totalCents: asNumber(line.totalCents),
      createdAt: line.createdAt ?? row.createdAt
    })),
    paymentTenders: paymentTenders.map((tender) => ({
      id: asString(tender.id),
      tenderType: asString(tender.tenderType, asString(row.paymentMethod, "cash")),
      amountCents: asNumber(tender.amountCents),
      reference: asNullableString(tender.reference),
      metadataJson: asNullableString(tender.metadataJson),
      recordedAt: tender.recordedAt ?? row.completedAt ?? row.createdAt
    })),
    __rawOutboxEvents: outboxEvents
  };
}

async function rawSaleByNeedle(input: GetSaleDetailInput, needle: string, scoped: boolean) {
  const where = scoped
    ? `s.businessId = ? AND (s.id = ? OR s.folio = ? OR s.clientRequestId = ?)`
    : `(s.id = ? OR s.folio = ? OR s.clientRequestId = ?)`;
  const params = scoped ? [input.businessId, needle, needle, needle] : [needle, needle, needle];

  const saleRows = await rawRows(
    `SELECT
       s.id, s.businessId, s.terminalId, s.cashSessionId, s.clientRequestId, s.folio, s.cashier,
       s.subtotalCents, s.discountCents, s.totalCents, s.completedAt, s.paymentMethod,
       s.cashReceivedCents, s.changeCents, s.status, s.createdAt,
       t.name AS terminalName,
       b.name AS businessName,
       COALESCE(terminalStore.id, cashStore.id) AS storeId,
       COALESCE(terminalStore.name, cashStore.name) AS storeName,
       cs.storeId AS cashSessionStoreId,
       cs.cashierId AS cashSessionCashierId,
       cs.cashier AS cashSessionCashier,
       cs.status AS cashSessionStatus,
       cs.openedAt AS cashSessionOpenedAt,
       cs.closedAt AS cashSessionClosedAt
     FROM Sale s
     LEFT JOIN Terminal t ON t.id = s.terminalId AND t.businessId = s.businessId
     LEFT JOIN Business b ON b.id = s.businessId
     LEFT JOIN Store terminalStore ON terminalStore.id = t.storeId AND terminalStore.businessId = s.businessId
     LEFT JOIN CashSession cs ON cs.id = s.cashSessionId AND cs.businessId = s.businessId
     LEFT JOIN Store cashStore ON cashStore.id = cs.storeId AND cashStore.businessId = cs.businessId
     WHERE ${where}
     ORDER BY s.rowid DESC
     LIMIT 1`,
    params
  );
  const saleRow = saleRows[0];
  if (!saleRow) return null;

  const saleBusinessId = asString(saleRow.businessId);
  const saleId = asString(saleRow.id);
  const [lines, paymentTenders, outboxEvents] = await Promise.all([
    rawRows(
      `SELECT id, businessId, saleId, productId, sku, productName, qty, priceCents, totalCents, createdAt
       FROM SaleLine
       WHERE businessId = ? AND saleId = ?
       ORDER BY rowid ASC`,
      [saleBusinessId, saleId]
    ),
    rawRows(
      `SELECT id, businessId, saleId, tenderType, amountCents, reference, metadataJson, recordedAt
       FROM SalePaymentTender
       WHERE businessId = ? AND saleId = ?
       ORDER BY rowid ASC`,
      [saleBusinessId, saleId]
    ),
    outboxEvidenceForSaleRaw({ businessId: saleBusinessId, id: saleId })
  ]);

  return hydrateRawSale(saleRow, lines, paymentTenders, outboxEvents);
}

async function getSaleDetailViaLegacyDateFallback(input: GetSaleDetailInput, needle: string) {
  const scopedSale = await rawSaleByNeedle(input, needle, true);
  if (scopedSale) return mapSaleDetail(scopedSale, "legacy_date_fallback");

  const localFallbackSale = await rawSaleByNeedle(input, needle, false);
  if (!localFallbackSale) return null;
  return mapSaleDetail(localFallbackSale, "legacy_date_fallback");
}

export async function getSaleDetail(input: GetSaleDetailInput) {
  const needle = normalizeTicketNeedle(input.saleIdOrFolio);
  if (!needle) return null;

  const or = ticketNeedleWhere(needle);

  let scopedSale;
  try {
    scopedSale = await prisma.sale.findFirst({
      where: { businessId: input.businessId, OR: or },
      include: { lines: true, paymentTenders: true, terminal: { include: { store: true, business: true } }, business: true, cashSession: { include: { store: true } } },
      orderBy: { createdAt: "desc" },
    });
  } catch (error) {
    if (isPrismaDateCoercionError(error)) return getSaleDetailViaLegacyDateFallback(input, needle);
    throw error;
  }

  if (scopedSale) return mapSaleDetail(scopedSale, "scoped");

  // PRISMA_TABLET_TICKET_DETAIL_NOT_FOUND_FIX_01:
  // Fallback local: algunos flujos visuales llegan con businessId omitido, cacheado o
  // diferente al usado al cerrar la venta. El ticket ya vive en la DB local, así que
  // intentamos recuperar por identificadores únicos visibles antes de mostrar 404.
  let localFallbackSale;
  try {
    localFallbackSale = await prisma.sale.findFirst({
      where: { OR: or },
      include: { lines: true, paymentTenders: true, terminal: { include: { store: true, business: true } }, business: true, cashSession: { include: { store: true } } },
      orderBy: { createdAt: "desc" },
    });
  } catch (error) {
    if (isPrismaDateCoercionError(error)) return getSaleDetailViaLegacyDateFallback(input, needle);
    throw error;
  }

  if (!localFallbackSale) return null;
  return mapSaleDetail(localFallbackSale, "local_alias_fallback");
}

function mapRawTicket(row: RawRow) {
  return {
    saleId: asString(row.id),
    folio: asString(row.folio),
    businessId: asString(row.businessId),
    terminalId: asString(row.terminalId),
    clientRequestId: asNullableString(row.clientRequestId),
    status: asString(row.status),
    createdAt: toIso(row.createdAt),
    totalCents: asNumber(row.totalCents),
  };
}

async function rawTicketMatches(input: GetSaleDetailInput, needle: string) {
  const like = `%${needle}%`;
  return rawRows(
    `SELECT id, folio, businessId, terminalId, clientRequestId, status, createdAt, totalCents
     FROM Sale
     WHERE businessId = ? AND (id LIKE ? OR folio LIKE ? OR clientRequestId LIKE ?)
     ORDER BY rowid DESC
     LIMIT 5`,
    [input.businessId, like, like, like]
  );
}

async function rawLatestTickets() {
  return rawRows(
    `SELECT id, folio, businessId, terminalId, clientRequestId, status, createdAt, totalCents
     FROM Sale
     ORDER BY rowid DESC
     LIMIT 5`
  );
}

async function rawOutboxMatches(needle: string) {
  const like = `%${needle}%`;
  return rawRows(
    `SELECT id, topic, aggregateId, businessId, terminalId, status, createdAt, lastError
     FROM OutboxEvent
     WHERE id LIKE ? OR aggregateId LIKE ? OR idempotencyKey LIKE ? OR payloadJson LIKE ?
     ORDER BY rowid DESC
     LIMIT 8`,
    [like, like, like, like]
  );
}

async function rawLatestOutboxEvents() {
  return rawRows(
    `SELECT id, topic, aggregateId, businessId, terminalId, status, createdAt, lastError
     FROM OutboxEvent
     ORDER BY rowid DESC
     LIMIT 8`
  );
}

async function rawSaleCount(whereSql = "", params: unknown[] = []) {
  const rows = await rawRows<{ count: number }>(`SELECT COUNT(*) AS count FROM Sale ${whereSql}`, params);
  return asNumber(rows[0]?.count);
}

async function getSaleLookupDiagnosticRaw(input: GetSaleDetailInput, needle: string, attemptedFields: string[]) {
  const [scopedTickets, latestTickets, matchedOutboxEvents, latestOutboxEvents, scopedTicketCount, totalTicketCount] = await Promise.all([
    needle ? rawTicketMatches(input, needle) : Promise.resolve([]),
    rawLatestTickets(),
    needle ? rawOutboxMatches(needle) : Promise.resolve([]),
    rawLatestOutboxEvents(),
    rawSaleCount("WHERE businessId = ?", [input.businessId]),
    rawSaleCount(),
  ]);

  return {
    requestedId: needle,
    businessId: input.businessId,
    attemptedFields,
    scopedTicketCount,
    totalTicketCount,
    scopedPartialMatches: scopedTickets.map(mapRawTicket),
    latestTickets: latestTickets.map(mapRawTicket),
    matchedOutboxEvents: matchedOutboxEvents.map(mapRawOutboxEvent),
    latestOutboxEvents: latestOutboxEvents.map(mapRawOutboxEvent),
    serverAdapters: [
      "products/tablet/app/app/api/pos/sales/detail/route.ts",
      "products/tablet/app/src/server/pos-api/sales-detail.prisma.ts",
      "products/tablet/app/src/server/prisma/client.ts",
      "legacy-date-fallback: raw SQLite read for P2023 date coercion"
    ],
    nextActions: [
      "Revisar si el folio pertenece a otro negocio o terminal local.",
      "Buscar por clientRequestId desde el recibo o evidencia outbox.",
      "Exportar diagnostico desde License Ops si soporte necesita evidencia.",
    ],
  };
}

export async function getSaleLookupDiagnostic(input: GetSaleDetailInput) {
  const needle = normalizeTicketNeedle(input.saleIdOrFolio);
  const attemptedFields = ["saleId", "folio", "clientRequestId", "local alias fallback"];
  const containsWhere = needle ? ticketNeedleContainsWhere(needle) : [];

  let scopedTickets;
  let latestTickets;
  let matchedOutboxEvents;
  let latestOutboxEvents;
  let scopedTicketCount;
  let totalTicketCount;

  try {
    [scopedTickets, latestTickets, matchedOutboxEvents, latestOutboxEvents, scopedTicketCount, totalTicketCount] = await Promise.all([
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
  } catch (error) {
    if (isPrismaDateCoercionError(error)) return getSaleLookupDiagnosticRaw(input, needle, attemptedFields);
    throw error;
  }

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
