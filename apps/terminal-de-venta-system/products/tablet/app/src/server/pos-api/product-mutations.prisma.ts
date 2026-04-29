import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { readBarcodeAvailabilityInput, readProductCreateInput, readProductUpdateInput, type BarcodeAvailabilityInput } from "./product-mutation-validators";

const DEFAULT_BUSINESS_NAME = "PRISMA Tablet Local";
const DEFAULT_LOCATION = "tablet-floor";

type TxClient = any;
const db = prisma as any;

function nowIso() {
  return new Date().toISOString();
}

function serializeProduct(product: any, barcodes: Array<{ code: string }> = []) {
  return {
    id: product.id,
    businessId: product.businessId,
    sku: product.sku,
    name: product.name,
    category: product.category,
    barcode: barcodes[0]?.code ?? null,
    barcodes: barcodes.map((item) => item.code),
    priceCents: product.priceCents,
    costCents: product.costCents,
    stockOnHand: product.stockOnHand,
    isActive: product.isActive,
    createdAt: product.createdAt,
    updatedAt: product.updatedAt
  };
}

async function ensureBusiness(businessId: string) {
  return prisma.business.upsert({
    where: { id: businessId },
    create: { id: businessId, name: DEFAULT_BUSINESS_NAME, currency: "MXN" },
    update: {}
  });
}

async function ensureSkuAvailable(businessId: string, sku: string, productId?: string) {
  const existing = await prisma.product.findUnique({ where: { businessId_sku: { businessId, sku } } });
  if (existing && existing.id !== productId) throw new Error("DUPLICATE_SKU");
}

async function ensureBarcodeAvailable(businessId: string, code: string | null, productId?: string) {
  if (!code) return null;
  const existing = await prisma.barcode.findUnique({ where: { businessId_code: { businessId, code } }, include: { product: true } });
  if (existing && existing.productId !== productId) throw new Error("DUPLICATE_BARCODE");
  return existing;
}

async function createOutboxEvent(tx: any, businessId: string, topic: string, aggregateId: string, payload: Record<string, unknown>) {
  return tx.outboxEvent.create({
    data: {
      id: randomUUID(),
      businessId,
      topic,
      aggregateId,
      payloadJson: JSON.stringify({ eventId: randomUUID(), topic, businessId, source: "tablet.catalog", occurredAt: nowIso(), schemaVersion: "1.0", payload }),
      status: "pending",
      attempts: 0
    }
  });
}

export async function barcodeAvailability(raw: Partial<BarcodeAvailabilityInput>) {
  const input = readBarcodeAvailabilityInput(raw);
  const barcode = await prisma.barcode.findUnique({
    where: { businessId_code: { businessId: input.businessId, code: input.code } },
    include: { product: true }
  });
  const available = !barcode || barcode.productId === input.productId;
  return {
    code: input.code,
    available,
    duplicateProduct: barcode && !available ? { id: barcode.product.id, sku: barcode.product.sku, name: barcode.product.name } : null
  };
}

export async function createTabletProduct(raw: any) {
  const input = readProductCreateInput(raw);
  await ensureBusiness(input.businessId);
  await ensureSkuAvailable(input.businessId, input.sku);
  await ensureBarcodeAvailable(input.businessId, input.barcode);

  const productId = randomUUID();
  return db.$transaction(async (tx: TxClient) => {
    const product = await tx.product.create({
      data: {
        id: productId,
        businessId: input.businessId,
        sku: input.sku,
        name: input.name,
        category: input.category,
        priceCents: input.priceCents,
        costCents: input.costCents,
        stockOnHand: input.stockOnHand,
        isActive: input.isActive
      }
    });

    const barcodeRows = input.barcode
      ? [await tx.barcode.create({ data: { id: randomUUID(), businessId: input.businessId, productId, code: input.barcode } })]
      : [];

    if (input.stockOnHand > 0) {
      await tx.stockMovement.create({
        data: {
          id: randomUUID(),
          businessId: input.businessId,
          productId,
          movement: "adjustment",
          qty: input.stockOnHand,
          reason: "alta_inicial_tablet",
          location: DEFAULT_LOCATION
        }
      });
    }

    await createOutboxEvent(tx, input.businessId, "catalog.product.created", productId, {
      productId,
      sku: input.sku,
      name: input.name,
      category: input.category,
      barcode: input.barcode,
      priceCents: input.priceCents,
      stockOnHand: input.stockOnHand,
      isActive: input.isActive
    });

    return serializeProduct(product, barcodeRows);
  });
}

export async function updateTabletProduct(raw: any) {
  const input = readProductUpdateInput(raw);
  await ensureBusiness(input.businessId);
  const existing = await prisma.product.findUnique({
    where: { id_businessId: { id: input.id!, businessId: input.businessId } },
    include: { barcodes: true }
  });
  if (!existing) throw new Error("PRODUCT_NOT_FOUND");
  await ensureSkuAvailable(input.businessId, input.sku, input.id);
  await ensureBarcodeAvailable(input.businessId, input.barcode, input.id);
  const delta = input.stockOnHand - existing.stockOnHand;

  return db.$transaction(async (tx: TxClient) => {
    const product = await tx.product.update({
      where: { id_businessId: { id: input.id!, businessId: input.businessId } },
      data: {
        sku: input.sku,
        name: input.name,
        category: input.category,
        priceCents: input.priceCents,
        costCents: input.costCents,
        stockOnHand: input.stockOnHand,
        isActive: input.isActive
      }
    });

    await tx.barcode.deleteMany({ where: { businessId: input.businessId, productId: input.id! } });
    const barcodeRows = input.barcode
      ? [await tx.barcode.create({ data: { id: randomUUID(), businessId: input.businessId, productId: input.id!, code: input.barcode } })]
      : [];

    if (delta !== 0) {
      await tx.stockMovement.create({
        data: {
          id: randomUUID(),
          businessId: input.businessId,
          productId: input.id!,
          movement: "adjustment",
          qty: delta,
          reason: "ajuste_catalogo_tablet",
          location: DEFAULT_LOCATION
        }
      });
    }

    await createOutboxEvent(tx, input.businessId, "catalog.product.updated", input.id!, {
      productId: input.id,
      before: { sku: existing.sku, name: existing.name, priceCents: existing.priceCents, stockOnHand: existing.stockOnHand, isActive: existing.isActive },
      after: { sku: input.sku, name: input.name, priceCents: input.priceCents, stockOnHand: input.stockOnHand, isActive: input.isActive }
    });

    return serializeProduct(product, barcodeRows);
  });
}

export function productMutationErrorToResponse(error: unknown) {
  const raw = error instanceof Error ? error.message : String(error);
  const map: Record<string, { status: number; message: string }> = {
    INVALID_PRODUCT_SKU: { status: 400, message: "El SKU debe tener entre 2 y 64 caracteres." },
    INVALID_PRODUCT_NAME: { status: 400, message: "El nombre del producto debe tener entre 2 y 160 caracteres." },
    INVALID_PRODUCT_CATEGORY: { status: 400, message: "La categoría debe tener entre 2 y 80 caracteres." },
    INVALID_PRODUCT_PRICE: { status: 400, message: "El precio de venta debe ser mayor a cero." },
    INVALID_PRODUCT_BARCODE: { status: 400, message: "El código de barras debe tener entre 3 y 64 caracteres." },
    MISSING_PRODUCT_ID: { status: 400, message: "Falta el identificador del producto." },
    MISSING_BARCODE: { status: 400, message: "Falta el código de barras." },
    PRODUCT_NOT_FOUND: { status: 404, message: "No encontramos ese producto." },
    DUPLICATE_SKU: { status: 409, message: "Ya existe un producto con ese SKU." },
    DUPLICATE_BARCODE: { status: 409, message: "Ese código de barras ya pertenece a otro producto." }
  };
  const found = map[raw] ?? { status: 500, message: "No se pudo guardar el producto." };
  return { code: map[raw] ? raw : "PRODUCT_SAVE_FAILED", status: found.status, message: found.message, details: { raw } };
}
