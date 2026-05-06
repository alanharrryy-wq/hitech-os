import { prisma } from "@/server/prisma/client";

export class BarcodeRepositoryPrisma {
  listRecent(limit = 25): Promise<any[]> {
    return prisma.barcode.findMany({
      include: { product: true },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }
}
