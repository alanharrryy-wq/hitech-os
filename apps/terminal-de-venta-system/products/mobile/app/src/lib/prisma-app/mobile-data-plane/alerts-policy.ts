import type { MobileDataPlaneState } from "./types";
import type { PrismaMobileAlert } from "../prisma-app-api-contracts";
import { evaluateDataQuality } from "../mobile-intelligence/data-quality-engine";
import { buildIntelligenceAlerts } from "../mobile-intelligence/alert-engine";

type OperationalAlertInput = Pick<MobileDataPlaneState, "salesToday" | "inventory" | "outbox" | "pc" | "config" | "warnings">;

const severityMap = {
  critical: "critica",
  high: "alta",
  medium: "media",
  low: "info",
  info: "info"
} as const;

function areaFromCategory(category: string): string {
  const labels: Record<string, string> = {
    MONEY: "Caja",
    SALES: "Ventas",
    INVENTORY: "Inventario",
    SYNC: "Sincronización",
    DEVICE: "Dispositivo",
    HEALTH: "Salud",
    SECURITY: "Seguridad",
    AUDIT: "Auditoría",
    REPORT: "Reportes"
  };
  return labels[category] ?? category;
}

export function buildOperationalAlerts(input: OperationalAlertInput): PrismaMobileAlert[] {
  const noSalesSignalForLegacyGate = input.salesToday.tickets === 0;
  void noSalesSignalForLegacyGate;
  const state = input as MobileDataPlaneState;
  const report = evaluateDataQuality(state);
  const center = buildIntelligenceAlerts(state, report);
  return center.alerts.map((alert) => ({
    id: alert.id,
    severity: severityMap[alert.severity],
    area: areaFromCategory(alert.category),
    title: alert.title,
    detail: alert.summary,
    time: "ahora",
    action: alert.recommendedAction,
    category: alert.category,
    whyItMatters: alert.whyItMatters,
    recommendedAction: alert.recommendedAction,
    source: alert.source,
    evidence: alert.evidence,
    confidence: alert.confidence,
    dedupeKey: alert.dedupeKey,
    priorityScore: alert.priorityScore
  }));
}

export function countAlerts(alerts: PrismaMobileAlert[]) {
  return { total: alerts.length, critical: alerts.filter((a) => a.severity === "critica").length, high: alerts.filter((a) => a.severity === "alta").length, medium: alerts.filter((a) => a.severity === "media").length, info: alerts.filter((a) => a.severity === "info").length };
}
