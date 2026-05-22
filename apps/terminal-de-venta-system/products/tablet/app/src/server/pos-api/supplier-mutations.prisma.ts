import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { DEFAULT_CASHIER, DEFAULT_TERMINAL_ID, POS_EVENT_SCHEMA_VERSION } from "@/server/pos-engine/constants";
import { DEFAULT_POS_API_BUSINESS_ID } from "./validators";

type TxClient = any;
const db = prisma as any;

function nowIso() { return new Date().toISOString(); }
function asString(value: unknown, fallback = "") { return typeof value === "string" ? value.trim() : fallback; }
function asBool(value: unknown, fallback = false) {
  if (value === true || value === "true" || value === "1") return true;
  if (value === false || value === "false" || value === "0") return false;
  return fallback;
}
function asInt(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) && Number.isInteger(n) ? n : null;
}
function requireLength(value: string, min: number, max: number, code: string) {
  if (value.length < min || value.length > max) throw new Error(code);
  return value;
}
function eventActorFromPayload(payload: Record<string, unknown>) {
  return asString(payload.actorId) || asString(payload.cashier) || DEFAULT_CASHIER;
}
function eventTerminalFromPayload(payload: Record<string, unknown>) {
  return asString(payload.terminalId) || DEFAULT_TERMINAL_ID;
}
async function ensureBusiness(tx: TxClient, businessId: string) {
  await tx.business.upsert({ where: { id: businessId }, create: { id: businessId, name: "PRISMA Tablet Local", currency: "MXN" }, update: {} });
}
async function createOutboxEvent(tx: TxClient, businessId: string, topic: string, aggregateId: string, payload: Record<string, unknown>) {
  const eventId = randomUUID();
  const terminalId = eventTerminalFromPayload(payload);
  const actorId = eventActorFromPayload(payload);
  const idempotencyKey = `${topic}:${businessId}:${terminalId}:${aggregateId}:${eventId}`;
  const occurredAt = nowIso();
  const envelope = {
    eventId,
    eventType: topic,
    topic,
    idempotencyKey,
    businessId,
    terminalId,
    actorId,
    source: "tablet.suppliers",
    occurredAt,
    aggregateId,
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
    correlationId: aggregateId,
    payload: { ...payload, businessId, terminalId, actorId }
  };
  await tx.outboxEvent.create({
    data: {
      id: eventId,
      businessId,
      terminalId,
      topic,
      aggregateId,
      idempotencyKey,
      payloadJson: JSON.stringify(envelope),
      source: "tablet.suppliers",
      schemaVersion: POS_EVENT_SCHEMA_VERSION,
      status: "pending"
    }
  });
  return envelope;
}
function serializeSupplier(row: any) {
  return { id: row.id, businessId: row.businessId, name: row.name, status: row.status, createdAt: row.createdAt, updatedAt: row.updatedAt };
}
function serializeProductSupplier(row: any) {
  return { id: row.id, businessId: row.businessId, productId: row.productId, supplierId: row.supplierId, isPrimary: row.isPrimary, status: row.status, leadTimeDays: row.leadTimeDays, createdAt: row.createdAt, updatedAt: row.updatedAt };
}
function readSupplierInput(raw: any, requireId = false, requireName = true) {
  const businessId = asString(raw?.businessId, DEFAULT_POS_API_BUSINESS_ID);
  const id = asString(raw?.id ?? raw?.supplierId) || (requireId ? "" : randomUUID());
  const name = asString(raw?.name ?? raw?.tradeName);
  const status = asString(raw?.status, "ACTIVE").toUpperCase() || "ACTIVE";
  if (requireId) requireLength(id, 4, 120, "MISSING_SUPPLIER_ID");
  if (requireName) requireLength(name, 2, 160, "INVALID_SUPPLIER_NAME");
  return { id, businessId, name, status, actorId: asString(raw?.actorId), terminalId: asString(raw?.terminalId) };
}
function readProductSupplierInput(raw: any) {
  const businessId = asString(raw?.businessId, DEFAULT_POS_API_BUSINESS_ID);
  const productId = asString(raw?.productId);
  const supplierId = asString(raw?.supplierId);
  requireLength(productId, 4, 120, "MISSING_PRODUCT_ID");
  requireLength(supplierId, 4, 120, "MISSING_SUPPLIER_ID");
  return {
    id: asString(raw?.id ?? raw?.linkId ?? raw?.productSupplierId) || `${productId}_${supplierId}`.slice(0, 120),
    businessId,
    productId,
    supplierId,
    isPrimary: asBool(raw?.isPrimary, false),
    status: asString(raw?.status, "ACTIVE").toUpperCase() || "ACTIVE",
    leadTimeDays: asInt(raw?.leadTimeDays),
    actorId: asString(raw?.actorId),
    terminalId: asString(raw?.terminalId)
  };
}
export async function createTabletSupplier(raw: any) {
  const input = readSupplierInput(raw, false, true);
  return db.$transaction(async (tx: TxClient) => {
    await ensureBusiness(tx, input.businessId);
    const existingName = await tx.supplier.findUnique({ where: { businessId_name: { businessId: input.businessId, name: input.name } } }).catch(() => null);
    if (existingName && existingName.id !== input.id) throw new Error("DUPLICATE_SUPPLIER_NAME");
    const supplier = await tx.supplier.create({ data: { id: input.id, businessId: input.businessId, name: input.name, status: input.status } });
    await createOutboxEvent(tx, input.businessId, "supplier.created", supplier.id, { supplierId: supplier.id, name: supplier.name, status: supplier.status, actorId: input.actorId, terminalId: input.terminalId });
    return serializeSupplier(supplier);
  });
}
export async function updateTabletSupplier(raw: any) {
  const input = readSupplierInput(raw, true, true);
  return db.$transaction(async (tx: TxClient) => {
    await ensureBusiness(tx, input.businessId);
    const supplier = await tx.supplier.update({ where: { id_businessId: { id: input.id, businessId: input.businessId } }, data: { name: input.name, status: input.status } });
    await createOutboxEvent(tx, input.businessId, "supplier.updated", supplier.id, { supplierId: supplier.id, name: supplier.name, status: supplier.status, actorId: input.actorId, terminalId: input.terminalId });
    return serializeSupplier(supplier);
  });
}
export async function disableTabletSupplier(raw: any) {
  const input = readSupplierInput(raw, true, false);
  return db.$transaction(async (tx: TxClient) => {
    await ensureBusiness(tx, input.businessId);
    const supplier = await tx.supplier.update({ where: { id_businessId: { id: input.id, businessId: input.businessId } }, data: { status: "DISABLED" } });
    await createOutboxEvent(tx, input.businessId, "supplier.disabled", supplier.id, { supplierId: supplier.id, name: supplier.name, status: supplier.status, actorId: input.actorId, terminalId: input.terminalId });
    return serializeSupplier(supplier);
  });
}
export async function linkTabletProductSupplier(raw: any) {
  const input = readProductSupplierInput(raw);
  return db.$transaction(async (tx: TxClient) => {
    await ensureBusiness(tx, input.businessId);
    const [product, supplier] = await Promise.all([
      tx.product.findFirst({ where: { id: input.productId, businessId: input.businessId } }),
      tx.supplier.findFirst({ where: { id: input.supplierId, businessId: input.businessId } })
    ]);
    if (!product) throw new Error("PRODUCT_NOT_FOUND");
    if (!supplier) throw new Error("SUPPLIER_NOT_FOUND");
    if (input.isPrimary) await tx.productSupplier.updateMany({ where: { businessId: input.businessId, productId: input.productId }, data: { isPrimary: false } });
    const link = await tx.productSupplier.upsert({
      where: { id: input.id },
      create: { id: input.id, businessId: input.businessId, productId: input.productId, supplierId: input.supplierId, isPrimary: input.isPrimary, status: input.status, leadTimeDays: input.leadTimeDays },
      update: { isPrimary: input.isPrimary, status: input.status, leadTimeDays: input.leadTimeDays }
    });
    await createOutboxEvent(tx, input.businessId, "product.supplier.linked", link.id, { productSupplierId: link.id, linkId: link.id, productId: link.productId, supplierId: link.supplierId, isPrimary: link.isPrimary, status: link.status, leadTimeDays: link.leadTimeDays, actorId: input.actorId, terminalId: input.terminalId });
    return serializeProductSupplier(link);
  });
}
export async function updateTabletProductSupplier(raw: any) {
  const input = readProductSupplierInput(raw);
  return db.$transaction(async (tx: TxClient) => {
    await ensureBusiness(tx, input.businessId);
    if (input.isPrimary) await tx.productSupplier.updateMany({ where: { businessId: input.businessId, productId: input.productId, NOT: { id: input.id } }, data: { isPrimary: false } });
    const link = await tx.productSupplier.update({ where: { id: input.id }, data: { isPrimary: input.isPrimary, status: input.status, leadTimeDays: input.leadTimeDays } });
    await createOutboxEvent(tx, input.businessId, "product.supplier.updated", link.id, { productSupplierId: link.id, linkId: link.id, productId: link.productId, supplierId: link.supplierId, isPrimary: link.isPrimary, status: link.status, leadTimeDays: link.leadTimeDays, actorId: input.actorId, terminalId: input.terminalId });
    return serializeProductSupplier(link);
  });
}
export async function unlinkTabletProductSupplier(raw: any) {
  const input = readProductSupplierInput(raw);
  return db.$transaction(async (tx: TxClient) => {
    await ensureBusiness(tx, input.businessId);
    const link = await tx.productSupplier.update({ where: { id: input.id }, data: { status: "INACTIVE", isPrimary: false } });
    await createOutboxEvent(tx, input.businessId, "product.supplier.unlinked", link.id, { productSupplierId: link.id, linkId: link.id, productId: link.productId, supplierId: link.supplierId, isPrimary: false, status: "INACTIVE", actorId: input.actorId, terminalId: input.terminalId });
    return serializeProductSupplier(link);
  });
}
export function supplierMutationErrorToResponse(error: unknown) {
  const raw = error instanceof Error ? error.message : String(error);
  const map: Record<string, { status: number; message: string }> = {
    INVALID_SUPPLIER_NAME: { status: 400, message: "El proveedor necesita nombre válido." },
    MISSING_SUPPLIER_ID: { status: 400, message: "Falta supplierId." },
    MISSING_PRODUCT_ID: { status: 400, message: "Falta productId." },
    DUPLICATE_SUPPLIER_NAME: { status: 409, message: "Ya existe un proveedor con ese nombre." },
    SUPPLIER_NOT_FOUND: { status: 404, message: "No encontramos ese proveedor." },
    PRODUCT_NOT_FOUND: { status: 404, message: "No encontramos ese producto." }
  };
  const found = map[raw] ?? { status: 500, message: "No se pudo guardar proveedor/producto-proveedor." };
  return { code: map[raw] ? raw : "SUPPLIER_SAVE_FAILED", status: found.status, message: found.message, details: { raw } };
}
