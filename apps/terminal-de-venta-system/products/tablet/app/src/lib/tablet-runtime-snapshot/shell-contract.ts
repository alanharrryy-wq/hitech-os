export type TabletRuntimeTone = "ok" | "warn" | "danger" | "neutral";

export type TabletShiftState = "open" | "closed" | "closing" | "review";
export type TabletConnectionState = "online" | "offline" | "pending" | "review";
export type TabletCatalogState = "ready" | "empty" | "stale" | "review";
export type TabletRuntimeModeVisible = "standalone" | "managed" | "degraded_managed";

export type TabletRuntimeIdentity = {
  businessId: string;
  businessName: string;
  storeName: string;
  terminalId: string;
  terminalName: string;
  operatorId: string;
  operatorName: string;
};

export type TabletRuntimeShift = {
  state: TabletShiftState;
  label: string;
  tone: TabletRuntimeTone;
  openedAt: string | null;
  cashSessionId: string | null;
  actionHref: string;
  actionLabel: string;
};

export type TabletRuntimeConnection = {
  state: TabletConnectionState;
  label: string;
  tone: TabletRuntimeTone;
  pendingEvents: number;
  failedEvents: number;
  conflictEvents: number;
  actionHref: string;
  actionLabel: string;
};

export type TabletRuntimeCatalog = {
  state: TabletCatalogState;
  label: string;
  tone: TabletRuntimeTone;
  activeProducts: number;
  lowStockProducts: number;
  inactiveProducts: number;
  lastMovementAt: string | null;
  actionHref: string;
  actionLabel: string;
};

export type TabletRuntimeSales = {
  date: string;
  ticketsClosed: number;
  totalCents: number;
  unitsSold: number;
  averageTicketCents: number;
};

export type TabletRuntimeCapability = {
  key: string;
  label: string;
  enabled: boolean;
  reason: string;
};

export type TabletRuntimeSnapshot = {
  schemaVersion: "tablet-runtime-snapshot.03b";
  generatedAt: string;
  mode: TabletRuntimeModeVisible;
  localSalesAllowed: true;
  pcRequiredForBasicSale: false;
  identity: TabletRuntimeIdentity;
  shift: TabletRuntimeShift;
  connection: TabletRuntimeConnection;
  catalog: TabletRuntimeCatalog;
  sales: TabletRuntimeSales;
  capabilities: TabletRuntimeCapability[];
  warnings: string[];
};

export const DEFAULT_TABLET_RUNTIME_SNAPSHOT: TabletRuntimeSnapshot = {
  schemaVersion: "tablet-runtime-snapshot.03b",
  generatedAt: "1970-01-01T00:00:00.000Z",
  mode: "standalone",
  localSalesAllowed: true,
  pcRequiredForBasicSale: false,
  identity: {
    businessId: "biz_tablet_standalone",
    businessName: "PRISMA Local",
    storeName: "Tienda principal",
    terminalId: "terminal_tablet_local_01",
    terminalName: "Terminal local",
    operatorId: "tablet-cashier",
    operatorName: "Operador"
  },
  shift: {
    state: "closed",
    label: "Turno cerrado",
    tone: "warn",
    openedAt: null,
    cashSessionId: null,
    actionHref: "/shift",
    actionLabel: "Abrir turno"
  },
  connection: {
    state: "online",
    label: "En linea",
    tone: "ok",
    pendingEvents: 0,
    failedEvents: 0,
    conflictEvents: 0,
    actionHref: "/sync",
    actionLabel: "Ver pendientes"
  },
  catalog: {
    state: "ready",
    label: "Catalogo listo",
    tone: "ok",
    activeProducts: 0,
    lowStockProducts: 0,
    inactiveProducts: 0,
    lastMovementAt: null,
    actionHref: "/catalog",
    actionLabel: "Ver catalogo"
  },
  sales: {
    date: "1970-01-01",
    ticketsClosed: 0,
    totalCents: 0,
    unitsSold: 0,
    averageTicketCents: 0
  },
  capabilities: [
    { key: "local_sale", label: "Venta local", enabled: true, reason: "La Tablet puede vender aunque PC no este disponible." },
    { key: "local_catalog", label: "Catalogo local", enabled: true, reason: "La busqueda usa los productos locales de la terminal." },
    { key: "pending_events", label: "Pendientes visibles", enabled: true, reason: "Los eventos pendientes se muestran sin lenguaje tecnico." }
  ],
  warnings: []
};
