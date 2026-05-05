import type {
  SmartPurchaseRecommendation,
  SmartPurchaseSignal,
  SupplierAccount,
  SupplierLifecycleSnapshot,
  SupplierPayable,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt
} from "./types";
import {
  actionLabel,
  calendarKindLabel,
  calendarTone,
  cashImpactLabel,
  cashImpactTone,
  cleanVisibleText,
  dateTime,
  entityLabel,
  friendlyFolio,
  money,
  payableStatusLabel,
  paymentConditionLabel,
  priorityLabel,
  priorityTone,
  readinessLabel,
  readinessTone,
  receivingStatusLabel,
  shortDateTime,
  supplierCategoryLabel,
  supplierStatusLabel,
  supplierStatusTone,
  surfaceLabel,
  topicLabel
} from "./visible-labels";

export interface SupplierOperatorBoardInput {
  generatedAt: string;
  suppliers: SupplierAccount[];
  recommendations: SmartPurchaseRecommendation[];
  signals: SmartPurchaseSignal[];
  openOrders: SupplierPurchaseOrder[];
  receivingQueue: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  lifecycle: SupplierLifecycleSnapshot;
}

export interface SupplierOperatorBoardModel {
  generatedAtLabel: string;
  summary: Array<{ id: string; label: string; value: string; note: string; tone: string }>;
  decisions: Array<{ id: string; label: string; value: string; helper: string; tone: string }>;
  recommendations: Array<{
    id: string;
    title: string;
    supplierName: string;
    priorityLabel: string;
    priorityTone: string;
    actionLabel: string;
    cashLabel: string;
    cashTone: string;
    summary: string;
    amount: string;
    dates: Array<{ label: string; value: string }>;
    lines: Array<{ id: string; productName: string; sku: string; stock: string; coverage: string; suggested: string; cost: string }>;
    reasons: string[];
  }>;
  suppliers: Array<{ id: string; name: string; category: string; status: string; tone: string; visit: string; payment: string; contact: string; action: string }>;
  calendar: Array<{ id: string; kind: string; supplierName: string; when: string; action: string; tone: string }>;
  orders: Array<{ id: string; folio: string; supplierName: string; status: string; total: string; reception: string; payment: string; nextAction: string; steps: Array<{ id: string; label: string; tone: string }> }>;
  receivings: Array<{ id: string; supplierName: string; status: string; expectedAt: string; differences: string; action: string }>;
  payables: Array<{ id: string; supplierName: string; dueDate: string; amount: string; status: string; pressure: string; action: string; tone: string }>;
  signals: Array<{ id: string; surface: string; title: string; message: string; allowedAction: string; pcOnly: string; tone: string }>;
  audit: Array<{ id: string; topic: string; entity: string; actor: string; when: string; summary: string }>;
  readiness: Array<{ id: string; label: string; status: string; evidence: string; description: string; action: string; tone: string }>;
}

export function buildSupplierOperatorBoardModel(input: SupplierOperatorBoardInput): SupplierOperatorBoardModel {
  const criticalSignals = input.signals.filter((signal) => signal.severity === "critical").length;
  const suggestedTotal = input.recommendations.reduce((sum, item) => sum + item.estimatedTotalCents, 0);
  const dueSoon = input.payables.filter((item) => item.status === "due_soon" || item.status === "overdue").reduce((sum, item) => sum + item.amountCents, 0);
  const activeSuppliers = input.suppliers.filter((supplier) => supplier.status === "active").length;
  const reviewSuppliers = input.suppliers.length - activeSuppliers;

  return {
    generatedAtLabel: dateTime(input.generatedAt),
    summary: [
      { id: "suggested", label: "Compra sugerida", value: money(suggestedTotal), note: "Suma de recomendaciones activas.", tone: "safe" },
      { id: "cash", label: "Pagos próximos", value: money(dueSoon), note: "Compromisos que pesan antes de comprar.", tone: dueSoon > 0 ? "warn" : "ok" },
      { id: "signals", label: "Señales críticas", value: String(criticalSignals), note: "Productos o proveedores que piden revisión.", tone: criticalSignals > 0 ? "urgent" : "ok" },
      { id: "receiving", label: "Recepciones con diferencia", value: String(input.lifecycle.counters.receivingsWithDifferences), note: "Diferencias visibles, no enterradas.", tone: input.lifecycle.counters.receivingsWithDifferences > 0 ? "warn" : "ok" },
      { id: "suppliers", label: "Proveedores activos", value: `${activeSuppliers}/${input.suppliers.length}`, note: reviewSuppliers > 0 ? `${reviewSuppliers} requieren revisión.` : "Directorio listo para operar.", tone: reviewSuppliers > 0 ? "warn" : "ok" },
      { id: "orders", label: "Pedidos con acción", value: String(input.lifecycle.counters.ordersNeedingAction), note: "Pedidos sugeridos, enviados o por recibir.", tone: input.lifecycle.counters.ordersNeedingAction > 0 ? "high" : "ok" }
    ],
    decisions: [
      { id: "buy", label: "Comprar hoy", value: String(input.recommendations.filter((item) => item.action === "create_order").length), helper: "Recomendaciones listas para pedido.", tone: "safe" },
      { id: "simulate", label: "Simular primero", value: String(input.recommendations.filter((item) => item.action === "simulate" || item.cashImpact === "tight").length), helper: "Compras que deben cuidar caja.", tone: "warn" },
      { id: "review", label: "Revisar datos", value: String(input.lifecycle.counters.warningGates + input.lifecycle.counters.blockedGates), helper: "Criterios que todavía piden atención.", tone: "review" }
    ],
    recommendations: input.recommendations.slice(0, 6).map((recommendation) => ({
      id: recommendation.id,
      title: cleanVisibleText(recommendation.title),
      supplierName: recommendation.supplierName,
      priorityLabel: priorityLabel(recommendation.priority),
      priorityTone: priorityTone(recommendation.priority),
      actionLabel: actionLabel(recommendation.action),
      cashLabel: cashImpactLabel(recommendation.cashImpact),
      cashTone: cashImpactTone(recommendation.cashImpact),
      summary: cleanVisibleText(recommendation.summary),
      amount: money(recommendation.estimatedTotalCents),
      dates: [
        { label: "Pedir", value: shortDateTime(recommendation.idealOrderDate) },
        { label: "Recibir", value: shortDateTime(recommendation.expectedReceptionDate) },
        { label: "Pagar", value: shortDateTime(recommendation.expectedPaymentDate) },
        { label: "Caja después", value: money(recommendation.cashAfterPurchaseCents) }
      ],
      lines: recommendation.lines.slice(0, 4).map((line) => ({
        id: line.id,
        productName: line.productName,
        sku: line.sku,
        stock: `${line.currentStockUnits} pzas`,
        coverage: `${line.coverageDaysBefore} días`,
        suggested: `${line.suggestedPackages} paq. / ${line.suggestedUnits} pzas`,
        cost: money(line.estimatedCostCents)
      })),
      reasons: recommendation.reasons.map(cleanVisibleText).slice(0, 5)
    })),
    suppliers: input.suppliers.map((supplier) => ({
      id: supplier.id,
      name: supplier.tradeName,
      category: supplierCategoryLabel(supplier.category),
      status: supplierStatusLabel(supplier.status),
      tone: supplierStatusTone(supplier.status),
      visit: supplier.visitRule ? `${supplier.visitRule.weekdays.join(", ")} · ${supplier.visitRule.approximateTime}` : "Sin calendario",
      payment: paymentConditionLabel(supplier.terms.paymentCondition),
      contact: supplier.contacts.find((contact) => contact.isPrimary)?.whatsapp ?? supplier.contacts[0]?.phone ?? "Sin contacto",
      action: supplier.status === "active" ? "Operar" : "Revisar antes de pedir"
    })),
    calendar: uniqueCalendar(input.lifecycle.calendar).slice(0, 12).map((event) => ({
      id: event.id,
      kind: calendarKindLabel(event.kind),
      supplierName: event.supplierName,
      when: shortDateTime(event.startsAt),
      action: cleanVisibleText(event.actionLabel),
      tone: calendarTone(event.severity)
    })),
    orders: input.lifecycle.orderWorkflow.slice(0, 8).map((order) => ({
      id: order.orderId,
      folio: friendlyFolio(order.folio),
      supplierName: order.supplierName,
      status: orderStatusText(order.status),
      total: money(order.totalCents),
      reception: shortDateTime(order.expectedReceptionDate),
      payment: shortDateTime(order.expectedPaymentDate),
      nextAction: cleanVisibleText(order.nextAction),
      steps: order.steps.map((step) => ({ id: `${order.orderId}-${step.id}`, label: cleanVisibleText(step.label), tone: step.status === "done" ? "ok" : step.status === "current" ? "high" : step.status === "next" ? "muted" : "review" }))
    })),
    receivings: input.receivingQueue.slice(0, 8).map((receipt) => ({
      id: receipt.id,
      supplierName: receipt.supplierName,
      status: receivingStatusLabel(receipt.status),
      expectedAt: shortDateTime(receipt.expectedAt),
      differences: receipt.differences.length ? `${receipt.differences.length} diferencia(s)` : "Sin diferencias",
      action: receipt.status === "with_differences" ? "Confirmar con motivo" : "Registrar recepción"
    })),
    payables: input.lifecycle.payablePlan.slice(0, 8).map((payable) => ({
      id: payable.payableId,
      supplierName: payable.supplierName,
      dueDate: shortDateTime(payable.dueDate),
      amount: money(payable.amountCents),
      status: payableStatusLabel(payable.status),
      pressure: cashImpactLabel(payable.cashPressure),
      action: cleanVisibleText(payable.recommendedAction),
      tone: cashImpactTone(payable.cashPressure)
    })),
    signals: input.lifecycle.surfaceSignals.slice(0, 8).map((signal) => ({
      id: signal.id,
      surface: surfaceLabel(signal.surface),
      title: cleanVisibleText(signal.title),
      message: cleanVisibleText(signal.message),
      allowedAction: cleanVisibleText(signal.allowedAction),
      pcOnly: cleanVisibleText(signal.forbiddenAction),
      tone: signal.severity
    })),
    audit: input.lifecycle.auditEvents.slice(0, 8).map((event) => ({
      id: event.id,
      topic: topicLabel(event.topic),
      entity: entityLabel(event.entityType),
      actor: event.actor.name,
      when: shortDateTime(event.createdAt),
      summary: cleanVisibleText(event.visibleSummary)
    })),
    readiness: input.lifecycle.readiness.map((gate) => ({
      id: gate.id,
      label: cleanVisibleText(gate.label),
      status: readinessLabel(gate.status),
      evidence: cleanVisibleText(gate.evidence),
      description: cleanVisibleText(gate.description),
      action: cleanVisibleText(gate.actionLabel),
      tone: readinessTone(gate.status)
    }))
  };
}

function uniqueCalendar(events: SupplierLifecycleSnapshot["calendar"]): SupplierLifecycleSnapshot["calendar"] {
  const seen = new Set<string>();
  const result: SupplierLifecycleSnapshot["calendar"] = [];
  for (const event of [...events].sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime())) {
    const key = `${event.kind}|${event.supplierId}|${event.title}|${event.startsAt}|${event.actionLabel}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push({ ...event, id: key.replace(/[^a-zA-Z0-9]+/g, "_") });
  }
  return result;
}

function orderStatusText(status: SupplierPurchaseOrder["status"]): string {
  const labels: Record<SupplierPurchaseOrder["status"], string> = {
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
