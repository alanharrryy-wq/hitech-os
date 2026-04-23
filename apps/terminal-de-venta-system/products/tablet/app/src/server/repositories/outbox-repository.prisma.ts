import { prisma } from "@/server/prisma/client";

export class OutboxRepositoryPrisma {
  listPending(limit = 50) {
    return prisma.outboxEvent.findMany({
      where: { status: { in: ["pending", "failed"] } },
      orderBy: { createdAt: "asc" },
      take: limit
    });
  }

  listRecent(limit = 25) {
    return prisma.outboxEvent.findMany({
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  listByAggregate(aggregateId: string, limit = 10) {
    return prisma.outboxEvent.findMany({
      where: { aggregateId },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }
}
