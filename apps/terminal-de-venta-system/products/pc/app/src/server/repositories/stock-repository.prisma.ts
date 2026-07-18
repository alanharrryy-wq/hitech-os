import { prisma } from "@/server/prisma/client";

export class StockRepositoryPrisma {
  listCritical(businessId: string, limit = 25, maxDaysCover = 2): Promise<any[]> {
    return prisma.stockSnapshot.findMany({
      where: { businessId, daysCover: { lt: maxDaysCover } },
      include: { product: true },
      orderBy: { daysCover: "asc" },
      take: limit
    });
  }

  listReplenishmentSignals(businessId: string, limit = 25): Promise<any[]> {
    return prisma.replenishmentSignal.findMany({
      where: { businessId },
      include: { product: true },
      orderBy: [{ priority: "asc" }, { createdAt: "desc" }],
      take: limit
    });
  }
}
