import { supplierLifecycleScenarios } from "./lifecycle-scenarios";
import { summarizeValidation, validateSupplierLifecycleSnapshot } from "./lifecycle-validator";
import type { SupplierDashboardSnapshot } from "./types";

export interface SupplierLifecycleReportSection {
  id: string;
  title: string;
  status: "ready" | "warning" | "blocked";
  bullets: string[];
}

export interface SupplierLifecycleReport {
  title: string;
  generatedAt: string;
  status: "ready" | "warning" | "blocked";
  summary: string;
  sections: SupplierLifecycleReportSection[];
  scenarioCount: number;
}

export function buildSupplierLifecycleReport(snapshot: SupplierDashboardSnapshot): SupplierLifecycleReport {
  const validation = validateSupplierLifecycleSnapshot(snapshot);
  const criticalRecommendations = snapshot.recommendations.filter((item) => item.priority === "critical").length;
  const blockedRecommendations = snapshot.recommendations.filter((item) => item.priority === "blocked" || item.cashImpact === "blocked").length;
  const paymentsAtRisk = snapshot.lifecycle.payablePlan.filter((item) => item.cashPressure === "tight" || item.cashPressure === "blocked" || item.status === "overdue").length;
  const sections: SupplierLifecycleReportSection[] = [
    {
      id: "smart_purchase",
      title: "Compra Inteligente",
      status: blockedRecommendations > 0 ? "warning" : "ready",
      bullets: [
        `${snapshot.recommendations.length} recomendaciones generadas.`,
        `${criticalRecommendations} recomendaciones criticas.`,
        `${blockedRecommendations} recomendaciones bloqueadas o con caja bloqueada.`,
        "Cada recomendacion conserva razones, fechas, impacto de caja y accion sugerida."
      ]
    },
    {
      id: "orders",
      title: "Pedidos",
      status: snapshot.openOrders.some((order) => !order.lines.length) ? "blocked" : "ready",
      bullets: [
        `${snapshot.openOrders.length} pedidos operativos visibles.`,
        `${snapshot.lifecycle.orderWorkflow.length} workflows construidos.`,
        "Los pedidos de Compra Inteligente conservan origen y auditoria."
      ]
    },
    {
      id: "receiving",
      title: "Recepciones",
      status: snapshot.lifecycle.counters.receivingsWithDifferences > 0 ? "warning" : "ready",
      bullets: [
        `${snapshot.receivingQueue.length} recepciones en cola.`,
        `${snapshot.lifecycle.movementPreview.length} movimientos de inventario previstos.`,
        `${snapshot.lifecycle.counters.receivingsWithDifferences} recepciones con diferencias por revisar.`
      ]
    },
    {
      id: "payables",
      title: "Cuentas por pagar",
      status: paymentsAtRisk > 0 ? "warning" : "ready",
      bullets: [
        `${snapshot.lifecycle.payablePlan.length} obligaciones consideradas en caja.`,
        `${paymentsAtRisk} pagos con presion de caja o vencimiento.`,
        "El presupuesto seguro considera reserva y pagos proximos."
      ]
    },
    {
      id: "audit",
      title: "Auditoria",
      status: snapshot.lifecycle.auditEvents.length > 0 ? "ready" : "blocked",
      bullets: [
        `${snapshot.lifecycle.auditEvents.length} eventos auditables construidos.`,
        "Acciones sensibles guardan actor, motivo, entidad y resumen visible.",
        "Recepciones con diferencia y pagos parciales quedan marcados para revision."
      ]
    },
    {
      id: "boundaries",
      title: "Frontera Tablet/App",
      status: snapshot.lifecycle.surfaceSignals.length > 0 ? "ready" : "warning",
      bullets: [
        `${snapshot.lifecycle.surfaceSignals.filter((signal) => signal.surface === "tablet").length} señales ligeras para Tablet.`,
        `${snapshot.lifecycle.surfaceSignals.filter((signal) => signal.surface === "mobile").length} alertas para App movil.`,
        "Ni Tablet ni App movil reemplazan captura pesada de PC."
      ]
    }
  ];
  return {
    title: "PRISMA PC Proveedores Lifecycle 02",
    generatedAt: snapshot.generatedAt,
    status: validation.status,
    summary: summarizeValidation(validation),
    sections,
    scenarioCount: supplierLifecycleScenarios.length
  };
}
