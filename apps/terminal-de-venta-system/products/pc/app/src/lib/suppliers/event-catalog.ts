import type { SupplierLifecycleEventTopic } from "./types";

export interface SupplierEventDefinition {
  topic: SupplierLifecycleEventTopic;
  domain: "supplier" | "purchase_order" | "receiving" | "payable" | "smart_purchase" | "stock";
  severity: "info" | "warning" | "critical";
  requiresReason: boolean;
  requiresPermission: string;
  visibleLabel: string;
  description: string;
  tabletAllowed: boolean;
  mobileAllowed: boolean;
}

export const supplierLifecycleEventCatalog: SupplierEventDefinition[] = [
  event("purchase_order.created", "purchase_order", "info", true, "purchase_order.create", "Pedido creado", "Se creo un pedido manual o desde calendario.", false, true),
  event("purchase_order.suggested", "purchase_order", "info", true, "smart_purchase.convert_to_order", "Pedido sugerido", "Compra Inteligente genero un pedido revisable.", false, true),
  event("purchase_order.approved", "purchase_order", "warning", false, "purchase_order.approve", "Pedido aprobado", "Un usuario autorizado aprobo el pedido.", false, true),
  event("purchase_order.sent", "purchase_order", "info", false, "purchase_order.send", "Pedido enviado", "El pedido fue marcado como enviado al proveedor.", false, true),
  event("purchase_order.cancelled", "purchase_order", "warning", true, "purchase_order.cancel", "Pedido cancelado", "El pedido fue cancelado con motivo.", false, true),
  event("purchase_order.converted_from_recommendation", "purchase_order", "warning", true, "smart_purchase.convert_to_order", "Convertido desde recomendacion", "La recomendacion fue convertida a pedido sugerido.", false, true),
  event("receiving.completed", "receiving", "warning", false, "receiving.complete", "Recepcion completa", "Se confirmo recepcion y se preparan movimientos de inventario.", false, true),
  event("receiving.completed_with_differences", "receiving", "critical", true, "receiving.complete", "Recepcion con diferencias", "La recepcion no coincide con lo pedido y requiere revision.", true, true),
  event("receiving.reverted", "receiving", "critical", true, "receiving.revert", "Recepcion revertida", "Se revierte una recepcion con movimiento inverso.", false, true),
  event("stock.increased_from_receiving", "stock", "warning", false, "receiving.complete", "Entrada por recepcion", "El inventario aumenta por mercancia recibida.", false, true),
  event("stock.reverted_from_receiving", "stock", "critical", true, "receiving.revert", "Inventario revertido", "Se revierte inventario afectado por recepcion.", false, true),
  event("supplier_payable.created", "payable", "warning", false, "supplier_payable.schedule", "Cuenta por pagar creada", "Se genero obligacion de pago a proveedor.", false, true),
  event("supplier_payable.partial_paid", "payable", "warning", true, "supplier_payable.pay", "Pago parcial", "Se registro abono y queda saldo pendiente.", false, true),
  event("supplier_payable.paid", "payable", "info", true, "supplier_payable.pay", "Pago cerrado", "La cuenta por pagar quedo cubierta.", false, true),
  event("smart_purchase.recommendation.simulated", "smart_purchase", "info", false, "smart_purchase.simulate", "Simulacion", "El usuario ajusto presupuesto o cantidades.", false, true),
  event("smart_purchase.recommendation.converted_to_order", "smart_purchase", "warning", true, "smart_purchase.convert_to_order", "Recomendacion a pedido", "La recomendacion genero pedido sugerido.", false, true),
  event("smart_purchase.recommendation.rejected", "smart_purchase", "warning", true, "smart_purchase.reject", "Recomendacion rechazada", "Usuario rechazo recomendacion con motivo.", false, true)
];

export function getSupplierEventDefinition(topic: SupplierLifecycleEventTopic): SupplierEventDefinition | undefined {
  return supplierLifecycleEventCatalog.find((definition) => definition.topic === topic);
}

export function listEventsAllowedForSurface(surface: "tablet" | "mobile"): SupplierEventDefinition[] {
  return supplierLifecycleEventCatalog.filter((definition) => surface === "tablet" ? definition.tabletAllowed : definition.mobileAllowed);
}

export function describeEventForBusiness(topic: SupplierLifecycleEventTopic): string {
  const definition = getSupplierEventDefinition(topic);
  return definition ? `${definition.visibleLabel}: ${definition.description}` : topic;
}

function event(topic: SupplierLifecycleEventTopic, domain: SupplierEventDefinition["domain"], severity: SupplierEventDefinition["severity"], requiresReason: boolean, requiresPermission: string, visibleLabel: string, description: string, tabletAllowed: boolean, mobileAllowed: boolean): SupplierEventDefinition {
  return { topic, domain, severity, requiresReason, requiresPermission, visibleLabel, description, tabletAllowed, mobileAllowed };
}
