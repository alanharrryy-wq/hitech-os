import { prisma } from "@/server/prisma/client";

export class StockRepositoryPrisma {
  listCritical(limit = 25): Promise<any[]> {
    return prisma.stockSnapshot.findMany({
      where: { daysCover: { lt: 2 } },
      include: { product: true },
      orderBy: { daysCover: "asc" },
      take: limit
    });
  }

  listReplenishmentSignals(limit = 25): Promise<any[]> {
    return prisma.replenishmentSignal.findMany({
      include: { product: true },
      orderBy: [{ priority: "asc" }, { createdAt: "desc" }],
      take: limit
    });
  }
}
