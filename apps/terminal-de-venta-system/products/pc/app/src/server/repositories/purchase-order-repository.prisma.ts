import { prisma } from "@/server/prisma/client";

export class PurchaseOrderRepositoryPrisma {
  listOpen(limit = 25): Promise<any[]> {
    return prisma.purchaseOrder.findMany({
      where: { status: { in: ["ordered", "partial"] } },
      include: { supplier: true, lines: true },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  listRecentReceipts(limit = 25): Promise<any[]> {
    return prisma.goodsReceipt.findMany({
      include: { supplier: true, lines: true },
      orderBy: { receivedAt: "desc" },
      take: limit
    });
  }
}
