import type {
  CashImpact,
  PaymentCondition,
  PurchaseRecommendationAction,
  PurchaseRecommendationPriority,
  PurchaseOrderStatus,
  ReceivingStatus,
  SupplierCalendarEvent,
  SupplierCategory,
  SupplierStatus,
  SupplierSurfaceSignal,
  PayableStatus
} from "./types";

const moneyFormatter = new Intl.NumberFormat("es-MX", {
  style: "currency",
  currency: "MXN",
  maximumFractionDigits: 0
});

const dateFormatter = new Intl.DateTimeFormat("es-MX", {
  dateStyle: "medium",
  timeStyle: "short"
});

const shortDateFormatter = new Intl.DateTimeFormat("es-MX", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit"
});

export function money(cents: number): string {
  return moneyFormatter.format((Number.isFinite(cents) ? cents : 0) / 100);
}

export function dateTime(value: string): string {
  return dateFormatter.format(new Date(value));
}

export function shortDateTime(value: string): string {
  return shortDateFormatter.format(new Date(value));
}

export function friendlyFolio(folio: string): string {
  return folio.replace(/^PO-/i, "Pedido ");
}

export function supplierStatusLabel(status: SupplierStatus): string {
  const labels: Record<SupplierStatus, string> = {
    active: "Activo",
    paused: "En pausa",
    blocked: "Requiere revisión"
  };
  return labels[status] ?? "Revisar";
}

export function supplierStatusTone(status: SupplierStatus): "ok" | "warn" | "review" {
  const tones: Record<SupplierStatus, "ok" | "warn" | "review"> = {
    active: "ok",
    paused: "warn",
    blocked: "review"
  };
  return tones[status] ?? "review";
}

export function supplierCategoryLabel(category: SupplierCategory | string): string {
  const labels: Record<string, string> = {
    bebidas: "Bebidas",
    snacks: "Botanas",
    lacteos: "Lácteos",
    abarrotes: "Abarrotes",
    limpieza: "Limpieza",
    farmacia: "Farmacia",
    panaderia: "Panadería",
    otros: "Otros"
  };
  return labels[category] ?? capitalize(category);
}

export function paymentConditionLabel(condition: PaymentCondition | string): string {
  const labels: Record<string, string> = {
    cash: "Contado",
    credit_7: "Crédito 7 días",
    credit_15: "Crédito 15 días",
    credit_30: "Crédito 30 días",
    consignment: "Consignación"
  };
  return labels[condition] ?? "Condición por revisar";
}

export function priorityLabel(priority: PurchaseRecommendationPriority): string {
  const labels: Record<PurchaseRecommendationPriority, string> = {
    critical: "Urgente",
    high: "Alta prioridad",
    safe: "Compra segura",
    wait: "Puede esperar",
    blocked: "Revisar antes",
    configure: "Faltan datos"
  };
  return labels[priority] ?? "Revisar";
}

export function priorityTone(priority: PurchaseRecommendationPriority): "urgent" | "high" | "safe" | "wait" | "review" | "setup" {
  const tones: Record<PurchaseRecommendationPriority, "urgent" | "high" | "safe" | "wait" | "review" | "setup"> = {
    critical: "urgent",
    high: "high",
    safe: "safe",
    wait: "wait",
    blocked: "review",
    configure: "setup"
  };
  return tones[priority] ?? "review";
}

export function actionLabel(action: PurchaseRecommendationAction): string {
  const labels: Record<PurchaseRecommendationAction, string> = {
    create_order: "Crear pedido sugerido",
    simulate: "Simular compra",
    wait: "Esperar",
    configure_supplier: "Completar proveedor",
    review_cost: "Revisar costo",
    block_purchase: "Revisar antes de comprar"
  };
  return labels[action] ?? "Revisar acción";
}

export function cashImpactLabel(impact: CashImpact): string {
  const labels: Record<CashImpact, string> = {
    safe: "Caja cómoda",
    careful: "Con cuidado",
    tight: "Caja apretada",
    blocked: "Revisar presupuesto"
  };
  return labels[impact] ?? "Revisar caja";
}

export function cashImpactTone(impact: CashImpact): "safe" | "careful" | "tight" | "review" {
  const tones: Record<CashImpact, "safe" | "careful" | "tight" | "review"> = {
    safe: "safe",
    careful: "careful",
    tight: "tight",
    blocked: "review"
  };
  return tones[impact] ?? "review";
}

export function orderStatusLabel(status: PurchaseOrderStatus): string {
  const labels: Record<PurchaseOrderStatus, string> = {
    draft: "Borrador",
    suggested: "Sugerido",
    approved: "Aprobado",
    sent: "Enviado",
    partially_received: "Recibido parcial",
    received: "Recibido",
    cancelled: "Cancelado",
    closed: "Cerrado"
  };
  return labels[status] ?? "Revisar pedido";
}

export function receivingStatusLabel(status: ReceivingStatus): string {
  const labels: Record<ReceivingStatus, string> = {
    pending: "Pendiente",
    capturing: "En captura",
    complete: "Completa",
    with_differences: "Con diferencias",
    cancelled: "Cancelada",
    reverted: "Revertida",
    needs_review: "Requiere revisión"
  };
  return labels[status] ?? "Revisar recepción";
}

export function payableStatusLabel(status: PayableStatus): string {
  const labels: Record<PayableStatus, string> = {
    scheduled: "Programado",
    due_soon: "Próximo",
    overdue: "Vencido",
    paid: "Pagado",
    disputed: "En revisión"
  };
  return labels[status] ?? "Revisar pago";
}

export function calendarKindLabel(kind: SupplierCalendarEvent["kind"]): string {
  const labels: Record<SupplierCalendarEvent["kind"], string> = {
    visit: "Visita de proveedor",
    order_cutoff: "Fecha límite para pedir",
    expected_receiving: "Recepción esperada",
    payment_due: "Pago próximo",
    recommendation: "Compra recomendada"
  };
  return labels[kind] ?? "Evento de proveedor";
}

export function calendarTone(severity: SupplierCalendarEvent["severity"]): "urgent" | "high" | "medium" | "low" {
  if (severity === "critical") return "urgent";
  return severity;
}

export function surfaceLabel(surface: SupplierSurfaceSignal["surface"]): string {
  return surface === "tablet" ? "Tablet" : "App móvil";
}

export function readinessLabel(status: "ready" | "warning" | "blocked"): string {
  const labels: Record<"ready" | "warning" | "blocked", string> = {
    ready: "Listo",
    warning: "Revisar",
    blocked: "Requiere datos"
  };
  return labels[status] ?? "Revisar";
}

export function readinessTone(status: "ready" | "warning" | "blocked"): "ok" | "warn" | "review" {
  const tones: Record<"ready" | "warning" | "blocked", "ok" | "warn" | "review"> = {
    ready: "ok",
    warning: "warn",
    blocked: "review"
  };
  return tones[status] ?? "review";
}

export function topicLabel(topic: string): string {
  const labels: Record<string, string> = {
    "purchase_order.created": "Pedido creado",
    "purchase_order.suggested": "Pedido sugerido",
    "purchase_order.approved": "Pedido aprobado",
    "purchase_order.sent": "Pedido enviado",
    "purchase_order.cancelled": "Pedido cancelado",
    "purchase_order.converted_from_recommendation": "Recomendación convertida en pedido",
    "receiving.completed": "Recepción completada",
    "receiving.completed_with_differences": "Recepción con diferencias",
    "receiving.reverted": "Recepción revertida",
    "stock.increased_from_receiving": "Inventario aumentado por recepción",
    "stock.reverted_from_receiving": "Inventario revertido por recepción",
    "supplier_payable.created": "Cuenta por pagar creada",
    "supplier_payable.partial_paid": "Pago parcial registrado",
    "supplier_payable.paid": "Cuenta pagada",
    "smart_purchase.recommendation.simulated": "Compra simulada",
    "smart_purchase.recommendation.converted_to_order": "Compra convertida en pedido",
    "smart_purchase.recommendation.rejected": "Recomendación descartada"
  };
  return labels[topic] ?? "Evento operativo";
}

export function entityLabel(entityType: string): string {
  const labels: Record<string, string> = {
    supplier: "Proveedor",
    purchase_order: "Pedido",
    receiving: "Recepción",
    payable: "Cuenta por pagar",
    smart_purchase: "Compra Inteligente",
    stock_movement: "Movimiento de inventario"
  };
  return labels[entityType] ?? "Registro";
}

export function cleanVisibleText(value: string): string {
  return value
    .replace(/\bPO-/g, "Pedido ")
    .replace(/\border_cutoff\b/g, "fecha límite")
    .replace(/\bexpected_receiving\b/g, "recepción esperada")
    .replace(/\bpayment_due\b/g, "pago próximo")
    .replace(/\bblocked\b/gi, "requiere revisión")
    .replace(/\bsync\b/gi, "sincronización")
    .replace(/\bbackoffice\b/gi, "panel administrativo");
}

function capitalize(value: string): string {
  if (!value) return "Revisar";
  return `${value.slice(0, 1).toUpperCase()}${value.slice(1)}`;
}
