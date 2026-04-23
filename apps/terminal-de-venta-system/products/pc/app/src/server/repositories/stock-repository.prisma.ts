import { prisma } from "@/server/prisma/client";

export class StockRepositoryPrisma {
  listCritical(limit = 25) {
    return prisma.stockSnapshot.findMany({
      where: { daysCover: { lt: 2 } },
      orderBy: { daysCover: "asc" },
      take: limit
    });
  }
}
