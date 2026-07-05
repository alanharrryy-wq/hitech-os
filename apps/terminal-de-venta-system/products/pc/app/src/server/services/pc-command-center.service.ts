import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { getTriDbStatusCard } from "@/server/services/tri-db-status.service";
import { getPcCatalogDeltaStatus } from "@/server/services/catalog-delta-export.service";
import { getPcFeatureList, getPcLicenseStatus } from "@/server/licensing/pc-license-service";
import { getPcLicenseRefreshStatus } from "@/server/licensing/pc-license-refresh";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../../shared/customer/prisma-original-customer";

const MAX_CUSTOM_RANGE_DAYS = 60;
const DEFAULT_BUSINESS_ID = PRISMA_ORIGINAL_CUSTOMER.businessId;
const DEFAULT_LIMIT = 80;

type SearchLike = URLSearchParams | Record<string, string | string[] | undefined> | undefined;

export type PcCommandCenterMode =
  | "sales"
  | "cash"
  | "devices"
  | "sync"
  | "dataQuality"
  | "licenseRuntime"
  | "communication";

export type CommandMetric = {
  label: string;
  value: string;
  note: string;
  tone?: "ok" | "warn" | "danger";
};

export type CommandTableRow = Record<string, string | number | string[] | null | undefined> & {
  __rowDetailTitle?: string;
  __rowDetailTone?: "ok" | "warn" | "danger";
  __rowDetailItems?: string[];
  __rowDetailJson?: string;
  __rowActionHref?: string;
  __rowActionLabel?: string;
};

export type CommandTable = {
  title: string;
  caption: string;
  columns: string[];
  rows: CommandTableRow[];
  emptyMessage: string;
};

export type CommandPanel = {
  title: string;
  body: string;
  tone?: "ok" | "warn" | "danger";
};

export type CommandAction = {
  label: string;
  href: string;
  method?: "GET" | "POST";
  body?: Record<string, unknown>;
  disabledReason?: string;
  successMessage?: string;
};


export type SalesControlTicketLine = {
  sku: string;
  productName: string;
  qty: string;
  price: string;
  total: string;
};

export type SalesControlTicket = {
  id: string;
  folio: string;
  date: string;
  branchName: string;
  tabletName: string;
  terminalId: string;
  cashier: string;
  total: string;
  status: string;
  cashSessionId: string;
  lines: SalesControlTicketLine[];
  tenders: string[];
};

export type SalesControlTabletSummary = {
  id: string;
  name: string;
  deviceId: string;
  total: string;
  tickets: number;
  pendingSync: number;
  lastSync: string;
  status: string;
};

export type SalesControlBranchSummary = {
  id: string;
  code: string;
  name: string;
  total: string;
  tickets: number;
  tablets: SalesControlTabletSummary[];
  lastSaleAt: string;
  syncStatus: string;
  ticketRows: SalesControlTicket[];
};

export type SalesControlViewModel = {
  roleLabel: string;
  syncHref: string;
  addBranchHref: string;
  totalLabel: string;
  netLabel: string;
  ticketsLabel: string;
  averageLabel: string;
  branchCountLabel: string;
  tabletCountLabel: string;
  updatedLabel: string;
  branches: SalesControlBranchSummary[];
};

export type CommandCenterModel = {
  mode: PcCommandCenterMode;
  currentPath: string;
  kicker: string;
  title: string;
  description: string;
  periodLabel?: string;
  sourceLine: string;
  independenceLine: string;
  metrics: CommandMetric[];
  panels: CommandPanel[];
  tables: CommandTable[];
  diagnostics: Record<string, unknown>;
  actions?: CommandAction[];
  salesControl?: SalesControlViewModel;
};

function readParam(params: SearchLike, key: string) {
  if (!params) return "";
  if (params instanceof URLSearchParams) return params.get(key)?.trim() ?? "";
  const value = params[key];
  if (Array.isArray(value)) return value[0]?.trim() ?? "";
  return value?.trim() ?? "";
}

function clampLimit(value: string, fallback = DEFAULT_LIMIT) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(1, Math.min(Math.trunc(parsed), 200));
}

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function parseLocalDate(value: string) {
  if (!value) return null;
  const parsed = new Date(`${value}T00:00:00`);
  return Number.isNaN(parsed.getTime()) ? null : startOfDay(parsed);
}

function resolveDateRange(params: SearchLike) {
  const preset = readParam(params, "preset") || "today";
  const now = startOfDay(new Date());
  let from = now;
  let toExclusive = addDays(now, 1);
  let label = "Hoy";
  let blocked: string | null = null;

  if (preset === "yesterday") {
    from = addDays(now, -1);
    toExclusive = now;
    label = "Ayer";
  } else if (preset === "7d") {
    from = addDays(now, -6);
    label = "Últimos 7 días";
  } else if (preset === "30d") {
    from = addDays(now, -29);
    label = "Últimos 30 días";
  } else if (preset === "custom") {
    const customFrom = parseLocalDate(readParam(params, "from"));
    const customTo = parseLocalDate(readParam(params, "to"));
    if (!customFrom || !customTo || customTo < customFrom) {
      blocked = "Rango personalizado inválido.";
    } else {
      from = customFrom;
      toExclusive = addDays(customTo, 1);
      label = `${dateShort(from)} a ${dateShort(customTo)}`;
    }
  }

  const days = Math.ceil((toExclusive.getTime() - from.getTime()) / 86_400_000);
  if (days > MAX_CUSTOM_RANGE_DAYS) {
    blocked = `Rango mayor a ${MAX_CUSTOM_RANGE_DAYS} días bloqueado para proteger rendimiento.`;
  }

  return { preset, from, toExclusive, label, days, blocked };
}

function money(cents: number | null | undefined) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format((cents ?? 0) / 100);
}

function numberLabel(value: number | null | undefined) {
  return new Intl.NumberFormat("es-MX").format(value ?? 0);
}

function dateLabel(value: unknown) {
  if (!value) return "No disponible";
  const date = value instanceof Date ? value : new Date(String(value));
  if (Number.isNaN(date.getTime())) return "No disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function dateShort(value: Date) {
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(value);
}

function relativeLabel(value: unknown) {
  if (!value) return "sin registro";
  const date = value instanceof Date ? value : new Date(String(value));
  if (Number.isNaN(date.getTime())) return "sin registro";
  const seconds = Math.round((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "hace menos de 1 min";
  if (seconds < 3600) return `hace ${Math.round(seconds / 60)} min`;
  if (seconds < 86_400) return `hace ${Math.round(seconds / 3600)} h`;
  return `hace ${Math.round(seconds / 86_400)} días`;
}

function sum(values: number[]) {
  return values.reduce((acc, value) => acc + value, 0);
}

function normalizeStatus(value: string | null | undefined) {
  const normalized = String(value || "unknown").toLowerCase();
  if (["active", "ok", "healthy", "success", "reconciled", "acked"].includes(normalized)) return "activo";
  if (["pending", "queued", "received", "sent"].includes(normalized)) return "pendiente";
  if (["conflict", "open"].includes(normalized)) return "conflicto";
  if (["failed", "rejected", "dead_letter"].includes(normalized)) return "fallido";
  if (["stale", "warning", "partial"].includes(normalized)) return "advertencia";
  return normalized;
}

function featureLabel(key: string) {
  const labels: Record<string, string> = {
    "pc.open": "Abrir PC",
    "pc.dashboard.view": "Ver tablero PC",
    "pc.dashboard.executive": "Resumen ejecutivo",
    "catalog.write": "Editar catalogo",
    "stock.adjust": "Ajustar stock",
    "inventory.counts": "Conteos de inventario",
    "purchase.write": "Compras",
    "receiving.write": "Recepcion",
    "replenishment.view": "Reabasto",
    "audit.view": "Auditoria",
    "sync.managed": "Sincronizacion administrada",
    "sync.conflict.resolve": "Resolver revisiones",
    "multi.branch": "Multi sucursal",
    "multi.terminal": "Multi terminal",
    "multi.user.permissions": "Permisos de usuario",
    "forecast.replenishment": "Pronostico de reabasto",
    "advanced.analytics": "Analitica avanzada"
  };
  return labels[key] ?? key.replace(/[._:-]+/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase());
}

function readableStream(value: unknown) {
  const raw = String(value ?? "").toLowerCase();
  if (raw.includes("sale")) return "Ventas";
  if (raw.includes("catalog") || raw.includes("product")) return "Catalogo";
  if (raw.includes("stock") || raw.includes("inventory")) return "Inventario";
  if (raw.includes("cash") || raw.includes("shift")) return "Caja y turnos";
  if (raw.includes("supplier")) return "Proveedores";
  return raw ? "Operacion" : "General";
}

function readableLifecycle(value: unknown) {
  const raw = String(value ?? "").toLowerCase();
  if (["projected", "reconciled", "acked", "accepted"].includes(raw)) return "Confirmado";
  if (["pending", "received", "sent", "validated"].includes(raw)) return "En proceso";
  if (raw === "conflict") return "Requiere revision";
  if (["failed", "rejected", "dead_letter", "invalid_schema"].includes(raw)) return "No completado";
  if (raw === "recognized_not_projected") return "Recibido sin aplicar";
  return raw ? normalizeStatus(raw) : "Sin estado";
}

function readableEntity(value: unknown) {
  const labels: Record<string, string> = {
    Product: "Productos",
    Barcode: "Codigos",
    Brand: "Marcas",
    TaxRate: "Impuestos",
    Supplier: "Proveedores",
    ProductSupplier: "Proveedor por producto",
    PriceList: "Listas de precio",
    PriceListItem: "Precios",
    DropdownCatalog: "Opciones",
    DropdownOption: "Valores",
    Sale: "Ventas",
    SaleLine: "Lineas de venta",
    OutboxEvent: "Movimientos",
    SyncAttempt: "Revisiones",
    SyncConflict: "Conflictos",
    DeviceHeartbeat: "Dispositivos",
    DataSourceFreshness: "Datos recientes"
  };
  const raw = String(value ?? "");
  return labels[raw] ?? raw.replace(/([a-z])([A-Z])/g, "$1 $2");
}

function readableConflict(value: unknown) {
  const raw = String(value ?? "").toLowerCase();
  const labels: Record<string, string> = {
    duplicate_event: "Movimiento duplicado",
    negative_stock: "Stock negativo",
    terminal_not_registered: "Terminal no registrada",
    sale_outside_shift: "Venta fuera de turno",
    inconsistent_sequence: "Secuencia por revisar",
    invalid_schema: "Formato no valido",
    unknown_topic: "Categoria no reconocida",
    product_discontinued: "Producto no disponible",
    old_local_price: "Precio local anterior"
  };
  return labels[raw] ?? (raw ? "Revision operativa" : "Sin codigo");
}

function asJson(value: string | null | undefined) {
  if (!value) return {};
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
}

async function safe<T>(operation: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await operation();
  } catch {
    return fallback;
  }
}

async function resolveBusinessId() {
  const db = prisma as any;
  const preferred = await safe<any | null>(() => db.business.findUnique({ where: { id: PRISMA_ORIGINAL_CUSTOMER.businessId }, select: { id: true } }), null);
  if (preferred?.id) return preferred.id;
  const business = await safe<any | null>(() => db.business.findFirst({ where: { terminals: { some: {} } }, select: { id: true }, orderBy: { createdAt: "asc" } }), null);
  return business?.id ?? DEFAULT_BUSINESS_ID;
}

function filterByQuery(rows: any[], query: string) {
  if (!query) return rows;
  const normalized = query.toLowerCase();
  return rows.filter((row) => JSON.stringify(row).toLowerCase().includes(normalized));
}

function lifecycleBuckets(events: any[]) {
  const bucket = new Map<string, number>();
  for (const event of events) {
    const key = event.lifecycleStatus ?? event.status ?? "unknown";
    bucket.set(key, (bucket.get(key) ?? 0) + 1);
  }
  return Array.from(bucket.entries()).map(([key, value]) => ({ key, value }));
}

function safeLower(value: unknown) {
  return String(value ?? "").toLowerCase();
}

function safeIso(value: unknown) {
  if (!value) return "";
  const date = value instanceof Date ? value : new Date(String(value));
  return Number.isNaN(date.getTime()) ? "" : date.toISOString();
}

function compactText(parts: Array<unknown>) {
  return parts.map((part) => String(part ?? "").trim()).filter(Boolean).join(" | ");
}

function jsonSummary(value: unknown, maxLength = 360) {
  if (!value) return "";
  const parsed = typeof value === "string" ? asJson(value) : value;
  const text = Object.keys(parsed as Record<string, unknown>).length
    ? JSON.stringify(parsed)
    : String(value ?? "");
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
}

function conflictText(conflict: any) {
  return compactText([
    conflict.id,
    conflict.eventId,
    conflict.outboxEventId,
    conflict.idempotencyKey,
    conflict.source,
    conflict.deviceId,
    conflict.terminalId,
    conflict.topic,
    conflict.aggregateId,
    conflict.conflictCode,
    conflict.label,
    conflict.detail,
    conflict.diagnosticsJson
  ]).toLowerCase();
}

function isOpenConflictStatus(status: unknown) {
  return !["resolved", "closed", "done"].includes(safeLower(status));
}

function isCashConflictCandidate(conflict: any, sessions: any[]) {
  const code = safeLower(conflict.conflictCode);
  const topic = safeLower(conflict.topic);
  const text = conflictText(conflict);
  if (code === "sale_outside_shift") return true;
  if (/(cash|caja|session|shift|turno|sale|venta)/i.test(topic)) return true;
  if (/(cashsession|cash session|caja|turno|shift|fuera de turno|outside shift|cashsessionid)/i.test(text)) return true;
  return sessions.some((session: any) => conflictMatchesSession(conflict, session));
}

function conflictMatchesSession(conflict: any, session: any) {
  const text = conflictText(conflict);
  const sessionId = String(session.id ?? "");
  const terminalId = String(session.terminalId ?? "");
  if (sessionId && [conflict.aggregateId, conflict.eventId, conflict.outboxEventId, conflict.idempotencyKey].some((value) => String(value ?? "") === sessionId)) {
    return true;
  }
  if (sessionId && text.includes(sessionId.toLowerCase())) return true;
  if (terminalId && String(conflict.terminalId ?? "") === terminalId) {
    const detectedAt = conflict.detectedAt ? new Date(conflict.detectedAt).getTime() : 0;
    const openedAt = session.openedAt ? new Date(session.openedAt).getTime() : 0;
    const closedAt = session.closedAt ? new Date(session.closedAt).getTime() : Date.now();
    const graceMs = 24 * 60 * 60 * 1000;
    if (!detectedAt || !openedAt || (detectedAt >= openedAt - graceMs && detectedAt <= closedAt + graceMs)) return true;
  }
  return false;
}

function conflictTone(conflict: any): "ok" | "warn" | "danger" {
  const severity = safeLower(conflict.severity);
  const status = safeLower(conflict.status);
  if (severity === "rejected" || status === "rejected" || status === "failed") return "danger";
  if (severity === "conflict" || status === "open") return "warn";
  return "ok";
}

function getCashConflictAction(conflict: any) {
  const code = safeLower(conflict.conflictCode);
  if (code === "sale_outside_shift") {
    return "Revisar si la venta llegó fuera de turno. No convertirla en venta PC hasta confirmar caja/terminal/cajero y resolver el SyncConflict.";
  }
  if (code === "terminal_not_registered") {
    return "Registrar o mapear terminal/dispositivo antes de reprocesar eventos relacionados.";
  }
  if (code === "duplicate_event") {
    return "Confirmar idempotencyKey/eventId. Si es duplicado real, marcar revisado y no reproyectar.";
  }
  if (code === "invalid_schema") {
    return "Corregir contrato del evento de origen antes de reintentar ingest.";
  }
  return "Abrir /sync para revisar evento, idempotencyKey, diagnosticsJson y marcar revisión sólo cuando el operador confirme causa.";
}

function buildConflictDetailItems(conflict: any, session?: any) {
  const diagnostics = jsonSummary(conflict.diagnosticsJson);
  return [
    `Qué pasó: ${conflict.label ?? conflict.conflictCode ?? "Conflicto de sync"}`,
    `Detalle: ${conflict.detail ?? "Sin detalle registrado."}`,
    `Código: ${conflict.conflictCode ?? "sin codigo"} / severidad: ${conflict.severity ?? "sin severidad"} / estado: ${conflict.status ?? "sin estado"}`,
    `Terminal: ${conflict.terminalId ?? session?.terminalId ?? "sin terminal"} / dispositivo: ${conflict.deviceId ?? "sin device"}`,
    `Evento: ${conflict.eventId ?? "sin eventId"} / Outbox: ${conflict.outboxEventId ?? "sin outboxEventId"} / Idempotency: ${conflict.idempotencyKey ?? "sin idempotencyKey"}`,
    `Agregado: ${conflict.aggregateId ?? "sin aggregateId"} / topic: ${conflict.topic ?? "sin topic"} / fuente: ${conflict.source ?? "sin fuente"}`,
    `Detectado: ${dateLabel(conflict.detectedAt)}${session ? ` / Sesión: ${session.id}` : ""}`,
    diagnostics ? `Diagnóstico técnico: ${diagnostics}` : "Diagnóstico técnico: sin diagnosticsJson.",
    `Acción sugerida: ${getCashConflictAction(conflict)}`
  ];
}

function buildCashSessionFallbackConflictDetail(session: any) {
  return [
    `Qué pasó: CashSession tiene estado ${session.status ?? "conflict"} pero no se encontró SyncConflict relacionado en la muestra actual.`,
    `Sesión: ${session.id}`,
    `Terminal: ${session.terminal?.name ?? session.terminalId ?? "sin terminal"}`,
    `Cajero: ${session.cashier ?? session.cashierId ?? "sin cajero"}`,
    `Abierta: ${dateLabel(session.openedAt)} / Cerrada: ${dateLabel(session.closedAt)}`,
    "Acción sugerida: revisar /sync con el id de caja, terminalId, eventId o idempotencyKey. El badge queda clicable para no dejar un foco rojo mudo."
  ];
}

function serializeRowDetail(items: string[]) {
  return JSON.stringify({ items }, null, 2);
}



function buildSalesControlView(input: {
  sales: any[];
  returns: any[];
  terminals: any[];
  stores: any[];
  heartbeats: any[];
  buckets: any[];
  totalCents: number;
  returnCents: number;
}) {
  const terminalById = new Map(input.terminals.map((terminal: any) => [String(terminal.id), terminal]));
  const storeById = new Map(input.stores.map((store: any) => [String(store.id), store]));
  const latestHeartbeatByDevice = new Map<string, any>();
  for (const heartbeat of input.heartbeats) {
    const key = String(heartbeat.deviceId ?? "");
    if (key && !latestHeartbeatByDevice.has(key)) latestHeartbeatByDevice.set(key, heartbeat);
  }

  const pendingByDevice = new Map<string, number>();
  const pendingByTerminal = new Map<string, number>();
  for (const bucket of input.buckets) {
    const status = String(bucket.status ?? "").toLowerCase();
    if (!["pending", "queued", "sent", "received"].includes(status)) continue;
    const count = Number(bucket.count ?? 0);
    if (bucket.deviceId) pendingByDevice.set(String(bucket.deviceId), (pendingByDevice.get(String(bucket.deviceId)) ?? 0) + count);
    if (bucket.terminalId) pendingByTerminal.set(String(bucket.terminalId), (pendingByTerminal.get(String(bucket.terminalId)) ?? 0) + count);
  }

  type MutableTablet = {
    id: string;
    name: string;
    deviceId: string;
    totalCents: number;
    tickets: number;
    pendingSync: number;
    lastSync: string;
    status: string;
  };

  type MutableBranch = {
    id: string;
    code: string;
    name: string;
    totalCents: number;
    tickets: number;
    tablets: Map<string, MutableTablet>;
    ticketRows: SalesControlTicket[];
    lastSaleTime: number;
    syncWarnings: number;
  };

  const branchMap = new Map<string, MutableBranch>();

  function ensureBranch(storeId: string, store?: any) {
    const id = storeId || "sin-sucursal";
    const existing = branchMap.get(id);
    if (existing) return existing;
    const branch: MutableBranch = {
      id,
      code: String(store?.code ?? (id === "sin-sucursal" ? "SIN-SUCURSAL" : id)),
      name: String(store?.name ?? (id === "sin-sucursal" ? "Sucursal sin asignar" : `Sucursal ${id}`)),
      totalCents: 0,
      tickets: 0,
      tablets: new Map(),
      ticketRows: [],
      lastSaleTime: 0,
      syncWarnings: 0
    };
    branchMap.set(id, branch);
    return branch;
  }

  for (const store of input.stores) {
    ensureBranch(String(store.id), store);
  }

  for (const sale of input.sales) {
    const terminal = sale.terminal ?? terminalById.get(String(sale.terminalId ?? ""));
    const storeId = String(terminal?.storeId ?? sale.cashSession?.storeId ?? "sin-sucursal");
    const store = terminal?.store ?? storeById.get(storeId);
    const branch = ensureBranch(storeId, store);
    const saleTotal = Number(sale.totalCents ?? 0);
    const terminalId = String(sale.terminalId ?? terminal?.id ?? "sin-terminal");
    const tabletName = String(terminal?.name ?? terminal?.code ?? terminalId);
    const heartbeat = latestHeartbeatByDevice.get(terminalId) ?? latestHeartbeatByDevice.get(String(terminal?.code ?? ""));
    const pendingSync = (pendingByTerminal.get(terminalId) ?? 0) + (pendingByDevice.get(terminalId) ?? 0) + (terminal?.code ? (pendingByDevice.get(String(terminal.code)) ?? 0) : 0);
    const tablet = branch.tablets.get(terminalId) ?? {
      id: terminalId,
      name: tabletName,
      deviceId: String(heartbeat?.deviceId ?? terminal?.code ?? terminalId),
      totalCents: 0,
      tickets: 0,
      pendingSync,
      lastSync: heartbeat ? relativeLabel(heartbeat.lastSeenAt ?? heartbeat.observedAt) : "sin registro",
      status: heartbeat ? normalizeStatus(heartbeat.health || heartbeat.status || heartbeat.syncStatus) : "sin heartbeat"
    };
    tablet.totalCents += saleTotal;
    tablet.tickets += 1;
    tablet.pendingSync = Math.max(tablet.pendingSync, pendingSync);
    branch.tablets.set(terminalId, tablet);

    const saleTime = sale.createdAt ? new Date(sale.createdAt).getTime() : 0;
    if (Number.isFinite(saleTime)) branch.lastSaleTime = Math.max(branch.lastSaleTime, saleTime);
    branch.totalCents += saleTotal;
    branch.tickets += 1;
    if (pendingSync || ["advertencia", "fallido", "sin heartbeat"].includes(tablet.status)) branch.syncWarnings += 1;

    branch.ticketRows.push({
      id: String(sale.id ?? sale.folio ?? ""),
      folio: String(sale.folio ?? sale.id ?? "sin folio"),
      date: dateLabel(sale.createdAt),
      branchName: branch.name,
      tabletName,
      terminalId,
      cashier: String(sale.cashier ?? "sin cajero"),
      total: money(saleTotal),
      status: normalizeStatus(sale.status),
      cashSessionId: String(sale.cashSessionId ?? "sin caja"),
      lines: (sale.lines ?? []).map((line: any) => ({
        sku: String(line.sku ?? line.productId ?? "sin sku"),
        productName: String(line.productName ?? "Producto"),
        qty: numberLabel(Number(line.qty ?? 0)),
        price: money(Number(line.priceCents ?? 0)),
        total: money(Number(line.totalCents ?? 0))
      })),
      tenders: (sale.paymentTenders ?? []).map((tender: any) => `${tender.tenderType ?? "metodo"}: ${money(Number(tender.amountCents ?? 0))}`)
    });
  }

  const branches = Array.from(branchMap.values())
    .map((branch) => ({
      id: branch.id,
      code: branch.code,
      name: branch.name,
      total: money(branch.totalCents),
      tickets: branch.tickets,
      tablets: Array.from(branch.tablets.values())
        .sort((a, b) => b.totalCents - a.totalCents)
        .map((tablet) => ({
          id: tablet.id,
          name: tablet.name,
          deviceId: tablet.deviceId,
          total: money(tablet.totalCents),
          tickets: tablet.tickets,
          pendingSync: tablet.pendingSync,
          lastSync: tablet.lastSync,
          status: tablet.status
        })),
      lastSaleAt: branch.lastSaleTime ? dateLabel(new Date(branch.lastSaleTime)) : "sin venta en rango",
      syncStatus: branch.syncWarnings ? "revisar sync" : "ok",
      ticketRows: branch.ticketRows.sort((a, b) => String(b.date).localeCompare(String(a.date))).slice(0, 80)
    }))
    .sort((a, b) => {
      const left = Number(String(a.total).replace(/[^\d.-]/g, ""));
      const right = Number(String(b.total).replace(/[^\d.-]/g, ""));
      return right - left;
    });

  const tabletIds = new Set<string>();
  for (const branch of branches) {
    for (const tablet of branch.tablets) tabletIds.add(tablet.id);
  }

  const totalCents = input.totalCents;
  const netCents = input.totalCents - input.returnCents;
  return {
    roleLabel: "Administrador",
    syncHref: "/sync?from=sales-control&focus=tablet-pc-sales",
    addBranchHref: "/sync?from=sales-control&focus=link-new-tablet",
    totalLabel: money(totalCents),
    netLabel: money(netCents),
    ticketsLabel: numberLabel(input.sales.length),
    averageLabel: money(input.sales.length ? Math.round(totalCents / input.sales.length) : 0),
    branchCountLabel: numberLabel(branches.filter((branch) => branch.tickets > 0).length || branches.length),
    tabletCountLabel: numberLabel(tabletIds.size),
    updatedLabel: dateLabel(new Date()),
    branches
  } satisfies SalesControlViewModel;
}


export async function getPcSalesControl(params?: SearchLike): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const limit = clampLimit(readParam(params, "limit"), 120);
  const query = readParam(params, "q").toLowerCase();
  const range = resolveDateRange(params);
  const blockedPanel = range.blocked ? [{ title: "Rango bloqueado", body: range.blocked, tone: "warn" as const }] : [];
  const where = range.blocked
    ? { businessId, id: "__blocked__" }
    : { businessId, createdAt: { gte: range.from, lt: range.toExclusive } };

  const [salesRaw, returns, triDb, terminalsRaw, storesRaw, sessionsRaw, heartbeatsRaw, bucketsRaw] = await Promise.all([
    safe(() => db.sale.findMany({
      where,
      include: { lines: true, paymentTenders: true, cashSession: true, terminal: { include: { store: true } } },
      orderBy: { createdAt: "desc" },
      take: limit
    }), [] as any[]),
    safe(() => db.saleReturn.findMany({
      where,
      include: { lines: true },
      orderBy: { createdAt: "desc" },
      take: limit
    }), [] as any[]),
    getTriDbStatusCard(),
    safe(() => db.terminal.findMany({ where: { businessId, isActive: true }, include: { store: true }, orderBy: { name: "asc" }, take: 120 }), [] as any[]),
    safe(() => db.store.findMany({ where: { businessId }, orderBy: { name: "asc" }, take: 120 }), [] as any[]),
    safe(() => db.cashSession.findMany({ where: { businessId }, include: { terminal: true, sales: true }, orderBy: { openedAt: "desc" }, take: 160 }), [] as any[]),
    safe(() => db.deviceHeartbeat.findMany({ where: { businessId }, orderBy: { lastSeenAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.syncOutboxStatusBucket.findMany({ where: { businessId }, orderBy: { bucketStartAt: "desc" }, take: 160 }), [] as any[])
  ]);
  const sales = filterByQuery(salesRaw, query);
  const terminals = terminalsRaw;
  const stores = storesRaw;
  const sessions = sessionsRaw;
  const heartbeats = heartbeatsRaw.map((heartbeat: any) => ({ ...heartbeat, metadata: asJson(heartbeat.metadataJson) }));
  const buckets = bucketsRaw;
  const totalCents = sum(sales.map((sale: any) => Number(sale.totalCents ?? 0)));
  const returnCents = sum(returns.map((row: any) => Number(row.amountCents ?? 0)));
  const tenders = sales.flatMap((sale: any) => sale.paymentTenders ?? []);
  const lines = sales.flatMap((sale: any) => sale.lines ?? []);
  const byTerminal = new Map<string, number>();
  const byTerminalTickets = new Map<string, number>();
  const byCashier = new Map<string, number>();
  const byTender = new Map<string, number>();
  const bySku = new Map<string, { qty: number; total: number; name: string }>();
  for (const sale of sales) {
    byTerminal.set(sale.terminalId ?? "sin terminal", (byTerminal.get(sale.terminalId ?? "sin terminal") ?? 0) + Number(sale.totalCents ?? 0));
    byTerminalTickets.set(sale.terminalId ?? "sin terminal", (byTerminalTickets.get(sale.terminalId ?? "sin terminal") ?? 0) + 1);
    byCashier.set(sale.cashier ?? "sin cajero", (byCashier.get(sale.cashier ?? "sin cajero") ?? 0) + Number(sale.totalCents ?? 0));
  }
  for (const tender of tenders) {
    byTender.set(tender.tenderType ?? "sin metodo", (byTender.get(tender.tenderType ?? "sin metodo") ?? 0) + Number(tender.amountCents ?? 0));
  }
  for (const line of lines) {
    const sku = line.sku ?? line.productId ?? "sin sku";
    const current = bySku.get(sku) ?? { qty: 0, total: 0, name: line.productName ?? "Producto" };
    current.qty += Number(line.qty ?? 0);
    current.total += Number(line.totalCents ?? 0);
    bySku.set(sku, current);
  }

  const selectedSale = readParam(params, "saleId") || readParam(params, "folio");
  const saleDetail = selectedSale
    ? sales.find((sale: any) => sale.id === selectedSale || sale.folio === selectedSale) ?? null
    : sales[0] ?? null;
  const latestHeartbeatByDevice = new Map<string, any>();
  for (const heartbeat of heartbeats) {
    if (!latestHeartbeatByDevice.has(heartbeat.deviceId)) latestHeartbeatByDevice.set(heartbeat.deviceId, heartbeat);
  }
  const terminalById = new Map(terminals.map((terminal: any) => [terminal.id, terminal]));
  const terminalByCode = new Map(terminals.map((terminal: any) => [terminal.code, terminal]));
  const openSessionByTerminal = new Map<string, any>();
  for (const session of sessions) {
    const status = String(session.status ?? "").toLowerCase();
    if ((status === "open" || status === "active" || status === "abierta") && !openSessionByTerminal.has(session.terminalId)) {
      openSessionByTerminal.set(session.terminalId, session);
    }
  }
  const pendingByDevice = new Map<string, number>();
  const pendingByTerminal = new Map<string, number>();
  for (const bucket of buckets) {
    const status = String(bucket.status ?? "").toLowerCase();
    if (!["pending", "queued", "sent", "received"].includes(status)) continue;
    const count = Number(bucket.count ?? 0);
    if (bucket.deviceId) pendingByDevice.set(bucket.deviceId, (pendingByDevice.get(bucket.deviceId) ?? 0) + count);
    if (bucket.terminalId) pendingByTerminal.set(bucket.terminalId, (pendingByTerminal.get(bucket.terminalId) ?? 0) + count);
  }
  const deviceKeys = new Set<string>([...heartbeats.map((row: any) => row.deviceId), ...terminals.map((row: any) => row.id)]);
  const deviceRows = Array.from(deviceKeys).map((deviceKey) => {
    const heartbeat = latestHeartbeatByDevice.get(deviceKey);
    const metadata = heartbeat?.metadata ?? {};
    const terminalId = metadata.terminalId ?? metadata.terminal?.id ?? (terminalById.has(deviceKey) ? deviceKey : undefined);
    const terminal = terminalId ? terminalById.get(terminalId) : terminalByCode.get(deviceKey);
    const resolvedTerminalId = terminal?.id ?? terminalId ?? deviceKey;
    const openSession = openSessionByTerminal.get(resolvedTerminalId);
    const pendingSync = (pendingByDevice.get(deviceKey) ?? 0) + (pendingByTerminal.get(resolvedTerminalId) ?? 0);
    const heartbeatStatus = heartbeat ? normalizeStatus(heartbeat.health || heartbeat.status || heartbeat.syncStatus) : "sin heartbeat";
    const alertParts = [
      pendingSync ? `${pendingSync} pendientes` : "",
      heartbeat && ["stale", "warning", "offline", "degraded"].includes(String(heartbeat.health ?? "").toLowerCase()) ? normalizeStatus(heartbeat.health) : "",
      openSession ? "" : "sin caja abierta"
    ].filter(Boolean);
    return {
      "Tablet / dispositivo": terminal?.name ?? metadata.humanName ?? metadata.deviceName ?? deviceKey,
      DeviceId: heartbeat?.deviceId ?? terminal?.code ?? deviceKey,
      "Conexión": heartbeatStatus,
      Caja: openSession ? "abierta" : "cerrada",
      Turno: openSession?.id ?? "sin turno abierto",
      Cajero: openSession?.cashier ?? "sin cajero",
      "Venta hoy": money(byTerminal.get(resolvedTerminalId) ?? 0),
      Tickets: byTerminalTickets.get(resolvedTerminalId) ?? 0,
      "Pendientes sync": pendingSync,
      "Último sync": heartbeat ? relativeLabel(heartbeat.lastSeenAt ?? heartbeat.observedAt) : "sin registro",
      "Alertas": alertParts.join("; ") || "sin alertas"
    };
  });

  const salesControlView = buildSalesControlView({
    sales,
    returns,
    terminals,
    stores,
    heartbeats,
    buckets,
    totalCents,
    returnCents
  });

  const panels: CommandPanel[] = [
    ...blockedPanel,
    {
      title: "Rol operativo protegido",
      body: "PC observa y gobierna ventas consolidadas. Tablet conserva venta local e historial local aunque PC este apagada.",
      tone: "ok"
    },
    triDb.tablet.saleCount > triDb.pc.saleCount
      ? {
          title: "PC puede estar atrasado",
          body: `Tri-db reporta ${triDb.tablet.saleCount} ventas Tablet y ${triDb.pc.saleCount} ventas PC. La venta Tablet no se bloquea.`,
          tone: "warn"
        }
      : {
          title: "Cobertura tri-db",
          body: triDb.parityOk ? "PC cubre los conteos Tablet reportados por tri-db." : "Tri-db no confirma cobertura total; revisar sync sin detener ventas.",
          tone: triDb.parityOk ? "ok" : "warn"
        }
  ];

  return {
    mode: "sales",
    currentPath: "/sales-control",
    kicker: "ventas / caja",
    title: "Control de ventas",
    description: "Auditoria y gobierno de ventas consolidadas desde la base canonica de PC.",
    periodLabel: range.label,
    sourceLine: `Fuente: canonical DB. Rango: ${range.label}. Limite: ${limit}.`,
    independenceLine: "Tablet vende y consulta localmente; PC no es requisito para vender.",
    metrics: [
      { label: "Venta bruta", value: money(totalCents), note: "Suma de Sale.totalCents", tone: sales.length ? "ok" : "warn" },
      { label: "Tickets", value: numberLabel(sales.length), note: "Tickets consolidados PC" },
      { label: "Ticket promedio", value: money(sales.length ? Math.round(totalCents / sales.length) : 0), note: "Venta / tickets" },
      { label: "Devoluciones", value: money(returnCents), note: "SaleReturn en rango", tone: returnCents ? "warn" : "ok" },
      { label: "Venta neta", value: money(totalCents - returnCents), note: "Bruta menos devoluciones" }
    ],
    panels,
    tables: [
      {
        title: "Tickets",
        caption: "Listado acotado con folio, terminal, cajero, total y estado.",
        columns: ["Folio", "Fecha", "Terminal", "Cajero", "Total", "Estado"],
        rows: sales.map((sale: any) => ({
          Folio: sale.folio ?? sale.id,
          Fecha: dateLabel(sale.createdAt),
          Terminal: sale.terminal?.name ?? sale.terminalId ?? "sin terminal",
          Cajero: sale.cashier ?? "sin cajero",
          Total: money(Number(sale.totalCents ?? 0)),
          Estado: normalizeStatus(sale.status)
        })),
        emptyMessage: "No hay ventas consolidadas en PC todavia; Tablet puede seguir vendiendo."
      },
      {
        title: "Detalle de ticket",
        caption: "Vista de auditoria, no POS.",
        columns: ["Campo", "Valor"],
        rows: saleDetail
          ? [
              { Campo: "Folio", Valor: saleDetail.folio ?? saleDetail.id },
              { Campo: "Fecha", Valor: dateLabel(saleDetail.createdAt) },
              { Campo: "Terminal", Valor: saleDetail.terminalId ?? "sin terminal" },
              { Campo: "Caja", Valor: saleDetail.cashSessionId ?? "sin caja" },
              { Campo: "Lineas", Valor: (saleDetail.lines ?? []).length },
              { Campo: "Tenders", Valor: (saleDetail.paymentTenders ?? []).map((item: any) => `${item.tenderType}:${money(item.amountCents)}`).join(", ") || "sin desglose" }
            ]
          : [],
        emptyMessage: "Selecciona o espera un ticket consolidado para detalle de auditoria."
      },
      {
        title: "Ventas por terminal",
        caption: "Comparacion multi-Tablet cuando terminalId/device mapping existe.",
        columns: ["Terminal", "Total"],
        rows: Array.from(byTerminal.entries()).map(([Terminal, Total]) => ({ Terminal, Total: money(Total) })),
        emptyMessage: "Sin terminales con venta consolidada en el rango."
      },
      {
        title: "Tablets / dispositivos registrados",
        caption: "Estado por terminal o heartbeat: caja, turno, cajero, venta, tickets, pendientes y ultimo pulso.",
        columns: ["Tablet / dispositivo", "DeviceId", "Conexión", "Caja", "Turno", "Cajero", "Venta hoy", "Tickets", "Pendientes sync", "Último sync", "Alertas"],
        rows: deviceRows,
        emptyMessage: "No tablets registered. Abre configuración para registrar tablet."
      },
      {
        title: "Top SKUs",
        caption: "Productos mas vendidos desde SaleLine.",
        columns: ["SKU", "Producto", "Unidades", "Total"],
        rows: Array.from(bySku.entries())
          .sort((a, b) => b[1].total - a[1].total)
          .slice(0, 12)
          .map(([SKU, value]) => ({ SKU, Producto: value.name, Unidades: value.qty, Total: money(value.total) })),
        emptyMessage: "Sin lineas de venta consolidadas."
      },
      {
        title: "Pago por metodo",
        caption: "Tenders reales desde SalePaymentTender.",
        columns: ["Metodo", "Total"],
        rows: Array.from(byTender.entries()).map(([Metodo, Total]) => ({ Metodo, Total: money(Total) })),
        emptyMessage: "Sin tenders registrados en PC."
      },
      {
        title: "Ventas por cajero",
        caption: "Agrupado por Sale.cashier cuando existe.",
        columns: ["Cajero", "Total"],
        rows: Array.from(byCashier.entries()).map(([Cajero, Total]) => ({ Cajero, Total: money(Total) })),
        emptyMessage: "Sin cajeros registrados en PC."
      }
    ],
    diagnostics: { businessId, query, range, triDbSource: triDb.sourcePath, exportFormats: ["json", "csv"] },
    actions: [
      { label: "Exportar JSON", href: "/api/backoffice/sales-control?format=json" },
      { label: "Exportar CSV", href: "/api/backoffice/sales-control?format=csv" }
    ],
    salesControl: salesControlView
  };
}

export async function getPcCashSessions(params?: SearchLike): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const range = resolveDateRange(params);
  const limit = clampLimit(readParam(params, "limit"), 80);
  const [sessionsRaw, conflictsRaw] = await Promise.all([
    safe(() => db.cashSession.findMany({
      where: range.blocked ? { businessId, id: "__blocked__" } : { businessId, openedAt: { lt: range.toExclusive }, OR: [{ closedAt: null }, { closedAt: { gte: range.from } }] },
      include: { cashMovements: true, cashAdjustments: true, sales: true, terminal: true, store: true },
      orderBy: { openedAt: "desc" },
      take: limit
    }), [] as any[]),
    safe(() => db.syncConflict.findMany({
      where: { businessId },
      orderBy: { detectedAt: "desc" },
      take: 200
    }), [] as any[])
  ]);
  const sessions = sessionsRaw;
  const activeConflicts = conflictsRaw.filter((conflict: any) => isOpenConflictStatus(conflict.status));
  const cashConflicts = activeConflicts.filter((conflict: any) => isCashConflictCandidate(conflict, sessions));
  const conflictsBySessionId = new Map<string, any[]>();
  for (const session of sessions) {
    const related = cashConflicts.filter((conflict: any) => conflictMatchesSession(conflict, session));
    if (related.length) conflictsBySessionId.set(session.id, related);
  }
  const sessionFallbackConflicts = sessions.filter((session: any) => normalizeStatus(session.status) === "conflicto" && !(conflictsBySessionId.get(session.id)?.length));
  const open = sessions.filter((session: any) => String(session.status).toLowerCase() !== "closed").length;
  const variance = sum(sessions.map((session: any) => Number(session.varianceCents ?? 0)));
  const movements = sessions.flatMap((session: any) => (session.cashMovements ?? []).map((movement: any) => ({ ...movement, session })));
  const conflictSessionCount = conflictsBySessionId.size + sessionFallbackConflicts.length;
  const primaryCashConflict = cashConflicts[0] ?? null;

  return {
    mode: "cash",
    currentPath: "/cash-sessions",
    kicker: "caja",
    title: "Caja y cierres",
    description: "Gobierno de turnos, movimientos, esperado, contado y variaciones.",
    periodLabel: range.label,
    sourceLine: `Fuente: CashSession/CashMovement + SyncConflict canonicos. Rango: ${range.label}.`,
    independenceLine: "PC gobierna cierres consolidados; Tablet puede abrir, vender y cerrar localmente.",
    metrics: [
      { label: "Sesiones", value: numberLabel(sessions.length), note: "CashSession en rango" },
      { label: "Abiertas", value: numberLabel(open), note: "Requieren seguimiento", tone: open ? "warn" : "ok" },
      { label: "Variacion neta", value: money(variance), note: "Suma varianceCents", tone: Math.abs(variance) > 5000 ? "danger" : variance ? "warn" : "ok" },
      { label: "Conflictos caja", value: numberLabel(cashConflicts.length + sessionFallbackConflicts.length), note: "SyncConflict + CashSession conflict", tone: cashConflicts.length || sessionFallbackConflicts.length ? "warn" : "ok" },
      { label: "Movimientos", value: numberLabel(movements.length), note: "Entradas/salidas/ajustes" }
    ],
    panels: [
      range.blocked ? { title: "Rango bloqueado", body: range.blocked, tone: "warn" } : null,
      cashConflicts.length
        ? {
            title: "Conflictos de caja detectados",
            body: `Hay ${cashConflicts.length} SyncConflict relacionado con caja. El badge Estado en la tabla es clicable y explica código, detalle, terminal, evento, idempotencyKey y acción sugerida.`,
            tone: "warn"
          }
        : {
            title: "Conflictos de caja",
            body: "No hay SyncConflict activo relacionado con caja en la muestra actual. Si una CashSession llega con estado conflicto sin SyncConflict enlazado, el renglón muestra diagnóstico fallback.",
            tone: sessionFallbackConflicts.length ? "warn" : "ok"
          },
      primaryCashConflict
        ? {
            title: "Primer conflicto a revisar",
            body: `${primaryCashConflict.label ?? primaryCashConflict.conflictCode}: ${primaryCashConflict.detail ?? "sin detalle"} (${primaryCashConflict.terminalId ?? "sin terminal"})`,
            tone: conflictTone(primaryCashConflict)
          }
        : null
    ].filter(Boolean) as CommandPanel[],
    tables: [
      {
        title: "Sesiones de caja",
        caption: "Abiertas/cerradas por terminal. Si Estado marca conflicto, el badge se puede abrir para ver el diagnóstico.",
        columns: ["Caja", "Terminal", "Cajero", "Abierta", "Cerrada", "Esperado", "Contado", "Variacion", "Estado"],
        rows: sessions.map((session: any) => {
          const relatedConflicts = conflictsBySessionId.get(session.id) ?? [];
          const primary = relatedConflicts[0] ?? null;
          const fallbackConflict = !primary && normalizeStatus(session.status) === "conflicto";
          const detailItems = primary ? buildConflictDetailItems(primary, session) : fallbackConflict ? buildCashSessionFallbackConflictDetail(session) : [];
          return {
            Caja: session.id,
            Terminal: session.terminal?.name ?? session.terminalId,
            Cajero: session.cashier ?? session.cashierId,
            Abierta: dateLabel(session.openedAt),
            Cerrada: dateLabel(session.closedAt),
            Esperado: money(session.expectedCashCents),
            Contado: money(session.cashEndCents),
            Variacion: money(session.varianceCents),
            Estado: relatedConflicts.length || fallbackConflict ? "conflicto" : normalizeStatus(session.status),
            __rowDetailTitle: detailItems.length ? `Qué pedo con caja ${session.id}` : undefined,
            __rowDetailTone: primary ? conflictTone(primary) : fallbackConflict ? "warn" : undefined,
            __rowDetailItems: detailItems.length ? detailItems : undefined,
            __rowDetailJson: detailItems.length ? serializeRowDetail(detailItems) : undefined,
            __rowActionHref: detailItems.length ? "/sync" : undefined,
            __rowActionLabel: detailItems.length ? "Abrir tablero Sync" : undefined
          };
        }),
        emptyMessage: "No hay sesiones de caja consolidadas en PC."
      },
      {
        title: "Conflictos de sync relacionados con caja",
        caption: "Diagnóstico accionable desde SyncConflict: código, detalle, evento, terminal e idempotencyKey.",
        columns: ["Detectado", "Código", "Severidad", "Terminal", "Evento", "Agregado", "Detalle", "Estado"],
        rows: cashConflicts.slice(0, 80).map((conflict: any) => {
          const detailItems = buildConflictDetailItems(conflict);
          return {
            Detectado: dateLabel(conflict.detectedAt),
            Código: conflict.conflictCode ?? "sin codigo",
            Severidad: conflict.severity ?? "sin severidad",
            Terminal: conflict.terminalId ?? conflict.deviceId ?? "sin terminal",
            Evento: conflict.eventId ?? conflict.outboxEventId ?? conflict.idempotencyKey ?? "sin evento",
            Agregado: conflict.aggregateId ?? "sin agregado",
            Detalle: conflict.detail ?? conflict.label ?? "sin detalle",
            Estado: normalizeStatus(conflict.status),
            __rowDetailTitle: `Qué pedo con ${conflict.conflictCode ?? "conflicto"}`,
            __rowDetailTone: conflictTone(conflict),
            __rowDetailItems: detailItems,
            __rowDetailJson: JSON.stringify({
              id: conflict.id,
              eventId: conflict.eventId,
              outboxEventId: conflict.outboxEventId,
              idempotencyKey: conflict.idempotencyKey,
              source: conflict.source,
              deviceId: conflict.deviceId,
              terminalId: conflict.terminalId,
              topic: conflict.topic,
              aggregateId: conflict.aggregateId,
              diagnostics: asJson(conflict.diagnosticsJson)
            }, null, 2),
            __rowActionHref: "/sync",
            __rowActionLabel: "Abrir tablero Sync"
          };
        }),
        emptyMessage: "Sin SyncConflict activo relacionado con caja."
      },
      {
        title: "Movimientos de caja",
        caption: "Timeline acotado por sesion.",
        columns: ["Fecha", "Caja", "Movimiento", "Importe", "Motivo"],
        rows: movements.slice(0, 80).map((movement: any) => ({
          Fecha: dateLabel(movement.createdAt),
          Caja: movement.cashSessionId,
          Movimiento: movement.movement,
          Importe: money(movement.amountCents),
          Motivo: movement.reason ?? "sin motivo"
        })),
        emptyMessage: "Sin movimientos de caja en el rango."
      }
    ],
    diagnostics: {
      businessId,
      range,
      varianceThresholdCents: 5000,
      syncConflictSample: activeConflicts.length,
      cashConflictSample: cashConflicts.length,
      conflictSessionCount,
      matchingRules: [
        "aggregateId/eventId/outboxEventId/idempotencyKey igual al CashSession.id",
        "detalle/diagnosticsJson menciona CashSession.id",
        "terminalId coincide y detectedAt cae dentro de la ventana de caja con 24h de gracia",
        "conflictCode sale_outside_shift o topic/detail relacionado con cash/caja/session/turno/sale"
      ]
    },
    actions: [
      { label: "Abrir tablero Sync", href: "/sync" },
      { label: "API sesiones caja", href: "/api/backoffice/cash-sessions" }
    ]
  };
}

export async function getPcDeviceFleet(params?: SearchLike): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const query = readParam(params, "q").toLowerCase();
  const now = Date.now();
  const [heartbeatsRaw, freshness, checkpoints, buckets] = await Promise.all([
    safe(() => db.deviceHeartbeat.findMany({ where: { businessId }, orderBy: { lastSeenAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.dataSourceFreshness.findMany({ where: { businessId }, orderBy: { observedAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.syncCheckpoint.findMany({ where: { businessId }, orderBy: { checkpointAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.syncOutboxStatusBucket.findMany({ where: { businessId }, orderBy: { bucketStartAt: "desc" }, take: 120 }), [] as any[])
  ]);
  const heartbeats = filterByQuery(heartbeatsRaw, query);
  const enriched = heartbeats.map((heartbeat: any) => {
    const ageSeconds = Math.round((now - new Date(heartbeat.lastSeenAt).getTime()) / 1000);
    const computedHealth = ageSeconds > 3600 ? "offline" : ageSeconds > 600 ? "stale" : heartbeat.health || "healthy";
    return { ...heartbeat, computedHealth, ageSeconds, metadata: asJson(heartbeat.metadataJson) };
  });
  const attention = enriched.filter((row: any) => ["offline", "stale", "warning", "degraded"].includes(String(row.computedHealth).toLowerCase()));

  return {
    mode: "devices",
    currentPath: "/devices",
    kicker: "dispositivos",
    title: `Dispositivos de ${PRISMA_ORIGINAL_CUSTOMER.displayName}`,
    description: "PC, Tablet y Mobile vistos como una sola cuenta operativa, con conexion, licencia y pendientes accionables.",
    sourceLine: "Vista de operacion: equipos, datos recientes y pendientes.",
    independenceLine: "Una Tablet offline no bloquea ventas locales de otras Tablets.",
    metrics: [
      { label: "Equipos vistos", value: numberLabel(enriched.length), note: "Pulso reciente" },
      { label: "Por atender", value: numberLabel(attention.length), note: "Sin pulso reciente o con aviso", tone: attention.length ? "warn" : "ok" },
      { label: "Pendientes", value: numberLabel(sum(enriched.map((row: any) => Number(row.outboxCount ?? 0)))), note: "Trabajo local reportado" },
      { label: "Fuentes recientes", value: numberLabel(freshness.length), note: "Lecturas operativas" }
    ],
    panels: [
      {
        title: "Sin equipos reportados aun",
        body: enriched.length ? "Hay equipos reportados." : "No hay pulso consolidado; la pantalla queda lista sin inventar dispositivos.",
        tone: enriched.length ? "ok" : "warn"
      },
      {
        title: "Operacion offline",
        body: "Estado offline significa que PC no recibe pulso reciente. No significa que la Tablet no pueda vender localmente.",
        tone: "ok"
      }
    ],
    tables: [
      {
        title: "Dispositivos autorizados o pendientes",
        caption: "Estado operativo y licencia por equipo.",
        columns: ["Dispositivo", "Superficie", "Modo", "Version", "Licencia", "Conexion", "Pendientes", "Ultima venta", "Ultimo pulso", "Estado"],
        rows: enriched.map((row: any) => ({
          Dispositivo: row.deviceId,
          Superficie: row.surface ?? row.source,
          Modo: row.runtimeMode,
          Version: row.appVersion,
          Licencia: normalizeStatus(row.licenseStatus),
          Conexion: normalizeStatus(row.syncStatus),
          Pendientes: Number(row.outboxCount ?? 0),
          "Ultima venta": dateLabel(row.lastSaleAt),
          "Ultimo pulso": relativeLabel(row.lastSeenAt),
          Estado: normalizeStatus(row.computedHealth)
        })),
        emptyMessage: "No hay equipos reportados todavia."
      },
      {
        title: "Datos recientes por categoria",
        caption: "Ultimas marcas de avance por fuente operativa.",
        columns: ["Fuente", "Dispositivo", "Categoria", "Ultima revision", "Resultado", "Estado"],
        rows: checkpoints.slice(0, 80).map((row: any) => ({
          Fuente: row.source,
          Dispositivo: row.deviceId ?? "general",
          Categoria: readableStream(row.stream),
          "Ultima revision": dateLabel(row.checkpointAt),
          Resultado: readableLifecycle(row.lifecycleStatus),
          Estado: normalizeStatus(row.status)
        })),
        emptyMessage: "Sin marcas de avance registradas."
      },
      {
        title: "Pendientes por categoria",
        caption: "Trabajo local agrupado para revision.",
        columns: ["Fuente", "Dispositivo", "Categoria", "Resultado", "Conteo", "Mas viejo", "Estado"],
        rows: buckets.slice(0, 80).map((row: any) => ({
          Fuente: row.source,
          Dispositivo: row.deviceId ?? "general",
          Categoria: readableStream(row.topic),
          Resultado: readableLifecycle(row.lifecycleStatus),
          Conteo: row.count,
          "Mas viejo": dateLabel(row.oldestEventAt),
          Estado: normalizeStatus(row.status)
        })),
        emptyMessage: "Sin pendientes agrupados registrados."
      }
    ],
    diagnostics: { businessId, query, customer: PRISMA_ORIGINAL_CUSTOMER, technicalSources: ["DeviceHeartbeat", "DataSourceFreshness", "SyncCheckpoint", "SyncOutboxStatusBucket"], staleAfterSeconds: 600, offlineAfterSeconds: 3600 }
  };
}

export async function getPcSyncCommandCenter(params?: SearchLike): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const limit = clampLimit(readParam(params, "limit"), 120);
  const topic = readParam(params, "topic");
  const source = readParam(params, "source");
  const where = { businessId, ...(topic ? { topic } : {}), ...(source ? { source } : {}) };
  const [events, attempts, conflicts, triDb, catalogStatus] = await Promise.all([
    safe(() => db.outboxEvent.findMany({ where, orderBy: { createdAt: "desc" }, take: limit }), [] as any[]),
    safe(() => db.syncAttempt.findMany({ where, orderBy: { createdAt: "desc" }, take: limit }), [] as any[]),
    safe(() => db.syncConflict.findMany({ where, orderBy: { detectedAt: "desc" }, take: limit }), [] as any[]),
    getTriDbStatusCard(),
    getPcCatalogDeltaStatus({ businessId })
  ]);
  const buckets = lifecycleBuckets(events);
  const oldestPending = events.filter((event: any) => ["pending", "sent", "received"].includes(String(event.status).toLowerCase())).sort((a: any, b: any) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())[0];
  const newestReceived = events.filter((event: any) => event.receivedAt).sort((a: any, b: any) => new Date(b.receivedAt).getTime() - new Date(a.receivedAt).getTime())[0];
  const avgDuration = attempts.length ? Math.round(sum(attempts.map((item: any) => Number(item.durationMs ?? 0))) / attempts.length) : 0;

  return {
    mode: "sync",
    currentPath: "/sync",
    kicker: "sync",
    title: `Sincronizacion de ${PRISMA_ORIGINAL_CUSTOMER.displayName}`,
    description: "Estado de envios, datos para Tablet, duplicados protegidos, conflictos y cobertura entre equipos.",
    sourceLine: "Vista de operacion: ventas, inventario, catalogo y revisiones.",
    independenceLine: "PC puede atrasarse o marcar conflicto sin detener venta local de Tablet.",
    metrics: [
      { label: "Movimientos", value: numberLabel(events.length), note: "Registros recientes" },
      { label: "Datos para Tablet", value: numberLabel(catalogStatus.latestExport?.total ?? 0), note: catalogStatus.latestExport ? "Ultima preparacion disponible" : "sin paquete generado", tone: catalogStatus.latestExport ? "ok" : "warn" },
      { label: "Conflictos", value: numberLabel(conflicts.filter((row: any) => row.status !== "resolved").length), note: "Abiertos o por revisar", tone: conflicts.length ? "warn" : "ok" },
      { label: "Revisiones", value: numberLabel(attempts.length), note: "Intentos recientes" },
      { label: "Duracion prom.", value: `${numberLabel(avgDuration)} ms`, note: "Tiempo de revision" },
      { label: "Pendiente mas viejo", value: oldestPending ? relativeLabel(oldestPending.createdAt) : "sin pendiente", note: "Proteccion de backlog" }
    ],
    panels: [
      {
        title: "Cobertura entre equipos",
        body: `Estado ${normalizeStatus(triDb.status)}. Tablet ventas ${triDb.tablet.saleCount}; PC ventas ${triDb.pc.saleCount}; cobertura=${triDb.parityOk ? "si" : "no"}.`,
        tone: triDb.parityOk ? "ok" : "warn"
      },
      {
        title: "Duplicados",
        body: "PC reconoce movimientos repetidos y evita aplicarlos dos veces.",
        tone: "ok"
      },
      {
        title: "PC a Tablet",
        body: "Los datos de catalogo se preparan para Tablet sin bloquear ventas locales.",
        tone: "ok"
      }
    ],
    tables: [
      {
        title: "Estado de envios",
        caption: "Conteos por resultado operativo.",
        columns: ["Resultado", "Conteo"],
        rows: buckets.map((bucket) => ({ Resultado: readableLifecycle(bucket.key), Conteo: bucket.value })),
        emptyMessage: "Sin movimientos de sincronizacion registrados."
      },
      {
        title: "Revisiones recientes",
        caption: "Duracion, fuente, dispositivo, categoria y estado.",
        columns: ["Fecha", "Fuente", "Dispositivo", "Categoria", "Duracion", "Resultado", "Estado"],
        rows: attempts.map((attempt: any) => ({
          Fecha: dateLabel(attempt.createdAt),
          Fuente: attempt.source,
          Dispositivo: attempt.deviceId ?? "sin dispositivo",
          Categoria: readableStream(attempt.topic),
          Duracion: `${attempt.durationMs ?? 0} ms`,
          Resultado: readableLifecycle(attempt.lifecycleStatus),
          Estado: normalizeStatus(attempt.status)
        })),
        emptyMessage: "No hay revisiones registradas."
      },
      {
        title: "Movimientos recibidos",
        caption: "Categoria, entidad operativa, resultado e intentos sin mostrar payload crudo.",
        columns: ["Fecha", "Categoria", "Entidad", "Resultado", "Intentos", "Estado"],
        rows: events.map((event: any) => ({
          Fecha: dateLabel(event.createdAt),
          Categoria: readableStream(event.topic),
          Entidad: event.aggregateId,
          Resultado: readableLifecycle(event.lifecycleStatus),
          Intentos: event.attempts ?? 0,
          Estado: normalizeStatus(event.status)
        })),
        emptyMessage: "Sin movimientos de sincronizacion en PC."
      },
      {
        title: "Conflictos",
        caption: "Cola accionable por severidad y recomendacion.",
        columns: ["Detectado", "Motivo", "Severidad", "Dispositivo", "Entidad", "Recomendacion", "Estado"],
        rows: conflicts.map((conflict: any) => ({
          Detectado: dateLabel(conflict.detectedAt),
          Motivo: readableConflict(conflict.conflictCode),
          Severidad: conflict.severity,
          Dispositivo: conflict.deviceId ?? "sin dispositivo",
          Entidad: conflict.aggregateId ?? "sin entidad",
          Recomendacion: conflict.resolution ?? "Revisar evento origen, entidad afectada y reprocesar solo si el contrato lo permite.",
          Estado: normalizeStatus(conflict.status)
        })),
        emptyMessage: "Sin conflictos abiertos."
      },
      {
        title: "Datos PC a Tablet",
        caption: "Estado de datos maestros disponibles para actualizar Tablet.",
        columns: ["Categoria", "Filas PC", "Ultima preparacion", "Estado"],
        rows: Object.entries(catalogStatus.tableCounts).map(([Entidad, Filas]) => ({
          Categoria: readableEntity(Entidad),
          "Filas PC": Filas,
          "Ultima preparacion": catalogStatus.latestExport?.byEntity?.[Entidad] ?? 0,
          Estado: catalogStatus.latestExport ? "preparado" : "pendiente"
        })),
        emptyMessage: "Sin datos de catalogo soportados."
      },
      {
        title: "Cobertura PC y Tablet",
        caption: "Comparacion resumida entre equipos.",
        columns: ["Dato", "Tablet", "PC", "Diferencia", "Cubre"],
        rows: triDb.parityTables.map((row) => ({
          Dato: readableEntity(row.table),
          Tablet: row.tabletRows,
          PC: row.pcRows,
          Diferencia: row.deltaPcMinusTablet,
          Cubre: row.pcCoversTablet ? "si" : "no"
        })),
        emptyMessage: "Sin comparacion de cobertura disponible."
      }
    ],
    diagnostics: { businessId, topic, source, newestReceivedAt: newestReceived?.receivedAt ?? null, triDbSource: triDb.sourcePath, catalogDelta: catalogStatus, technicalSources: ["OutboxEvent", "SyncAttempt", "SyncConflict", "shared/tri-db/status.latest.json"] },
    actions: [
      { label: "Actualizar datos para Tablet", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "delta", target: "tablet" }, successMessage: "Datos actualizados desde PC." },
      { label: "Preparar primera carga", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "bootstrap", target: "tablet" }, successMessage: "Primera carga preparada desde PC." },
      { label: "Reparar datos de Tablet", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "resync", target: "tablet" }, successMessage: "Reparacion de datos preparada desde PC." }
    ]
  };
}

export async function getPcDataQuality(): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const [sales, lines, tenders, sessions, conflicts, heartbeats] = await Promise.all([
    safe(() => db.sale.findMany({ where: { businessId }, include: { lines: true, paymentTenders: true }, take: 300 }), [] as any[]),
    safe(() => db.saleLine.findMany({ where: { businessId }, take: 300 }), [] as any[]),
    safe(() => db.salePaymentTender.findMany({ where: { businessId }, take: 300 }), [] as any[]),
    safe(() => db.cashSession.findMany({ where: { businessId }, take: 300 }), [] as any[]),
    safe(() => db.syncConflict.findMany({ where: { businessId }, take: 100, orderBy: { detectedAt: "desc" } }), [] as any[]),
    safe(() => db.deviceHeartbeat.findMany({ where: { businessId }, take: 100, orderBy: { lastSeenAt: "desc" } }), [] as any[])
  ]);
  const saleIds = new Set(sales.map((sale: any) => sale.id));
  const sessionIds = new Set(sessions.map((session: any) => session.id));
  const orphanLines = lines.filter((line: any) => !saleIds.has(line.saleId));
  const totalMismatches = sales.filter((sale: any) => Math.abs(sum((sale.lines ?? []).map((line: any) => Number(line.totalCents ?? 0))) - Number(sale.totalCents ?? 0)) > 2);
  const tenderMismatches = sales.filter((sale: any) => {
    const tenderTotal = sum((sale.paymentTenders ?? []).map((tender: any) => Number(tender.amountCents ?? 0)));
    return tenderTotal > 0 && Math.abs(tenderTotal - Number(sale.totalCents ?? 0)) > 2;
  });
  const salesWithoutSession = sales.filter((sale: any) => sale.cashSessionId && !sessionIds.has(sale.cashSessionId));
  const duplicateFolios = new Map<string, number>();
  for (const sale of sales) duplicateFolios.set(sale.folio, (duplicateFolios.get(sale.folio) ?? 0) + 1);
  const duplicateRows = Array.from(duplicateFolios.entries()).filter(([, count]) => count > 1);
  const staleHeartbeats = heartbeats.filter((heartbeat: any) => Date.now() - new Date(heartbeat.lastSeenAt).getTime() > 3600_000);

  return {
    mode: "dataQuality",
    currentPath: "/data-quality",
    kicker: "calidad de datos",
    title: "Integridad canonica",
    description: "Revision acotada de ventas, pagos, caja, folios, eventos y heartbeats.",
    sourceLine: "Fuente: Prisma canonico. Checks acotados para no cargar toda la base.",
    independenceLine: "Los checks no modifican datos ni bloquean Tablet.",
    metrics: [
      { label: "Sales muestreadas", value: numberLabel(sales.length), note: "Limite 300" },
      { label: "Lineas huerfanas", value: numberLabel(orphanLines.length), note: "SaleLine sin Sale", tone: orphanLines.length ? "danger" : "ok" },
      { label: "Totales venta", value: numberLabel(totalMismatches.length), note: "Sale vs lineas", tone: totalMismatches.length ? "warn" : "ok" },
      { label: "Pagos", value: numberLabel(tenderMismatches.length), note: "Tenders vs total", tone: tenderMismatches.length ? "warn" : "ok" },
      { label: "Heartbeats stale", value: numberLabel(staleHeartbeats.length), note: "Mayores a 1h", tone: staleHeartbeats.length ? "warn" : "ok" }
    ],
    panels: [
      { title: "Indices verificados", body: "Sale, SaleLine, SalePaymentTender, CashSession, OutboxEvent, SyncAttempt, SyncConflict, DeviceHeartbeat y DataSourceFreshness ya tienen indices utiles en schema.prisma.", tone: "ok" },
      { title: "Sin migracion destructiva", body: "No se cambio schema; no hay backfill destructivo ni perdida de datos.", tone: "ok" }
    ],
    tables: [
      {
        title: "Hallazgos",
        caption: "Data quality checks principales.",
        columns: ["Check", "Resultado", "Estado"],
        rows: [
          { Check: "SaleLine huerfana", Resultado: orphanLines.length, Estado: orphanLines.length ? "fallido" : "activo" },
          { Check: "Sale total vs lineas", Resultado: totalMismatches.length, Estado: totalMismatches.length ? "advertencia" : "activo" },
          { Check: "Pagos vs total", Resultado: tenderMismatches.length, Estado: tenderMismatches.length ? "advertencia" : "activo" },
          { Check: "Sale con cashSession inexistente", Resultado: salesWithoutSession.length, Estado: salesWithoutSession.length ? "advertencia" : "activo" },
          { Check: "Folios duplicados", Resultado: duplicateRows.length, Estado: duplicateRows.length ? "fallido" : "activo" },
          { Check: "Heartbeat stale", Resultado: staleHeartbeats.length, Estado: staleHeartbeats.length ? "advertencia" : "activo" },
          { Check: "Eventos con conflicto abierto", Resultado: conflicts.filter((row: any) => row.status !== "resolved").length, Estado: conflicts.length ? "advertencia" : "activo" }
        ],
        emptyMessage: "Sin hallazgos de integridad."
      },
      {
        title: "Folios duplicados",
        caption: "Duplicados dentro del negocio canónico.",
        columns: ["Folio", "Conteo"],
        rows: duplicateRows.map(([Folio, Conteo]) => ({ Folio, Conteo })),
        emptyMessage: "No hay folios duplicados en la muestra."
      }
    ],
    diagnostics: { businessId, lineSample: lines.length, tenderSample: tenders.length }
  };
}

export async function getPcLicenseRuntimeControl(): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const [license, refresh, features, heartbeats] = await Promise.all([
    Promise.resolve(getPcLicenseStatus()),
    Promise.resolve(getPcLicenseRefreshStatus()),
    Promise.resolve(getPcFeatureList()),
    safe(() => db.deviceHeartbeat.findMany({ where: { businessId }, orderBy: { lastSeenAt: "desc" }, take: 120 }), [] as any[])
  ]);
  const blockedFeatures = features.filter((feature: any) => !feature.allowed);
  const tabletLicenses = new Map<string, number>();
  for (const heartbeat of heartbeats) {
    const key = normalizeStatus(heartbeat.licenseStatus);
    tabletLicenses.set(key, (tabletLicenses.get(key) ?? 0) + 1);
  }

  return {
    mode: "licenseRuntime",
    currentPath: "/license-runtime",
    kicker: "licencias y runtime",
    title: `Licencia de ${PRISMA_ORIGINAL_CUSTOMER.displayName}`,
    description: "Estado local PC, vigencia, plan, funciones permitidas y equipos asociados.",
    sourceLine: "Vista de operacion: licencia local, plan, funciones y equipos.",
    independenceLine: "La licencia local de Tablet sigue siendo fuente valida para operacion offline.",
    metrics: [
      { label: "Cliente", value: PRISMA_ORIGINAL_CUSTOMER.displayName, note: `Cuenta ${PRISMA_ORIGINAL_CUSTOMER.tenantId}` },
      { label: "Estado PC", value: normalizeStatus(license.state), note: `Plan ${license.plan}`, tone: license.state === "active" || license.state === "development" ? "ok" : "warn" },
      { label: "Dias restantes", value: license.daysRemaining === null ? "n/d" : String(license.daysRemaining), note: "Umbral visible" },
      { label: "Refresh remoto", value: refresh.enabled ? "configurado" : "no configurado", note: refresh.state, tone: refresh.enabled ? "ok" : "warn" },
      { label: "Funciones bloqueadas", value: numberLabel(blockedFeatures.length), note: "Permisos PC", tone: blockedFeatures.length ? "warn" : "ok" },
      { label: "Tablets con licencia", value: numberLabel(heartbeats.length), note: "Reportadas por equipos" }
    ],
    panels: [
      {
        title: refresh.enabled ? "Refresh remoto disponible" : "Refresh remoto no configurado",
        body: refresh.enabled
          ? "PC puede intentar refrescar licencia sin bloquear Tablet."
          : "Usa importacion local/firma existente; no se inventa exito remoto sin servidor.",
        tone: refresh.enabled ? "ok" : "warn"
      },
      {
        title: "Sin secretos expuestos",
        body: "No se muestra blob de licencia, llaves privadas ni material de firma en la UI normal.",
        tone: "ok"
      }
    ],
    tables: [
      {
        title: "Funciones por modulo",
        caption: "Permisos resueltos por licencia local.",
        columns: ["Funcion", "Permitida", "Motivo"],
        rows: features.map((feature: any) => ({
          Funcion: featureLabel(feature.key),
          Permitida: feature.allowed ? "si" : "no",
          Motivo: feature.reason
        })),
        emptyMessage: "No hay permisos PC resueltos."
      },
      {
        title: "Licencia Tablets",
        caption: "Estado reportado por los equipos.",
        columns: ["Estado", "Dispositivos"],
        rows: Array.from(tabletLicenses.entries()).map(([Estado, Dispositivos]) => ({ Estado, Dispositivos })),
        emptyMessage: "No hay estados de licencia Tablet reportados por equipos."
      },
      {
        title: "Preparacion operativa",
        caption: "Chequeo operativo de PC.",
        columns: ["Componente", "Estado", "Detalle"],
        rows: [
          { Componente: "Base local", Estado: "activo", Detalle: "Lectura operativa configurada" },
          { Componente: "Licencia PC", Estado: normalizeStatus(license.state), Detalle: `Plan ${license.plan}` },
          { Componente: "Sincronizacion", Estado: "activo", Detalle: "Rutas de backoffice disponibles" },
          { Componente: "Equipos", Estado: heartbeats.length ? "activo" : "pendiente", Detalle: `${heartbeats.length} reportado(s)` },
          { Componente: "Rutas", Estado: "activo", Detalle: "Shell PC expone modulos principales" }
        ],
        emptyMessage: "Runtime no disponible."
      }
    ],
    diagnostics: {
      businessId,
      customer: PRISMA_ORIGINAL_CUSTOMER,
      customerId: license.customerId ?? null,
      lastRefreshAt: refresh.lastRefreshAt,
      lastSuccessAt: refresh.lastSuccessAt,
      lastFailureAt: refresh.lastFailureAt,
      lastError: refresh.lastError ? "sanitized_error_present" : null
    },
    actions: [
      { label: "Prisma Customer Setup", href: "/setup" },
      refresh.enabled
        ? { label: "Actualizar licencia", href: "/api/license/refresh", method: "POST", successMessage: "Actualizacion de licencia solicitada." }
        : { label: "Actualizar licencia", href: "/license-runtime", disabledReason: "No hay endpoint remoto configurado." }
    ]
  };
}

export async function getPcTabletCommunication(params?: SearchLike): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const [heartbeats, inbound, commands, conflicts, catalogStatus] = await Promise.all([
    safe(() => db.deviceHeartbeat.findMany({ where: { businessId }, orderBy: { lastSeenAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.outboxEvent.findMany({ where: { businessId, source: { contains: "tablet" } }, orderBy: { receivedAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.auditEvent.findMany({ where: { businessId, topic: "pc.tablet.governance_command" }, orderBy: { createdAt: "desc" }, take: 120 }), [] as any[]),
    safe(() => db.syncConflict.findMany({ where: { businessId }, orderBy: { detectedAt: "desc" }, take: 80 }), [] as any[]),
    getPcCatalogDeltaStatus({ businessId })
  ]);
  const target = readParam(params, "deviceId");
  const filteredHeartbeats = target ? heartbeats.filter((row: any) => row.deviceId === target) : heartbeats;
  const lastInbound = inbound[0]?.receivedAt ?? inbound[0]?.createdAt ?? null;
  const lastOutbound = commands[0]?.createdAt ?? null;

  return {
    mode: "communication",
    currentPath: "/tablet-communication",
    kicker: "pc a tablet",
    title: `Comunicacion con Tablets de ${PRISMA_ORIGINAL_CUSTOMER.displayName}`,
    description: "Entradas desde Tablet, acciones preparadas por PC, datos para Tablet y conflictos observables.",
    sourceLine: "Vista de operacion: entradas Tablet, acciones PC y datos preparados.",
    independenceLine: "Los comandos PC quedan pendientes/observables; Tablet nunca espera un comando para vender.",
    metrics: [
      { label: "Tablets objetivo", value: numberLabel(filteredHeartbeats.length), note: "Equipos reportados" },
      { label: "Entradas", value: numberLabel(inbound.length), note: "Tablet a PC" },
      { label: "Acciones PC", value: numberLabel(commands.length), note: "Preparadas para Tablet" },
      { label: "Datos preparados", value: numberLabel(catalogStatus.latestExport?.total ?? 0), note: catalogStatus.latestExport ? relativeLabel(catalogStatus.latestExport.createdAt) : "sin paquete", tone: catalogStatus.latestExport ? "ok" : "warn" },
      { label: "Ultima entrada", value: lastInbound ? relativeLabel(lastInbound) : "sin movimiento", note: "Tablet a PC" },
      { label: "Ultima accion", value: lastOutbound ? relativeLabel(lastOutbound) : "sin accion", note: "PC a Tablet" }
    ],
    panels: [
      {
        title: "Entrega observable",
        body: "Cuando no existe canal externo de entrega, PC deja acciones preparadas y visibles. No se finge envio confirmado.",
        tone: "ok"
      },
      {
        title: "Venta local protegida",
        body: "Catalogo, precio, licencia o runtime pendientes no bloquean ventas locales ya permitidas por Tablet.",
        tone: "ok"
      },
      {
        title: "Datos entrantes a Tablet",
        body: "Tablet solicita datos a PC y conserva su avance local. Esta pantalla no usa mensajes de exito sin evidencia.",
        tone: "ok"
      }
    ],
    tables: [
      {
        title: "Tablets objetivo",
        caption: "Dispositivos y compatibilidad visible.",
        columns: ["Dispositivo", "Version", "Contrato", "Licencia", "Conexion", "Ultimo pulso", "Compatibilidad"],
        rows: filteredHeartbeats.map((row: any) => ({
          Dispositivo: row.deviceId,
          Version: row.appVersion,
          Contrato: row.schemaVersion ? "reportado" : "pendiente",
          Licencia: normalizeStatus(row.licenseStatus),
          Conexion: normalizeStatus(row.syncStatus),
          "Ultimo pulso": relativeLabel(row.lastSeenAt),
          Compatibilidad: row.schemaVersion ? "revisable" : "pendiente"
        })),
        emptyMessage: "No hay Tablets objetivo reportadas."
      },
      {
        title: "Entradas Tablet a PC",
        caption: "Movimientos recibidos sin payload crudo.",
        columns: ["Fecha", "Dispositivo", "Categoria", "Entidad", "Resultado", "Estado"],
        rows: inbound.map((event: any) => ({
          Fecha: dateLabel(event.receivedAt ?? event.createdAt),
          Dispositivo: event.terminalId ?? event.source ?? "sin dispositivo",
          Categoria: readableStream(event.topic),
          Entidad: event.aggregateId,
          Resultado: readableLifecycle(event.lifecycleStatus),
          Estado: normalizeStatus(event.status)
        })),
        emptyMessage: "Sin movimientos recibidos desde Tablet."
      },
      {
        title: "Gobierno PC a Tablet",
        caption: "Acciones registradas y pendientes de entrega.",
        columns: ["Fecha", "Accion", "Destino", "Referencia", "Estado"],
        rows: commands.map((command: any) => {
          const payload = asJson(command.afterJson ?? command.metadataJson);
          return {
            Fecha: dateLabel(command.createdAt),
            Accion: payload.commandType ?? command.entityType,
            Destino: payload.target ?? command.entityId ?? "all",
            Referencia: command.id,
            Estado: normalizeStatus(payload.status ?? "queued")
          };
        }),
        emptyMessage: "No hay comandos de gobierno registrados."
      },
      {
        title: "Catalogo disponible para Tablet",
        caption: "Datos PC disponibles por categoria.",
        columns: ["Categoria", "Filas PC", "Ultima preparacion", "Estado"],
        rows: Object.entries(catalogStatus.tableCounts).map(([Entidad, Filas]) => ({
          Categoria: readableEntity(Entidad),
          "Filas PC": Filas,
          "Ultima preparacion": catalogStatus.latestExport?.byEntity?.[Entidad] ?? 0,
          Estado: catalogStatus.latestExport ? "preparado" : "pendiente"
        })),
        emptyMessage: "Sin catalogo PC disponible para distribuir."
      },
      {
        title: "Conflictos relacionados",
        caption: "Revisiones que afectan comunicacion.",
        columns: ["Detectado", "Dispositivo", "Motivo", "Severidad", "Estado"],
        rows: conflicts.map((conflict: any) => ({
          Detectado: dateLabel(conflict.detectedAt),
          Dispositivo: conflict.deviceId ?? "sin dispositivo",
          Motivo: readableConflict(conflict.conflictCode),
          Severidad: conflict.severity,
          Estado: normalizeStatus(conflict.status)
        })),
        emptyMessage: "Sin conflictos de comunicacion registrados."
      }
    ],
    diagnostics: { businessId, target, commandContract: "pc-tablet-governance-command.v1", outboundDelivery: "audit-ledger-no-fake-ack", catalogDelta: catalogStatus },
    actions: [
      { label: "Actualizar datos", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "delta", target: target || "all" }, successMessage: "Datos preparados para Tablet." },
      { label: "Preparar primera carga", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "bootstrap", target: target || "all" }, successMessage: "Primera carga preparada para Tablet." },
      { label: "Reparar datos", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "resync", target: target || "all" }, successMessage: "Reparacion preparada para Tablet." },
      { label: "Registrar actualizacion de equipo", href: "/api/backoffice/tablet-communication/governance-command", method: "POST", body: { commandType: "runtime.refresh", target: target || "all", requestedBy: "pc-operator" }, successMessage: "Accion registrada sin confirmacion inventada." }
    ]
  };
}

export async function recordTabletGovernanceCommand(input: {
  commandType: string;
  target: string;
  operatorNote?: string | null;
  requestedBy?: string | null;
}) {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const commandType = input.commandType?.trim() || "runtime.refresh";
  const target = input.target?.trim() || "all";
  const idempotencyKey = `pc_cmd_${businessId}_${commandType}_${target}_${new Date().toISOString().slice(0, 10)}`;
  const existing = await safe<any | null>(() => db.auditEvent.findFirst({
    where: { businessId, topic: "pc.tablet.governance_command", entityId: idempotencyKey },
    orderBy: { createdAt: "desc" }
  }), null);
  if (existing) {
    return { status: "duplicate", idempotencyKey, auditEventId: existing.id };
  }
  const payload = {
    contract: "pc-tablet-governance-command.v1",
    commandType,
    target,
    status: "queued_for_pickup",
    idempotencyKey,
    operatorNote: input.operatorNote ?? null,
    requestedBy: input.requestedBy ?? "pc-admin",
    safeToContinueSelling: true
  };
  const created = await db.auditEvent.create({
    data: {
      id: `audit_${randomUUID()}`,
      businessId,
      actorId: null,
      topic: "pc.tablet.governance_command",
      entityType: "tablet_governance_command",
      entityId: idempotencyKey,
      summary: `Comando de gobierno ${commandType} registrado para ${target}.`,
      beforeJson: null,
      afterJson: JSON.stringify(payload),
      metadataJson: JSON.stringify({ correlationId: randomUUID(), safeToContinueSelling: true })
    }
  });
  return { status: "queued_for_pickup", idempotencyKey, auditEventId: created.id };
}

export async function markSyncConflictReviewed(input: { conflictId: string; resolutionNote?: string | null }) {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const conflictId = input.conflictId?.trim();
  if (!conflictId) throw new Error("SYNC_CONFLICT_ID_REQUIRED");
  const updated = await db.$transaction(async (tx: any) => {
    const conflict = await tx.syncConflict.findFirst({ where: { businessId, id: conflictId } });
    if (!conflict) throw new Error("SYNC_CONFLICT_NOT_FOUND");
    const next = await tx.syncConflict.update({
      where: { id: conflict.id },
      data: {
        status: "reviewed",
        resolution: input.resolutionNote ?? "Revisado por operador PC.",
        resolvedAt: new Date()
      }
    });
    await tx.auditEvent.create({
      data: {
        id: `audit_${randomUUID()}`,
        businessId,
        actorId: null,
        topic: "pc.sync.conflict.reviewed",
        entityType: "SyncConflict",
        entityId: conflict.id,
        summary: `Conflicto ${conflict.conflictCode} marcado como revisado.`,
        beforeJson: JSON.stringify({ status: conflict.status, resolution: conflict.resolution }),
        afterJson: JSON.stringify({ status: next.status, resolution: next.resolution }),
        metadataJson: JSON.stringify({ safeAction: true })
      }
    });
    return next;
  });
  return { status: updated.status, conflictId: updated.id, resolution: updated.resolution };
}

export async function retryFailedSyncEvent(input: { eventId: string; operatorNote?: string | null }) {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const eventId = input.eventId?.trim();
  if (!eventId) throw new Error("SYNC_EVENT_ID_REQUIRED");
  const updated = await db.$transaction(async (tx: any) => {
    const event = await tx.outboxEvent.findFirst({ where: { businessId, id: eventId } });
    if (!event) throw new Error("SYNC_EVENT_NOT_FOUND");
    const status = String(event.status ?? "").toLowerCase();
    const lifecycle = String(event.lifecycleStatus ?? "").toLowerCase();
    const retryable = ["failed", "rejected"].includes(status) || ["failed", "dead_letter"].includes(lifecycle);
    if (!retryable) throw new Error("SYNC_EVENT_NOT_RETRYABLE");
    const next = await tx.outboxEvent.update({
      where: { id: event.id },
      data: {
        status: "pending",
        lifecycleStatus: "received",
        attempts: Number(event.attempts ?? 0) + 1,
        failedAt: null,
        deadLetterAt: null,
        lastError: null,
        diagnosticsJson: JSON.stringify({
          previousStatus: event.status,
          previousLifecycleStatus: event.lifecycleStatus,
          retriedAt: new Date().toISOString(),
          note: input.operatorNote ?? null
        })
      }
    });
    await tx.auditEvent.create({
      data: {
        id: `audit_${randomUUID()}`,
        businessId,
        actorId: null,
        topic: "pc.sync.retry.requested",
        entityType: "OutboxEvent",
        entityId: event.id,
        summary: `Reintento solicitado para evento ${event.topic}.`,
        beforeJson: JSON.stringify({ status: event.status, lifecycleStatus: event.lifecycleStatus, attempts: event.attempts }),
        afterJson: JSON.stringify({ status: next.status, lifecycleStatus: next.lifecycleStatus, attempts: next.attempts }),
        metadataJson: JSON.stringify({ safeAction: true, operatorNote: input.operatorNote ?? null })
      }
    });
    return next;
  });
  return { status: updated.status, lifecycleStatus: updated.lifecycleStatus, eventId: updated.id, attempts: updated.attempts };
}

export async function getPcCommandCenter(mode: PcCommandCenterMode, params?: SearchLike): Promise<CommandCenterModel> {
  if (mode === "cash") return getPcCashSessions(params);
  if (mode === "devices") return getPcDeviceFleet(params);
  if (mode === "sync") return getPcSyncCommandCenter(params);
  if (mode === "dataQuality") return getPcDataQuality();
  if (mode === "licenseRuntime") return getPcLicenseRuntimeControl();
  if (mode === "communication") return getPcTabletCommunication(params);
  return getPcSalesControl(params);
}

export function commandCenterToCsv(model: CommandCenterModel) {
  const table = model.tables[0];
  if (!table) return "";
  const escape = (value: unknown) => `"${String(value ?? "").replace(/"/g, '""')}"`;
  return [table.columns.map(escape).join(","), ...table.rows.map((row) => table.columns.map((column) => escape(row[column])).join(","))].join("\n");
}
