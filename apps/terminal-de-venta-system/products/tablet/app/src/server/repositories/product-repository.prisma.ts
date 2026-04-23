import { prisma } from "@/server/prisma/client";

export class ProductRepositoryPrisma {
  listActive(limit = 25) {
    return prisma.product.findMany({
      where: { isActive: true },
      orderBy: { updatedAt: "desc" },
      take: limit
    });
  }
}
