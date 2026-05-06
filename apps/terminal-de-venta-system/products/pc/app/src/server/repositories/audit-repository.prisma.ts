import { prisma } from "@/server/prisma/client";

export class AuditRepositoryPrisma {
  listOpen(limit = 25) {
    return prisma.auditCount.findMany({
      where: { status: { in: ["open", "review"] } },
      orderBy: { countedAt: "desc" },
      take: limit
    });
  }
}
