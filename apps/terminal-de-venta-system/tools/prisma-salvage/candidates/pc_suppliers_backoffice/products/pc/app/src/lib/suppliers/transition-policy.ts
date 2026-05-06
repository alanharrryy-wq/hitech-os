import type { PayableStatus, PurchaseOrderStatus, ReceivingStatus, SupplierStatus } from "./types";

export interface TransitionRule<TState extends string> {
  from: TState;
  to: TState;
  label: string;
  allowedRoles: string[];
  requiresReason: boolean;
  auditTopic: string;
  description: string;
}

export interface TransitionCheckResult {
  ok: boolean;
  code: string;
  message: string;
  requiresReason: boolean;
}

export const supplierStatusTransitions: TransitionRule<SupplierStatus>[] = [
  rule("active", "paused", "Pausar proveedor", ["Administrador", "Dueño"], true, "supplier.paused", "Pausar proveedor lo saca de recomendaciones activas."),
  rule("paused", "active", "Reactivar proveedor", ["Administrador", "Dueño"], true, "supplier.reactivated", "Reactivar proveedor permite pedidos y recomendaciones."),
  rule("active", "blocked", "Bloquear proveedor", ["Dueño"], true, "supplier.blocked", "Bloquear proveedor impide pedidos nuevos."),
  rule("paused", "blocked", "Bloquear proveedor pausado", ["Dueño"], true, "supplier.blocked", "Bloqueo formal con motivo."),
  rule("blocked", "active", "Reactivar proveedor bloqueado", ["Dueño"], true, "supplier.reactivated", "Reactivar requiere revision de motivo previo.")
];

export const purchaseOrderTransitions: TransitionRule<PurchaseOrderStatus>[] = [
  rule("draft", "suggested", "Guardar como sugerido", ["Encargado", "Administrador", "Dueño"], true, "purchase_order.suggested", "Pedido nacido desde recomendacion o calendario."),
  rule("draft", "approved", "Aprobar borrador", ["Administrador", "Dueño"], false, "purchase_order.approved", "Pedido manual aprobado."),
  rule("suggested", "approved", "Aprobar sugerido", ["Administrador", "Dueño"], false, "purchase_order.approved", "Revisa cantidades antes de aprobar."),
  rule("approved", "sent", "Marcar enviado", ["Encargado", "Administrador", "Dueño"], false, "purchase_order.sent", "El pedido queda listo para seguimiento de recepcion."),
  rule("sent", "partially_received", "Recibir parcial", ["Encargado", "Administrador", "Dueño"], true, "receiving.completed_with_differences", "Recepcion incompleta requiere motivo."),
  rule("sent", "received", "Recibir completo", ["Encargado", "Administrador", "Dueño"], false, "receiving.completed", "Recepcion completa genera movimientos."),
  rule("partially_received", "received", "Completar recepcion", ["Encargado", "Administrador", "Dueño"], false, "receiving.completed", "Completar faltantes."),
  rule("received", "closed", "Cerrar pedido", ["Administrador", "Dueño"], false, "purchase_order.closed", "Pedido cerrado tras recepcion y cuenta por pagar."),
  rule("draft", "cancelled", "Cancelar borrador", ["Encargado", "Administrador", "Dueño"], true, "purchase_order.cancelled", "Cancelacion con motivo."),
  rule("suggested", "cancelled", "Cancelar sugerido", ["Administrador", "Dueño"], true, "purchase_order.cancelled", "Cancelar pedido sugerido con motivo."),
  rule("approved", "cancelled", "Cancelar aprobado", ["Administrador", "Dueño"], true, "purchase_order.cancelled", "Cancelar pedido aprobado debe dejar rastro."),
  rule("sent", "cancelled", "Cancelar enviado", ["Dueño"], true, "purchase_order.cancelled", "Cancelar pedido enviado es sensible.")
];

export const receivingTransitions: TransitionRule<ReceivingStatus>[] = [
  rule("pending", "capturing", "Iniciar captura", ["Encargado", "Administrador", "Dueño"], false, "receiving.created", "Preparar recepcion."),
  rule("capturing", "complete", "Confirmar completa", ["Encargado", "Administrador", "Dueño"], false, "receiving.completed", "Actualizar inventario."),
  rule("capturing", "with_differences", "Confirmar con diferencias", ["Encargado", "Administrador", "Dueño"], true, "receiving.completed_with_differences", "Diferencias requieren motivo."),
  rule("with_differences", "needs_review", "Mandar a revision", ["Encargado", "Administrador", "Dueño"], true, "receiving.completed_with_differences", "No cerrar hasta resolver diferencias."),
  rule("complete", "reverted", "Revertir recepcion", ["Dueño"], true, "receiving.reverted", "Reversion crea movimiento inverso."),
  rule("with_differences", "reverted", "Revertir con diferencias", ["Dueño"], true, "receiving.reverted", "Reversion sensible."),
  rule("pending", "cancelled", "Cancelar pendiente", ["Administrador", "Dueño"], true, "receiving.cancelled", "Cancelar recepcion pendiente."),
  rule("capturing", "cancelled", "Cancelar captura", ["Administrador", "Dueño"], true, "receiving.cancelled", "Cancelar captura antes de afectar inventario.")
];

export const payableTransitions: TransitionRule<PayableStatus>[] = [
  rule("scheduled", "due_soon", "Marcar proximo", ["Administrador", "Dueño"], false, "supplier_payable.scheduled", "Pago entrara a presupuesto seguro."),
  rule("due_soon", "paid", "Pagar", ["Administrador", "Dueño"], true, "supplier_payable.paid", "Pago completo."),
  rule("overdue", "paid", "Pagar vencido", ["Administrador", "Dueño"], true, "supplier_payable.paid", "Cerrar deuda vencida."),
  rule("due_soon", "disputed", "Disputar", ["Administrador", "Dueño"], true, "supplier_payable.cancelled", "Pago en disputa requiere motivo."),
  rule("overdue", "disputed", "Disputar vencido", ["Dueño"], true, "supplier_payable.cancelled", "Disputa sensible."),
  rule("scheduled", "paid", "Pago anticipado", ["Administrador", "Dueño"], true, "supplier_payable.paid", "Pago antes de vencimiento.")
];

export function canTransition<TState extends string>(rules: TransitionRule<TState>[], from: TState, to: TState, role: string, reason?: string): TransitionCheckResult {
  const transition = rules.find((item) => item.from === from && item.to === to);
  if (!transition) return { ok: false, code: "TRANSITION_NOT_ALLOWED", message: `No se permite cambiar de ${from} a ${to}.`, requiresReason: false };
  if (!transition.allowedRoles.includes(role)) return { ok: false, code: "ROLE_NOT_ALLOWED", message: `${role} no puede ejecutar: ${transition.label}.`, requiresReason: transition.requiresReason };
  if (transition.requiresReason && (!reason || reason.trim().length < 8)) return { ok: false, code: "REASON_REQUIRED", message: "Esta transicion requiere motivo claro.", requiresReason: true };
  return { ok: true, code: "TRANSITION_ALLOWED", message: transition.description, requiresReason: transition.requiresReason };
}

export function explainAllowedOrderNextStates(status: PurchaseOrderStatus, role: string): string[] {
  return purchaseOrderTransitions.filter((item) => item.from === status && item.allowedRoles.includes(role)).map((item) => `${item.to}: ${item.label}`);
}

export function explainAllowedReceivingNextStates(status: ReceivingStatus, role: string): string[] {
  return receivingTransitions.filter((item) => item.from === status && item.allowedRoles.includes(role)).map((item) => `${item.to}: ${item.label}`);
}

export function explainAllowedPayableNextStates(status: PayableStatus, role: string): string[] {
  return payableTransitions.filter((item) => item.from === status && item.allowedRoles.includes(role)).map((item) => `${item.to}: ${item.label}`);
}

function rule<TState extends string>(from: TState, to: TState, label: string, allowedRoles: string[], requiresReason: boolean, auditTopic: string, description: string): TransitionRule<TState> {
  return { from, to, label, allowedRoles, requiresReason, auditTopic, description };
}
