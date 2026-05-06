import { prisma } from "@/server/prisma/client";
import type { CatalogFilters, CatalogProductRecord } from "@/modules/catalog/types";

function toDateLabel(value: Date | string | null | undefined) {
  if (!value) return "No disponible";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function toIso(value: Date | string | null | undefined) {
  if (!value) return new Date(0).toISOString();
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return new Date(0).toISOString();
  return date.toISOString();
}

function whereFromFilters(filters: CatalogFilters) {
  const where: Record<string, unknown> = {};
  if (filters.status === "active") where.isActive = true;
  if (filters.status === "inactive") where.isActive = false;
  if (filters.category && filters.category !== "all") where.category = filters.category;
  const q = filters.q.trim();
  if (q) {
    where.OR = [
      { sku: { contains: q } },
      { name: { contains: q } },
      { category: { contains: q } },
      { barcodes: { some: { code: { contains: q } } } }
    ];
  }
  return where;
}

export class CatalogRepository {
  async listProducts(filters: CatalogFilters, limit = 250): Promise<CatalogProductRecord[]> {
    const db = prisma as any;
    const rows = await db.product.findMany({
      where: whereFromFilters(filters),
      include: {
        barcodes: true,
        stockSnapshots: { orderBy: { daysCover: "asc" }, take: 1 }
      },
      orderBy: [{ isActive: "desc" }, { updatedAt: "desc" }],
      take: limit
    });

    return rows.map((row: any) => {
      const firstSnapshot = row.stockSnapshots?.[0];
      return {
        id: row.id,
        businessId: row.businessId,
        sku: row.sku,
        name: row.name,
        category: row.category,
        priceCents: Number(row.priceCents ?? 0),
        costCents: Number(row.costCents ?? 0),
        stockOnHand: Number(row.stockOnHand ?? 0),
        isActive: Boolean(row.isActive),
        updatedAt: toIso(row.updatedAt),
        updatedAtLabel: toDateLabel(row.updatedAt),
        barcodes: (row.barcodes ?? []).map((barcode: { code: string }) => barcode.code).filter(Boolean),
        daysCover: typeof firstSnapshot?.daysCover === "number" ? firstSnapshot.daysCover : null,
        issues: []
      } satisfies CatalogProductRecord;
    });
  }

  async listCategories(): Promise<string[]> {
    const db = prisma as any;
    const rows = await db.product.findMany({
      select: { category: true },
      distinct: ["category"],
      orderBy: { category: "asc" },
      take: 100
    });
    return rows.map((row: { category: string }) => row.category).filter(Boolean);
  }
}
