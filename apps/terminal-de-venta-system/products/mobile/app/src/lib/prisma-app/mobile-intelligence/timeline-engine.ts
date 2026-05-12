import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { ActionInbox, AlertCenter, DataQualityReport, TimelineEvent } from "./contracts";
import { TimelineEventSchema } from "./contracts";
import { evidence } from "./evidence";

function event(input: TimelineEvent): TimelineEvent {
  return TimelineEventSchema.parse(input);
}

export function buildIntelligenceTimeline(state: MobileDataPlaneState, alerts: AlertCenter, inbox: ActionInbox, report: DataQualityReport): TimelineEvent[] {
  const generatedAt = report.generatedAt;
  const events: TimelineEvent[] = [];
  const firstSale = state.salesToday.sales[0];
  const lastSale = state.salesToday.sales[state.salesToday.sales.length - 1];

  if (firstSale) {
    events.push(event({
      id: `sale-first-${firstSale.id}`,
      type: "sales",
      occurredAt: firstSale.completedAt,
      title: "Primera venta registrada",
      detail: `${firstSale.ticketNumber} por ${firstSale.totalCents} centavos.`,
      whyItMatters: "Confirma que Tablet alimenta Mobile con venta real.",
      recommendedAction: "Usar como base de ritmo y comparar contra el pico del día.",
      severity: "info",
      source: "Tablet POS",
      evidence: [evidence("timeline-first-sale", "Ticket", "Tablet POS", firstSale.ticketNumber)]
    }));
  }

  if (lastSale && lastSale.id !== firstSale?.id) {
    events.push(event({
      id: `sale-last-${lastSale.id}`,
      type: "sales",
      occurredAt: lastSale.completedAt,
      title: "Última venta recibida",
      detail: `${lastSale.ticketNumber} actualiza el pulso comercial.`,
      whyItMatters: "Mide frescura de venta para decisiones móviles.",
      recommendedAction: "Validar inventario/caja si fue hora pico.",
      severity: "info",
      source: "Tablet POS",
      evidence: [evidence("timeline-last-sale", "Ticket", "Tablet POS", lastSale.ticketNumber)]
    }));
  }

  for (const alert of alerts.alerts.slice(0, 6)) {
    events.push(event({
      id: `alert-${alert.id}`,
      type: "alert",
      occurredAt: alert.lastSeenAt,
      title: alert.title,
      detail: alert.summary,
      whyItMatters: alert.whyItMatters,
      recommendedAction: alert.recommendedAction,
      severity: alert.severity,
      source: alert.source,
      evidence: alert.evidence
    }));
  }

  for (const action of inbox.items.slice(0, 4)) {
    events.push(event({
      id: `action-${action.id}`,
      type: "action",
      occurredAt: generatedAt,
      title: action.title,
      detail: action.reason,
      whyItMatters: action.impact,
      recommendedAction: action.recommendedAction,
      severity: action.priority <= 1 ? "critical" : action.priority === 2 ? "high" : action.priority === 3 ? "medium" : "low",
      source: action.ownerRole,
      evidence: action.evidence
    }));
  }

  if (events.length === 0) {
    events.push(event({
      id: "timeline-empty-snapshot",
      type: "system",
      occurredAt: generatedAt,
      title: "Snapshot sin eventos relevantes",
      detail: "No se recibieron ventas, alertas o acciones reales para ordenar.",
      whyItMatters: "PRISMA muestra vacío honesto en vez de rellenar timeline.",
      recommendedAction: "Confirmar fuentes o esperar operación real.",
      severity: "info",
      source: "Mobile Snapshot",
      evidence: [evidence("timeline-empty", "DataQuality", "Mobile", report.runtimeMode)]
    }));
  }

  return events
    .sort((a, b) => Date.parse(b.occurredAt) - Date.parse(a.occurredAt))
    .slice(0, 18);
}

