import { prisma } from "@/server/prisma/client";

export class AuditRepositoryPrisma {
  listOpen(businessId: string, limit = 25) {
    return prisma.auditCount.findMany({
      where: { businessId, status: { in: ["open", "review"] } },
      orderBy: { countedAt: "desc" },
      take: limit
    });
  }
}
