import type { MobileDataPlaneState } from "./types";

export type DataPlaneFinding = { id: string; severity: "info" | "warning" | "blocker"; title: string; detail: string; fix: string };

export function diagnoseMobileDataPlane(state: MobileDataPlaneState): DataPlaneFinding[] {
  const findings: DataPlaneFinding[] = [];
  const tabletOk = state.probes.some((probe) => probe.id === "tablet" && probe.ok);
  const pcOk = state.probes.some((probe) => probe.id === "pc" && probe.ok);
  const localOk = state.probes.some((probe) => probe.id === "local" && probe.ok);
  if (!tabletOk) findings.push({ id: "tablet-heartbeat-pending", severity: localOk ? "warning" : "blocker", title: "Heartbeat Tablet pendiente", detail: localOk ? "Mobile lee datos operativos disponibles desde fuente local." : "Mobile necesita una fuente operativa certificada para ventas e inventario.", fix: "Certificar heartbeat Tablet o revisar PRISMA_MOBILE_TABLET_ORIGIN sin tocar el proceso activo." });
  if (!pcOk) findings.push({ id: "pc-certification-pending", severity: "warning", title: "Consolidado PC pendiente", detail: "Mobile mantiene supervisión con las fuentes disponibles mientras se certifica PC.", fix: "Verificar contrato PC cuando se requiera gobierno o auditoría fina." });
  if (state.salesToday.tickets === 0) findings.push({ id: "no-tickets", severity: "info", title: "Sin tickets hoy", detail: "No hay tickets en la respuesta de ventas del día.", fix: "Cerrar una venta real desde Tablet POS o esperar la primera operación del día." });
  if (state.inventory.items.length === 0) findings.push({ id: "no-inventory", severity: "warning", title: "Inventario vacío", detail: "La watchlist no recibió SKUs.", fix: "Confirmar endpoint /api/pos/inventory/low-stock." });
  if (state.outbox.failed > 0) findings.push({ id: "outbox-failed", severity: "warning", title: "Outbox con fallos", detail: `${state.outbox.failed} eventos están fallidos.`, fix: "Revisar sync y exportación de eventos." });
  return findings;
}
