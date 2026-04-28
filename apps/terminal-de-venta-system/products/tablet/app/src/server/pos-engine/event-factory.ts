import {
  POS_EVENT_INVENTORY_LOW_STOCK_DETECTED,
  POS_EVENT_SALE_COMPLETED,
  POS_EVENT_SALE_CREATED,
  POS_EVENT_STOCK_DECREMENTED,
  POS_EVENT_TICKET_CLOSED
} from "./constants";
import type { CompleteLocalSaleResult, PosEngineEvent, PosSaleLineResult } from "./types";

export const POS_ENGINE_EVENT_FACTORY_TOPICS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected"
] as const;

export function saleCreatedEvent(saleId: string, folio: string, businessId: string): PosEngineEvent {
  return {
    topic: POS_EVENT_SALE_CREATED,
    aggregateId: saleId,
    payload: { saleId, folio, businessId }
  };
}

export function saleCompletedEvent(result: Omit<CompleteLocalSaleResult, "events">): PosEngineEvent {
  return {
    topic: POS_EVENT_SALE_COMPLETED,
    aggregateId: result.saleId,
    payload: {
      saleId: result.saleId,
      folio: result.folio,
      businessId: result.businessId,
      terminalId: result.terminalId,
      cashSessionId: result.cashSessionId,
      cashier: result.cashier,
      totalCents: result.totalCents,
      status: result.status,
      lineCount: result.lines.length,
      createdAt: result.createdAt.toISOString()
    }
  };
}

export function ticketClosedEvent(result: Omit<CompleteLocalSaleResult, "events">): PosEngineEvent {
  return {
    topic: POS_EVENT_TICKET_CLOSED,
    aggregateId: result.saleId,
    payload: {
      saleId: result.saleId,
      folio: result.folio,
      totalCents: result.totalCents,
      items: result.lines.map((line) => ({
        productId: line.productId,
        sku: line.sku,
        qty: line.qty,
        totalCents: line.totalCents
      }))
    }
  };
}

export function stockDecrementedEvents(saleId: string, lines: PosSaleLineResult[]): PosEngineEvent[] {
  return lines.map((line) => ({
    topic: POS_EVENT_STOCK_DECREMENTED,
    aggregateId: line.productId,
    payload: {
      saleId,
      productId: line.productId,
      sku: line.sku,
      qty: line.qty,
      stockAfter: line.stockAfter
    }
  }));
}

export function lowStockEvents(saleId: string, threshold: number, lines: PosSaleLineResult[]): PosEngineEvent[] {
  return lines
    .filter((line) => line.stockAfter <= threshold)
    .map((line) => ({
      topic: POS_EVENT_INVENTORY_LOW_STOCK_DETECTED,
      aggregateId: line.productId,
      payload: {
        saleId,
        productId: line.productId,
        sku: line.sku,
        stockAfter: line.stockAfter,
        threshold
      }
    }));
}
