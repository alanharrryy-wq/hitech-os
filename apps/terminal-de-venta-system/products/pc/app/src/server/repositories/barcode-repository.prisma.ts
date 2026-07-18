import { prisma } from "@/server/prisma/client";

export class BarcodeRepositoryPrisma {
  listRecent(businessId: string, limit = 25): Promise<any[]> {
    return prisma.barcode.findMany({
      where: { businessId },
      include: { product: true },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }
}
