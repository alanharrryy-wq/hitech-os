import type { Prisma } from "../../../.generated/prisma-client";
import { prisma } from "../prisma/client";
import type { ProductResolveInput, ProductSearchInput } from "./validators";

export type PosApiProduct = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  category: string;
  mediaRef: string | null;
  barcode: string | null;
  barcodes: string[];
  priceCents: number;
  price: number;
  costCents: number;
  stockOnHand: number;
  lowStockThreshold: number;
  isActive: boolean;
  updatedAt: string;
};

const PRODUCT_SELECT = {
  id: true,
  businessId: true,
  sku: true,
  name: true,
  category: true,
  priceCents: true,
  costCents: true,
  stockOnHand: true,
  isActive: true,
  updatedAt: true,
  barcodes: { select: { code: true } }
} satisfies Prisma.ProductSelect;

const BARCODE_PRODUCT_INCLUDE = {
  product: { select: PRODUCT_SELECT }
} satisfies Prisma.BarcodeInclude;

type ProductRow = Prisma.ProductGetPayload<{ select: typeof PRODUCT_SELECT }>;

function toApiProduct(row: ProductRow, mediaRef: string | null = null): PosApiProduct {
  const barcodes = row.barcodes.map((barcode) => barcode.code);
  return {
    id: row.id,
    businessId: row.businessId,
    sku: row.sku,
    name: row.name,
    category: row.category,
    mediaRef,
    barcode: barcodes[0] ?? null,
    barcodes,
    priceCents: row.priceCents,
    price: row.priceCents / 100,
    costCents: row.costCents,
    stockOnHand: row.stockOnHand,
    lowStockThreshold: 5,
    isActive: row.isActive,
    updatedAt: row.updatedAt instanceof Date ? row.updatedAt.toISOString() : String(row.updatedAt)
  };
}

function isMissingMediaRefColumn(error: unknown) {
  if (!(error instanceof Error)) return false;
  return /(?:column|campo).*(?:Product\.)?mediaRef.*(?:does not exist|no existe)|no such column.*mediaRef/i.test(error.message);
}

async function mediaRefsFor(productIds: string[]) {
  if (!productIds.length) return new Map<string, string | null>();
  const placeholders = productIds.map(() => "?").join(", ");
  try {
    const rows = await prisma.$queryRawUnsafe<Array<{ id: string; mediaRef: string | null }>>(
      `SELECT "id", "mediaRef" FROM "Product" WHERE "id" IN (${placeholders})`,
      ...productIds
    );
    return new Map(rows.map((row) => [row.id, row.mediaRef]));
  } catch (error) {
    if (isMissingMediaRefColumn(error)) return new Map<string, string | null>();
    throw error;
  }
}

export async function searchProducts(input: ProductSearchInput): Promise<PosApiProduct[]> {
  const q = input.q.trim();
  if (!q) {
    const rows = await prisma.product.findMany({
      where: {
        businessId: input.businessId,
        ...(input.includeInactive ? {} : { isActive: true })
      },
      select: PRODUCT_SELECT,
      orderBy: [{ isActive: "desc" }, { name: "asc" }],
      take: input.limit
    });
    const mediaRefs = await mediaRefsFor(rows.map((row) => row.id));
    return rows.map((row) => toApiProduct(row, mediaRefs.get(row.id) ?? null));
  }

  const barcodeRows = await prisma.barcode.findMany({
    where: {
      businessId: input.businessId,
      code: { contains: q }
    },
    include: BARCODE_PRODUCT_INCLUDE,
    take: input.limit
  });

  const barcodeProductIds = barcodeRows.map((row) => row.productId);

  const rows = await prisma.product.findMany({
    where: {
      businessId: input.businessId,
      ...(input.includeInactive ? {} : { isActive: true }),
      OR: [
        { sku: { contains: q } },
        { name: { contains: q } },
        { category: { contains: q } },
        ...(barcodeProductIds.length ? [{ id: { in: barcodeProductIds } }] : [])
      ]
    },
    select: PRODUCT_SELECT,
    orderBy: [{ isActive: "desc" }, { name: "asc" }],
    take: input.limit
  });

  const candidates = [...rows, ...barcodeRows.map((row) => row.product)];
  const mediaRefs = await mediaRefsFor(candidates.map((row) => row.id));
  const byId = new Map<string, PosApiProduct>();
  for (const row of rows) byId.set(row.id, toApiProduct(row, mediaRefs.get(row.id) ?? null));
  for (const row of barcodeRows) {
    if (row.product && (input.includeInactive || row.product.isActive)) {
      byId.set(row.product.id, toApiProduct(row.product, mediaRefs.get(row.product.id) ?? null));
    }
  }

  return [...byId.values()].slice(0, input.limit);
}

export async function resolveProduct(input: ProductResolveInput): Promise<PosApiProduct | null> {
  const code = input.code.trim();
  const barcode = await prisma.barcode.findFirst({
    where: { businessId: input.businessId, code },
    include: BARCODE_PRODUCT_INCLUDE
  });

  if (barcode?.product) {
    const mediaRefs = await mediaRefsFor([barcode.product.id]);
    return toApiProduct(barcode.product, mediaRefs.get(barcode.product.id) ?? null);
  }

  const product = await prisma.product.findFirst({
    where: {
      businessId: input.businessId,
      OR: [{ id: code }, { sku: code }]
    },
    select: PRODUCT_SELECT
  });

  if (!product) return null;
  const mediaRefs = await mediaRefsFor([product.id]);
  return toApiProduct(product, mediaRefs.get(product.id) ?? null);
}
