import { prisma } from "@/server/prisma/client";

export class ShiftRepositoryPrisma {
  findOpenShift(cashierId: string): Promise<any | null> {
    return prisma.cashSession.findFirst({
      where: { cashierId, status: "OPEN" },
      orderBy: { openedAt: "desc" }
    });
  }

  findOpenSessionByTerminal(terminalId: string): Promise<any | null> {
    return prisma.cashSession.findFirst({
      where: { terminalId, status: "OPEN" },
      orderBy: { openedAt: "desc" }
    });
  }

  listRecent(limit = 10): Promise<any[]> {
    return prisma.cashSession.findMany({
      orderBy: { openedAt: "desc" },
      take: limit
    });
  }
}
