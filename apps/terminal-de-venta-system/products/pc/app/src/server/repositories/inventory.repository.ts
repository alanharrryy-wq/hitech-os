import { prisma } from "@/server/prisma/client";
import type { InventoryFilters } from "@/modules/inventory/types";

function containsFilter(filters: InventoryFilters) {
  const q = filters.q.trim();
  if (!q) return undefined;
  return [
    { product: { sku: { contains: q } } },
    { product: { name: { contains: q } } },
    { location: { contains: q } }
  ];
}

export class InventoryRepository {
  async listSnapshots(filters: InventoryFilters, limit = 300): Promise<any[]> {
    const db = prisma as any;
    const where: Record<string, unknown> = {};
    const or = containsFilter(filters);
    if (or) where.OR = or;
    if (filters.location !== "all") where.location = filters.location;
    if (filters.state === "critical") where.OR = [...(Array.isArray(where.OR) ? where.OR : []), { available: { lte: 0 } }, { daysCover: { lt: 2 } }];
    if (filters.state === "low") where.daysCover = { gte: 2, lt: 5 };
    if (filters.state === "ok") where.daysCover = { gte: 5 };

    return db.stockSnapshot.findMany({
      where,
      include: { product: true },
      orderBy: [{ daysCover: "asc" }, { snapshotAt: "desc" }],
      take: limit
    });
  }

  async listMovements(filters: InventoryFilters, limit = 300): Promise<any[]> {
    const db = prisma as any;
    const where: Record<string, unknown> = {};
    const q = filters.q.trim();
    if (q) {
      where.OR = [
        { product: { sku: { contains: q } } },
        { product: { name: { contains: q } } },
        { reason: { contains: q } },
        { location: { contains: q } },
        { movement: { contains: q } }
      ];
    }
    if (filters.location !== "all") where.location = filters.location;

    return db.stockMovement.findMany({
      where,
      include: { product: true },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  async listCounts(filters: InventoryFilters, limit = 250): Promise<any[]> {
    const db = prisma as any;
    const where: Record<string, unknown> = {};
    const q = filters.q.trim();
    if (q) {
      where.OR = [
        { location: { contains: q } },
        { countedBy: { contains: q } },
        { status: { contains: q } }
      ];
    }
    if (filters.location !== "all") where.location = filters.location;
    if (filters.countStatus !== "all") where.status = filters.countStatus;

    return db.auditCount.findMany({
      where,
      orderBy: { countedAt: "desc" },
      take: limit
    });
  }
}
