import { prisma } from "@/server/prisma/client";

export class BarcodeRepositoryPrisma {
  listRecent(limit = 25) {
    return prisma.barcode.findMany({
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }
}
