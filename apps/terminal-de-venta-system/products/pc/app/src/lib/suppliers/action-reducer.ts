import type {
  SupplierAuditEvent,
  SupplierLifecycleSnapshot,
  SupplierPayable,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt
} from "./types";

export type SupplierLifecycleAction =
  | { type: "ORDER_CREATED"; order: SupplierPurchaseOrder; auditEvents: SupplierAuditEvent[] }
  | { type: "ORDER_STATUS_CHANGED"; orderId: string; status: SupplierPurchaseOrder["status"]; auditEvents: SupplierAuditEvent[] }
  | { type: "RECEIVING_CONFIRMED"; receipt: SupplierReceivingReceipt; payable?: SupplierPayable; auditEvents: SupplierAuditEvent[] }
  | { type: "PAYABLE_UPDATED"; payable: SupplierPayable; auditEvents: SupplierAuditEvent[] }
  | { type: "AUDIT_APPENDED"; auditEvents: SupplierAuditEvent[] }
  | { type: "SIGNAL_ACKNOWLEDGED"; signalId: string; auditEvents: SupplierAuditEvent[] };

export interface SupplierLifecycleState {
  orders: SupplierPurchaseOrder[];
  receipts: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  auditEvents: SupplierAuditEvent[];
  acknowledgedSignalIds: string[];
}

export interface SupplierLifecycleReduceResult {
  state: SupplierLifecycleState;
  changed: boolean;
  message: string;
}

export function createLifecycleState(snapshot: Pick<SupplierLifecycleSnapshot, "auditEvents"> & { orders?: SupplierPurchaseOrder[]; receipts?: SupplierReceivingReceipt[]; payables?: SupplierPayable[] }): SupplierLifecycleState {
  return { orders: snapshot.orders ?? [], receipts: snapshot.receipts ?? [], payables: snapshot.payables ?? [], auditEvents: snapshot.auditEvents, acknowledgedSignalIds: [] };
}

export function reduceSupplierLifecycleAction(state: SupplierLifecycleState, action: SupplierLifecycleAction): SupplierLifecycleReduceResult {
  switch (action.type) {
    case "ORDER_CREATED":
      return { state: { ...state, orders: upsertById(state.orders, action.order), auditEvents: prependAudit(state.auditEvents, action.auditEvents) }, changed: true, message: `Pedido ${action.order.folio} agregado al ciclo operativo.` };
    case "ORDER_STATUS_CHANGED": {
      let changed = false;
      const orders = state.orders.map((order) => {
        if (order.id !== action.orderId) return order;
        changed = order.status !== action.status;
        return { ...order, status: action.status };
      });
      return { state: { ...state, orders, auditEvents: prependAudit(state.auditEvents, action.auditEvents) }, changed, message: changed ? "Estado de pedido actualizado." : "No hubo cambio de estado." };
    }
    case "RECEIVING_CONFIRMED":
      return { state: { ...state, receipts: upsertById(state.receipts, action.receipt), payables: action.payable ? upsertById(state.payables, action.payable) : state.payables, auditEvents: prependAudit(state.auditEvents, action.auditEvents) }, changed: true, message: action.receipt.status === "with_differences" ? "Recepcion con diferencias registrada." : "Recepcion completa registrada." };
    case "PAYABLE_UPDATED":
      return { state: { ...state, payables: upsertById(state.payables, action.payable), auditEvents: prependAudit(state.auditEvents, action.auditEvents) }, changed: true, message: action.payable.status === "paid" ? "Cuenta por pagar cerrada." : "Cuenta por pagar actualizada." };
    case "AUDIT_APPENDED":
      return { state: { ...state, auditEvents: prependAudit(state.auditEvents, action.auditEvents) }, changed: action.auditEvents.length > 0, message: `${action.auditEvents.length} eventos agregados.` };
    case "SIGNAL_ACKNOWLEDGED":
      return { state: { ...state, acknowledgedSignalIds: state.acknowledgedSignalIds.includes(action.signalId) ? state.acknowledgedSignalIds : [action.signalId, ...state.acknowledgedSignalIds], auditEvents: prependAudit(state.auditEvents, action.auditEvents) }, changed: true, message: "Señal reconocida sin cerrar la operacion pesada." };
  }
}

export function reduceManySupplierLifecycleActions(state: SupplierLifecycleState, actions: SupplierLifecycleAction[]): SupplierLifecycleReduceResult {
  let current = state;
  let changed = false;
  const messages: string[] = [];
  for (const action of actions) {
    const result = reduceSupplierLifecycleAction(current, action);
    current = result.state;
    changed = changed || result.changed;
    messages.push(result.message);
  }
  return { state: current, changed, message: messages.join(" ") };
}

export function summarizeLifecycleState(state: SupplierLifecycleState) {
  return {
    orders: state.orders.length,
    receipts: state.receipts.length,
    payables: state.payables.length,
    auditEvents: state.auditEvents.length,
    acknowledgedSignals: state.acknowledgedSignalIds.length,
    openOrders: state.orders.filter((order) => !["cancelled", "closed", "received"].includes(order.status)).length,
    receiptsWithDifferences: state.receipts.filter((receipt) => receipt.status === "with_differences").length,
    payablesAtRisk: state.payables.filter((payable) => payable.status === "overdue" || payable.status === "due_soon").length
  };
}

function upsertById<T extends { id: string }>(items: T[], item: T): T[] {
  const exists = items.some((existing) => existing.id === item.id);
  if (!exists) return [item, ...items];
  return items.map((existing) => existing.id === item.id ? item : existing);
}

function prependAudit(existing: SupplierAuditEvent[], incoming: SupplierAuditEvent[]): SupplierAuditEvent[] {
  if (!incoming.length) return existing;
  const seen = new Set<string>();
  const merged: SupplierAuditEvent[] = [];
  for (const event of [...incoming, ...existing]) {
    if (seen.has(event.id)) continue;
    seen.add(event.id);
    merged.push(event);
  }
  return merged.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}

export function buildActionFromOrder(order: SupplierPurchaseOrder, auditEvents: SupplierAuditEvent[]): SupplierLifecycleAction {
  return { type: "ORDER_CREATED", order, auditEvents };
}

export function buildActionFromReceiving(receipt: SupplierReceivingReceipt, payable: SupplierPayable | undefined, auditEvents: SupplierAuditEvent[]): SupplierLifecycleAction {
  return { type: "RECEIVING_CONFIRMED", receipt, payable, auditEvents };
}

export function buildActionFromPayment(payable: SupplierPayable, auditEvents: SupplierAuditEvent[]): SupplierLifecycleAction {
  return { type: "PAYABLE_UPDATED", payable, auditEvents };
}
