import type { TabletRuntimeSnapshot, TabletRuntimeTone } from "./shell-contract";

const MONEY_FORMATTER = new Intl.NumberFormat("es-MX", {
  style: "currency",
  currency: "MXN",
  maximumFractionDigits: 0
});

const INTEGER_FORMATTER = new Intl.NumberFormat("es-MX", {
  maximumFractionDigits: 0
});

export function formatRuntimeMoney(cents: number) {
  return MONEY_FORMATTER.format(Math.max(0, Math.round(cents)) / 100);
}

export function formatRuntimeInteger(value: number) {
  return INTEGER_FORMATTER.format(Math.max(0, Math.round(value)));
}

export function compactRuntimeDateTime(value: string | null) {
  if (!value) return "Sin hora registrada";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Hora no valida";
  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

export function getRuntimeModeLabel(snapshot: Pick<TabletRuntimeSnapshot, "mode">) {
  if (snapshot.mode === "managed") return "Operacion administrada";
  if (snapshot.mode === "degraded_managed") return "Operacion degradada";
  return "Venta autonoma";
}

export function getRuntimeHeaderLine(snapshot: TabletRuntimeSnapshot) {
  const tickets = formatRuntimeInteger(snapshot.sales.ticketsClosed);
  const total = formatRuntimeMoney(snapshot.sales.totalCents);
  return `${snapshot.identity.storeName} · ${tickets} tickets · ${total}`;
}

export function getRuntimeActionLabel(snapshot: TabletRuntimeSnapshot) {
  if (snapshot.shift.state === "closed") return "Abrir turno";
  if (snapshot.connection.state === "offline") return "Revisar conexion";
  if (snapshot.connection.pendingEvents > 0) return "Ver pendientes";
  if (snapshot.catalog.lowStockProducts > 0) return "Ver existencias";
  return "Ir a vender";
}

export function getRuntimeActionHref(snapshot: TabletRuntimeSnapshot) {
  if (snapshot.shift.state === "closed") return "/shift";
  if (snapshot.connection.state === "offline" || snapshot.connection.pendingEvents > 0) return "/sync";
  if (snapshot.catalog.lowStockProducts > 0) return "/stock";
  return "/pos";
}

export function mergeRuntimeTone(left: TabletRuntimeTone, right: TabletRuntimeTone): TabletRuntimeTone {
  const priority: Record<TabletRuntimeTone, number> = { danger: 4, warn: 3, neutral: 2, ok: 1 };
  return priority[left] >= priority[right] ? left : right;
}

export function getRuntimeOverallTone(snapshot: TabletRuntimeSnapshot): TabletRuntimeTone {
  return [snapshot.shift.tone, snapshot.connection.tone, snapshot.catalog.tone].reduce(mergeRuntimeTone, "ok" as TabletRuntimeTone);
}

export function getRuntimeOperatorLine(snapshot: TabletRuntimeSnapshot) {
  return `${snapshot.identity.operatorName} · ${snapshot.identity.terminalName}`;
}

export function getPendingEventsLabel(snapshot: TabletRuntimeSnapshot) {
  const total = snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
  if (total === 0) return "Sin pendientes";
  if (snapshot.connection.conflictEvents > 0) return "Revisar pendientes";
  if (snapshot.connection.failedEvents > 0) return "Reintentar pendientes";
  return `${formatRuntimeInteger(total)} pendientes por enviar`;
}

export function getCatalogPressureLabel(snapshot: TabletRuntimeSnapshot) {
  if (snapshot.catalog.state === "empty") return "Catalogo vacio";
  if (snapshot.catalog.lowStockProducts > 0) return `${formatRuntimeInteger(snapshot.catalog.lowStockProducts)} con pocas piezas`;
  return `${formatRuntimeInteger(snapshot.catalog.activeProducts)} productos activos`;
}

export function buildRuntimeAuditSummary(snapshot: TabletRuntimeSnapshot) {
  return {
    schemaVersion: snapshot.schemaVersion,
    generatedAt: snapshot.generatedAt,
    localSalesAllowed: snapshot.localSalesAllowed,
    pcRequiredForBasicSale: snapshot.pcRequiredForBasicSale,
    visibleState: {
      shift: snapshot.shift.label,
      connection: snapshot.connection.label,
      catalog: snapshot.catalog.label,
      pending: getPendingEventsLabel(snapshot)
    }
  };
}
