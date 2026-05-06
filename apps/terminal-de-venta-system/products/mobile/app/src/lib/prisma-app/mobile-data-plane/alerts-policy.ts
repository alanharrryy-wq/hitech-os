import type { MobileDataPlaneState } from "./types";
import type { PrismaMobileAlert } from "../prisma-app-api-contracts";
import { classifyInventoryState } from "./inventory-adapter";
import { minutesAgoLabel } from "./money";

type OperationalAlertInput = Pick<MobileDataPlaneState, "salesToday" | "inventory" | "outbox" | "pc" | "config" | "warnings">;

function alert(id: string, severity: PrismaMobileAlert["severity"], area: string, title: string, detail: string, action: string, time = "ahora"): PrismaMobileAlert {
  return { id, severity, area, title, detail, action, time };
}

export function buildOperationalAlerts(input: OperationalAlertInput): PrismaMobileAlert[] {
  const alerts: PrismaMobileAlert[] = [];
  for (const item of input.inventory.items.slice(0, 20)) {
    const state = classifyInventoryState(item);
    if (state === "critico") alerts.push(alert(`stock-${item.sku}`, "critica", "Inventario", `${item.name} sin existencia`, `SKU ${item.sku} está en cero. Venta en riesgo real, no de PowerPoint.`, "Revisar reabasto o bloquear venta."));
    if (state === "reponer") alerts.push(alert(`reorder-${item.sku}`, "alta", "Inventario", `${item.name} por reponer`, `Quedan ${item.stockQty} piezas contra mínimo ${item.lowStockThreshold}.`, "Programar reposición."));
  }
  if (input.outbox.failed > 0) alerts.push(alert("outbox-failed", "alta", "Sincronización", "Eventos fallidos en outbox", `${input.outbox.failed} eventos no se han sincronizado correctamente.`, "Abrir bitácora de sync."));
  if (input.outbox.pending > 0) alerts.push(alert("outbox-pending", "media", "Sincronización", "Eventos pendientes", `${input.outbox.pending} eventos siguen en cola. Último sync: ${minutesAgoLabel(input.outbox.lastSyncedAt)}.`, "Mantener conexión o exportar eventos."));
  if (!input.pc.ok) alerts.push(alert("pc-offline", "media", "Backoffice", "PC no disponible", "La app móvil sigue leyendo Tablet si existe, pero el backoffice no respondió.", "Revisar PC cuando sea necesario gobernar inventario."));
  if (input.salesToday.tickets === 0) alerts.push(alert("no-sales", "info", "Ventas", "Aún no hay tickets hoy", "La venta del día sigue en cero o Tablet no devolvió tickets.", "Confirmar que Tablet POS esté arriba."));
  input.warnings.forEach((warning, index) => alerts.push(alert(`warning-${index}`, "info", "Configuración", "Advertencia de data-plane", warning, "Revisar variables de entorno.")));
  return alerts;
}

export function countAlerts(alerts: PrismaMobileAlert[]) {
  return { total: alerts.length, critical: alerts.filter((a) => a.severity === "critica").length, high: alerts.filter((a) => a.severity === "alta").length, medium: alerts.filter((a) => a.severity === "media").length, info: alerts.filter((a) => a.severity === "info").length };
}
