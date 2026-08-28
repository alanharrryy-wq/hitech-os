import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { appendWave3Audit } from "@/server/services/wave3-mutation-audit";

type SupplierWriteInput = { name?: unknown; status?: unknown };

function supplierView(row: any) {
  return { id: row.id, businessId: row.businessId, name: row.name, status: row.status, createdAt: row.createdAt, updatedAt: row.updatedAt };
}

function supplierName(value: unknown) {
  const name = typeof value === "string" ? value.trim() : "";
  if (name.length < 2) throw new Error("SUPPLIER_NAME_REQUIRED");
  return name.slice(0, 180);
}

function supplierStatus(value: unknown, fallback = "ACTIVE") {
  const status = typeof value === "string" ? value.trim().toUpperCase() : fallback;
  if (!/^[A-Z_]{2,40}$/.test(status)) throw new Error("SUPPLIER_STATUS_INVALID");
  return status;
}

export async function createSupplierRecord(input: SupplierWriteInput) {
  const businessId = await resolvePcBusinessScope();
  const name = supplierName(input.name);
  const status = supplierStatus(input.status);
  const db = prisma as any;
  const duplicate = await db.supplier.findFirst({ where: { businessId, name }, select: { id: true } });
  if (duplicate) throw new Error("SUPPLIER_NAME_EXISTS");
  return db.$transaction(async (tx: any) => {
    const supplier = await tx.supplier.create({ data: { id: randomUUID(), businessId, name, status } });
    await appendWave3Audit(tx, { businessId, topic: "supplier.created", entityType: "Supplier", entityId: supplier.id, summary: `Proveedor ${name} creado desde PC Wave 3`, after: supplierView(supplier) });
    return supplierView(supplier);
  });
}

export async function getSupplierRecord(supplierId: string) {
  const businessId = await resolvePcBusinessScope();
  const supplier = await (prisma as any).supplier.findFirst({ where: { id: supplierId, businessId } });
  return supplier ? supplierView(supplier) : null;
}

export async function updateSupplierRecord(supplierId: string, input: SupplierWriteInput) {
  const businessId = await resolvePcBusinessScope();
  const db = prisma as any;
  const current = await db.supplier.findFirst({ where: { id: supplierId, businessId } });
  if (!current) return null;
  const data: Record<string, unknown> = {};
  if (input.name !== undefined) data.name = supplierName(input.name);
  if (input.status !== undefined) data.status = supplierStatus(input.status);
  if (Object.keys(data).length === 0) throw new Error("SUPPLIER_UPDATE_EMPTY");
  if (typeof data.name === "string" && data.name !== current.name) {
    const duplicate = await db.supplier.findFirst({ where: { businessId, name: data.name, NOT: { id: supplierId } }, select: { id: true } });
    if (duplicate) throw new Error("SUPPLIER_NAME_EXISTS");
  }
  return db.$transaction(async (tx: any) => {
    const supplier = await tx.supplier.update({ where: { id: supplierId }, data });
    await appendWave3Audit(tx, { businessId, topic: "supplier.updated", entityType: "Supplier", entityId: supplierId, summary: `Proveedor ${supplier.name} actualizado desde PC Wave 3`, before: supplierView(current), after: supplierView(supplier) });
    return supplierView(supplier);
  });
}

export async function deleteSupplierRecord(supplierId: string) {
  const businessId = await resolvePcBusinessScope();
  const db = prisma as any;
  const current = await db.supplier.findFirst({ where: { id: supplierId, businessId } });
  if (!current) return null;
  try {
    return await db.$transaction(async (tx: any) => {
      await tx.supplier.delete({ where: { id: supplierId } });
      await appendWave3Audit(tx, { businessId, topic: "supplier.deleted", entityType: "Supplier", entityId: supplierId, summary: `Proveedor ${current.name} eliminado desde PC Wave 3`, before: supplierView(current), after: null });
      return supplierView(current);
    });
  } catch (error) {
    if ((error as any)?.code === "P2003") throw new Error("SUPPLIER_IN_USE");
    throw error;
  }
}
