import crypto from "node:crypto";
import { prisma } from "../prisma/client";
import { POS_EVENT_SCHEMA_VERSION, POS_EVENT_SOURCE } from "../pos-engine/constants";
import { makePosId } from "../pos-engine/ids";
import { assertTabletOperationalPermission, type TabletPermissionEvidence } from "../pos-security/permissions.prisma";
import type { InventoryOperationInput, InventoryOperationResult, InventoryOperationsSnapshot } from "./types";
import { InventoryOperationError } from "./types";

type TxClient = any;
const TOPIC_STOCK_ADJUSTED = "stock.adjusted";
const TOPIC_INVENTORY_OPERATION_RECORDED = "inventory.operation.recorded";

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (!value || typeof value !== "object") return value;
  return Object.keys(value as Record<string, unknown>).sort().reduce<Record<string, unknown>>((result, key) => {
    result[key] = stable((value as Record<string, unknown>)[key]);
    return result;
  }, {});
}

function payloadHash(value: unknown) {
  return crypto.createHash("sha256").update(JSON.stringify(stable(value))).digest("hex");
}

function idempotencyKey(input: InventoryOperationInput) {
  return `${TOPIC_STOCK_ADJUSTED}:${input.businessId}:${input.terminalId}:${input.clientRequestId}`;
}

async function ensureContext(tx: TxClient, input: InventoryOperationInput) {
  const [business, terminal] = await Promise.all([
    tx.business.findUnique({ where: { id: input.businessId }, select: { id: true } }),
    tx.terminal.findFirst({ where: { id: input.terminalId, businessId: input.businessId, isActive: true } })
  ]);
  if (!business) throw new InventoryOperationError("BUSINESS_NOT_FOUND", "No existe el negocio local.", 409);
  if (!terminal) throw new InventoryOperationError("TERMINAL_NOT_FOUND", "No existe una terminal activa para inventario.", 409);
  const permission = await assertTabletOperationalPermission({
    businessId: input.businessId,
    terminalId: input.terminalId,
    actorId: input.actorId,
    permission: "inventory:adjust"
  }, tx);
  const actor = await tx.user.findFirst({ where: { id: input.actorId, businessId: input.businessId, status: "ACTIVE" }, select: { id: true } });
  return { terminal, actorId: actor?.id ?? null, permission };
}

async function existingResult(tx: TxClient, input: InventoryOperationInput): Promise<InventoryOperationResult | null> {
  const event = await tx.outboxEvent.findFirst({ where: { businessId: input.businessId, idempotencyKey: idempotencyKey(input) } });
  if (!event) return null;
  const envelope = JSON.parse(event.payloadJson || "{}") as { payload?: { result?: InventoryOperationResult } };
  if (!envelope.payload?.result) throw new InventoryOperationError("INVENTORY_IDEMPOTENCY_INCONSISTENT", "Existe evento idempotente sin resultado de inventario.", 409);
  return { ...envelope.payload.result, deduplicated: true };
}

async function persistEvidence(tx: TxClient, input: InventoryOperationInput, context: { terminal: any; actorId: string | null; permission: TabletPermissionEvidence }, result: InventoryOperationResult) {
  const createdAt = new Date(result.createdAt);
  const tenantId = process.env.PRISMA_TENANT_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TENANT_ID?.trim() || "";
  const deviceId = process.env.PRISMA_TABLET_DEVICE_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TABLET_DEVICE_ID?.trim() || input.terminalId;
  const createEnvelope = (topic: string, aggregateId: string, originRecordId: string, eventId: string, eventKey: string, payload: Record<string, unknown>, sequenceOffset: number) => ({
    eventId,
    source: POS_EVENT_SOURCE,
    subject: `prisma://sync/${encodeURIComponent(tenantId || "unresolved-tenant")}/${encodeURIComponent(input.businessId)}/${encodeURIComponent(context.terminal.storeId)}/${encodeURIComponent(input.terminalId)}/${encodeURIComponent(deviceId)}/${topic}/${encodeURIComponent(aggregateId)}`,
    eventType: topic,
    topic,
    eventVersion: "1.0.0",
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
    tenantId,
    businessId: input.businessId,
    storeId: context.terminal.storeId,
    terminalId: input.terminalId,
    deviceId,
    actorId: input.actorId,
    aggregateId,
    originRecordId,
    idempotencyKey: eventKey,
    sequence: createdAt.getTime() * 1000 + sequenceOffset,
    correlationId: result.operationId,
    causationId: input.clientRequestId,
    traceId: input.clientRequestId,
    occurredAt: createdAt.toISOString(),
    capturedAt: createdAt.toISOString(),
    payloadHash: payloadHash(payload),
    payload
  });

  const operationEventId = makePosId("evt");
  const operationPayload = { contract: "PRISMA_TABLET_INVENTORY_OPERATIONS_V1", action: input.action, permission: context.permission, result };
  const operationEnvelope = createEnvelope(
    TOPIC_INVENTORY_OPERATION_RECORDED,
    result.operationId,
    result.operationId,
    operationEventId,
    idempotencyKey(input),
    operationPayload,
    0
  );
  await tx.outboxEvent.create({
    data: {
      id: operationEventId,
      businessId: input.businessId,
      terminalId: input.terminalId,
      topic: TOPIC_INVENTORY_OPERATION_RECORDED,
      aggregateId: result.operationId,
      idempotencyKey: operationEnvelope.idempotencyKey,
      payloadJson: JSON.stringify(operationEnvelope),
      source: POS_EVENT_SOURCE,
      schemaVersion: POS_EVENT_SCHEMA_VERSION,
      status: "pending",
      createdAt
    }
  });

  const stockChanges = result.affectedProducts.filter((affected) => affected.deltaQty !== 0);
  for (const [index, affected] of stockChanges.entries()) {
    const eventId = makePosId("evt");
    const stockPayload = {
      contract: "PRISMA_TABLET_STOCK_ADJUSTED_V1",
      operationId: result.operationId,
      action: input.action,
      productId: affected.productId,
      sku: affected.sku,
      qty: affected.deltaQty,
      stockBefore: affected.beforeQty,
      stockAfter: affected.afterQty,
      reason: input.action === "receive" ? `Recepción ${input.purchaseOrderId}` : input.reason,
      location: input.location,
      createdAt: result.createdAt
    };
    const stockEnvelope = createEnvelope(
      TOPIC_STOCK_ADJUSTED,
      affected.productId,
      result.operationId,
      eventId,
      `${idempotencyKey(input)}:stock:${affected.productId}`,
      stockPayload,
      index + 1
    );
    await tx.outboxEvent.create({
      data: {
        id: eventId,
        businessId: input.businessId,
        terminalId: input.terminalId,
        topic: TOPIC_STOCK_ADJUSTED,
        aggregateId: affected.productId,
        idempotencyKey: stockEnvelope.idempotencyKey,
        payloadJson: JSON.stringify(stockEnvelope),
        source: POS_EVENT_SOURCE,
        schemaVersion: POS_EVENT_SCHEMA_VERSION,
        status: "pending",
        createdAt
      }
    });
  }
  await tx.auditEvent.create({ data: { id: makePosId("audit"), businessId: input.businessId, actorId: context.actorId, topic: `inventory.${input.action}.completed`, entityType: "inventory_operation", entityId: result.operationId, summary: `Operación de inventario ${input.action} completada en Tablet.`, afterJson: JSON.stringify(result), metadataJson: JSON.stringify({ clientRequestId: input.clientRequestId, terminalId: input.terminalId, actorId: input.actorId, permission: context.permission.permission, authorizationMode: context.permission.authorizationMode }), createdAt } });
}

async function productOrThrow(tx: TxClient, businessId: string, productId: string) {
  const product = await tx.product.findFirst({ where: { id: productId, businessId, isActive: true } });
  if (!product) throw new InventoryOperationError("PRODUCT_NOT_FOUND", "El producto no existe o está inactivo.", 404, { productId });
  return product;
}

async function adjust(tx: TxClient, input: Extract<InventoryOperationInput, { action: "adjust" }>): Promise<InventoryOperationResult> {
  const product = await productOrThrow(tx, input.businessId, input.productId);
  if (product.stockOnHand === input.targetQty) throw new InventoryOperationError("NO_STOCK_CHANGE", "La existencia capturada ya coincide con el producto.", 409, { productId: product.id, stockOnHand: product.stockOnHand });
  const createdAt = new Date();
  const operationId = makePosId("inventory_adjust");
  await tx.product.update({ where: { id: product.id }, data: { stockOnHand: input.targetQty } });
  await tx.stockMovement.create({ data: { id: makePosId("stock_move"), businessId: input.businessId, productId: product.id, movement: "adjustment", qty: input.targetQty - product.stockOnHand, reason: input.reason, location: input.location, beforeQty: product.stockOnHand, afterQty: input.targetQty, sourceType: "manual_adjustment", sourceId: operationId, createdAt } });
  return { operationId, action: input.action, businessId: input.businessId, terminalId: input.terminalId, actorId: input.actorId, clientRequestId: input.clientRequestId, createdAt: createdAt.toISOString(), deduplicated: false, affectedProducts: [{ productId: product.id, sku: product.sku, name: product.name, beforeQty: product.stockOnHand, afterQty: input.targetQty, deltaQty: input.targetQty - product.stockOnHand }] };
}

async function count(tx: TxClient, input: Extract<InventoryOperationInput, { action: "count" }>): Promise<InventoryOperationResult> {
  const createdAt = new Date();
  const operationId = makePosId("inventory_count");
  const affectedProducts = [];
  for (const line of input.lines) {
    const product = await productOrThrow(tx, input.businessId, line.productId);
    const deltaQty = line.countedQty - product.stockOnHand;
    if (deltaQty !== 0) {
      await tx.product.update({ where: { id: product.id }, data: { stockOnHand: line.countedQty } });
      await tx.stockMovement.create({ data: { id: makePosId("stock_move"), businessId: input.businessId, productId: product.id, movement: "count", qty: deltaQty, reason: input.reason, location: input.location, beforeQty: product.stockOnHand, afterQty: line.countedQty, sourceType: "inventory_count", sourceId: operationId, createdAt } });
    }
    affectedProducts.push({ productId: product.id, sku: product.sku, name: product.name, beforeQty: product.stockOnHand, afterQty: line.countedQty, deltaQty });
  }
  const variance = affectedProducts.reduce((sum, line) => sum + line.deltaQty, 0);
  await tx.auditCount.create({ data: { id: operationId, businessId: input.businessId, location: input.location, countedBy: input.actorId, variance, status: "COMPLETED", countedAt: createdAt } });
  return { operationId, action: input.action, businessId: input.businessId, terminalId: input.terminalId, actorId: input.actorId, clientRequestId: input.clientRequestId, createdAt: createdAt.toISOString(), deduplicated: false, affectedProducts, count: { id: operationId, lineCount: affectedProducts.length, variance } };
}

async function receive(tx: TxClient, input: Extract<InventoryOperationInput, { action: "receive" }>): Promise<InventoryOperationResult> {
  const order = await tx.purchaseOrder.findFirst({ where: { id: input.purchaseOrderId, businessId: input.businessId }, include: { supplier: true, lines: true, goodsReceipts: { include: { lines: true } } } });
  if (!order) throw new InventoryOperationError("PURCHASE_ORDER_NOT_FOUND", "La orden de compra no existe.", 404);
  if (["CANCELLED", "CLOSED", "RECEIVED"].includes(String(order.status).toUpperCase())) throw new InventoryOperationError("PURCHASE_ORDER_NOT_RECEIVABLE", "La orden ya no admite recepciones.", 409, { status: order.status });
  const orderLines = new Map(order.lines.map((line: any) => [line.id, line]));
  const previouslyReceived = new Map<string, number>();
  for (const receipt of order.goodsReceipts) for (const line of receipt.lines) if (line.purchaseOrderLineId) previouslyReceived.set(line.purchaseOrderLineId, (previouslyReceived.get(line.purchaseOrderLineId) ?? 0) + line.qtyReceived);
  const selected = input.lines.map((requestLine) => {
    const line: any = orderLines.get(requestLine.purchaseOrderLineId);
    if (!line) throw new InventoryOperationError("PURCHASE_ORDER_LINE_NOT_FOUND", "Una línea no pertenece a la orden.", 404, { purchaseOrderLineId: requestLine.purchaseOrderLineId });
    const remaining = Math.max(0, line.qtyOrdered - (previouslyReceived.get(line.id) ?? 0));
    if (requestLine.qtyReceived > remaining) throw new InventoryOperationError("RECEIPT_EXCEEDS_REMAINING", "La recepción excede la cantidad pendiente.", 409, { purchaseOrderLineId: line.id, remaining, requested: requestLine.qtyReceived });
    return { line, qtyReceived: requestLine.qtyReceived };
  });
  const createdAt = new Date();
  const operationId = makePosId("goods_receipt");
  const suffix = input.clientRequestId.replace(/[^a-z0-9]/gi, "").slice(-8).toUpperCase() || operationId.slice(-8).toUpperCase();
  const folio = `REC-${createdAt.toISOString().slice(0, 10).replaceAll("-", "")}-${suffix}`;
  const computed = selected.map(({ line, qtyReceived }) => {
    const lineSubtotalCents = line.unitCostCents * qtyReceived;
    const lineTaxCents = line.qtyOrdered > 0 ? Math.round((line.lineTaxCents * qtyReceived) / line.qtyOrdered) : 0;
    return { line, qtyReceived, lineSubtotalCents, lineTaxCents, lineTotalCents: lineSubtotalCents + lineTaxCents };
  });
  const subtotalCents = computed.reduce((sum, line) => sum + line.lineSubtotalCents, 0);
  const taxCents = computed.reduce((sum, line) => sum + line.lineTaxCents, 0);
  const totalCents = computed.reduce((sum, line) => sum + line.lineTotalCents, 0);
  await tx.goodsReceipt.create({ data: { id: operationId, businessId: input.businessId, purchaseOrderId: order.id, supplierId: order.supplierId, folio, status: "POSTED", receivedAt: createdAt, subtotalCents, taxCents, totalCents, updatedAt: createdAt } });
  const affectedProducts = [];
  for (const item of computed) {
    const product = await productOrThrow(tx, input.businessId, item.line.productId);
    const afterQty = product.stockOnHand + item.qtyReceived;
    await tx.goodsReceiptLine.create({ data: { id: makePosId("receipt_line"), businessId: input.businessId, goodsReceiptId: operationId, purchaseOrderLineId: item.line.id, productId: product.id, sku: item.line.sku, name: item.line.name, qtyReceived: item.qtyReceived, unitCostCents: item.line.unitCostCents, lineSubtotalCents: item.lineSubtotalCents, lineTaxCents: item.lineTaxCents, lineTotalCents: item.lineTotalCents, createdAt } });
    await tx.product.update({ where: { id: product.id }, data: { stockOnHand: afterQty, costCents: item.line.unitCostCents } });
    await tx.stockMovement.create({ data: { id: makePosId("stock_move"), businessId: input.businessId, productId: product.id, movement: "receipt", qty: item.qtyReceived, reason: input.reference ? `Recepción ${folio}: ${input.reference}` : `Recepción ${folio}`, location: input.location, beforeQty: product.stockOnHand, afterQty, sourceType: "goods_receipt", sourceId: operationId, createdAt } });
    affectedProducts.push({ productId: product.id, sku: product.sku, name: product.name, beforeQty: product.stockOnHand, afterQty, deltaQty: item.qtyReceived });
    previouslyReceived.set(item.line.id, (previouslyReceived.get(item.line.id) ?? 0) + item.qtyReceived);
  }
  const fullyReceived = order.lines.every((line: any) => (previouslyReceived.get(line.id) ?? 0) >= line.qtyOrdered);
  await tx.purchaseOrder.update({ where: { id: order.id }, data: { status: fullyReceived ? "RECEIVED" : "PARTIAL", updatedAt: createdAt } });
  return { operationId, action: input.action, businessId: input.businessId, terminalId: input.terminalId, actorId: input.actorId, clientRequestId: input.clientRequestId, createdAt: createdAt.toISOString(), deduplicated: false, affectedProducts, receipt: { id: operationId, folio, purchaseOrderId: order.id, status: "POSTED", subtotalCents, taxCents, totalCents } };
}

export class InventoryOperationsRepository {
  constructor(private readonly db: any = prisma) {}

  async snapshot(input: { businessId: string; terminalId: string }): Promise<InventoryOperationsSnapshot> {
    const [orders, recentCounts] = await Promise.all([
      this.db.purchaseOrder.findMany({ where: { businessId: input.businessId, status: { notIn: ["CANCELLED", "CLOSED", "RECEIVED"] } }, include: { supplier: true, lines: true, goodsReceipts: { include: { lines: true } } }, orderBy: { createdAt: "desc" }, take: 20 }),
      this.db.auditCount.findMany({ where: { businessId: input.businessId }, orderBy: { countedAt: "desc" }, take: 10 })
    ]);
    return {
      purchaseOrders: orders.map((order: any) => {
        const received = new Map<string, number>();
        for (const receipt of order.goodsReceipts) for (const line of receipt.lines) if (line.purchaseOrderLineId) received.set(line.purchaseOrderLineId, (received.get(line.purchaseOrderLineId) ?? 0) + line.qtyReceived);
        return { id: order.id, folio: order.folio, supplierId: order.supplierId, supplierName: order.supplier?.name ?? "Proveedor", status: order.status, lines: order.lines.map((line: any) => { const qtyReceived = received.get(line.id) ?? 0; return { id: line.id, productId: line.productId, sku: line.sku, name: line.name, qtyOrdered: line.qtyOrdered, qtyReceived, qtyRemaining: Math.max(0, line.qtyOrdered - qtyReceived) }; }).filter((line: any) => line.qtyRemaining > 0) };
      }).filter((order: any) => order.lines.length > 0),
      recentCounts: recentCounts.map((row: any) => ({ id: row.id, location: row.location, countedBy: row.countedBy, variance: row.variance, status: row.status, countedAt: row.countedAt.toISOString() }))
    };
  }

  async execute(input: InventoryOperationInput): Promise<InventoryOperationResult> {
    return this.db.$transaction(async (tx: TxClient) => {
      const context = await ensureContext(tx, input);
      const duplicate = await existingResult(tx, input);
      if (duplicate) return duplicate;
      const result = input.action === "adjust" ? await adjust(tx, input) : input.action === "count" ? await count(tx, input) : await receive(tx, input);
      await persistEvidence(tx, input, context, result);
      return result;
    });
  }
}

export const inventoryOperationsRepository = new InventoryOperationsRepository();
