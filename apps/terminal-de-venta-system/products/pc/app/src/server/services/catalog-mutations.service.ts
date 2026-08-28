import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { appendWave3Audit } from "@/server/services/wave3-mutation-audit";

type ProductWriteInput = {
  sku?: unknown;
  name?: unknown;
  category?: unknown;
  priceCents?: unknown;
  costCents?: unknown;
  stockOnHand?: unknown;
  isActive?: unknown;
};

function requiredText(value: unknown, code: string, min = 1) {
  const text = typeof value === "string" ? value.trim() : "";
  if (text.length < min) throw new Error(code);
  return text;
}

function optionalInteger(value: unknown, code: string, fallback?: number) {
  if (value === undefined && fallback !== undefined) return fallback;
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 0) throw new Error(code);
  return parsed;
}

function productView(row: any) {
  return {
    id: row.id,
    businessId: row.businessId,
    sku: row.sku,
    name: row.name,
    category: row.category,
    priceCents: row.priceCents,
    costCents: row.costCents,
    stockOnHand: row.stockOnHand,
    isActive: row.isActive,
    createdAt: row.createdAt,
    updatedAt: row.updatedAt
  };
}

export async function createCatalogProduct(input: ProductWriteInput) {
  const businessId = await resolvePcBusinessScope();
  const sku = requiredText(input.sku, "CATALOG_SKU_REQUIRED", 2).slice(0, 80);
  const name = requiredText(input.name, "CATALOG_NAME_REQUIRED", 2).slice(0, 180);
  const category = requiredText(input.category, "CATALOG_CATEGORY_REQUIRED", 1).slice(0, 120);
  const priceCents = optionalInteger(input.priceCents, "CATALOG_PRICE_INVALID", 0);
  const costCents = optionalInteger(input.costCents, "CATALOG_COST_INVALID", 0);
  const stockOnHand = optionalInteger(input.stockOnHand, "CATALOG_STOCK_INVALID", 0);
  const db = prisma as any;

  const duplicate = await db.product.findFirst({ where: { businessId, sku }, select: { id: true } });
  if (duplicate) throw new Error("CATALOG_SKU_EXISTS");

  return db.$transaction(async (tx: any) => {
    const product = await tx.product.create({
      data: {
        id: randomUUID(),
        businessId,
        sku,
        name,
        category,
        priceCents,
        costCents,
        stockOnHand,
        isActive: input.isActive === false ? false : true
      }
    });
    await appendWave3Audit(tx, {
      businessId,
      topic: "catalog.product.created",
      entityType: "Product",
      entityId: product.id,
      summary: `Producto ${sku} creado desde PC Wave 3`,
      after: productView(product)
    });
    return productView(product);
  });
}

export async function getCatalogProduct(productId: string) {
  const businessId = await resolvePcBusinessScope();
  const row = await (prisma as any).product.findFirst({ where: { id: productId, businessId } });
  return row ? productView(row) : null;
}

export async function updateCatalogProduct(productId: string, input: ProductWriteInput) {
  const businessId = await resolvePcBusinessScope();
  const db = prisma as any;
  const current = await db.product.findFirst({ where: { id: productId, businessId } });
  if (!current) return null;

  const data: Record<string, unknown> = {};
  if (input.sku !== undefined) data.sku = requiredText(input.sku, "CATALOG_SKU_REQUIRED", 2).slice(0, 80);
  if (input.name !== undefined) data.name = requiredText(input.name, "CATALOG_NAME_REQUIRED", 2).slice(0, 180);
  if (input.category !== undefined) data.category = requiredText(input.category, "CATALOG_CATEGORY_REQUIRED", 1).slice(0, 120);
  if (input.priceCents !== undefined) data.priceCents = optionalInteger(input.priceCents, "CATALOG_PRICE_INVALID");
  if (input.costCents !== undefined) data.costCents = optionalInteger(input.costCents, "CATALOG_COST_INVALID");
  if (input.stockOnHand !== undefined) data.stockOnHand = optionalInteger(input.stockOnHand, "CATALOG_STOCK_INVALID");
  if (input.isActive !== undefined) data.isActive = Boolean(input.isActive);
  if (Object.keys(data).length === 0) throw new Error("CATALOG_UPDATE_EMPTY");

  if (typeof data.sku === "string" && data.sku !== current.sku) {
    const duplicate = await db.product.findFirst({ where: { businessId, sku: data.sku, NOT: { id: productId } }, select: { id: true } });
    if (duplicate) throw new Error("CATALOG_SKU_EXISTS");
  }

  return db.$transaction(async (tx: any) => {
    const product = await tx.product.update({ where: { id: productId }, data });
    await appendWave3Audit(tx, {
      businessId,
      topic: "catalog.product.updated",
      entityType: "Product",
      entityId: productId,
      summary: `Producto ${product.sku} actualizado desde PC Wave 3`,
      before: productView(current),
      after: productView(product)
    });
    return productView(product);
  });
}

export async function deleteCatalogProduct(productId: string) {
  const businessId = await resolvePcBusinessScope();
  const db = prisma as any;
  const current = await db.product.findFirst({ where: { id: productId, businessId } });
  if (!current) return null;

  try {
    return await db.$transaction(async (tx: any) => {
      await tx.product.delete({ where: { id: productId } });
      await appendWave3Audit(tx, {
        businessId,
        topic: "catalog.product.deleted",
        entityType: "Product",
        entityId: productId,
        summary: `Producto ${current.sku} eliminado desde PC Wave 3`,
        before: productView(current),
        after: null
      });
      return productView(current);
    });
  } catch (error) {
    if ((error as any)?.code === "P2003") throw new Error("CATALOG_PRODUCT_IN_USE");
    throw error;
  }
}
