import { prisma } from "@/server/prisma/client";

export class ProductRepositoryPrisma {
  listActive(businessId: string, limit = 25): Promise<any[]> {
    return prisma.product.findMany({
      where: { businessId, isActive: true },
      include: { barcodes: true, stockSnapshots: true },
      orderBy: { updatedAt: "desc" },
      take: limit
    });
  }

  countActive(businessId: string): Promise<number> {
    return prisma.product.count({ where: { businessId, isActive: true } });
  }
}
