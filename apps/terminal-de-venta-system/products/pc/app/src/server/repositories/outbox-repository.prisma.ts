import { prisma } from "@/server/prisma/client";

export class OutboxRepositoryPrisma {
  listPending(limit = 50): Promise<any[]> {
    return prisma.outboxEvent.findMany({
      where: { status: { in: ["pending", "failed"] } },
      orderBy: { createdAt: "asc" },
      take: limit
    });
  }
}
