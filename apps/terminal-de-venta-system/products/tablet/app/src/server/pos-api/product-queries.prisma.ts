import { prisma } from "../prisma/client";
import type { ProductResolveInput, ProductSearchInput } from "./validators";

export type PosApiProduct = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  category: string;
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

function toApiProduct(row: ProductRow): PosApiProduct {
  const barcodes = Array.isArray(row.barcodes) ? row.barcodes.map((b: any) => String(b.code)) : [];
  return {
    id: row.id,
    businessId: row.businessId,
    sku: row.sku,
    name: row.name,
    category: row.category,
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
    return rows.map(toApiProduct);
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

  const byId = new Map<string, PosApiProduct>();
  for (const row of rows) byId.set(row.id, toApiProduct(row));
  for (const row of barcodeRows) {
    if (row.product && (input.includeInactive || row.product.isActive)) {
      byId.set(row.product.id, toApiProduct(row.product));
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

  if (barcode?.product) return toApiProduct(barcode.product);

  const product = await prisma.product.findFirst({
    where: {
      businessId: input.businessId,
      OR: [{ id: code }, { sku: code }]
    },
    include: { barcodes: true }
  });

  return product ? toApiProduct(product) : null;
}
