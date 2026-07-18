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
  async listSnapshots(businessId: string, filters: InventoryFilters, limit = 300): Promise<any[]> {
    const db = prisma as any;
    const where: Record<string, unknown> = { businessId };
    const conditions: Record<string, unknown>[] = [];
    const or = containsFilter(filters);
    if (or) conditions.push({ OR: or });
    if (filters.location !== "all") conditions.push({ location: filters.location });
    if (filters.state === "critical") conditions.push({ OR: [{ available: { lte: 0 } }, { daysCover: { lt: 2 } }] });
    if (filters.state === "low") conditions.push({ daysCover: { gte: 2, lt: 5 } });
    if (filters.state === "ok") conditions.push({ daysCover: { gte: 5 } });
    if (conditions.length > 0) where.AND = conditions;

    return db.stockSnapshot.findMany({
      where,
      include: { product: true },
      orderBy: [{ daysCover: "asc" }, { snapshotAt: "desc" }],
      take: limit
    });
  }

  async listMovements(businessId: string, filters: InventoryFilters, limit = 300): Promise<any[]> {
    const db = prisma as any;
    const where: Record<string, unknown> = { businessId };
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

    const query = {
      where,
      select: {
        id: true,
        businessId: true,
        productId: true,
        movement: true,
        qty: true,
        reason: true,
        location: true,
        createdAt: true,
        product: { select: { sku: true, name: true } }
      },
      orderBy: { createdAt: "desc" },
      take: limit
    };

    try {
      return await db.stockMovement.findMany(query);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const isSchemaDrift = message.includes("beforeQty") || message.includes("afterQty") || message.includes("does not exist in the current database");
      if (!isSchemaDrift) throw error;
      return [];
    }
  }

  async listCounts(businessId: string, filters: InventoryFilters, limit = 250): Promise<any[]> {
    const db = prisma as any;
    const where: Record<string, unknown> = { businessId };
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
