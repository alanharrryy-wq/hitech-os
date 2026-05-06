export type TabletPaymentEventTopic =
  | "tablet.payment.panel.opened"
  | "tablet.payment.method.selected"
  | "tablet.payment.confirm.requested"
  | "tablet.payment.confirm.blocked"
  | "tablet.payment.confirm.completed"
  | "tablet.payment.confirm.failed"
  | "tablet.ticket.success.visible"
  | "tablet.sales.today.opened"
  | "tablet.ticket.detail.opened"
  | "tablet.return.contextual.opened"
  | "tablet.return.contextual.completed";

export type TabletPaymentEvent = {
  eventId: string;
  topic: TabletPaymentEventTopic;
  occurredAt: string;
  businessId: string | null;
  terminalId: string | null;
  operatorId: string | null;
  saleId: string | null;
  clientRequestId: string | null;
  payload: Record<string, string | number | boolean | null>;
};

export function createTabletPaymentEvent(input: Omit<TabletPaymentEvent, "eventId" | "occurredAt"> & { eventId?: string; occurredAt?: string }): TabletPaymentEvent {
  return {
    eventId: input.eventId ?? `evt_tablet_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`,
    occurredAt: input.occurredAt ?? new Date().toISOString(),
    topic: input.topic,
    businessId: input.businessId,
    terminalId: input.terminalId,
    operatorId: input.operatorId,
    saleId: input.saleId,
    clientRequestId: input.clientRequestId,
    payload: input.payload,
  };
}

export function eventVisibleSummary(event: TabletPaymentEvent) {
  const byTopic: Record<TabletPaymentEventTopic, string> = {
    "tablet.payment.panel.opened": "Se abrió Cobro dentro de Vender.",
    "tablet.payment.method.selected": "Se eligió método de pago.",
    "tablet.payment.confirm.requested": "Se solicitó confirmar venta.",
    "tablet.payment.confirm.blocked": "La venta fue bloqueada por regla operativa.",
    "tablet.payment.confirm.completed": "La venta quedó cerrada.",
    "tablet.payment.confirm.failed": "La venta no quedó confirmada.",
    "tablet.ticket.success.visible": "Se mostró ticket cerrado.",
    "tablet.sales.today.opened": "Se abrió Ventas de hoy.",
    "tablet.ticket.detail.opened": "Se abrió detalle de ticket.",
    "tablet.return.contextual.opened": "Se inició devolución desde ticket.",
    "tablet.return.contextual.completed": "Se registró devolución contextual.",
  };
  return byTopic[event.topic];
}

export function assertEventHasOperationalIdentity(event: TabletPaymentEvent) {
  const missing: string[] = [];
  if (!event.eventId) missing.push("eventId");
  if (!event.topic) missing.push("topic");
  if (!event.occurredAt) missing.push("occurredAt");
  if (event.topic.includes("payment") && !event.clientRequestId) missing.push("clientRequestId");
  return { ok: missing.length === 0, missing };
}
