import { prisma } from "@/server/prisma/client";

export class SaleRepositoryPrisma {
  listRecent(limit = 25) {
    return prisma.sale.findMany({
      orderBy: { createdAt: "desc" },
      take: limit,
      include: { lines: true }
    });
  }
}
