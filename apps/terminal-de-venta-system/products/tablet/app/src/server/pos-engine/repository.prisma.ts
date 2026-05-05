import { prisma } from "../prisma/client";
import {
  DEFAULT_BUSINESS_ID,
  DEFAULT_CASHIER,
  DEFAULT_LOCATION,
  DEFAULT_LOW_STOCK_THRESHOLD,
  DEFAULT_TERMINAL_ID,
  OUTBOX_STATUS_PENDING,
  SALE_STATUS_COMPLETED,
  STOCK_MOVEMENT_SALE,
  STOCK_REASON_SALE_COMPLETED
} from "./constants";
import { PosEngineError, assertNonEmpty, assertPositiveQuantity } from "./errors";
import {
  lowStockEvents,
  saleCompletedEvent,
  saleCreatedEvent,
  stockDecrementedEvents,
  ticketClosedEvent
} from "./event-factory";
import { makeLocalSaleFolio, makePosId } from "./ids";
import { addCents, multiplyCents } from "./money";
import type {
  CompleteLocalSaleInput,
  CompleteLocalSaleResult,
  PosCartLineInput,
  PosEngineEvent,
  PosEngineRepository,
  PosResolvedProduct,
  PosSaleLineResult
} from "./types";

type TxClient = any;

function normalizeLines(lines: PosCartLineInput[]) {
  assertNonEmpty(lines);

  const byKey = new Map<string, PosCartLineInput>();
  for (const line of lines) {
    assertPositiveQuantity(line.qty, { productId: line.productId, sku: line.sku, barcode: line.barcode });
    const key = line.productId ? `id:${line.productId}` : line.sku ? `sku:${line.sku}` : line.barcode ? `barcode:${line.barcode}` : null;
    if (!key) {
      throw new PosEngineError("PRODUCT_NOT_FOUND", "Cada línea debe traer productId, sku o barcode.", { line });
    }

    const existing = byKey.get(key);
    if (existing) {
      byKey.set(key, { ...existing, qty: existing.qty + line.qty });
    } else {
      byKey.set(key, { ...line });
    }
  }

  return [...byKey.values()];
}

async function resolveProduct(tx: TxClient, businessId: string, line: PosCartLineInput): Promise<PosResolvedProduct> {
  const product = line.productId
    ? await tx.product.findFirst({ where: { id: line.productId, businessId } })
    : line.sku
      ? await tx.product.findFirst({ where: { sku: line.sku, businessId } })
      : line.barcode
        ? await tx.barcode
            .findFirst({ where: { code: line.barcode, businessId }, include: { product: true } })
            .then((row: any) => row?.product ?? null)
        : null;

  if (!product) {
    throw new PosEngineError("PRODUCT_NOT_FOUND", "Producto no encontrado en catálogo local de Tablet.", { line });
  }

  if (!product.isActive) {
    throw new PosEngineError("PRODUCT_INACTIVE", "Producto inactivo; no puede venderse en Tablet.", {
      productId: product.id,
      sku: product.sku
    });
  }

  return product;
}

function ensureStock(product: PosResolvedProduct, requestedQty: number, allowNegativeStock: boolean) {
  if (!allowNegativeStock && product.stockOnHand < requestedQty) {
    throw new PosEngineError("INSUFFICIENT_STOCK", "Stock insuficiente para cerrar la venta local.", {
      productId: product.id,
      sku: product.sku,
      stockOnHand: product.stockOnHand,
      requestedQty
    });
  }
}

async function persistOutboxEvents(tx: TxClient, businessId: string, events: PosEngineEvent[]) {
  for (const event of events) {
    await tx.outboxEvent.create({
      data: {
        id: event.eventId,
        businessId,
        topic: event.topic,
        aggregateId: event.aggregateId,
        payloadJson: JSON.stringify(event),
        status: OUTBOX_STATUS_PENDING,
        createdAt: new Date(event.occurredAt)
      }
    });
  }
}

export class PrismaPosEngineRepository implements PosEngineRepository {
  private readonly db: any;

  constructor(db = prisma) {
    this.db = db;
  }

  async completeLocalSale(input: CompleteLocalSaleInput): Promise<CompleteLocalSaleResult> {
    const businessId = input.businessId ?? DEFAULT_BUSINESS_ID;
    const terminalId = input.terminalId ?? DEFAULT_TERMINAL_ID;
    const requestedCashSessionId = input.cashSessionId ?? null;
    const cashier = input.cashier ?? DEFAULT_CASHIER;
    const location = input.location ?? DEFAULT_LOCATION;
    const allowNegativeStock = input.allowNegativeStock ?? false;
    const lowStockThreshold = input.lowStockThreshold ?? DEFAULT_LOW_STOCK_THRESHOLD;
    const normalizedLines = normalizeLines(input.lines);
    const paymentMethod = input.paymentMethod ?? "cash";
    const cashReceivedCents = input.cashReceivedCents ?? null;
    const changeCents = input.changeCents ?? 0;

    return this.db.$transaction(async (tx: TxClient) => {
      const business = await tx.business.findUnique({ where: { id: businessId } });
      if (!business) {
        throw new PosEngineError("BUSINESS_NOT_FOUND", "No existe el negocio local para registrar la venta.", { businessId });
      }

      const terminal = await tx.terminal.findFirst({ where: { id: terminalId, businessId, isActive: true } });
      if (!terminal) {
        throw new PosEngineError("TERMINAL_NOT_FOUND", "No existe una terminal local activa para cerrar la venta.", {
          businessId,
          terminalId
        });
      }

      // PRISMA HARDENING 01: sale idempotency by businessId + clientRequestId.
      if (input.clientRequestId) {
        const existingSale = await tx.sale.findFirst({
          where: { businessId, clientRequestId: input.clientRequestId },
          include: { lines: true }
        });
        if (existingSale) {
          return {
            saleId: existingSale.id,
            folio: existingSale.folio,
            businessId,
            terminalId: existingSale.terminalId,
            cashSessionId: existingSale.cashSessionId ?? null,
            cashier: existingSale.cashier,
            totalCents: existingSale.totalCents,
            paymentMethod: existingSale.paymentMethod ?? "cash",
            cashReceivedCents: existingSale.cashReceivedCents ?? null,
            changeCents: existingSale.changeCents ?? 0,
            status: SALE_STATUS_COMPLETED as "COMPLETED",
            createdAt: existingSale.createdAt,
            lines: existingSale.lines.map((line: any) => ({ id: line.id, productId: line.productId, sku: line.sku, productName: line.productName, qty: line.qty, priceCents: line.priceCents, totalCents: line.totalCents, stockBefore: 0, stockAfter: 0 })),
            events: []
          };
        }
      }

      const activeCashSession = requestedCashSessionId
        ? await tx.cashSession.findFirst({ where: { id: requestedCashSessionId, businessId, terminalId, status: "OPEN" } })
        : await tx.cashSession.findFirst({ where: { businessId, terminalId, status: "OPEN" }, orderBy: { openedAt: "desc" } });

      if (!activeCashSession) {
        throw new PosEngineError("SHIFT_NOT_OPEN", "Abre turno antes de cerrar ventas en esta terminal.", { businessId, terminalId, requestedCashSessionId });
      }

      const cashSessionId = activeCashSession.id;

      const now = new Date();
      const saleId = makePosId("sale");
      const folio = makeLocalSaleFolio(now);
      const lineResults: PosSaleLineResult[] = [];

      for (const line of normalizedLines) {
        const product = await resolveProduct(tx, businessId, line);
        ensureStock(product, line.qty, allowNegativeStock);

        const totalCents = multiplyCents(product.priceCents, line.qty);
        const stockAfter = product.stockOnHand - line.qty;
        const lineId = makePosId("sale_line");

        await tx.product.update({
          where: { id: product.id },
          data: { stockOnHand: stockAfter }
        });

        await tx.stockMovement.create({
          data: {
            id: makePosId("stock_move"),
            businessId,
            productId: product.id,
            movement: STOCK_MOVEMENT_SALE,
            qty: -line.qty,
            reason: STOCK_REASON_SALE_COMPLETED,
            location
          }
        });

        lineResults.push({
          id: lineId,
          productId: product.id,
          sku: product.sku,
          productName: product.name,
          qty: line.qty,
          priceCents: product.priceCents,
          totalCents,
          stockBefore: product.stockOnHand,
          stockAfter
        });
      }

      const totalCents = addCents(lineResults.map((line) => line.totalCents));

      await tx.sale.create({
        data: {
          id: saleId,
          businessId,
          terminalId,
          cashSessionId,
          clientRequestId: input.clientRequestId ?? null,
          folio,
          cashier,
          totalCents,
          paymentMethod,
          cashReceivedCents,
          changeCents,
          status: SALE_STATUS_COMPLETED,
          createdAt: now
        }
      });

      for (const line of lineResults) {
        await tx.saleLine.create({
          data: {
            id: line.id,
            businessId,
            saleId,
            productId: line.productId,
            sku: line.sku,
            productName: line.productName,
            qty: line.qty,
            priceCents: line.priceCents,
            totalCents: line.totalCents,
            createdAt: now
          }
        });
      }

      const resultWithoutEvents = {
        saleId,
        folio,
        businessId,
        terminalId,
        cashSessionId,
        cashier,
        totalCents,
        paymentMethod,
        cashReceivedCents,
        changeCents,
        status: SALE_STATUS_COMPLETED as "COMPLETED",
        createdAt: now,
        lines: lineResults
      };

      const eventContext = { businessId, terminalId, actorId: cashier, occurredAt: now };
      const events: PosEngineEvent[] = [
        saleCreatedEvent(saleId, folio, eventContext),
        saleCompletedEvent(resultWithoutEvents, eventContext),
        ticketClosedEvent(resultWithoutEvents, eventContext),
        ...stockDecrementedEvents(saleId, lineResults, eventContext),
        ...lowStockEvents(saleId, lowStockThreshold, lineResults, eventContext)
      ];

      await persistOutboxEvents(tx, businessId, events);

      return {
        ...resultWithoutEvents,
        events
      };
    });
  }
}

export const posEngineRepository = new PrismaPosEngineRepository();
