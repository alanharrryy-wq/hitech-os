import type { ActionInbox, ActionItem, AlertCenter, MobileAlert } from "./contracts";
import { ActionInboxSchema } from "./contracts";

function ownerForCategory(category: MobileAlert["category"]): string {
  const owners: Record<MobileAlert["category"], string> = {
    MONEY: "Encargado de caja",
    SALES: "Dueño / supervisor",
    INVENTORY: "Inventario",
    SYNC: "Sincronización",
    DEVICE: "Operación Tablet",
    HEALTH: "Operación",
    SECURITY: "Control",
    AUDIT: "Control",
    REPORT: "Backoffice"
  };
  return owners[category];
}

function priorityFromAlert(alert: MobileAlert): number {
  if (alert.category === "MONEY" && (alert.severity === "critical" || alert.severity === "high")) return 1;
  if (alert.category === "INVENTORY" && (alert.severity === "critical" || alert.severity === "high")) return 2;
  if (alert.category === "SYNC" && alert.severity === "medium") return 3;
  if (alert.severity === "critical") return 1;
  if (alert.severity === "high") return 2;
  if (alert.severity === "medium") return 3;
  if (alert.severity === "low") return 4;
  return 5;
}

function dueAtForPriority(priority: number, generatedAt: string): string | null {
  if (priority > 3) return null;
  const date = new Date(generatedAt);
  date.setMinutes(date.getMinutes() + (priority === 1 ? 15 : priority === 2 ? 60 : 180));
  return date.toISOString();
}

function fromAlert(alert: MobileAlert): ActionItem {
  const priority = priorityFromAlert(alert);
  return {
    id: `action-${alert.id}`,
    alertId: alert.id,
    title: alert.title,
    reason: alert.summary,
    impact: alert.whyItMatters,
    recommendedAction: alert.recommendedAction,
    ownerRole: ownerForCategory(alert.category),
    priority,
    priorityScore: alert.priorityScore,
    dueAt: dueAtForPriority(priority, alert.lastSeenAt),
    evidence: alert.evidence
  };
}

export function buildIntelligenceActionInbox(alertCenter: AlertCenter): ActionInbox {
  const items = alertCenter.alerts
    .map(fromAlert)
    .sort((a, b) => a.priority - b.priority || b.priorityScore - a.priorityScore || a.title.localeCompare(b.title, "es-MX"))
    .slice(0, 20);

  return ActionInboxSchema.parse({
    items,
    primaryAction: items[0] ?? null
  });
}

