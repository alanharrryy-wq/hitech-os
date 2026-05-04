import type {
  SmartPurchaseRecommendation,
  SupplierAccount,
  SupplierAuditEvent,
  SupplierPayable,
  SupplierProductLink,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt
} from "./types";

export interface PrismaSupplierRecord { id: string; businessId: string; tradeName: string; legalName: string | null; category: string; status: string; notes: string | null; createdAt: string; updatedAt: string; }
export interface PrismaSupplierContactRecord { id: string; supplierId: string; name: string; role: string; phone: string | null; whatsapp: string | null; email: string | null; isPrimary: boolean; }
export interface PrismaSupplierScheduleRecord { id: string; supplierId: string; cadence: string; weekdaysJson: string; approximateTime: string; orderCutoffWeekday: string; orderCutoffTime: string; leadTimeDays: number; nextVisitDate: string; nextOrderCutoff: string; }
export interface PrismaSupplierTermsRecord { id: string; supplierId: string; paymentCondition: string; creditDays: number; minimumOrderCents: number; creditLimitCents: number; usualDiscountBps: number; shippingCostCents: number; returnPolicy: string; }
export interface PrismaSupplierProductRecord { id: string; supplierId: string; productId: string; isPrimary: boolean; packageSize: number; minPurchaseUnits: number; recentCostCents: number; lastCostUpdateAt: string; }
export interface PrismaPurchaseOrderRecord { id: string; businessId: string; supplierId: string; folio: string; source: string; status: string; createdAt: string; expectedReceptionDate: string; expectedPaymentDate: string; totalCents: number; recommendationId: string | null; }
export interface PrismaPurchaseOrderLineRecord { id: string; orderId: string; productId: string; skuSnapshot: string; nameSnapshot: string; orderedUnits: number; receivedUnits: number; unitCostCents: number; expectedTotalCents: number; }
export interface PrismaReceivingReceiptRecord { id: string; orderId: string | null; supplierId: string; status: string; expectedAt: string; receivedAt: string | null; reason: string | null; }
export interface PrismaReceivingDifferenceRecord { id: string; receiptId: string; productId: string; skuSnapshot: string; nameSnapshot: string; expectedUnits: number; receivedUnits: number; reason: string; note: string; }
export interface PrismaSupplierPayableRecord { id: string; supplierId: string; orderId: string | null; dueDate: string; amountCents: number; status: string; notes: string | null; }
export interface PrismaSupplierAuditEventRecord { id: string; topic: string; actorId: string; actorName: string; actorRole: string; entityType: string; entityId: string; supplierId: string | null; supplierName: string | null; beforeJson: string | null; afterJson: string | null; reason: string; createdAt: string; source: string; visibleSummary: string; requiresReview: boolean; }
export interface PrismaSmartPurchaseRecommendationRecord { id: string; supplierId: string | null; supplierName: string; priority: string; action: string; cashImpact: string; title: string; summary: string; generatedAt: string; idealOrderDate: string; expectedReceptionDate: string; expectedPaymentDate: string; estimatedTotalCents: number; safeBudgetCents: number; cashAfterPurchaseCents: number; reasonsJson: string; auditRequired: boolean; blockedReason: string | null; }

export function mapSupplierToPrisma(supplier: SupplierAccount, businessId: string): { supplier: PrismaSupplierRecord; contacts: PrismaSupplierContactRecord[]; schedule?: PrismaSupplierScheduleRecord; terms: PrismaSupplierTermsRecord } {
  return {
    supplier: { id: supplier.id, businessId, tradeName: supplier.tradeName, legalName: supplier.legalName ?? null, category: supplier.category, status: supplier.status, notes: supplier.notes ?? null, createdAt: supplier.createdAt, updatedAt: supplier.updatedAt },
    contacts: supplier.contacts.map((contact) => ({ id: contact.id, supplierId: supplier.id, name: contact.name, role: contact.role, phone: contact.phone ?? null, whatsapp: contact.whatsapp ?? null, email: contact.email ?? null, isPrimary: contact.isPrimary })),
    schedule: supplier.visitRule ? { id: `sched_${supplier.id}`, supplierId: supplier.id, cadence: supplier.visitRule.cadence, weekdaysJson: JSON.stringify(supplier.visitRule.weekdays), approximateTime: supplier.visitRule.approximateTime, orderCutoffWeekday: supplier.visitRule.orderCutoffWeekday, orderCutoffTime: supplier.visitRule.orderCutoffTime, leadTimeDays: supplier.visitRule.leadTimeDays, nextVisitDate: supplier.visitRule.nextVisitDate, nextOrderCutoff: supplier.visitRule.nextOrderCutoff } : undefined,
    terms: { id: `terms_${supplier.id}`, supplierId: supplier.id, paymentCondition: supplier.terms.paymentCondition, creditDays: supplier.terms.creditDays, minimumOrderCents: supplier.terms.minimumOrderCents, creditLimitCents: supplier.terms.creditLimitCents, usualDiscountBps: supplier.terms.usualDiscountBps, shippingCostCents: supplier.terms.shippingCostCents, returnPolicy: supplier.terms.returnPolicy }
  };
}

export function mapSupplierProductToPrisma(link: SupplierProductLink): PrismaSupplierProductRecord {
  return { id: link.id, supplierId: link.supplierId, productId: link.productId, isPrimary: link.isPrimary, packageSize: link.packageSize, minPurchaseUnits: link.minPurchaseUnits, recentCostCents: link.recentCostCents, lastCostUpdateAt: link.lastCostUpdateAt };
}

export function mapOrderToPrisma(order: SupplierPurchaseOrder, businessId: string, recommendationId: string | null = null): { order: PrismaPurchaseOrderRecord; lines: PrismaPurchaseOrderLineRecord[] } {
  return {
    order: { id: order.id, businessId, supplierId: order.supplierId, folio: order.folio, source: order.source, status: order.status, createdAt: order.createdAt, expectedReceptionDate: order.expectedReceptionDate, expectedPaymentDate: order.expectedPaymentDate, totalCents: order.totalCents, recommendationId },
    lines: order.lines.map((line) => ({ id: line.id, orderId: order.id, productId: line.productId, skuSnapshot: line.sku, nameSnapshot: line.name, orderedUnits: line.orderedUnits, receivedUnits: line.receivedUnits, unitCostCents: line.unitCostCents, expectedTotalCents: line.expectedTotalCents }))
  };
}

export function mapReceiptToPrisma(receipt: SupplierReceivingReceipt, reason: string | null = null): { receipt: PrismaReceivingReceiptRecord; differences: PrismaReceivingDifferenceRecord[] } {
  return {
    receipt: { id: receipt.id, orderId: receipt.orderId ?? null, supplierId: receipt.supplierId, status: receipt.status, expectedAt: receipt.expectedAt, receivedAt: receipt.receivedAt ?? null, reason },
    differences: receipt.differences.map((difference, index) => ({ id: `diff_${receipt.id}_${index + 1}`, receiptId: receipt.id, productId: difference.productId, skuSnapshot: difference.sku, nameSnapshot: difference.name, expectedUnits: difference.expectedUnits, receivedUnits: difference.receivedUnits, reason: difference.reason, note: difference.note }))
  };
}

export function mapPayableToPrisma(payable: SupplierPayable): PrismaSupplierPayableRecord {
  return { id: payable.id, supplierId: payable.supplierId, orderId: payable.orderId ?? null, dueDate: payable.dueDate, amountCents: payable.amountCents, status: payable.status, notes: payable.notes ?? null };
}

export function mapAuditEventToPrisma(event: SupplierAuditEvent): PrismaSupplierAuditEventRecord {
  return { id: event.id, topic: event.topic, actorId: event.actor.id, actorName: event.actor.name, actorRole: event.actor.role, entityType: event.entityType, entityId: event.entityId, supplierId: event.supplierId ?? null, supplierName: event.supplierName ?? null, beforeJson: event.before ? JSON.stringify(event.before) : null, afterJson: event.after ? JSON.stringify(event.after) : null, reason: event.reason, createdAt: event.createdAt, source: event.source, visibleSummary: event.visibleSummary, requiresReview: event.requiresReview };
}

export function mapRecommendationToPrisma(recommendation: SmartPurchaseRecommendation): PrismaSmartPurchaseRecommendationRecord {
  return { id: recommendation.id, supplierId: recommendation.supplierId ?? null, supplierName: recommendation.supplierName, priority: recommendation.priority, action: recommendation.action, cashImpact: recommendation.cashImpact, title: recommendation.title, summary: recommendation.summary, generatedAt: recommendation.generatedAt, idealOrderDate: recommendation.idealOrderDate, expectedReceptionDate: recommendation.expectedReceptionDate, expectedPaymentDate: recommendation.expectedPaymentDate, estimatedTotalCents: recommendation.estimatedTotalCents, safeBudgetCents: recommendation.safeBudgetCents, cashAfterPurchaseCents: recommendation.cashAfterPurchaseCents, reasonsJson: JSON.stringify(recommendation.reasons), auditRequired: recommendation.auditRequired, blockedReason: recommendation.blockedReason ?? null };
}

export function estimatePrismaWritePlan(input: { suppliers: SupplierAccount[]; links: SupplierProductLink[]; orders: SupplierPurchaseOrder[]; receipts: SupplierReceivingReceipt[]; payables: SupplierPayable[]; recommendations: SmartPurchaseRecommendation[]; auditEvents: SupplierAuditEvent[] }) {
  return {
    Supplier: input.suppliers.length,
    SupplierContact: input.suppliers.reduce((sum, supplier) => sum + supplier.contacts.length, 0),
    SupplierSchedule: input.suppliers.filter((supplier) => supplier.visitRule).length,
    SupplierTerms: input.suppliers.length,
    SupplierProduct: input.links.length,
    PurchaseOrder: input.orders.length,
    PurchaseOrderLine: input.orders.reduce((sum, order) => sum + order.lines.length, 0),
    ReceivingReceipt: input.receipts.length,
    ReceivingDifference: input.receipts.reduce((sum, receipt) => sum + receipt.differences.length, 0),
    SupplierPayable: input.payables.length,
    SmartPurchaseRecommendation: input.recommendations.length,
    SupplierAuditEvent: input.auditEvents.length
  };
}
