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
  PosPaymentMethod,
  PosSalePaymentMethod,
  PosEngineRepository,
  PosModifierSelectionInput,
  PosModifierSelectionSnapshot,
  PosResolvedProduct,
  PosSaleLineResult,
  SalePaymentTenderInput,
  SalePaymentTenderResult
} from "./types";

type TxClient = any;

function normalizeLines(lines: PosCartLineInput[]) {
  assertNonEmpty(lines);

  const byKey = new Map<string, PosCartLineInput>();
  for (const line of lines) {
    assertPositiveQuantity(line.qty, { productId: line.productId, sku: line.sku, barcode: line.barcode });
    const modifierKey = (line.modifierSelections ?? [])
      .map((selection) => `${selection.modifierGroupId}:${[...selection.optionIds].sort().join(",")}`)
      .sort()
      .join("|");
    const baseKey = line.productId ? `id:${line.productId}` : line.sku ? `sku:${line.sku}` : line.barcode ? `barcode:${line.barcode}` : null;
    const key = baseKey ? `${baseKey}|${modifierKey}` : null;
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

type ModifierRow = {
  modifierGroupId: string;
  groupName: string;
  minSelections: number;
  maxSelections: number;
  required: number | boolean;
  optionId: string | null;
  optionName: string | null;
  priceDeltaCents: number | null;
  optionStatus: string | null;
};

async function resolveModifierSelections(tx: TxClient, businessId: string, productId: string, selections: PosModifierSelectionInput[] | undefined) {
  if (!selections?.length) return { priceDeltaCents: 0, snapshot: [] as PosModifierSelectionSnapshot[] };

  const rows = await tx.$queryRawUnsafe(
    `SELECT l."modifierGroupId", g."name" AS "groupName", g."minSelections", g."maxSelections", l."required",
      o."id" AS "optionId", o."name" AS "optionName", o."priceDeltaCents", o."status" AS "optionStatus"
     FROM "ProductModifierGroup" l
     JOIN "ModifierGroup" g ON g."id" = l."modifierGroupId" AND g."businessId" = l."businessId"
     LEFT JOIN "ModifierOption" o ON o."modifierGroupId" = g."id" AND o."businessId" = g."businessId"
     WHERE l."businessId" = ? AND l."productId" = ? AND l."status" = 'ACTIVE' AND g."status" = 'ACTIVE'
     ORDER BY l."sortOrder" ASC, g."sortOrder" ASC, o."sortOrder" ASC, o."id" ASC`,
    businessId,
    productId
  ).catch((error: unknown) => {
    throw new PosEngineError("MODIFIER_CATALOG_UNAVAILABLE", "La configuración de modificadores no está disponible en la Tablet.", {
      productId,
      cause: error instanceof Error ? error.message : "modifier query failed"
    });
  }) as ModifierRow[];

  const byGroup = new Map<string, { groupName: string; minSelections: number; maxSelections: number; required: boolean; options: Map<string, ModifierRow> }>();
  for (const row of rows) {
    const group = byGroup.get(row.modifierGroupId) ?? {
      groupName: row.groupName,
      minSelections: Math.max(0, Number(row.minSelections ?? 0)),
      maxSelections: Math.max(1, Number(row.maxSelections ?? 1)),
      required: row.required === true || Number(row.required) === 1,
      options: new Map<string, ModifierRow>()
    };
    if (row.optionId) group.options.set(row.optionId, row);
    byGroup.set(row.modifierGroupId, group);
  }

  const selectedGroups = new Map(selections.map((selection) => [selection.modifierGroupId, selection]));
  for (const [groupId, selection] of selectedGroups) {
    const group = byGroup.get(groupId);
    if (!group) throw new PosEngineError("MODIFIER_GROUP_NOT_AVAILABLE", "El grupo de modificadores no corresponde al producto seleccionado.", { productId, modifierGroupId: groupId });
    if (selection.optionIds.length < group.minSelections || selection.optionIds.length > group.maxSelections) {
      throw new PosEngineError("MODIFIER_SELECTION_COUNT_INVALID", "La cantidad de opciones seleccionadas no cumple la regla del grupo.", { productId, modifierGroupId: groupId, minSelections: group.minSelections, maxSelections: group.maxSelections });
    }
  }
  for (const [groupId, group] of byGroup) {
    if ((group.required || group.minSelections > 0) && !selectedGroups.has(groupId)) {
      throw new PosEngineError("MODIFIER_SELECTION_REQUIRED", "Falta una selección obligatoria para el producto.", { productId, modifierGroupId: groupId });
    }
  }

  const snapshot: PosModifierSelectionSnapshot[] = [];
  let priceDeltaCents = 0;
  for (const selection of selections) {
    const group = byGroup.get(selection.modifierGroupId)!;
    const options = selection.optionIds.map((optionId) => {
      const option = group.options.get(optionId);
      if (!option || option.optionStatus !== "ACTIVE" || !option.optionName) {
        throw new PosEngineError("MODIFIER_OPTION_NOT_AVAILABLE", "Una opción seleccionada ya no está disponible.", { productId, modifierGroupId: selection.modifierGroupId, optionId });
      }
      const delta = Math.trunc(Number(option.priceDeltaCents ?? 0));
      priceDeltaCents += delta;
      return { optionId, name: option.optionName, priceDeltaCents: delta };
    });
    snapshot.push({ modifierGroupId: selection.modifierGroupId, groupName: group.groupName, options });
  }
  return { priceDeltaCents, snapshot };
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
        idempotencyKey: event.idempotencyKey ?? null,
        payloadJson: JSON.stringify(event),
        terminalId: event.terminalId,
        source: event.source,
        schemaVersion: event.schemaVersion,
        status: OUTBOX_STATUS_PENDING,
        createdAt: new Date(event.occurredAt)
      }
    });
  }
}

function normalizePaymentTenders(input: {
  paymentMethod: CompleteLocalSaleInput["paymentMethod"];
  cashReceivedCents: number | null;
  totalCents: number;
  paymentTenders?: SalePaymentTenderInput[];
}): { tenders: SalePaymentTenderInput[]; paymentMethod: PosSalePaymentMethod; cashReceivedCents: number | null; changeCents: number } {
  const rawTenders = Array.isArray(input.paymentTenders) && input.paymentTenders.length
    ? input.paymentTenders
    : input.paymentMethod === "cash"
      ? [{ tenderType: "cash" as const, amountCents: input.cashReceivedCents ?? 0, reference: null }]
      : [{ tenderType: (input.paymentMethod === "card" || input.paymentMethod === "transfer" ? input.paymentMethod : "cash") as PosPaymentMethod, amountCents: input.totalCents, reference: null }];

  const tenders = rawTenders
    .map((tender) => ({
      tenderType: tender.tenderType,
      amountCents: Math.round(Number(tender.amountCents ?? 0)),
      reference: typeof tender.reference === "string" && tender.reference.trim() ? tender.reference.trim().slice(0, 120) : null
    }))
    .filter((tender) => tender.amountCents > 0);

  if (!tenders.length) throw new PosEngineError("PAYMENT_TENDER_REQUIRED", "Captura al menos un método de pago con importe.", {});
  if (tenders.some((tender) => tender.tenderType !== "cash" && tender.tenderType !== "card" && tender.tenderType !== "transfer")) {
    throw new PosEngineError("INVALID_PAYMENT_METHOD", "Método de pago inválido.", {});
  }

  const paidCents = addCents(tenders.map((tender) => tender.amountCents));
  const cashPaidCents = addCents(tenders.filter((tender) => tender.tenderType === "cash").map((tender) => tender.amountCents));
  const nonCashPaidCents = paidCents - cashPaidCents;
  if (nonCashPaidCents > input.totalCents) {
    throw new PosEngineError("NON_CASH_OVERPAYMENT", "Tarjeta o transferencia no deben exceder el total pendiente.", { totalCents: input.totalCents, nonCashPaidCents });
  }
  if (paidCents < input.totalCents) {
    throw new PosEngineError("PAYMENT_INCOMPLETE", "El pago no cubre el total del ticket.", { totalCents: input.totalCents, paidCents });
  }

  const changeCents = paidCents - input.totalCents;
  const paymentMethod: PosSalePaymentMethod = tenders.length === 1 ? tenders[0].tenderType : "mixed";
  return { tenders, paymentMethod, cashReceivedCents: cashPaidCents > 0 ? cashPaidCents : null, changeCents };
}

export class PrismaPosEngineRepository implements PosEngineRepository {
  private readonly db: any;

  constructor(db = prisma) {
    this.db = db;
  }

  async completeLocalSale(input: CompleteLocalSaleInput): Promise<CompleteLocalSaleResult> {
    const businessId = input.businessId ?? DEFAULT_BUSINESS_ID;
    let terminalId = input.terminalId ?? DEFAULT_TERMINAL_ID;
    const requestedCashSessionId = input.cashSessionId ?? null;
    const requestedCustomerId = input.customerId?.trim() || null;
    const cashier = input.cashier ?? DEFAULT_CASHIER;
    const location = input.location ?? DEFAULT_LOCATION;
    const allowNegativeStock = input.allowNegativeStock ?? false;
    const lowStockThreshold = input.lowStockThreshold ?? DEFAULT_LOW_STOCK_THRESHOLD;
    const normalizedLines = normalizeLines(input.lines);
    const requestedPaymentMethod = input.paymentMethod ?? "cash";
    const requestedCashReceivedCents = input.cashReceivedCents ?? null;

    return this.db.$transaction(async (tx: TxClient) => {
      const business = await tx.business.findUnique({ where: { id: businessId } });
      if (!business) {
        throw new PosEngineError("BUSINESS_NOT_FOUND", "No existe el negocio local para registrar la venta.", { businessId });
      }

      if (requestedCustomerId) {
        const customer = await tx.$queryRaw<Array<{ id: string }>>`
          SELECT "id" FROM "Customer"
          WHERE "businessId" = ${businessId} AND "id" = ${requestedCustomerId} AND "isActive" = true
          LIMIT 1
        `.catch((error: unknown) => {
          throw new PosEngineError("SALE_CUSTOMER_PROJECTION_UNAVAILABLE", "La proyección local de clientes no está disponible.", {
            businessId,
            cause: error instanceof Error ? error.message : "customer projection query failed"
          });
        });
        if (!customer[0]) {
          throw new PosEngineError("SALE_CUSTOMER_NOT_FOUND", "El cliente seleccionado no está disponible en la base local de Tablet.", {
            businessId,
            customerId: requestedCustomerId
          });
        }
      }

      let terminal = await tx.terminal.findFirst({ where: { id: terminalId, businessId, isActive: true } });
      if (!terminal) {
        terminal = await tx.terminal.findFirst({ where: { businessId, isActive: true }, orderBy: { id: "asc" } });
        if (terminal?.id) terminalId = terminal.id;
      }
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
          include: { lines: true, paymentTenders: true }
        });
        if (existingSale) {
          return {
            saleId: existingSale.id,
            folio: existingSale.folio,
            businessId,
            terminalId: existingSale.terminalId,
            cashSessionId: existingSale.cashSessionId ?? null,
            customerId: existingSale.customerId ?? null,
            clientRequestId: existingSale.clientRequestId ?? null,
            cashier: existingSale.cashier,
            subtotalCents: existingSale.subtotalCents ?? existingSale.totalCents,
            discountCents: existingSale.discountCents ?? 0,
            totalCents: existingSale.totalCents,
            paymentMethod: existingSale.paymentMethod ?? "cash",
            cashReceivedCents: existingSale.cashReceivedCents ?? null,
            changeCents: existingSale.changeCents ?? 0,
            paymentTenders: existingSale.paymentTenders.map((tender: any) => ({ id: tender.id, tenderType: tender.tenderType, amountCents: tender.amountCents, reference: tender.reference ?? null, recordedAt: tender.recordedAt })),
            status: SALE_STATUS_COMPLETED as "COMPLETED",
            createdAt: existingSale.createdAt,
            completedAt: existingSale.completedAt ?? existingSale.createdAt,
            lines: existingSale.lines.map((line: any) => ({ id: line.id, productId: line.productId, sku: line.sku, productName: line.productName, qty: line.qty, priceCents: line.priceCents, totalCents: line.totalCents, stockBefore: 0, stockAfter: 0, modifierSelections: [] })),
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

        const modifiers = await resolveModifierSelections(tx, businessId, product.id, line.modifierSelections);
        const unitPriceCents = product.priceCents + modifiers.priceDeltaCents;
        if (unitPriceCents < 0) {
          throw new PosEngineError("MODIFIER_PRICE_INVALID", "Los modificadores no pueden dejar un precio unitario negativo.", { productId: product.id, productPriceCents: product.priceCents, priceDeltaCents: modifiers.priceDeltaCents });
        }
        const totalCents = multiplyCents(unitPriceCents, line.qty);
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
            location,
            beforeQty: product.stockOnHand,
            afterQty: stockAfter,
            sourceType: "sale",
            sourceId: saleId
          }
        });

        lineResults.push({
          id: lineId,
          productId: product.id,
          sku: product.sku,
          productName: product.name,
          qty: line.qty,
          priceCents: unitPriceCents,
          totalCents,
          stockBefore: product.stockOnHand,
          stockAfter,
          modifierSelections: modifiers.snapshot
        });
      }

      const totalCents = addCents(lineResults.map((line) => line.totalCents));
      const payment = normalizePaymentTenders({
        paymentMethod: requestedPaymentMethod,
        cashReceivedCents: requestedCashReceivedCents,
        totalCents,
        paymentTenders: input.paymentTenders
      });

      await tx.sale.create({
        data: {
          id: saleId,
          businessId,
          terminalId,
          cashSessionId,
          customerId: requestedCustomerId,
          clientRequestId: input.clientRequestId ?? null,
          folio,
          cashier,
          subtotalCents: totalCents,
          discountCents: 0,
          totalCents,
          completedAt: now,
          paymentMethod: payment.paymentMethod,
          cashReceivedCents: payment.cashReceivedCents,
          changeCents: payment.changeCents,
          status: SALE_STATUS_COMPLETED,
          createdAt: now
        }
      });

      await tx.auditEvent.create({
        data: {
          id: makePosId("audit"),
          businessId,
          actorId: null,
          topic: "pos.sale.completed",
          entityType: "Sale",
          entityId: saleId,
          summary: "Venta local completada en Tablet.",
          afterJson: JSON.stringify({ saleId, customerId: requestedCustomerId, totalCents, paymentMethod: payment.paymentMethod }),
          metadataJson: JSON.stringify({ source: "tablet-pos", privacy: "customer_id_only", clientRequestId: input.clientRequestId ?? null }),
          createdAt: now
        }
      });

      const paymentTenders: SalePaymentTenderResult[] = [];
      for (const tender of payment.tenders) {
        const row = await tx.salePaymentTender.create({
          data: {
            id: makePosId("tender"),
            businessId,
            saleId,
            tenderType: tender.tenderType,
            amountCents: tender.amountCents,
            reference: tender.reference,
            metadataJson: JSON.stringify({ contract: "PRISMA_TABLET_MIXED_PAYMENT_V1", changeCents: tender.tenderType === "cash" ? payment.changeCents : 0 }),
            recordedAt: now
          }
        });
        paymentTenders.push({ id: row.id, tenderType: row.tenderType, amountCents: row.amountCents, reference: row.reference ?? null, recordedAt: row.recordedAt });
      }

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
        if (line.modifierSelections.length) {
          await tx.$executeRawUnsafe(
            'UPDATE "SaleLine" SET "modifierSnapshotJson" = ? WHERE "id" = ? AND "businessId" = ?',
            JSON.stringify({ contract: "PRISMA_SALE_LINE_MODIFIERS_V1", groups: line.modifierSelections }),
            line.id,
            businessId
          );
        }
      }

      const resultWithoutEvents = {
        saleId,
        folio,
        businessId,
        terminalId,
        cashSessionId,
        customerId: requestedCustomerId,
        clientRequestId: input.clientRequestId ?? null,
        cashier,
        subtotalCents: totalCents,
        discountCents: 0,
        totalCents,
        paymentMethod: payment.paymentMethod,
        cashReceivedCents: payment.cashReceivedCents,
        changeCents: payment.changeCents,
        paymentTenders,
        status: SALE_STATUS_COMPLETED as "COMPLETED",
        createdAt: now,
        completedAt: now,
        lines: lineResults
      };

      // PRISMA_SYNC_DEFINITIVE_1607_EVENT_SCOPE
      const eventContext = {
        tenantId: process.env.PRISMA_TENANT_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TENANT_ID?.trim() || "",
        businessId,
        storeId: terminal.storeId,
        terminalId,
        deviceId: process.env.PRISMA_TABLET_DEVICE_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TABLET_DEVICE_ID?.trim() || terminalId,
        actorId: cashier,
        occurredAt: now
      };
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
