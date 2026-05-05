import type { MobileDataPlaneState } from "./types";
import { minutesAgoLabel } from "./money";

export type MobileDataReadinessLevel = "ready" | "partial" | "empty" | "offline" | "blocked";

export type MobileDataReadinessAction = {
  title: string;
  detail: string;
  owner: string;
  priority: "alta" | "media" | "baja";
};

export type MobileDataReadinessReport = {
  level: MobileDataReadinessLevel;
  label: string;
  headline: string;
  detail: string;
  sourceSummary: string;
  salesState: "with_sales" | "empty" | "unavailable";
  inventoryState: "with_items" | "empty" | "unavailable";
  pcState: "connected" | "unavailable";
  syncState: "clean" | "pending" | "failed" | "unknown";
  facts: string[];
  actions: MobileDataReadinessAction[];
};

function upstreamOk(state: MobileDataPlaneState, id: "tablet" | "pc"): boolean {
  return state.probes.some((probe) => probe.id === id && probe.ok);
}

function readableSourceSummary(state: MobileDataPlaneState): string {
  const tablet = upstreamOk(state, "tablet") ? "Tablet conectada" : "Tablet sin respuesta";
  const pc = upstreamOk(state, "pc") ? "PC conectada" : "PC sin respuesta";
  const mode = state.runtimeMode === "connected" ? "lectura completa" : state.runtimeMode === "partial" ? "lectura parcial" : "sin fuentes activas";
  return `${tablet} · ${pc} · ${mode}`;
}

function addOnce(target: string[], value: string): void {
  if (!target.includes(value)) target.push(value);
}

function classifySync(state: MobileDataPlaneState): MobileDataReadinessReport["syncState"] {
  if (state.outbox.failed > 0) return "failed";
  if (state.outbox.pending > 0) return "pending";
  if (!state.outbox.lastSyncedAt && state.runtimeMode === "offline") return "unknown";
  return "clean";
}

export function deriveMobileDataReadiness(state: MobileDataPlaneState): MobileDataReadinessReport {
  const facts: string[] = [];
  const actions: MobileDataReadinessAction[] = [];
  const tabletAvailable = upstreamOk(state, "tablet");
  const pcAvailable = upstreamOk(state, "pc");
  const salesState: MobileDataReadinessReport["salesState"] = tabletAvailable ? (state.salesToday.tickets > 0 ? "with_sales" : "empty") : "unavailable";
  const inventoryState: MobileDataReadinessReport["inventoryState"] = tabletAvailable ? (state.inventory.items.length > 0 ? "with_items" : "empty") : "unavailable";
  const pcState: MobileDataReadinessReport["pcState"] = pcAvailable ? "connected" : "unavailable";
  const syncState = classifySync(state);

  if (salesState === "with_sales") addOnce(facts, `${state.salesToday.tickets} tickets cerrados hoy`);
  if (salesState === "empty") addOnce(facts, "Tablet respondió, pero todavía no hay ventas cerradas hoy");
  if (salesState === "unavailable") addOnce(facts, "Ventas no disponibles porque Tablet POS no respondió");

  if (inventoryState === "with_items") addOnce(facts, `${state.inventory.items.length} SKUs en watchlist operativa`);
  if (inventoryState === "empty") addOnce(facts, "Inventario operativo sin SKUs recibidos");
  if (inventoryState === "unavailable") addOnce(facts, "Inventario no disponible porque Tablet POS no respondió");

  if (pcState === "connected") addOnce(facts, "Backoffice disponible para lectura consolidada");
  else addOnce(facts, "Backoffice no disponible; la lectura móvil queda centrada en Tablet/local");

  if (syncState === "failed") addOnce(facts, `${state.outbox.failed} eventos de sync fallidos`);
  if (syncState === "pending") addOnce(facts, `${state.outbox.pending} eventos pendientes de sync`);
  if (syncState === "clean") addOnce(facts, `Sync sin pendientes críticos · ${minutesAgoLabel(state.outbox.lastSyncedAt)}`);
  if (syncState === "unknown") addOnce(facts, "Sync sin confirmación reciente");

  if (!tabletAvailable) {
    actions.push({ title: "Levantar Tablet POS", detail: "Sin Tablet no hay ventas, stock operativo ni outbox confiable para la app móvil.", owner: "Operación", priority: "alta" });
  }
  if (tabletAvailable && state.salesToday.tickets === 0) {
    actions.push({ title: "Confirmar primera venta real", detail: "La lectura está conectada, pero todavía no existe ticket cerrado hoy.", owner: "Caja", priority: "media" });
  }
  if (tabletAvailable && state.inventory.items.length === 0) {
    actions.push({ title: "Confirmar endpoint de inventario", detail: "La app no recibió SKUs para watchlist; revisa stock bajo o catálogo local.", owner: "Inventario", priority: "media" });
  }
  if (!pcAvailable) {
    actions.push({ title: "Revisar PC Backoffice", detail: "No bloquea la lectura de Tablet, pero sí limita comparación, gobierno y consolidado.", owner: "Backoffice", priority: "baja" });
  }
  if (state.outbox.failed > 0) {
    actions.push({ title: "Resolver eventos fallidos", detail: "Hay eventos que no llegaron limpios; conviene exportar o reintentar sync.", owner: "Sincronización", priority: "alta" });
  } else if (state.outbox.pending > 0) {
    actions.push({ title: "Mantener conexión para sync", detail: "Hay eventos pendientes; no es incendio, pero tampoco decoración.", owner: "Sincronización", priority: "media" });
  }
  if (actions.length === 0) {
    actions.push({ title: "Revisión normal de cierre", detail: "Fuentes conectadas y sin pendientes críticos visibles.", owner: "Dueño / encargado", priority: "baja" });
  }

  const empty = tabletAvailable && state.salesToday.tickets === 0 && state.inventory.items.length === 0;
  const attention = state.outbox.failed > 0 || state.inventory.critical > 0;
  const partial = state.runtimeMode === "partial" || !pcAvailable || state.warnings.length > 0;
  const level: MobileDataReadinessLevel = !tabletAvailable
    ? state.runtimeMode === "offline" ? "offline" : "blocked"
    : empty
      ? "empty"
      : attention || partial
        ? "partial"
        : "ready";

  const labels: Record<MobileDataReadinessLevel, string> = {
    ready: "Datos listos",
    partial: "Lectura parcial",
    empty: "Esperando operación",
    offline: "Sin fuentes activas",
    blocked: "Fuente clave pendiente"
  };
  const headlines: Record<MobileDataReadinessLevel, string> = {
    ready: "La app ya tiene lectura operativa confiable.",
    partial: "La app sirve para decidir, pero hay una fuente o señal por revisar.",
    empty: "PRISMA en línea. Tu negocio ya responde.",
    offline: "La app no tiene fuentes activas en este momento.",
    blocked: "Tablet POS es necesaria para alimentar ventas e inventario móvil."
  };
  const details: Record<MobileDataReadinessLevel, string> = {
    ready: "Ventas, inventario y salud de sync llegan sin señales críticas.",
    partial: "La información visible separa datos reales, vacíos operativos y fuentes caídas para no vender humo con corbata.",
    empty: "Aún no hay ventas registradas. Cuando Tablet cierre tickets, el resumen aparecerá aquí.",
    offline: "Muestra estado honesto y acciones claras en lugar de rellenar con datos inventados.",
    blocked: "Primero hay que recuperar Tablet POS o configurar PRISMA_MOBILE_TABLET_ORIGIN."
  };

  return {
    level,
    label: labels[level],
    headline: headlines[level],
    detail: details[level],
    sourceSummary: readableSourceSummary(state),
    salesState,
    inventoryState,
    pcState,
    syncState,
    facts: facts.slice(0, 5),
    actions: actions.slice(0, 4)
  };
}
