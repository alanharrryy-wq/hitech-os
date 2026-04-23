import { prisma } from "@/server/prisma/client";

export class ShiftRepositoryPrisma {
  findOpenShift(cashierId: string) {
    return prisma.shift.findFirst({
      where: { cashierId, closedAt: null },
      orderBy: { openedAt: "desc" }
    });
  }
}
