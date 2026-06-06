import { prisma } from "../prisma/client";
import { DEFAULT_CASHIER, DEFAULT_TERMINAL_ID, POS_EVENT_SCHEMA_VERSION } from "../pos-engine/constants";
import { makePosId } from "../pos-engine/ids";

function asString(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function asNullableString(value: unknown) {
  const text = asString(value);
  return text || null;
}

function asInt(value: unknown) {
  if (Number.isInteger(value)) return value as number;
  if (typeof value === "number" && Number.isFinite(value)) return Math.trunc(value);
  if (typeof value === "string" && value.trim() && Number.isInteger(Number(value))) return Number(value);
  return null;
}

function restoreStockFor(input: any, line: any) {
  if (line?.restoreStock === true || line?.restoreStock === "true" || line?.restoreStock === "1") return true;
  if (line?.restoreStock === false || line?.restoreStock === "false" || line?.restoreStock === "0") return false;
  const reason = `${input?.reason ?? ""} ${input?.reasonLabel ?? ""}`.toLowerCase();
  return !(reason.includes("damaged") || reason.includes("damage") || reason.includes("defect") || reason.includes("merma"));
}

function normalizeReturnLines(input: any) {
  return (Array.isArray(input.lines) ? input.lines : [])
    .filter((line: any) => line && typeof line === "object")
    .map((line: any, index: number) => {
      const qty = asInt(line.qty) ?? 0;
      const unitPriceCents = asInt(line.unitPriceCents ?? line.priceCents) ?? 0;
      const amountCents = asInt(line.amountCents ?? line.totalCents) ?? qty * unitPriceCents;
      return {
        id: asString(line.id) || makePosId("return_line"),
        saleLineId: asNullableString(line.saleLineId),
        productId: asString(line.productId),
        sku: asString(line.sku),
        productName: asString(line.productName ?? line.name) || asString(line.sku) || `Producto devuelto ${index + 1}`,
        qty,
        unitPriceCents,
        amountCents,
        restoreStock: restoreStockFor(input, line)
      };
    })
    .filter((line: any) => line.productId && line.qty > 0 && line.amountCents > 0);
}

function sumAmount(lines: Array<{ amountCents: number }>) {
  return lines.reduce((sum, line) => sum + line.amountCents, 0);
}

function envelopeBase(input: any, options: { eventId: string; topic: string; terminalId: string; actorId: string; aggregateId: string; correlationId: string; occurredAt: Date; source: string; payload: Record<string, unknown>; }) {
  return {
    eventId: options.eventId,
    eventType: options.topic,
    topic: options.topic,
    idempotencyKey: `${options.topic}:${input.businessId}:${options.terminalId}:${options.aggregateId}:${options.eventId}`,
    businessId: input.businessId,
    terminalId: options.terminalId,
    actorId: options.actorId,
    aggregateId: options.aggregateId,
    correlationId: options.correlationId,
    source: options.source,
    occurredAt: options.occurredAt.toISOString(),
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
    payload: options.payload
  };
}

async function activeCashSession(tx: any, input: any, terminalId: string, sale: any) {
  const requested = asString(input.cashSessionId) || asString(sale?.cashSessionId);
  if (requested) {
    const session = await tx.cashSession.findFirst({ where: { id: requested, businessId: input.businessId } });
    if (session) return session;
  }
  return tx.cashSession.findFirst({ where: { businessId: input.businessId, terminalId, status: "OPEN" }, orderBy: { openedAt: "desc" } });
}

async function validateReturnAgainstSale(tx: any, input: any, normalizedLines: any[]) {
  const saleNeedle = asString(input.saleId);
  const saleFolio = asString(input.saleFolio);
  const sale = await tx.sale.findFirst({
    where: { businessId: input.businessId, OR: [ ...(saleNeedle ? [{ id: saleNeedle }] : []), ...(saleFolio ? [{ folio: saleFolio }] : []) ] },
    include: { lines: true }
  });
  if (!sale) throw new Error("RETURN_SALE_NOT_FOUND");
  const previous = await tx.saleReturnLine.findMany({
    where: { businessId: input.businessId, saleId: sale.id, saleReturn: { status: { not: "CANCELLED" } } },
    select: { saleLineId: true, productId: true, qty: true }
  });
  const returnedBySaleLine = new Map<string, number>();
  const returnedByProduct = new Map<string, number>();
  for (const row of previous) {
    if (row.saleLineId) returnedBySaleLine.set(row.saleLineId, (returnedBySaleLine.get(row.saleLineId) ?? 0) + row.qty);
    returnedByProduct.set(row.productId, (returnedByProduct.get(row.productId) ?? 0) + row.qty);
  }
  for (const line of normalizedLines) {
    const saleLine = line.saleLineId ? sale.lines.find((candidate: any) => candidate.id === line.saleLineId) : sale.lines.find((candidate: any) => candidate.productId === line.productId);
    if (!saleLine) throw new Error("RETURN_QTY_EXCEEDS_AVAILABLE");
    const alreadyReturned = line.saleLineId ? (returnedBySaleLine.get(saleLine.id) ?? 0) : (returnedByProduct.get(line.productId) ?? 0);
    const available = Math.max(0, saleLine.qty - alreadyReturned);
    if (line.qty > available) throw new Error("RETURN_QTY_EXCEEDS_AVAILABLE");
  }
  if (sumAmount(normalizedLines) !== input.amountCents) throw new Error("RETURN_AMOUNT_MISMATCH");
  return sale;
}

export async function createSaleReturn(input: any) {
  const now = new Date();
  const topic = "sale.refunded";
  const terminalId = asString(input.terminalId) || DEFAULT_TERMINAL_ID;
  const actorId = asString(input.actorId ?? input.cashier) || DEFAULT_CASHIER;
  const normalizedLines = normalizeReturnLines(input);
  if (!normalizedLines.length) throw new Error("RETURN_LINES_REQUIRED");
  const db = prisma as any;
  return db.$transaction(async (tx: any) => {
    const sale = await validateReturnAgainstSale(tx, input, normalizedLines);
    const cashSession = await activeCashSession(tx, input, terminalId, sale);
    const saleReturn = await tx.saleReturn.create({ data: { id: makePosId("return"), businessId: input.businessId, saleFolio: input.saleFolio, reason: input.reasonLabel || input.reason, amountCents: input.amountCents, status: "CREATED", cashier: input.cashier, createdAt: now } });
    let cashMovement: any = null;
    if (cashSession?.id) {
      cashMovement = await tx.cashMovement.create({ data: { id: makePosId("cash_refund"), businessId: input.businessId, cashSessionId: cashSession.id, movement: "REFUND", amountCents: -Math.abs(input.amountCents), reason: `Devolución ${input.saleFolio}`, createdAt: now } });
    }
    for (const [index, line] of normalizedLines.entries()) {
      const product = await tx.product.findFirst({ where: { id: line.productId, businessId: input.businessId } });
      const stockMovementId = line.restoreStock ? makePosId("stock_return") : null;
      if (line.restoreStock && product) {
        await tx.stockMovement.create({ data: { id: stockMovementId, businessId: input.businessId, productId: line.productId, movement: "return", qty: line.qty, reason: topic, location: "tablet-floor", beforeQty: product.stockOnHand, afterQty: product.stockOnHand + line.qty, sourceType: topic, sourceId: saleReturn.id, createdAt: now } });
        await tx.product.update({ where: { id: line.productId }, data: { stockOnHand: { increment: line.qty } } });
      }
      await tx.saleReturnLine.create({ data: { id: line.id || `${saleReturn.id}_line_${index + 1}`, businessId: input.businessId, saleReturnId: saleReturn.id, saleId: sale.id, saleLineId: line.saleLineId, productId: line.productId, sku: line.sku || product?.sku || line.productId, productName: line.productName || product?.name || line.productId, qty: line.qty, amountCents: line.amountCents, restoreStock: line.restoreStock, stockMovementId, createdAt: now } });
    }
    const returnEventId = makePosId("event");
    const cashMovementPayload = cashMovement ? { cashMovementId: cashMovement.id, cashSessionId: cashMovement.cashSessionId, movement: cashMovement.movement, amountCents: cashMovement.amountCents, reason: cashMovement.reason, createdAt: now.toISOString() } : null;
    const returnEnvelope = envelopeBase(input, { eventId: returnEventId, topic, terminalId, actorId, aggregateId: saleReturn.id, correlationId: sale.id || input.saleFolio || saleReturn.id, source: "tablet-pos-contextual-return", occurredAt: now, payload: { returnId: saleReturn.id, saleId: sale.id, saleFolio: input.saleFolio, reason: input.reason || "other", reasonLabel: input.reasonLabel || saleReturn.reason, notes: input.notes || null, amountCents: input.amountCents, cashier: input.cashier || actorId, terminalId, cashSessionId: cashSession?.id ?? null, cashMovementId: cashMovement?.id ?? null, cashImpact: cashMovementPayload, actorId, lines: normalizedLines } });
    await tx.outboxEvent.create({ data: { id: returnEventId, businessId: input.businessId, terminalId, topic, aggregateId: saleReturn.id, idempotencyKey: returnEnvelope.idempotencyKey, status: "pending", createdAt: now, source: returnEnvelope.source, schemaVersion: POS_EVENT_SCHEMA_VERSION, payloadJson: JSON.stringify(returnEnvelope) } });
    const events = [topic];
    if (cashMovement) {
      const cashEnvelope = envelopeBase(input, { eventId: cashMovement.id, topic: "cash.movement.recorded", terminalId, actorId, aggregateId: cashMovement.cashSessionId, correlationId: saleReturn.id, source: "tablet-pos-contextual-return", occurredAt: now, payload: { cashMovementId: cashMovement.id, cashSessionId: cashMovement.cashSessionId, movement: cashMovement.movement, amountCents: cashMovement.amountCents, reason: cashMovement.reason, saleReturnId: saleReturn.id, saleId: sale.id, saleFolio: input.saleFolio, createdAt: now.toISOString() } });
      await tx.outboxEvent.create({ data: { id: cashMovement.id, businessId: input.businessId, terminalId, topic: "cash.movement.recorded", aggregateId: cashMovement.cashSessionId, idempotencyKey: cashEnvelope.idempotencyKey, status: "pending", createdAt: now, source: cashEnvelope.source, schemaVersion: POS_EVENT_SCHEMA_VERSION, payloadJson: JSON.stringify(cashEnvelope) } });
      events.push("cash.movement.recorded");
    }
    return { returnId: saleReturn.id, saleId: sale.id, saleFolio: saleReturn.saleFolio, reason: saleReturn.reason, amountCents: saleReturn.amountCents, status: saleReturn.status, cashier: saleReturn.cashier, createdAt: saleReturn.createdAt, lineCount: normalizedLines.length, cashImpact: cashMovementPayload, topic, events };
  });
}
