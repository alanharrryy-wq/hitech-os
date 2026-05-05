import type { MobileDataPlaneState } from "./types";

export type DataPlaneFinding = { id: string; severity: "info" | "warning" | "blocker"; title: string; detail: string; fix: string };

export function diagnoseMobileDataPlane(state: MobileDataPlaneState): DataPlaneFinding[] {
  const findings: DataPlaneFinding[] = [];
  const tabletOk = state.probes.some((probe) => probe.id === "tablet" && probe.ok);
  const pcOk = state.probes.some((probe) => probe.id === "pc" && probe.ok);
  if (!tabletOk) findings.push({ id: "tablet-unreachable", severity: "blocker", title: "Tablet POS no respondió", detail: "La app móvil no puede ver ventas ni inventario operativo.", fix: "Levantar Tablet en 3120 o ajustar PRISMA_MOBILE_TABLET_ORIGIN." });
  if (!pcOk) findings.push({ id: "pc-unreachable", severity: "warning", title: "PC Backoffice no respondió", detail: "La app móvil puede operar como supervisor de Tablet, pero pierde consolidado/backoffice.", fix: "Levantar PC en 3130 o ajustar PRISMA_MOBILE_PC_ORIGIN." });
  if (state.salesToday.tickets === 0) findings.push({ id: "no-tickets", severity: "info", title: "Sin tickets hoy", detail: "No hay tickets en la respuesta de ventas del día.", fix: "Hacer una venta de prueba real desde Tablet POS." });
  if (state.inventory.items.length === 0) findings.push({ id: "no-inventory", severity: "warning", title: "Inventario vacío", detail: "La watchlist no recibió SKUs.", fix: "Confirmar endpoint /api/pos/inventory/low-stock." });
  if (state.outbox.failed > 0) findings.push({ id: "outbox-failed", severity: "warning", title: "Outbox con fallos", detail: `${state.outbox.failed} eventos están fallidos.`, fix: "Revisar sync y exportación de eventos." });
  return findings;
}
