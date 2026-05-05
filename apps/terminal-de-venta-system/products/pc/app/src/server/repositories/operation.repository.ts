import { prisma } from "@/server/prisma/client";

export class OperationRepository {
  async listPurchaseOrders(limit = 50): Promise<any[]> {
    const db = prisma as any;
    return db.purchaseOrder.findMany({
      include: {
        supplier: true,
        lines: true,
        goodsReceipts: { include: { lines: true } }
      },
      orderBy: [{ expectedAt: "asc" }, { createdAt: "desc" }],
      take: limit
    });
  }

  async listGoodsReceipts(limit = 50): Promise<any[]> {
    const db = prisma as any;
    return db.goodsReceipt.findMany({
      include: {
        supplier: true,
        lines: true,
        purchaseOrder: { include: { lines: true } }
      },
      orderBy: { receivedAt: "desc" },
      take: limit
    });
  }

  async listReplenishmentSignals(limit = 50): Promise<any[]> {
    const db = prisma as any;
    return db.replenishmentSignal.findMany({
      include: { product: { include: { stockSnapshots: true } } },
      orderBy: [{ priority: "desc" }, { createdAt: "desc" }],
      take: limit
    });
  }

  async listSales(limit = 250): Promise<any[]> {
    const db = prisma as any;
    return db.sale.findMany({
      include: { lines: true },
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  async listReturns(limit = 250): Promise<any[]> {
    const db = prisma as any;
    return db.saleReturn.findMany({
      orderBy: { createdAt: "desc" },
      take: limit
    });
  }

  async listStockSnapshots(limit = 250): Promise<any[]> {
    const db = prisma as any;
    return db.stockSnapshot.findMany({
      include: { product: true },
      orderBy: { daysCover: "asc" },
      take: limit
    });
  }
}
