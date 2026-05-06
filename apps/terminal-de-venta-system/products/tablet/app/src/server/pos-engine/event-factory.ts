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
  "inventory.low_stock_detected"
] as const;

type PosEventContext = {
  businessId: string;
  terminalId: string;
  actorId: string;
  occurredAt: Date;
};

function makeEvent(topic: string, aggregateId: string, context: PosEventContext, payload: Record<string, unknown>): PosEngineEvent {
  return {
    eventId: makePosId("evt"),
    topic,
    businessId: context.businessId,
    terminalId: context.terminalId,
    actorId: context.actorId,
    source: POS_EVENT_SOURCE,
    occurredAt: context.occurredAt.toISOString(),
    aggregateId,
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
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
