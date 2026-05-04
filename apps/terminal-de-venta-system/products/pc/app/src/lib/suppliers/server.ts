import { buildSmartPurchaseOutput, simulatePurchase } from "./smart-purchase-engine";
import { buildSupplierLifecycleSnapshot, confirmSupplierReceiving, createSuggestedOrderFromRecommendation, registerSupplierPayment } from "./lifecycle-engine";
import { receivingQueue, supplierAccounts, supplierLifecycleFixtures, supplierOrders, supplierPayables, supplierProductLinks } from "./fixtures";
import { buildSupplierLifecycleReport } from "./lifecycle-report";
import { buildSupplierDataQualityReport } from "./data-quality";
import { buildSupplierExportBundle } from "./export-contracts";
import { loadSupplierInventoryBridge, mergeSupplierProductLinksWithInventory } from "./inventory-bridge";
import type { ConfirmReceivingInput, CreateSuggestedOrderInput, PurchaseSimulationInput, RegisterSupplierPaymentInput, SupplierActor, SupplierDashboardSnapshot } from "./types";

const NOW = "2026-05-02T16:30:00.000Z";
const DEFAULT_ACTOR: SupplierActor = supplierLifecycleFixtures.actor;

export async function getSupplierDashboardSnapshot(): Promise<SupplierDashboardSnapshot> {
  const inventoryBridge = await loadSupplierInventoryBridge({ now: NOW, productLinks: supplierProductLinks });
  const inventoryAwareProductLinks = mergeSupplierProductLinksWithInventory(supplierProductLinks, inventoryBridge);

  const generated = buildSmartPurchaseOutput({
    now: NOW,
    availableCashCents: supplierLifecycleFixtures.cashPolicy.availableCashCents,
    reserveCashCents: supplierLifecycleFixtures.cashPolicy.reserveCashCents,
    suppliers: supplierAccounts,
    productLinks: inventoryAwareProductLinks,
    payables: supplierPayables
  });

  const base = {
    generatedAt: NOW,
    suppliers: supplierAccounts,
    productLinks: inventoryAwareProductLinks,
    signals: generated.signals,
    recommendations: generated.recommendations,
    openOrders: supplierOrders,
    receivingQueue,
    payables: supplierPayables
  };

  const lifecycle = buildSupplierLifecycleSnapshot({
    now: NOW,
    suppliers: base.suppliers,
    recommendations: base.recommendations,
    openOrders: base.openOrders,
    receivingQueue: base.receivingQueue,
    payables: base.payables,
    availableCashCents: supplierLifecycleFixtures.cashPolicy.availableCashCents,
    reserveCashCents: supplierLifecycleFixtures.cashPolicy.reserveCashCents,
    unresolvedSyncSignals: [...supplierLifecycleFixtures.unresolvedSyncSignals]
  });

  return { ...base, lifecycle, inventoryBridge };
}

export async function getSupplierOperationsSnapshot() {
  const snapshot = await getSupplierDashboardSnapshot();
  return {
    generatedAt: snapshot.generatedAt,
    lifecycle: snapshot.lifecycle,
    report: buildSupplierLifecycleReport(snapshot),
    policyNotes: supplierLifecycleFixtures.policyNotes,
    cashPolicy: supplierLifecycleFixtures.cashPolicy
  };
}

export async function getSupplierInventoryBridgeSnapshot() {
  const snapshot = await getSupplierDashboardSnapshot();
  return snapshot.inventoryBridge;
}

export async function getSupplierDataQualityReport() {
  const snapshot = await getSupplierDashboardSnapshot();
  return buildSupplierDataQualityReport(snapshot);
}

export async function getSupplierExportBundle() {
  const snapshot = await getSupplierDashboardSnapshot();
  return buildSupplierExportBundle(snapshot);
}

export async function runSmartPurchaseSimulation(input: Partial<PurchaseSimulationInput>) {
  const snapshot = await getSupplierDashboardSnapshot();
  const recommendationId = requireString(input.recommendationId, "recommendationId");
  const recommendation = snapshot.recommendations.find((item) => item.id === recommendationId);
  if (!recommendation) throw new Error("No encontramos esa recomendacion.");
  return simulatePurchase({
    recommendationId,
    budgetCents: Number.isFinite(input.budgetCents) ? Number(input.budgetCents) : recommendation.safeBudgetCents,
    excludedLineIds: Array.isArray(input.excludedLineIds) ? input.excludedLineIds.map(String) : [],
    quantityOverrides: normalizeQuantityOverrides(input.quantityOverrides)
  }, snapshot.recommendations);
}

export async function createOrderFromSmartPurchase(input: Partial<CreateSuggestedOrderInput>) {
  const snapshot = await getSupplierDashboardSnapshot();
  return createSuggestedOrderFromRecommendation({
    recommendationId: requireString(input.recommendationId, "recommendationId"),
    actor: normalizeActor(input.actor),
    reason: requireString(input.reason, "reason"),
    budgetCents: Number.isFinite(input.budgetCents) ? Number(input.budgetCents) : undefined,
    excludedLineIds: Array.isArray(input.excludedLineIds) ? input.excludedLineIds.map(String) : [],
    quantityOverrides: normalizeQuantityOverrides(input.quantityOverrides)
  }, snapshot);
}

export async function confirmReceivingFromOrder(input: Partial<ConfirmReceivingInput>) {
  const snapshot = await getSupplierDashboardSnapshot();
  return confirmSupplierReceiving({
    orderId: requireString(input.orderId, "orderId"),
    actor: normalizeActor(input.actor),
    reason: requireString(input.reason, "reason"),
    receivedUnitsByLineId: normalizeQuantityOverrides(input.receivedUnitsByLineId),
    receivedAt: typeof input.receivedAt === "string" ? input.receivedAt : undefined
  }, snapshot);
}

export async function registerPayablePayment(input: Partial<RegisterSupplierPaymentInput>) {
  const snapshot = await getSupplierDashboardSnapshot();
  return registerSupplierPayment({
    payableId: requireString(input.payableId, "payableId"),
    actor: normalizeActor(input.actor),
    reason: requireString(input.reason, "reason"),
    amountCents: Number(input.amountCents ?? 0),
    paidAt: typeof input.paidAt === "string" ? input.paidAt : undefined
  }, snapshot);
}

export function formatMoney(cents: number): string {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function labelPriority(priority: string): string {
  return {
    critical: "Crítica",
    high: "Alta",
    safe: "Segura",
    wait: "Esperar",
    blocked: "Revisar antes de comprar",
    configure: "Configurar"
  }[priority] ?? priority;
}

export function labelCashImpact(impact: string): string {
  return {
    safe: "Compra segura",
    careful: "Compra con cuidado",
    tight: "Caja apretada",
    blocked: "Revisar presupuesto"
  }[impact] ?? impact;
}

export function labelGateStatus(status: string): string {
  return { ready: "Listo", warning: "Revisar", blocked: "Requiere datos" }[status] ?? status;
}

export function labelSurface(surface: string): string {
  return { tablet: "Tablet", mobile: "App móvil" }[surface] ?? surface;
}

export function labelOrderStatus(status: string): string { return { draft: "Borrador", suggested: "Sugerido", approved: "Aprobado", sent: "Enviado", partially_received: "Recibido parcialmente", received: "Recibido", cancelled: "Cancelado", closed: "Cerrado" }[status] ?? status; }
export function labelCalendarKind(kind: string): string { return { visit: "Visita", order_cutoff: "Fecha límite de pedido", expected_receiving: "Recepción esperada", payment_due: "Pago próximo", recommendation: "Compra recomendada" }[kind] ?? kind; }
export function labelLifecycleTopic(topic: string): string { return { "purchase_order.created": "Pedido creado", "purchase_order.suggested": "Pedido sugerido", "purchase_order.approved": "Pedido aprobado", "purchase_order.sent": "Pedido enviado", "purchase_order.cancelled": "Pedido cancelado", "purchase_order.converted_from_recommendation": "Recomendación convertida en pedido", "receiving.completed": "Recepción completada", "receiving.completed_with_differences": "Recepción con diferencias", "receiving.reverted": "Recepción revertida", "stock.increased_from_receiving": "Inventario aumentado por recepción", "stock.reverted_from_receiving": "Inventario revertido por recepción", "supplier_payable.created": "Cuenta por pagar creada", "supplier_payable.partial_paid": "Pago parcial registrado", "supplier_payable.paid": "Cuenta pagada", "smart_purchase.recommendation.simulated": "Compra simulada", "smart_purchase.recommendation.converted_to_order": "Compra convertida en pedido", "smart_purchase.recommendation.rejected": "Recomendación descartada" }[topic] ?? topic; }
export function labelEntityType(entityType: string): string { return { supplier: "Proveedor", purchase_order: "Pedido", receiving: "Recepción", payable: "Cuenta por pagar", smart_purchase: "Compra Inteligente", stock_movement: "Movimiento de inventario" }[entityType] ?? entityType; }

function normalizeActor(actor: unknown): SupplierActor {
  if (!actor || typeof actor !== "object") return DEFAULT_ACTOR;
  const value = actor as Partial<SupplierActor>;
  return {
    id: typeof value.id === "string" ? value.id : DEFAULT_ACTOR.id,
    name: typeof value.name === "string" ? value.name : DEFAULT_ACTOR.name,
    role: typeof value.role === "string" ? value.role : DEFAULT_ACTOR.role
  };
}

function requireString(value: unknown, field: string): string {
  if (typeof value !== "string" || value.trim().length === 0) throw new Error(`Falta ${field}.`);
  return value.trim();
}

function normalizeQuantityOverrides(value: unknown): Record<string, number> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  const result: Record<string, number> = {};
  for (const [key, raw] of Object.entries(value as Record<string, unknown>)) {
    const numeric = Number(raw);
    if (Number.isFinite(numeric)) result[key] = numeric;
  }
  return result;
}
