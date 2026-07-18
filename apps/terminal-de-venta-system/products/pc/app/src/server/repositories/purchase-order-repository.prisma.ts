import { prisma } from "@/server/prisma/client";

export class PurchaseOrderRepositoryPrisma {
  listOpen(businessId: string, limit = 25): Promise<any[]> {
    return prisma.purchaseOrder.findMany({
      where: { businessId, status: { in: ["ordered", "partial"] } },
      include: { supplier: true, lines: true },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  listRecentReceipts(businessId: string, limit = 25): Promise<any[]> {
    return prisma.goodsReceipt.findMany({
      where: { businessId },
      include: { supplier: true, lines: true },
      orderBy: { receivedAt: "desc" },
      take: limit
    });
  }
}
