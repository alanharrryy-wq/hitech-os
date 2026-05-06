import type { TabletRuntimeSnapshot, TabletRuntimeTone } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { formatRuntimeInteger, getPendingEventsLabel } from "@/lib/tablet-runtime-snapshot/view-model";

export type TabletOperationalPriorityKey =
  | "shift_closed"
  | "connection_pending"
  | "connection_failed"
  | "connection_conflict"
  | "catalog_empty"
  | "catalog_review"
  | "stock_pressure"
  | "quiet_day";

export type TabletOperationalPriority = {
  key: TabletOperationalPriorityKey;
  title: string;
  description: string;
  href: string;
  action: string;
  tone: TabletRuntimeTone;
  weight: number;
  reasonSignals: string[];
};

function positiveInteger(value: number): number {
  return Number.isFinite(value) && value > 0 ? Math.trunc(value) : 0;
}

function pushPriority(list: TabletOperationalPriority[], priority: TabletOperationalPriority): void {
  list.push(priority);
}

function sortPriorities(list: TabletOperationalPriority[]): TabletOperationalPriority[] {
  return [...list].sort((a, b) => {
    if (b.weight !== a.weight) return b.weight - a.weight;
    return a.title.localeCompare(b.title, "es-MX");
  });
}

function buildConnectionPriorities(snapshot: TabletRuntimeSnapshot, priorities: TabletOperationalPriority[]): void {
  const pending = positiveInteger(snapshot.connection.pendingEvents);
  const failed = positiveInteger(snapshot.connection.failedEvents);
  const conflicts = positiveInteger(snapshot.connection.conflictEvents);
  const total = pending + failed + conflicts;

  if (conflicts > 0) {
    pushPriority(priorities, {
      key: "connection_conflict",
      title: "Revisar pendientes",
      description: `${formatRuntimeInteger(conflicts)} operaciones necesitan revision antes de cerrar el dia con confianza.`,
      href: snapshot.connection.actionHref,
      action: snapshot.connection.actionLabel,
      tone: "danger",
      weight: 95,
      reasonSignals: ["Hay conflictos", "La venta local sigue separada del bloqueo administrativo"]
    });
    return;
  }

  if (failed > 0) {
    pushPriority(priorities, {
      key: "connection_failed",
      title: "Revisar sincronizacion",
      description: `${formatRuntimeInteger(failed)} operaciones no se enviaron bien. La caja no debe quedarse con pendientes invisibles.`,
      href: snapshot.connection.actionHref,
      action: snapshot.connection.actionLabel,
      tone: "danger",
      weight: 88,
      reasonSignals: ["Hay envios fallidos", "Conviene revisar antes de corte"]
    });
    return;
  }

  if (total > 0) {
    pushPriority(priorities, {
      key: "connection_pending",
      title: "Pendientes por enviar",
      description: `${getPendingEventsLabel(snapshot)} esperando confirmacion. La Tablet vende, pero no conviene dejar eso como calcetin bajo la cama.`,
      href: snapshot.connection.actionHref,
      action: snapshot.connection.actionLabel,
      tone: snapshot.connection.tone,
      weight: 72,
      reasonSignals: ["Hay operaciones locales", "La conexion puede ponerse al corriente"]
    });
  }
}

function buildCatalogPriorities(snapshot: TabletRuntimeSnapshot, priorities: TabletOperationalPriority[]): void {
  const activeProducts = positiveInteger(snapshot.catalog.activeProducts);
  const lowStock = positiveInteger(snapshot.catalog.lowStockProducts);

  if (activeProducts === 0 || snapshot.catalog.state === "empty") {
    pushPriority(priorities, {
      key: "catalog_empty",
      title: "Catalogo por revisar",
      description: "No hay productos activos suficientes para vender con confianza. Sin catalogo, la caja queda como tiendita sin anaqueles.",
      href: snapshot.catalog.actionHref,
      action: snapshot.catalog.actionLabel,
      tone: "warn",
      weight: 82,
      reasonSignals: ["Catalogo sin productos activos", "Venta local necesita productos listos"]
    });
    return;
  }

  if (snapshot.catalog.state === "review" || snapshot.catalog.state === "stale") {
    pushPriority(priorities, {
      key: "catalog_review",
      title: "Catalogo por revisar",
      description: "El catalogo tiene señales que conviene validar antes de prometer productos en mostrador.",
      href: snapshot.catalog.actionHref,
      action: snapshot.catalog.actionLabel,
      tone: snapshot.catalog.tone,
      weight: 66,
      reasonSignals: ["Catalogo no esta limpio", "La venta puede seguir con cuidado"]
    });
  }

  if (lowStock > 0) {
    pushPriority(priorities, {
      key: "stock_pressure",
      title: "Existencias con presion",
      description: `${formatRuntimeInteger(lowStock)} productos tienen pocas piezas o riesgo de quiebre. Mejor verlo antes de ofrecer lo que ya casi no existe.`,
      href: "/stock",
      action: "Ver existencias",
      tone: "warn",
      weight: 64,
      reasonSignals: ["Hay stock bajo", "La venta depende de inventario local"]
    });
  }
}

function buildShiftPriorities(snapshot: TabletRuntimeSnapshot, priorities: TabletOperationalPriority[]): void {
  if (snapshot.shift.state !== "open") {
    pushPriority(priorities, {
      key: "shift_closed",
      title: "Turno cerrado",
      description: "La Tablet puede vender localmente, pero conviene abrir turno para que caja, tickets y corte queden amarrados.",
      href: snapshot.shift.actionHref,
      action: snapshot.shift.actionLabel,
      tone: snapshot.shift.tone,
      weight: 90,
      reasonSignals: ["Turno no abierto", "Caja necesita corte limpio"]
    });
  }
}

function buildQuietDayPriority(snapshot: TabletRuntimeSnapshot, priorities: TabletOperationalPriority[]): void {
  if (priorities.length > 0) return;
  if (snapshot.shift.state !== "open") return;
  if (positiveInteger(snapshot.sales.ticketsClosed) > 0) return;

  pushPriority(priorities, {
    key: "quiet_day",
    title: "Arranque limpio",
    description: "No hay alertas fuertes. La siguiente accion sana es vender y dejar que los tickets empiecen a contar la historia del dia.",
    href: "/pos",
    action: "Ir a vender",
    tone: "ok",
    weight: 20,
    reasonSignals: ["Turno abierto", "Sin pendientes criticos", "Sin ventas todavia"]
  });
}

export function buildTabletOperationalPriorities(snapshot: TabletRuntimeSnapshot): TabletOperationalPriority[] {
  const priorities: TabletOperationalPriority[] = [];
  buildShiftPriorities(snapshot, priorities);
  buildConnectionPriorities(snapshot, priorities);
  buildCatalogPriorities(snapshot, priorities);
  buildQuietDayPriority(snapshot, priorities);
  return sortPriorities(priorities).slice(0, 4);
}

export function getHighestOperationalPriority(snapshot: TabletRuntimeSnapshot): TabletOperationalPriority | null {
  return buildTabletOperationalPriorities(snapshot)[0] ?? null;
}
