import { prisma } from "@/server/prisma/client";

export class PurchaseOrderRepositoryPrisma {
  listOpen(limit = 25) {
    return prisma.purchaseOrder.findMany({
      where: { status: { in: ["ordered", "partial"] } },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }
}
