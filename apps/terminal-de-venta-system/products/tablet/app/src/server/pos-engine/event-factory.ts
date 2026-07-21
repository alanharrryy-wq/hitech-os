import crypto from "node:crypto";
import {
  POS_EVENT_SCHEMA_VERSION,
  POS_EVENT_INVENTORY_LOW_STOCK_DETECTED,
  POS_EVENT_SOURCE,
  POS_EVENT_SALE_COMPLETED,
  POS_EVENT_SALE_CREATED,
  POS_EVENT_STOCK_DECREMENTED,
  POS_EVENT_TICKET_CLOSED
} from "./constants";
import { makePosId } from "./ids";
import type { CompleteLocalSaleResult, PosEngineEvent, PosSaleLineResult } from "./types";

export const POS_ENGINE_EVENT_FACTORY_TOPICS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected",
  "cash.session.opened",
  "cash.movement.recorded"
] as const;

const POS_EVENT_VERSION = "1.0.0";

type PosEventContext = {
  tenantId?: string;
  customerId?: string;
  businessId: string;
  storeId?: string;
  terminalId: string;
  deviceId?: string;
  actorId: string;
  occurredAt: Date;
  correlationId?: string;
  causationId?: string;
  traceId?: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (!isRecord(value)) return value;
  return Object.keys(value).sort().reduce<Record<string, unknown>>((acc, key) => {
    acc[key] = stable(value[key]);
    return acc;
  }, {});
}

function sha256(value: unknown) {
  return crypto.createHash("sha256").update(JSON.stringify(stable(value))).digest("hex");
}

function pick(...values: unknown[]) {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function sequenceFor(at: Date, eventId: string) {
  const suffix = [...eventId].reduce((sum, char) => (sum + char.charCodeAt(0)) % 1000, 0);
  return at.getTime() * 1000 + suffix;
}

function makeSubject(input: {
  tenantId: string;
  businessId: string;
  storeId: string;
  terminalId: string;
  deviceId: string;
  topic: string;
  aggregateId: string;
}) {
  return [
    "prisma://sync",
    encodeURIComponent(input.tenantId || "unresolved-tenant"),
    encodeURIComponent(input.businessId),
    encodeURIComponent(input.storeId || "unresolved-store"),
    encodeURIComponent(input.terminalId),
    encodeURIComponent(input.deviceId),
    encodeURIComponent(input.topic),
    encodeURIComponent(input.aggregateId)
  ].join("/");
}

function makeEvent(topic: string, aggregateId: string, context: PosEventContext, payload: Record<string, unknown>): PosEngineEvent {
  const eventId = makePosId("evt");
  const capturedAt = context.occurredAt.toISOString();
  const tenantId = pick(context.tenantId, process.env.PRISMA_TENANT_ID, process.env.NEXT_PUBLIC_PRISMA_TENANT_ID);
  const customerId = pick(context.customerId, process.env.PRISMA_CUSTOMER_ID, process.env.NEXT_PUBLIC_PRISMA_CUSTOMER_ID);
  const storeId = pick(context.storeId, process.env.PRISMA_TABLET_STORE_ID, process.env.NEXT_PUBLIC_PRISMA_TABLET_STORE_ID);
  const deviceId = pick(context.deviceId, process.env.PRISMA_TABLET_DEVICE_ID, process.env.NEXT_PUBLIC_PRISMA_TABLET_DEVICE_ID, context.terminalId);
  const originRecordId = pick(payload.saleId, payload.returnId, payload.productId, payload.cashSessionId, aggregateId);
  const correlationId = pick(context.correlationId, aggregateId);
  const causationId = pick(context.causationId, correlationId);
  const traceId = pick(context.traceId, correlationId, eventId);
  const idempotencyScope = typeof payload.saleId === "string" ? `${aggregateId}:${payload.saleId}` : aggregateId;
  const payloadHash = sha256(payload);

  return {
    eventId,
    source: POS_EVENT_SOURCE,
    subject: makeSubject({ tenantId, businessId: context.businessId, storeId, terminalId: context.terminalId, deviceId, topic, aggregateId }),
    eventType: topic,
    topic,
    eventVersion: POS_EVENT_VERSION,
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
    tenantId,
    ...(customerId ? { customerId } : {}),
    businessId: context.businessId,
    storeId,
    terminalId: context.terminalId,
    deviceId,
    actorId: context.actorId,
    aggregateId,
    originRecordId,
    idempotencyKey: `${topic}:${context.businessId}:${context.terminalId}:${idempotencyScope}`,
    sequence: sequenceFor(context.occurredAt, eventId),
    correlationId,
    causationId,
    traceId,
    occurredAt: capturedAt,
    capturedAt,
    payloadHash,
    payload
  };
}

export function saleCreatedEvent(saleId: string, folio: string, context: PosEventContext): PosEngineEvent {
  return makeEvent(POS_EVENT_SALE_CREATED, saleId, context, {
    saleId,
    folio,
    businessId: context.businessId,
    terminalId: context.terminalId
  });
}

export function saleCompletedEvent(result: Omit<CompleteLocalSaleResult, "events">, context: PosEventContext): PosEngineEvent {
  return makeEvent(POS_EVENT_SALE_COMPLETED, result.saleId, context, {
    saleId: result.saleId,
    folio: result.folio,
    businessId: result.businessId,
    terminalId: result.terminalId,
    cashSessionId: result.cashSessionId,
    ...(result.customerId ? { saleCustomerId: result.customerId } : {}),
    cashier: result.cashier,
    totalCents: result.totalCents,
    paymentMethod: result.paymentMethod,
    cashReceivedCents: result.cashReceivedCents,
    changeCents: result.changeCents,
    paymentBreakdownContract: "PRISMA_TABLET_MIXED_PAYMENT_V1",
    tenders: result.paymentTenders.map((tender) => ({
      id: tender.id,
      tenderType: tender.tenderType,
      amountCents: tender.amountCents,
      reference: tender.reference ?? null,
      recordedAt: tender.recordedAt.toISOString()
    })),
    status: result.status,
    lineCount: result.lines.length,
    lines: result.lines.map((line) => ({
      id: line.id,
      productId: line.productId,
      sku: line.sku,
      productName: line.productName,
      qty: line.qty,
      priceCents: line.priceCents,
      totalCents: line.totalCents
    })),
    createdAt: result.createdAt.toISOString()
  });
}

export function ticketClosedEvent(result: Omit<CompleteLocalSaleResult, "events">, context: PosEventContext): PosEngineEvent {
  return makeEvent(POS_EVENT_TICKET_CLOSED, result.saleId, context, {
    saleId: result.saleId,
    folio: result.folio,
    totalCents: result.totalCents,
    paymentMethod: result.paymentMethod,
    changeCents: result.changeCents,
    paymentBreakdownContract: "PRISMA_TABLET_MIXED_PAYMENT_V1",
    tenders: result.paymentTenders.map((tender) => ({
      id: tender.id,
      tenderType: tender.tenderType,
      amountCents: tender.amountCents,
      reference: tender.reference ?? null,
      recordedAt: tender.recordedAt.toISOString()
    })),
    items: result.lines.map((line) => ({
      productId: line.productId,
      sku: line.sku,
      qty: line.qty,
      totalCents: line.totalCents
    }))
  });
}

export function stockDecrementedEvents(saleId: string, lines: PosSaleLineResult[], context: PosEventContext): PosEngineEvent[] {
  return lines.map((line) =>
    makeEvent(POS_EVENT_STOCK_DECREMENTED, line.productId, context, {
      saleId,
      productId: line.productId,
      sku: line.sku,
      qty: line.qty,
      stockBefore: line.stockBefore,
      stockAfter: line.stockAfter
    })
  );
}

export function lowStockEvents(saleId: string, threshold: number, lines: PosSaleLineResult[], context: PosEventContext): PosEngineEvent[] {
  return lines
    .filter((line) => line.stockAfter <= threshold)
    .map((line) =>
      makeEvent(POS_EVENT_INVENTORY_LOW_STOCK_DETECTED, line.productId, context, {
        saleId,
        productId: line.productId,
        sku: line.sku,
        stockAfter: line.stockAfter,
        threshold
      })
    );
}
