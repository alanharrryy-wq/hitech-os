import { randomUUID } from "node:crypto";
import { prisma } from "../prisma/client";
import { DEFAULT_POS_API_BUSINESS_ID } from "./validators";

export const SALES_RESET_CONFIRMATION = "BORRAR VENTAS TABLET";

const SALE_OUTBOX_TOPICS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "sale.return.created",
  "sale.refunded",
  "cash.session.opened",
  "cash.movement.recorded",
  "shift.opened",
  "shift.closed"
];

export type SalesResetPreview = {
  businessId: string;
  scope: "sales_cash_outbox";
  counts: Record<string, number>;
  preserves: string[];
  confirmationPhrase: string;
  generatedAt: string;
};

async function countsForBusiness(businessId: string): Promise<Record<string, number>> {
  const db = prisma as any;
  const count = async (delegateName: string, where: Record<string, unknown>) => {
    const delegate = db[delegateName];
    if (!delegate?.count) return 0;
    return delegate.count({ where }).catch(() => 0);
  };
  const [sales, saleLines, tenders, returns, returnLines, cashSessions, cashMovements, cashAdjustments, saleOutboxEvents, saleStockMovements] = await Promise.all([
    count("sale", { businessId }),
    count("saleLine", { businessId }),
    count("salePaymentTender", { businessId }),
    count("saleReturn", { businessId }),
    count("saleReturnLine", { businessId }),
    count("cashSession", { businessId }),
    count("cashMovement", { businessId }),
    count("cashAdjustment", { businessId }),
    count("outboxEvent", { businessId, topic: { in: SALE_OUTBOX_TOPICS } }),
    count("stockMovement", { businessId, sourceType: "sale" })
  ]);

  return { sales, saleLines, tenders, returns, returnLines, cashSessions, cashMovements, cashAdjustments, saleOutboxEvents, saleStockMovements };
}

export async function previewSalesReset(businessId = DEFAULT_POS_API_BUSINESS_ID): Promise<SalesResetPreview> {
  return {
    businessId,
    scope: "sales_cash_outbox",
    counts: await countsForBusiness(businessId),
    preserves: [
      "licencia local y configuración de runtime",
      "catálogo local",
      "existencias y movimientos de inventario",
      "usuarios, roles y permisos",
      "eventos de auditoría de reset"
    ],
    confirmationPhrase: SALES_RESET_CONFIRMATION,
    generatedAt: new Date().toISOString()
  };
}

export async function performSalesReset(input: { businessId?: string; confirmation: string; operatorNote?: string | null }) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  if (input.confirmation !== SALES_RESET_CONFIRMATION) {
    throw new Error("SALES_RESET_CONFIRMATION_REQUIRED");
  }

  const before = await countsForBusiness(businessId);
  const db = prisma as any;
  const deleteMany = async (tx: any, delegateName: string, where: Record<string, unknown>) => {
    const delegate = tx[delegateName];
    if (!delegate?.deleteMany) return { count: 0, skipped: true };
    return delegate.deleteMany({ where }).catch(() => ({ count: 0, skipped: true }));
  };
  const resetId = `sales_reset_${randomUUID()}`;
  const result = await db.$transaction(async (tx: any) => {
    await deleteMany(tx, "saleReturnLine", { businessId });
    await deleteMany(tx, "saleReturn", { businessId });
    await deleteMany(tx, "salePaymentTender", { businessId });
    await deleteMany(tx, "saleLine", { businessId });
    await deleteMany(tx, "cashAdjustment", { businessId });
    await deleteMany(tx, "cashMovement", { businessId });
    await deleteMany(tx, "sale", { businessId });
    await deleteMany(tx, "cashSession", { businessId });
    await deleteMany(tx, "outboxEvent", { businessId, topic: { in: SALE_OUTBOX_TOPICS } });
    await tx.auditEvent.create({
      data: {
        id: resetId,
        businessId,
        actorId: null,
        topic: "tablet.sales.reset",
        entityType: "tablet_sales_db",
        entityId: businessId,
        summary: "Reset seguro de ventas/caja/outbox de Tablet ejecutado con confirmación explícita.",
        beforeJson: JSON.stringify(before),
        afterJson: null,
        metadataJson: JSON.stringify({
          operatorNote: input.operatorNote ?? null,
          preserved: ["license", "runtime_config", "catalog", "inventory", "users", "roles"],
          stockMovementsPreserved: true
        })
      }
    });
    return { resetId };
  });
  const after = await countsForBusiness(businessId);
  return { ...result, businessId, before, after, preservesLicenseConfig: true, preservesCatalogAndInventory: true };
}
