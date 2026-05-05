import type { TabletRuntimeSnapshot, TabletRuntimeTone } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { formatRuntimeInteger, formatRuntimeMoney, getPendingEventsLabel, getRuntimeActionHref, getRuntimeActionLabel } from "@/lib/tablet-runtime-snapshot/view-model";
import { buildTabletOperationalPriorities } from "@/lib/tablet-home/operational-priority";

export type TabletHomeAction = {
  href: string;
  label: string;
  title: string;
  description: string;
  tone: TabletRuntimeTone;
  priority: "primary" | "secondary" | "contextual";
};

export type TabletHomeMetric = {
  label: string;
  value: string;
  note: string;
  tone: TabletRuntimeTone;
};

export type TabletHomeAlert = {
  title: string;
  description: string;
  href: string;
  action: string;
  tone: TabletRuntimeTone;
};

export type TabletHomeViewModel = {
  hero: {
    title: string;
    subtitle: string;
    primaryHref: string;
    primaryLabel: string;
    secondaryHref: string;
    secondaryLabel: string;
  };
  metrics: TabletHomeMetric[];
  actions: TabletHomeAction[];
  alerts: TabletHomeAlert[];
  checklist: Array<{ label: string; ready: boolean; note: string }>;
};

function toneForReady(ready: boolean): TabletRuntimeTone {
  return ready ? "ok" : "warn";
}

export function buildTabletHomeViewModel(snapshot: TabletRuntimeSnapshot): TabletHomeViewModel {
  const shiftOpen = snapshot.shift.state === "open";
  const hasPending = snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents > 0;
  const catalogReady = snapshot.catalog.state === "ready" || snapshot.catalog.state === "review";
  const hasStockPressure = snapshot.catalog.lowStockProducts > 0;

  const primaryHref = getRuntimeActionHref(snapshot);
  const primaryLabel = getRuntimeActionLabel(snapshot);

  const metrics: TabletHomeMetric[] = [
    {
      label: "Ventas del dia",
      value: formatRuntimeMoney(snapshot.sales.totalCents),
      note: `${formatRuntimeInteger(snapshot.sales.ticketsClosed)} tickets cerrados`,
      tone: snapshot.sales.ticketsClosed > 0 ? "ok" : "neutral"
    },
    {
      label: "Ticket promedio",
      value: formatRuntimeMoney(snapshot.sales.averageTicketCents),
      note: `${formatRuntimeInteger(snapshot.sales.unitsSold)} unidades vendidas`,
      tone: snapshot.sales.averageTicketCents > 0 ? "ok" : "neutral"
    },
    {
      label: "Pendientes",
      value: getPendingEventsLabel(snapshot),
      note: snapshot.connection.label,
      tone: snapshot.connection.tone
    },
    {
      label: "Catalogo",
      value: formatRuntimeInteger(snapshot.catalog.activeProducts),
      note: hasStockPressure ? `${formatRuntimeInteger(snapshot.catalog.lowStockProducts)} productos con pocas piezas` : snapshot.catalog.label,
      tone: snapshot.catalog.tone
    }
  ];

  const actions: TabletHomeAction[] = [
    {
      href: primaryHref,
      label: primaryLabel,
      title: shiftOpen ? "Seguir vendiendo" : "Abrir turno",
      description: shiftOpen ? "La terminal esta lista para operar ventas locales." : "Abre caja antes de arrancar ventas del turno.",
      tone: shiftOpen ? "ok" : "warn",
      priority: "primary"
    },
    {
      href: "/pos",
      label: "Ir a vender",
      title: "Vender",
      description: "Busca producto, arma ticket y manda a cobro.",
      tone: "ok",
      priority: "secondary"
    },
    {
      href: "/sales/today",
      label: "Ver tickets",
      title: "Ventas de hoy",
      description: "Consulta tickets cerrados y abre acciones sobre ventas.",
      tone: "neutral",
      priority: "secondary"
    },
    {
      href: "/stock",
      label: "Revisar stock",
      title: "Existencias",
      description: "Mira productos con pocas piezas y quiebres operativos.",
      tone: hasStockPressure ? "warn" : "neutral",
      priority: "contextual"
    }
  ];

  const alerts: TabletHomeAlert[] = buildTabletOperationalPriorities(snapshot).map((priority) => ({
    title: priority.title,
    description: priority.description,
    href: priority.href,
    action: priority.action,
    tone: priority.tone
  }));

  return {
    hero: {
      title: shiftOpen ? "Listo para vender" : "Prepara el turno",
      subtitle: shiftOpen
        ? "La Tablet tiene venta local activa, estado visible y pendientes bajo control operativo."
        : "Abre turno para que caja, tickets y corte queden limpios desde el primer cobro.",
      primaryHref,
      primaryLabel,
      secondaryHref: "/sales/today",
      secondaryLabel: "Ventas de hoy"
    },
    metrics,
    actions,
    alerts,
    checklist: [
      { label: "Turno", ready: shiftOpen, note: snapshot.shift.label },
      { label: "Conexion", ready: snapshot.connection.state !== "offline", note: snapshot.connection.label },
      { label: "Catalogo", ready: catalogReady, note: snapshot.catalog.label },
      { label: "Venta local", ready: snapshot.localSalesAllowed, note: snapshot.localSalesAllowed ? "Permitida" : "Bloqueada" },
      { label: "PC requerido", ready: !snapshot.pcRequiredForBasicSale, note: snapshot.pcRequiredForBasicSale ? "Revisar dependencia" : "No requerido" }
    ].map((item) => ({ ...item, tone: toneForReady(item.ready) }))
  };
}
