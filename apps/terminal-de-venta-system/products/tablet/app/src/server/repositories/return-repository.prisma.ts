import { prisma } from "@/server/prisma/client";

export class ReturnRepositoryPrisma {
  listRecent(limit = 25): Promise<any[]> {
    return prisma.saleReturn.findMany({
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }
}
