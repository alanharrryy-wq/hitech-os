import { simulatePurchase } from "./smart-purchase-engine";
import type {
  CashImpact,
  ConfirmReceivingInput,
  CreateSuggestedOrderInput,
  IsoDate,
  RegisterSupplierPaymentInput,
  SmartPurchaseLine,
  SmartPurchaseRecommendation,
  SupplierAccount,
  SupplierActionResult,
  SupplierAuditEvent,
  SupplierCalendarEvent,
  SupplierDashboardSnapshot,
  SupplierInventoryMovementPreview,
  SupplierLifecycleEventTopic,
  SupplierLifecycleSnapshot,
  SupplierOrderWorkflowCard,
  SupplierOrderWorkflowStep,
  SupplierPayable,
  SupplierPayablePlan,
  SupplierPurchaseOrder,
  SupplierPurchaseOrderLine,
  SupplierReadinessGate,
  SupplierReceivingDifference,
  SupplierReceivingReceipt,
  SupplierSurfaceSignal
} from "./types";

const DAY_MS = 24 * 60 * 60 * 1000;
const DEFAULT_NOW = "2026-05-02T16:30:00.000Z";

export interface BuildSupplierLifecycleInput {
  now: IsoDate;
  suppliers: SupplierAccount[];
  recommendations: SmartPurchaseRecommendation[];
  openOrders: SupplierPurchaseOrder[];
  receivingQueue: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  availableCashCents: number;
  reserveCashCents: number;
  unresolvedSyncSignals?: Array<{ id: string; source: string; message: string; severity: "critical" | "high" | "medium" | "low" }>;
}

export function buildSupplierLifecycleSnapshot(input: BuildSupplierLifecycleInput): SupplierLifecycleSnapshot {
  const suppliersById = new Map(input.suppliers.map((supplier) => [supplier.id, supplier]));
  const orderWorkflow = input.openOrders.map((order) => buildOrderWorkflow(order));
  const movementPreview = buildMovementPreview(input.openOrders, input.receivingQueue);
  const payablePlan = buildPayablePlan(input.payables, input.availableCashCents, input.reserveCashCents);
  const calendar = buildCalendarEvents(input.now, input.suppliers, input.recommendations, input.openOrders, input.receivingQueue, input.payables);
  const auditEvents = buildSyntheticAuditTrail(input.now, input.recommendations, input.openOrders, input.receivingQueue, input.payables, movementPreview);
  const readiness = buildReadinessGates(input, orderWorkflow, movementPreview, payablePlan, auditEvents);
  const surfaceSignals = buildSurfaceSignals(input.recommendations, input.receivingQueue, input.payables, input.unresolvedSyncSignals ?? []);

  return {
    generatedAt: input.now,
    readiness,
    calendar,
    orderWorkflow,
    movementPreview,
    payablePlan,
    auditEvents,
    surfaceSignals,
    counters: {
      readyGates: readiness.filter((gate) => gate.status === "ready").length,
      warningGates: readiness.filter((gate) => gate.status === "warning").length,
      blockedGates: readiness.filter((gate) => gate.status === "blocked").length,
      calendarEvents: calendar.length,
      ordersNeedingAction: orderWorkflow.filter((card) => card.steps.some((step) => step.status === "current" || step.status === "blocked")).length,
      receivingsWithDifferences: input.receivingQueue.filter((receipt) => receipt.status === "with_differences" || receipt.differences.length > 0).length,
      auditEvents: auditEvents.length
    }
  };
}

export function createSuggestedOrderFromRecommendation(
  input: CreateSuggestedOrderInput,
  snapshot: SupplierDashboardSnapshot
): SupplierActionResult<{ order: SupplierPurchaseOrder; simulationTotalCents: number }> {
  const recommendation = snapshot.recommendations.find((item) => item.id === input.recommendationId);
  if (!recommendation) {
    return blocked("RECOMMENDATION_NOT_FOUND", "No encontramos esa recomendacion. Actualiza Compra Inteligente antes de crear pedido.");
  }
  if (!input.reason || input.reason.trim().length < 8) {
    return blocked("REASON_REQUIRED", "Captura un motivo claro para convertir la recomendacion en pedido.");
  }
  if (!canActorCreateOrder(input.actor.role)) {
    return blocked("PERMISSION_DENIED", "Este rol no puede crear pedidos sugeridos desde Compra Inteligente.");
  }
  if (recommendation.priority === "blocked" || recommendation.cashImpact === "blocked") {
    return blocked("PURCHASE_BLOCKED", recommendation.blockedReason ?? "La compra esta bloqueada por caja, proveedor o datos faltantes.");
  }
  if (!recommendation.lines.length) {
    return blocked("EMPTY_RECOMMENDATION", "La recomendacion no tiene productos comprables.");
  }

  const simulation = simulatePurchase(
    {
      recommendationId: recommendation.id,
      budgetCents: input.budgetCents ?? recommendation.safeBudgetCents,
      excludedLineIds: input.excludedLineIds ?? [],
      quantityOverrides: input.quantityOverrides ?? {}
    },
    snapshot.recommendations
  );

  if (!simulation.canCreateOrder) {
    return {
      ok: false,
      code: "SIMULATION_BLOCKED",
      message: "La simulacion no permite crear pedido. Ajusta presupuesto, cantidades o productos incluidos.",
      warnings: simulation.warnings,
      auditEvents: [auditEvent({
        topic: "smart_purchase.recommendation.simulated",
        entityType: "smart_purchase",
        entityId: recommendation.id,
        supplierId: recommendation.supplierId,
        supplierName: recommendation.supplierName,
        actor: input.actor,
        reason: input.reason,
        source: "pc.smart_purchase",
        visibleSummary: "Simulacion bloqueada antes de crear pedido sugerido.",
        after: { cashImpact: simulation.cashImpact, totalCents: simulation.simulatedTotalCents }
      })]
    };
  }

  const order: SupplierPurchaseOrder = {
    id: `po_suggested_${recommendation.id}`,
    folio: `CI-${recommendation.id.toUpperCase()}`,
    supplierId: recommendation.supplierId ?? "supplier_missing",
    supplierName: recommendation.supplierName,
    source: "smart_purchase",
    status: recommendation.auditRequired ? "suggested" : "approved",
    createdAt: DEFAULT_NOW,
    expectedReceptionDate: recommendation.expectedReceptionDate,
    expectedPaymentDate: recommendation.expectedPaymentDate,
    totalCents: simulation.simulatedTotalCents,
    lines: simulation.includedLines.map((line) => toOrderLine(line)),
    auditTrail: [
      `Origen: Compra Inteligente ${recommendation.id}`,
      `Motivo: ${input.reason}`,
      `Actor: ${input.actor.name}`,
      `Cobertura: ${simulation.coverageSummary}`,
      `Impacto de caja: ${simulation.cashImpact}`
    ]
  };

  const auditEvents = [
    auditEvent({
      topic: "smart_purchase.recommendation.converted_to_order",
      entityType: "smart_purchase",
      entityId: recommendation.id,
      supplierId: recommendation.supplierId,
      supplierName: recommendation.supplierName,
      actor: input.actor,
      reason: input.reason,
      source: "pc.smart_purchase",
      visibleSummary: `Recomendacion convertida a pedido ${order.folio}.`,
      after: { orderId: order.id, folio: order.folio, totalCents: order.totalCents }
    }),
    auditEvent({
      topic: "purchase_order.suggested",
      entityType: "purchase_order",
      entityId: order.id,
      supplierId: order.supplierId,
      supplierName: order.supplierName,
      actor: input.actor,
      reason: input.reason,
      source: "pc.suppliers",
      visibleSummary: `Pedido sugerido creado para ${order.supplierName}.`,
      after: { status: order.status, totalCents: order.totalCents, lines: order.lines.length }
    })
  ];

  return {
    ok: true,
    code: "SUGGESTED_ORDER_CREATED",
    message: "Pedido creado desde Compra Inteligente. Revisa cantidades antes de enviarlo.",
    data: { order, simulationTotalCents: simulation.simulatedTotalCents },
    warnings: simulation.warnings,
    auditEvents
  };
}

export function confirmSupplierReceiving(
  input: ConfirmReceivingInput,
  snapshot: SupplierDashboardSnapshot
): SupplierActionResult<{ receipt: SupplierReceivingReceipt; movementPreview: SupplierInventoryMovementPreview[]; payable?: SupplierPayable }> {
  const order = snapshot.openOrders.find((item) => item.id === input.orderId);
  if (!order) return blocked("ORDER_NOT_FOUND", "No encontramos el pedido para registrar recepcion.");
  if (!input.reason || input.reason.trim().length < 8) return blocked("REASON_REQUIRED", "Captura un motivo o referencia de recepcion.");
  if (!canActorReceive(input.actor.role)) return blocked("PERMISSION_DENIED", "Este rol no puede confirmar recepciones.");
  if (order.status === "cancelled" || order.status === "closed" || order.status === "received") {
    return blocked("ORDER_CLOSED", "No puedes recibir contra un pedido cancelado, cerrado o ya recibido.");
  }

  const differences: SupplierReceivingDifference[] = [];
  const movements: SupplierInventoryMovementPreview[] = [];
  let receivedTotalCents = 0;

  for (const line of order.lines) {
    const receivedUnits = normalizeUnits(input.receivedUnitsByLineId[line.id] ?? line.orderedUnits);
    receivedTotalCents += receivedUnits * line.unitCostCents;
    if (receivedUnits !== line.orderedUnits) {
      differences.push({
        productId: line.productId,
        sku: line.sku,
        name: line.name,
        expectedUnits: line.orderedUnits,
        receivedUnits,
        reason: receivedUnits < line.orderedUnits ? "partial" : "extra",
        note: receivedUnits < line.orderedUnits ? "Recepcion parcial: faltan unidades contra pedido." : "Sobre-recepcion: llegaron mas unidades de las pedidas."
      });
    }
    movements.push({
      id: `mov_${order.id}_${line.id}`,
      productId: line.productId,
      sku: line.sku,
      productName: line.name,
      beforeQty: 0,
      deltaQty: receivedUnits,
      afterQty: receivedUnits,
      reason: "receiving",
      sourceId: order.id,
      sourceLabel: order.folio
    });
  }

  const receipt: SupplierReceivingReceipt = {
    id: `recv_${order.id}`,
    orderId: order.id,
    supplierId: order.supplierId,
    supplierName: order.supplierName,
    status: differences.length ? "with_differences" : "complete",
    expectedAt: order.expectedReceptionDate,
    receivedAt: input.receivedAt ?? DEFAULT_NOW,
    differences
  };

  const payable: SupplierPayable | undefined = receivedTotalCents > 0 ? {
    id: `pay_${receipt.id}`,
    supplierId: order.supplierId,
    supplierName: order.supplierName,
    orderId: order.id,
    dueDate: order.expectedPaymentDate,
    amountCents: receivedTotalCents,
    status: "scheduled",
    notes: differences.length ? "Generada desde recepcion con diferencias; revisar antes de pagar completo." : "Generada desde recepcion completa."
  } : undefined;

  const auditEvents = [
    auditEvent({
      topic: differences.length ? "receiving.completed_with_differences" : "receiving.completed",
      entityType: "receiving",
      entityId: receipt.id,
      supplierId: order.supplierId,
      supplierName: order.supplierName,
      actor: input.actor,
      reason: input.reason,
      source: "pc.receiving",
      visibleSummary: differences.length ? "Recepcion confirmada con diferencias." : "Recepcion confirmada y lista para afectar inventario.",
      after: { status: receipt.status, differences: differences.length }
    }),
    ...movements.map((movement) => auditEvent({
      topic: "stock.increased_from_receiving" as SupplierLifecycleEventTopic,
      entityType: "stock_movement" as const,
      entityId: movement.id,
      supplierId: order.supplierId,
      supplierName: order.supplierName,
      actor: input.actor,
      reason: input.reason,
      source: "pc.receiving" as const,
      visibleSummary: `Entrada prevista para ${movement.productName}: +${movement.deltaQty} unidades.`,
      after: movement as unknown as Record<string, unknown>
    }))
  ];
  if (payable) {
    auditEvents.push(auditEvent({
      topic: "supplier_payable.created",
      entityType: "payable",
      entityId: payable.id,
      supplierId: order.supplierId,
      supplierName: order.supplierName,
      actor: input.actor,
      reason: input.reason,
      source: "pc.payables",
      visibleSummary: `Cuenta por pagar generada por recepcion de ${order.supplierName}.`,
      after: { amountCents: payable.amountCents, dueDate: payable.dueDate, status: payable.status }
    }));
  }

  return {
    ok: true,
    code: differences.length ? "RECEIVING_CONFIRMED_WITH_DIFFERENCES" : "RECEIVING_CONFIRMED",
    message: differences.length ? "Recepcion confirmada con diferencias. Revisa los productos marcados antes de cerrar el pedido." : "Recepcion confirmada. El inventario fue actualizado y quedo registro de la entrada.",
    data: { receipt, movementPreview: movements, payable },
    warnings: differences.map((difference) => `${difference.sku}: esperado ${difference.expectedUnits}, recibido ${difference.receivedUnits}.`),
    auditEvents
  };
}

export function registerSupplierPayment(
  input: RegisterSupplierPaymentInput,
  snapshot: SupplierDashboardSnapshot
): SupplierActionResult<{ payable: SupplierPayable; remainingCents: number }> {
  const payable = snapshot.payables.find((item) => item.id === input.payableId);
  if (!payable) return blocked("PAYABLE_NOT_FOUND", "No encontramos la cuenta por pagar.");
  if (!canActorPay(input.actor.role)) return blocked("PERMISSION_DENIED", "Este rol no puede registrar pagos a proveedor.");
  if (!input.reason || input.reason.trim().length < 8) return blocked("REASON_REQUIRED", "Captura una referencia o motivo de pago.");
  if (input.amountCents <= 0) return blocked("INVALID_PAYMENT_AMOUNT", "El pago debe ser mayor a cero.");
  if (payable.status === "paid") return blocked("PAYABLE_ALREADY_PAID", "Esta cuenta por pagar ya esta cerrada.");

  const paid = Math.min(input.amountCents, payable.amountCents);
  const remaining = Math.max(0, payable.amountCents - paid);
  const updated: SupplierPayable = {
    ...payable,
    amountCents: remaining,
    status: remaining === 0 ? "paid" : "due_soon",
    notes: remaining === 0 ? "Pago registrado y cuenta cerrada." : `Pago parcial registrado; quedan ${remaining} centavos.`
  };
  const topic: SupplierLifecycleEventTopic = remaining === 0 ? "supplier_payable.paid" : "supplier_payable.partial_paid";

  return {
    ok: true,
    code: remaining === 0 ? "PAYABLE_PAID" : "PAYABLE_PARTIAL_PAYMENT",
    message: remaining === 0 ? "Pago registrado. La cuenta por pagar quedo cerrada." : "Pago parcial registrado. La cuenta por pagar sigue pendiente.",
    data: { payable: updated, remainingCents: remaining },
    warnings: remaining === 0 ? [] : ["Queda saldo pendiente; considera impacto en el siguiente presupuesto seguro."],
    auditEvents: [auditEvent({
      topic,
      entityType: "payable",
      entityId: payable.id,
      supplierId: payable.supplierId,
      supplierName: payable.supplierName,
      actor: input.actor,
      reason: input.reason,
      source: "pc.payables",
      visibleSummary: remaining === 0 ? `Pago cerrado para ${payable.supplierName}.` : `Pago parcial registrado para ${payable.supplierName}.`,
      before: { amountCents: payable.amountCents, status: payable.status },
      after: { amountCents: updated.amountCents, status: updated.status }
    })]
  };
}

function buildOrderWorkflow(order: SupplierPurchaseOrder): SupplierOrderWorkflowCard {
  const steps: SupplierOrderWorkflowStep[] = [
    step("draft", "Borrador", order.status === "draft"),
    step("suggested", "Sugerido", order.status === "suggested"),
    step("approved", "Aprobado", order.status === "approved"),
    step("sent", "Enviado", order.status === "sent"),
    step("partially_received", "Recepcion parcial", order.status === "partially_received"),
    step("received", "Recibido", order.status === "received"),
    step("closed", "Cerrado", order.status === "closed")
  ];
  const currentIndex = steps.findIndex((item) => item.status === "current");
  return {
    orderId: order.id,
    folio: order.folio,
    supplierName: order.supplierName,
    status: order.status,
    source: order.source,
    totalCents: order.totalCents,
    expectedReceptionDate: order.expectedReceptionDate,
    expectedPaymentDate: order.expectedPaymentDate,
    nextAction: nextOrderAction(order),
    risk: order.status === "suggested" ? "Revisar cantidades antes de enviar; viene de Compra Inteligente." : order.status === "sent" ? "Registrar recepcion cuando llegue mercancia." : "Mantener trazabilidad hasta cerrar.",
    steps: steps.map((item, index) => {
      if (item.status === "current") return item;
      if (currentIndex >= 0 && index < currentIndex) return { ...item, status: "done" };
      return { ...item, status: "next" };
    })
  };
}

function step(id: string, label: string, current: boolean): SupplierOrderWorkflowStep {
  return {
    id,
    label,
    status: current ? "current" : "next",
    description: current ? "Estado actual del pedido." : "Paso esperado del ciclo operativo."
  };
}

function nextOrderAction(order: SupplierPurchaseOrder): string {
  const actions: Record<SupplierPurchaseOrder["status"], string> = {
    draft: "Completar lineas y aprobar pedido",
    suggested: "Revisar recomendacion y aprobar",
    approved: "Marcar como enviado",
    sent: "Registrar recepción",
    partially_received: "Completar recepcion o cerrar diferencia",
    received: "Crear o revisar cuenta por pagar",
    cancelled: "Ver auditoria de cancelacion",
    closed: "Consultar historial"
  };
  return actions[order.status];
}

function buildMovementPreview(orders: SupplierPurchaseOrder[], receipts: SupplierReceivingReceipt[]): SupplierInventoryMovementPreview[] {
  const byOrder = new Map(orders.map((order) => [order.id, order]));
  const previews: SupplierInventoryMovementPreview[] = [];
  for (const receipt of receipts) {
    const order = receipt.orderId ? byOrder.get(receipt.orderId) : undefined;
    if (!order) continue;
    for (const line of order.lines) {
      const difference = receipt.differences.find((item) => item.productId === line.productId || item.sku === line.sku);
      const received = difference ? Math.max(0, difference.receivedUnits) : Math.max(0, line.orderedUnits - line.receivedUnits);
      previews.push({
        id: `preview_${receipt.id}_${line.id}`,
        productId: line.productId,
        sku: line.sku,
        productName: line.name,
        beforeQty: 0,
        deltaQty: received,
        afterQty: received,
        reason: "receiving",
        sourceId: receipt.id,
        sourceLabel: order.folio
      });
    }
  }
  return previews;
}

function buildPayablePlan(payables: SupplierPayable[], availableCashCents: number, reserveCashCents: number): SupplierPayablePlan[] {
  const safeBudget = Math.max(0, availableCashCents - reserveCashCents);
  return payables.map((payable) => {
    const cashAfter = safeBudget - payable.amountCents;
    const pressure = classifyCashPressure(payable.amountCents, safeBudget, cashAfter, reserveCashCents);
    return {
      payableId: payable.id,
      supplierId: payable.supplierId,
      supplierName: payable.supplierName,
      dueDate: payable.dueDate,
      amountCents: payable.amountCents,
      status: payable.status,
      cashPressure: pressure,
      recommendedAction: payable.status === "overdue" ? "Pagar o negociar antes de aprobar compra nueva." : pressure === "tight" ? "Reservar caja antes de crear pedido." : "Mantener programado.",
      auditRequired: payable.status === "overdue" || pressure === "tight" || pressure === "blocked"
    };
  }).sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime());
}

function buildCalendarEvents(
  now: IsoDate,
  suppliers: SupplierAccount[],
  recommendations: SmartPurchaseRecommendation[],
  orders: SupplierPurchaseOrder[],
  receipts: SupplierReceivingReceipt[],
  payables: SupplierPayable[]
): SupplierCalendarEvent[] {
  const events: SupplierCalendarEvent[] = [];
  for (const supplier of suppliers) {
    if (supplier.visitRule) {
      events.push(calendarEvent(supplier.id, supplier.tradeName, "visit", `Visita de ${supplier.tradeName}`, supplier.visitRule.nextVisitDate, daysUntil(now, supplier.visitRule.nextVisitDate) <= 2 ? "high" : "medium", "Ver proveedor"));
      events.push(calendarEvent(supplier.id, supplier.tradeName, "order_cutoff", `Fecha límite de pedido: ${supplier.tradeName}`, supplier.visitRule.nextOrderCutoff, daysUntil(now, supplier.visitRule.nextOrderCutoff) <= 1 ? "critical" : "high", "Crear pedido"));
    }
  }
  for (const recommendation of recommendations.slice(0, 8)) {
    events.push(calendarEvent(recommendation.supplierId ?? "missing", recommendation.supplierName, "recommendation", recommendation.title, recommendation.idealOrderDate, recommendation.priority === "critical" ? "critical" : "high", "Ver recomendación"));
  }
  for (const order of orders) {
    events.push(calendarEvent(order.supplierId, order.supplierName, "expected_receiving", `Recepción esperada ${order.folio}`, order.expectedReceptionDate, order.status === "sent" ? "high" : "medium", "Registrar recepción"));
  }
  for (const receipt of receipts) {
    events.push(calendarEvent(receipt.supplierId, receipt.supplierName, "expected_receiving", receipt.status === "with_differences" ? "Recepción con diferencias" : "Recepción pendiente", receipt.expectedAt, receipt.status === "with_differences" ? "critical" : "high", "Confirmar recepción"));
  }
  for (const payable of payables) {
    events.push(calendarEvent(payable.supplierId, payable.supplierName, "payment_due", `Pago ${payable.supplierName}`, payable.dueDate, payable.status === "overdue" ? "critical" : "medium", "Revisar pago"));
  }
  return events.sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime());
}

function calendarEvent(supplierId: string, supplierName: string, kind: SupplierCalendarEvent["kind"], title: string, startsAt: IsoDate, severity: SupplierCalendarEvent["severity"], actionLabel: string): SupplierCalendarEvent {
  return { id: `${kind}_${supplierId}_${title}_${startsAt}`.replace(/[^a-zA-Z0-9_]/g, "_"), supplierId, supplierName, kind, title, startsAt, severity, actionLabel, actionHref: "/proveedores" };
}

function buildSyntheticAuditTrail(
  now: IsoDate,
  recommendations: SmartPurchaseRecommendation[],
  orders: SupplierPurchaseOrder[],
  receipts: SupplierReceivingReceipt[],
  payables: SupplierPayable[],
  movements: SupplierInventoryMovementPreview[]
): SupplierAuditEvent[] {
  const actor = { id: "system_prisma", name: "PRISMA", role: "Sistema" };
  const events: SupplierAuditEvent[] = [];
  for (const recommendation of recommendations.slice(0, 8)) {
    events.push(auditEvent({ topic: "smart_purchase.recommendation.simulated", entityType: "smart_purchase", entityId: recommendation.id, supplierId: recommendation.supplierId, supplierName: recommendation.supplierName, actor, reason: "Corrida automatica de Compra Inteligente.", source: "pc.smart_purchase", visibleSummary: `${recommendation.title}: ${recommendation.summary}`, after: { priority: recommendation.priority, cashImpact: recommendation.cashImpact, totalCents: recommendation.estimatedTotalCents }, createdAt: now }));
  }
  for (const order of orders) {
    events.push(auditEvent({ topic: order.source === "smart_purchase" ? "purchase_order.converted_from_recommendation" : "purchase_order.created", entityType: "purchase_order", entityId: order.id, supplierId: order.supplierId, supplierName: order.supplierName, actor, reason: "Pedido operativo visible en Proveedores.", source: "pc.suppliers", visibleSummary: `${order.folio} en estado ${order.status}.`, after: { status: order.status, totalCents: order.totalCents }, createdAt: order.createdAt }));
  }
  for (const receipt of receipts) {
    events.push(auditEvent({ topic: receipt.status === "with_differences" ? "receiving.completed_with_differences" : "receiving.completed", entityType: "receiving", entityId: receipt.id, supplierId: receipt.supplierId, supplierName: receipt.supplierName, actor, reason: "Recepcion pendiente de cierre operativo.", source: "pc.receiving", visibleSummary: receipt.status === "with_differences" ? "Recepcion con diferencias requiere motivo." : "Recepcion pendiente de confirmar.", after: { status: receipt.status, differences: receipt.differences.length }, createdAt: receipt.receivedAt ?? receipt.expectedAt }));
  }
  for (const payable of payables) {
    events.push(auditEvent({ topic: "supplier_payable.created", entityType: "payable", entityId: payable.id, supplierId: payable.supplierId, supplierName: payable.supplierName, actor, reason: "Cuenta por pagar derivada de compra o recepcion.", source: "pc.payables", visibleSummary: `${payable.supplierName}: pago ${payable.status}.`, after: { amountCents: payable.amountCents, dueDate: payable.dueDate, status: payable.status }, createdAt: payable.dueDate }));
  }
  for (const movement of movements.slice(0, 8)) {
    events.push(auditEvent({ topic: "stock.increased_from_receiving", entityType: "stock_movement", entityId: movement.id, actor, reason: "Vista previa de movimiento por recepcion.", source: "pc.receiving", visibleSummary: `${movement.productName}: +${movement.deltaQty} unidades al confirmar recepcion.`, after: movement as unknown as Record<string, unknown>, createdAt: now }));
  }
  return events.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}

function buildReadinessGates(input: BuildSupplierLifecycleInput, workflows: SupplierOrderWorkflowCard[], movements: SupplierInventoryMovementPreview[], payables: SupplierPayablePlan[], audit: SupplierAuditEvent[]): SupplierReadinessGate[] {
  const activeSuppliers = input.suppliers.filter((supplier) => supplier.status === "active").length;
  const recommendations = input.recommendations.length;
  const diffReceipts = input.receivingQueue.filter((receipt) => receipt.differences.length > 0).length;
  return [
    gate("suppliers", "Proveedores activos", activeSuppliers > 0 ? "ready" : "blocked", `${activeSuppliers} proveedores activos con reglas comerciales.`, "Sin proveedores activos no hay Compra Inteligente confiable.", "Agregar proveedor"),
    gate("smart_purchase", "Recomendaciones explicables", recommendations > 0 ? "ready" : "blocked", `${recommendations} recomendaciones generadas con razones y caja.`, "Compra Inteligente debe explicar cada sugerencia.", "Generar recomendaciones"),
    gate("orders", "Pedidos accionables", workflows.length > 0 ? "ready" : "warning", `${workflows.length} pedidos visibles en ciclo operativo.`, "La recomendacion debe poder convertirse a pedido.", "Crear pedido sugerido"),
    gate("receiving", "Recepciones trazables", movements.length > 0 ? "ready" : "warning", `${movements.length} movimientos previstos por recepcion.`, "Recepcion confirmada debe crear movimiento de inventario.", "Registrar recepción"),
    gate("differences", "Diferencias con motivo", diffReceipts === 0 ? "ready" : "warning", `${diffReceipts} recepciones tienen diferencias por revisar.`, "Las diferencias no se borran; se explican.", "Revisar diferencias"),
    gate("payables", "Pagos considerados en caja", payables.length > 0 ? "ready" : "warning", `${payables.length} cuentas por pagar afectan presupuesto seguro.`, "Caja y pagos proximos deben limitar compras.", "Ver cuentas por pagar"),
    gate("audit", "Auditoría generada", audit.length > 0 ? "ready" : "blocked", `${audit.length} eventos auditables construidos.`, "Toda acción sensible debe dejar rastro.", "Ver auditoria"),
    gate("sync", "Datos pendientes visibles", (input.unresolvedSyncSignals ?? []).length ? "warning" : "ready", `${(input.unresolvedSyncSignals ?? []).length} senales de sincronizacion pendientes.`, "Si hay eventos pendientes, no se finge certeza absoluta.", "Revisar sincronizacion")
  ];
}

function buildSurfaceSignals(recommendations: SmartPurchaseRecommendation[], receipts: SupplierReceivingReceipt[], payables: SupplierPayable[], syncSignals: Array<{ id: string; source: string; message: string; severity: "critical" | "high" | "medium" | "low" }>): SupplierSurfaceSignal[] {
  const signals: SupplierSurfaceSignal[] = [];
  for (const recommendation of recommendations.filter((item) => item.priority === "critical" || item.cashImpact === "tight").slice(0, 5)) {
    signals.push({ id: `mobile_${recommendation.id}`, surface: "mobile", title: "Compra critica por revisar", message: `${recommendation.supplierName}: ${recommendation.summary}`, severity: recommendation.priority === "critical" ? "critical" : "high", allowedAction: "Ver impacto y aprobar bajo limite configurado", forbiddenAction: "Editar proveedor completo o cambiar reglas de presupuesto" });
    signals.push({ id: `tablet_${recommendation.id}`, surface: "tablet", title: "Producto critico", message: "Hay productos criticos. Revisa Compra Inteligente en PC.", severity: "high", allowedAction: "Mostrar aviso ligero durante operacion", forbiddenAction: "Administrar proveedores desde caja" });
  }
  for (const receipt of receipts.filter((item) => item.status === "with_differences" || item.status === "pending").slice(0, 4)) {
    signals.push({ id: `tablet_receiving_${receipt.id}`, surface: "tablet", title: "Recepción pendiente", message: `${receipt.supplierName}: confirma con encargado antes de ajustar inventario.`, severity: receipt.status === "with_differences" ? "critical" : "medium", allowedAction: "Mostrar recepcion pendiente", forbiddenAction: "Cerrar recepcion con diferencias" });
  }
  for (const payable of payables.filter((item) => item.status === "overdue" || item.status === "due_soon").slice(0, 4)) {
    signals.push({ id: `mobile_payable_${payable.id}`, surface: "mobile", title: "Pago proximo", message: `${payable.supplierName}: pago por revisar antes de aprobar compras nuevas.`, severity: payable.status === "overdue" ? "critical" : "medium", allowedAction: "Ver monto y fecha", forbiddenAction: "Cancelar cuenta por pagar sin PC" });
  }
  for (const sync of syncSignals) {
    signals.push({ id: `sync_${sync.id}`, surface: "mobile", title: sync.source, message: sync.message, severity: sync.severity, allowedAction: "Mostrar advertencia de datos pendientes", forbiddenAction: "Fingir recomendacion definitiva" });
  }
  return signals;
}

function auditEvent(args: Omit<SupplierAuditEvent, "id" | "createdAt" | "requiresReview"> & { createdAt?: IsoDate }): SupplierAuditEvent {
  const createdAt = args.createdAt ?? DEFAULT_NOW;
  return {
    ...args,
    id: `${args.topic}_${args.entityId}_${createdAt}`.replace(/[^a-zA-Z0-9_]/g, "_"),
    createdAt,
    requiresReview: args.topic.includes("with_differences") || args.topic.includes("reverted") || args.topic.includes("rejected") || args.topic.includes("partial_paid")
  };
}

function toOrderLine(line: SmartPurchaseLine): SupplierPurchaseOrderLine {
  return {
    id: `pol_${line.id}`,
    productId: line.productId,
    sku: line.sku,
    name: line.productName,
    orderedUnits: line.suggestedUnits,
    receivedUnits: 0,
    unitCostCents: line.unitCostCents,
    expectedTotalCents: line.estimatedCostCents
  };
}

function gate(id: string, label: string, status: SupplierReadinessGate["status"], evidence: string, description: string, actionLabel: string): SupplierReadinessGate {
  return { id, label, status, evidence, description, actionLabel };
}

function blocked<TPayload>(code: string, message: string): SupplierActionResult<TPayload> {
  return { ok: false, code, message, warnings: [message], auditEvents: [] };
}

function canActorCreateOrder(role: string): boolean {
  return ["Encargado", "Administrador", "Dueño", "Sistema"].includes(role);
}
function canActorReceive(role: string): boolean {
  return ["Encargado", "Administrador", "Dueño", "Sistema"].includes(role);
}
function canActorPay(role: string): boolean {
  return ["Administrador", "Dueño"].includes(role);
}
function normalizeUnits(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.floor(value));
}
function daysUntil(now: IsoDate, target: IsoDate): number {
  return Math.ceil((new Date(target).getTime() - new Date(now).getTime()) / DAY_MS);
}
function classifyCashPressure(amountCents: number, safeBudgetCents: number, cashAfterCents: number, reserveCents: number): CashImpact {
  if (amountCents > safeBudgetCents || cashAfterCents < 0) return "blocked";
  if (cashAfterCents < reserveCents * 0.5) return "tight";
  if (amountCents > safeBudgetCents * 0.55) return "careful";
  return "safe";
}
