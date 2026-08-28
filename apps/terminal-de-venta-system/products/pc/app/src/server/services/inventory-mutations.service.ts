import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { appendWave3Audit } from "@/server/services/wave3-mutation-audit";

type StockAdjustmentInput = { productId?: unknown; delta?: unknown; reason?: unknown; location?: unknown };
type CountWriteInput = { location?: unknown; countedBy?: unknown; variance?: unknown; status?: unknown };

function requiredText(value: unknown, code: string, min = 1, max = 180) {
  const text = typeof value === "string" ? value.trim() : "";
  if (text.length < min) throw new Error(code);
  return text.slice(0, max);
}

function countView(row: any) {
  return { id: row.id, businessId: row.businessId, location: row.location, countedBy: row.countedBy, variance: row.variance, status: row.status, countedAt: row.countedAt };
}

function normalizeCountStatus(value: unknown) {
  const status = typeof value === "string" ? value.trim().toLowerCase() : "";
  if (!new Set(["open", "review", "closed"]).has(status)) throw new Error("COUNT_STATUS_INVALID");
  return status;
}

export async function adjustInventoryStock(input: StockAdjustmentInput) {
  const businessId = await resolvePcBusinessScope();
  const productId = requiredText(input.productId, "STOCK_PRODUCT_REQUIRED", 1, 120);
  const reason = requiredText(input.reason, "STOCK_REASON_REQUIRED", 3, 240);
  const location = requiredText(input.location, "STOCK_LOCATION_REQUIRED", 1, 120);
  const delta = Number(input.delta);
  if (!Number.isInteger(delta) || delta === 0) throw new Error("STOCK_DELTA_INVALID");
  const db = prisma as any;

  return db.$transaction(async (tx: any) => {
    const product = await tx.product.findFirst({ where: { id: productId, businessId } });
    if (!product) throw new Error("STOCK_PRODUCT_NOT_FOUND");
    const snapshot = await tx.stockSnapshot.findUnique({ where: { businessId_productId_location: { businessId, productId, location } } });
    const currentTotal = Number(product.stockOnHand ?? 0);
    const currentLocation = Number(snapshot?.onHand ?? currentTotal);
    const nextTotal = currentTotal + delta;
    const nextLocation = currentLocation + delta;
    if (nextTotal < 0 || nextLocation < 0) throw new Error("STOCK_NEGATIVE_BLOCKED");
    const reserved = Number(snapshot?.reserved ?? 0);
    const now = new Date();

    const updatedProduct = await tx.product.update({ where: { id: productId }, data: { stockOnHand: nextTotal } });
    const updatedSnapshot = await tx.stockSnapshot.upsert({
      where: { businessId_productId_location: { businessId, productId, location } },
      create: {
        id: randomUUID(), businessId, productId, location,
        onHand: nextLocation, reserved, available: nextLocation - reserved,
        daysCover: Number(snapshot?.daysCover ?? 0), snapshotAt: now
      },
      update: { onHand: nextLocation, reserved, available: nextLocation - reserved, snapshotAt: now }
    });
    const movement = await tx.stockMovement.create({
      data: {
        id: randomUUID(), businessId, productId,
        movement: delta > 0 ? "adjust_up" : "adjust_down",
        qty: Math.abs(delta), reason, location
      }
    });
    await appendWave3Audit(tx, {
      businessId,
      topic: "inventory.stock.adjusted",
      entityType: "Product",
      entityId: productId,
      summary: `Stock ajustado ${delta > 0 ? "+" : ""}${delta} en ${location}`,
      before: { stockOnHand: currentTotal, locationOnHand: currentLocation },
      after: { stockOnHand: updatedProduct.stockOnHand, locationOnHand: updatedSnapshot.onHand, movementId: movement.id },
      metadata: { reason, location, delta }
    });
    return {
      product: { id: updatedProduct.id, sku: updatedProduct.sku, stockOnHand: updatedProduct.stockOnHand },
      snapshot: { id: updatedSnapshot.id, location: updatedSnapshot.location, onHand: updatedSnapshot.onHand, reserved: updatedSnapshot.reserved, available: updatedSnapshot.available, snapshotAt: updatedSnapshot.snapshotAt },
      movement: { id: movement.id, movement: movement.movement, qty: movement.qty, reason: movement.reason, location: movement.location, createdAt: movement.createdAt },
      delta
    };
  });
}

export async function createInventoryCount(input: CountWriteInput) {
  const businessId = await resolvePcBusinessScope();
  const location = requiredText(input.location, "COUNT_LOCATION_REQUIRED", 1, 120);
  const countedBy = requiredText(input.countedBy, "COUNT_ACTOR_REQUIRED", 2, 120);
  const variance = input.variance === undefined ? 0 : Number(input.variance);
  if (!Number.isInteger(variance)) throw new Error("COUNT_VARIANCE_INVALID");
  const status = input.status === undefined ? "open" : normalizeCountStatus(input.status);
  if (status !== "open") throw new Error("COUNT_CREATE_MUST_BE_OPEN");
  const db = prisma as any;
  return db.$transaction(async (tx: any) => {
    const count = await tx.auditCount.create({ data: { id: randomUUID(), businessId, location, countedBy, variance, status: "open", countedAt: new Date() } });
    await appendWave3Audit(tx, { businessId, topic: "inventory.count.opened", entityType: "AuditCount", entityId: count.id, summary: `Conteo abierto en ${location}`, after: countView(count) });
    return countView(count);
  });
}

export async function getInventoryCount(countId: string) {
  const businessId = await resolvePcBusinessScope();
  const row = await (prisma as any).auditCount.findFirst({ where: { id: countId, businessId } });
  return row ? countView(row) : null;
}

export async function updateInventoryCount(countId: string, input: CountWriteInput) {
  const businessId = await resolvePcBusinessScope();
  const db = prisma as any;
  const current = await db.auditCount.findFirst({ where: { id: countId, businessId } });
  if (!current) return null;
  if (current.status === "closed") throw new Error("COUNT_ALREADY_CLOSED");

  const targetStatus = input.status === undefined ? current.status : normalizeCountStatus(input.status);
  const allowed = current.status === "open" ? new Set(["open", "review", "closed"]) : new Set(["review", "closed"]);
  if (!allowed.has(targetStatus)) throw new Error("COUNT_TRANSITION_INVALID");
  const data: Record<string, unknown> = { countedAt: new Date() };
  if (input.location !== undefined) data.location = requiredText(input.location, "COUNT_LOCATION_REQUIRED", 1, 120);
  if (input.countedBy !== undefined) data.countedBy = requiredText(input.countedBy, "COUNT_ACTOR_REQUIRED", 2, 120);
  if (input.variance !== undefined) {
    const variance = Number(input.variance);
    if (!Number.isInteger(variance)) throw new Error("COUNT_VARIANCE_INVALID");
    data.variance = variance;
  }
  data.status = targetStatus;

  return db.$transaction(async (tx: any) => {
    const updated = await tx.auditCount.update({ where: { id: countId }, data });
    await appendWave3Audit(tx, {
      businessId,
      topic: targetStatus === "closed" ? "inventory.count.closed" : "inventory.count.reviewed",
      entityType: "AuditCount",
      entityId: countId,
      summary: `Conteo ${targetStatus} en ${updated.location}`,
      before: countView(current),
      after: countView(updated)
    });
    return countView(updated);
  });
}
