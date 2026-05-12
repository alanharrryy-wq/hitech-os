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

type PosEventContext = {
  businessId: string;
  terminalId: string;
  actorId: string;
  occurredAt: Date;
};

function makeEvent(topic: string, aggregateId: string, context: PosEventContext, payload: Record<string, unknown>): PosEngineEvent {
  const eventId = makePosId("evt");
  const idempotencyScope = typeof payload.saleId === "string" ? `${aggregateId}:${payload.saleId}` : aggregateId;
  return {
    eventId,
    eventType: topic,
    topic,
    idempotencyKey: `${topic}:${context.businessId}:${context.terminalId}:${idempotencyScope}`,
    businessId: context.businessId,
    terminalId: context.terminalId,
    actorId: context.actorId,
    source: POS_EVENT_SOURCE,
    occurredAt: context.occurredAt.toISOString(),
    aggregateId,
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
    correlationId: aggregateId,
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
      cashier: result.cashier,
      totalCents: result.totalCents,
      paymentMethod: result.paymentMethod,
      cashReceivedCents: result.cashReceivedCents,
      changeCents: result.changeCents,
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
