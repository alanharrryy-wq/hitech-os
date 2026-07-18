import { prisma } from "@/server/prisma/client";

export class OperationRepository {
  async listPurchaseOrders(businessId: string, limit = 50): Promise<any[]> {
    const db = prisma as any;
    return db.purchaseOrder.findMany({
      where: { businessId },
      include: {
        supplier: true,
        lines: true,
        goodsReceipts: { include: { lines: true } }
      },
      orderBy: [{ expectedAt: "asc" }, { createdAt: "desc" }],
      take: limit
    });
  }

  async listGoodsReceipts(businessId: string, limit = 50): Promise<any[]> {
    const db = prisma as any;
    return db.goodsReceipt.findMany({
      where: { businessId },
      include: {
        supplier: true,
        lines: true,
        purchaseOrder: { include: { lines: true } }
      },
      orderBy: { receivedAt: "desc" },
      take: limit
    });
  }

  async listReplenishmentSignals(businessId: string, limit = 50): Promise<any[]> {
    const db = prisma as any;
    return db.replenishmentSignal.findMany({
      where: { businessId },
      include: { product: { include: { stockSnapshots: true } } },
      orderBy: [{ priority: "desc" }, { createdAt: "desc" }],
      take: limit
    });
  }

  async listSales(businessId: string, limit = 250): Promise<any[]> {
    const db = prisma as any;
    const safeLimit = Math.max(1, Math.min(Number(limit) || 250, 500));

    try {
      return await db.sale.findMany({
        where: { businessId },
        select: {
          id: true,
          businessId: true,
          terminalId: true,
          cashSessionId: true,
          folio: true,
          cashier: true,
          totalCents: true,
          status: true,
          createdAt: true,
          lines: true
        },
        orderBy: { createdAt: "desc" },
        take: safeLimit
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const isSchemaDrift = message.includes("clientRequestId") || message.includes("does not exist in the current database");
      if (!isSchemaDrift) throw error;

      return await db.$queryRawUnsafe(
        `SELECT id, businessId, terminalId, cashSessionId, folio, cashier, totalCents, status, createdAt FROM Sale WHERE businessId = ? ORDER BY createdAt DESC LIMIT ${safeLimit}`,
        businessId
      );
    }
  }

  async listReturns(businessId: string, limit = 250): Promise<any[]> {
    const db = prisma as any;
    return db.saleReturn.findMany({
      where: { businessId },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  async listStockSnapshots(businessId: string, limit = 250): Promise<any[]> {
    const db = prisma as any;
    return db.stockSnapshot.findMany({
      where: { businessId },
      include: { product: true },
      orderBy: { daysCover: "asc" },
      take: limit
    });
  }
}
