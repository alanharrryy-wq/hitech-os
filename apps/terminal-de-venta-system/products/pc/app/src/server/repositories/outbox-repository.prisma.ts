import { prisma } from "@/server/prisma/client";

export class OutboxRepositoryPrisma {
  listPending(businessId: string, limit = 50): Promise<any[]> {
    return prisma.outboxEvent.findMany({
      where: { businessId, status: { in: ["pending", "failed"] } },
      orderBy: { createdAt: "asc" },
      take: limit
    });
  }
}
