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

type ProductRow = any;

function toApiProduct(row: ProductRow, mediaRef: string | null = null): PosApiProduct {
  const barcodes = Array.isArray(row.barcodes) ? row.barcodes.map((b: any) => String(b.code)) : [];
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

async function mediaRefsFor(productIds: string[]) {
  if (!productIds.length) return new Map<string, string | null>();
  const placeholders = productIds.map(() => "?").join(", ");
  const rows = await prisma.$queryRawUnsafe<Array<{ id: string; mediaRef: string | null }>>(
    `SELECT "id", "mediaRef" FROM "Product" WHERE "id" IN (${placeholders})`,
    ...productIds
  );
  return new Map(rows.map((row) => [row.id, row.mediaRef]));
}

export async function searchProducts(input: ProductSearchInput): Promise<PosApiProduct[]> {
  const q = input.q.trim();
  if (!q) {
    const rows = await prisma.product.findMany({
      where: {
        businessId: input.businessId,
        ...(input.includeInactive ? {} : { isActive: true })
      },
      include: { barcodes: true },
      orderBy: [{ isActive: "desc" }, { name: "asc" }],
      take: input.limit
    });
    const mediaRefs = await mediaRefsFor(rows.map((row: any) => row.id));
    return rows.map((row: any) => toApiProduct(row, mediaRefs.get(row.id) ?? null));
  }

  const barcodeRows = await prisma.barcode.findMany({
    where: {
      businessId: input.businessId,
      code: { contains: q }
    },
    include: { product: { include: { barcodes: true } } },
    take: input.limit
  });

  const barcodeProductIds = barcodeRows.map((row: any) => row.productId);

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
    include: { barcodes: true },
    orderBy: [{ isActive: "desc" }, { name: "asc" }],
    take: input.limit
  });

  const candidates = [...rows, ...barcodeRows.flatMap((row: any) => row.product ? [row.product] : [])];
  const mediaRefs = await mediaRefsFor(candidates.map((row: any) => row.id));
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
    include: { product: { include: { barcodes: true } } }
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
    include: { barcodes: true }
  });

  if (!product) return null;
  const mediaRefs = await mediaRefsFor([product.id]);
  return toApiProduct(product, mediaRefs.get(product.id) ?? null);
}
