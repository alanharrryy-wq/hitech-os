import { prisma } from "@/server/prisma/client";

export class ProductRepositoryPrisma {
  listActive(limit = 25): Promise<any[]> {
    return prisma.product.findMany({
      where: { isActive: true },
      include: { barcodes: true, stockSnapshots: true },
      orderBy: { updatedAt: "desc" },
      take: limit
    });
  }
}
