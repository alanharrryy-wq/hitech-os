import { prisma } from "@/server/prisma/client";

export class SaleRepositoryPrisma {
  listRecent(limit = 25): Promise<any[]> {
    return prisma.sale.findMany({
      orderBy: { createdAt: "desc" },
      take: limit,
      include: { lines: true }
    });
  }

  listTopProducts(limit = 5): Promise<any[]> {
    return prisma.saleLine.findMany({
      orderBy: { totalCents: "desc" },
      take: limit
    });
  }
}
