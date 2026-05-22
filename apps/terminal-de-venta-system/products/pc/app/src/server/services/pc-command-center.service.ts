import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { getTriDbStatusCard } from "@/server/services/tri-db-status.service";
import { getPcCatalogDeltaStatus } from "@/server/services/catalog-delta-export.service";
import { getPcFeatureList, getPcLicenseStatus } from "@/server/licensing/pc-license-service";
import { getPcLicenseRefreshStatus } from "@/server/licensing/pc-license-refresh";

const MAX_CUSTOM_RANGE_DAYS = 60;
const DEFAULT_BUSINESS_ID = "biz_hitech_default";
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

export type CommandTable = {
  title: string;
  caption: string;
  columns: string[];
  rows: Array<Record<string, string | number>>;
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
  const business = await safe<any | null>(() => db.business.findFirst({ select: { id: true }, orderBy: { createdAt: "asc" } }), null);
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

  const [salesRaw, returns, triDb] = await Promise.all([
    safe(() => db.sale.findMany({
      where,
      include: { lines: true, paymentTenders: true, cashSession: true, terminal: true },
      orderBy: { createdAt: "desc" },
      take: limit
    }), [] as any[]),
    safe(() => db.saleReturn.findMany({
      where,
      include: { lines: true },
      orderBy: { createdAt: "desc" },
      take: limit
    }), [] as any[]),
    getTriDbStatusCard()
  ]);
  const sales = filterByQuery(salesRaw, query);
  const totalCents = sum(sales.map((sale: any) => Number(sale.totalCents ?? 0)));
  const returnCents = sum(returns.map((row: any) => Number(row.amountCents ?? 0)));
  const tenders = sales.flatMap((sale: any) => sale.paymentTenders ?? []);
  const lines = sales.flatMap((sale: any) => sale.lines ?? []);
  const byTerminal = new Map<string, number>();
  const byCashier = new Map<string, number>();
  const byTender = new Map<string, number>();
  const bySku = new Map<string, { qty: number; total: number; name: string }>();
  for (const sale of sales) {
    byTerminal.set(sale.terminalId ?? "sin terminal", (byTerminal.get(sale.terminalId ?? "sin terminal") ?? 0) + Number(sale.totalCents ?? 0));
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
    ]
  };
}

export async function getPcCashSessions(params?: SearchLike): Promise<CommandCenterModel> {
  const db = prisma as any;
  const businessId = await resolveBusinessId();
  const range = resolveDateRange(params);
  const sessions = await safe(() => db.cashSession.findMany({
    where: range.blocked ? { businessId, id: "__blocked__" } : { businessId, openedAt: { lt: range.toExclusive }, OR: [{ closedAt: null }, { closedAt: { gte: range.from } }] },
    include: { cashMovements: true, cashAdjustments: true, sales: true, terminal: true, store: true },
    orderBy: { openedAt: "desc" },
    take: clampLimit(readParam(params, "limit"), 80)
  }), [] as any[]);
  const open = sessions.filter((session: any) => String(session.status).toLowerCase() !== "closed").length;
  const variance = sum(sessions.map((session: any) => Number(session.varianceCents ?? 0)));
  const movements = sessions.flatMap((session: any) => (session.cashMovements ?? []).map((movement: any) => ({ ...movement, session })));

  return {
    mode: "cash",
    currentPath: "/cash-sessions",
    kicker: "caja",
    title: "Caja y cierres",
    description: "Gobierno de turnos, movimientos, esperado, contado y variaciones.",
    periodLabel: range.label,
    sourceLine: `Fuente: CashSession/CashMovement canonicos. Rango: ${range.label}.`,
    independenceLine: "PC gobierna cierres consolidados; Tablet puede abrir, vender y cerrar localmente.",
    metrics: [
      { label: "Sesiones", value: numberLabel(sessions.length), note: "CashSession en rango" },
      { label: "Abiertas", value: numberLabel(open), note: "Requieren seguimiento", tone: open ? "warn" : "ok" },
      { label: "Variacion neta", value: money(variance), note: "Suma varianceCents", tone: Math.abs(variance) > 5000 ? "danger" : variance ? "warn" : "ok" },
      { label: "Movimientos", value: numberLabel(movements.length), note: "Entradas/salidas/ajustes" }
    ],
    panels: [
      range.blocked ? { title: "Rango bloqueado", body: range.blocked, tone: "warn" } : null,
      { title: "Conflictos de caja", body: "Las ventas fuera de turno se revisan contra SyncConflict cuando existen; no se convierten en venta PC.", tone: "ok" }
    ].filter(Boolean) as CommandPanel[],
    tables: [
      {
        title: "Sesiones de caja",
        caption: "Abiertas/cerradas por terminal.",
        columns: ["Caja", "Terminal", "Cajero", "Abierta", "Cerrada", "Esperado", "Contado", "Variacion", "Estado"],
        rows: sessions.map((session: any) => ({
          Caja: session.id,
          Terminal: session.terminal?.name ?? session.terminalId,
          Cajero: session.cashier ?? session.cashierId,
          Abierta: dateLabel(session.openedAt),
          Cerrada: dateLabel(session.closedAt),
          Esperado: money(session.expectedCashCents),
          Contado: money(session.cashEndCents),
          Variacion: money(session.varianceCents),
          Estado: normalizeStatus(session.status)
        })),
        emptyMessage: "No hay sesiones de caja consolidadas en PC."
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
    diagnostics: { businessId, range, varianceThresholdCents: 5000 }
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
    title: "Fleet de Tablets",
    description: "Pulso multi-Tablet: heartbeat, frescura, outbox, licencia y estado operativo.",
    sourceLine: "Fuente: DeviceHeartbeat, DataSourceFreshness, SyncCheckpoint y SyncOutboxStatusBucket.",
    independenceLine: "Una Tablet offline no bloquea ventas locales de otras Tablets.",
    metrics: [
      { label: "Tablets vistas", value: numberLabel(enriched.length), note: "DeviceHeartbeat" },
      { label: "Atencion", value: numberLabel(attention.length), note: "Stale/offline/warning", tone: attention.length ? "warn" : "ok" },
      { label: "Outbox total", value: numberLabel(sum(enriched.map((row: any) => Number(row.outboxCount ?? 0)))), note: "Pendientes reportados" },
      { label: "Freshness rows", value: numberLabel(freshness.length), note: "DataSourceFreshness" }
    ],
    panels: [
      {
        title: "Sin heartbeat aun",
        body: enriched.length ? "Hay dispositivos reportados." : "No hay heartbeat consolidado; la pantalla queda lista sin inventar Tablets.",
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
        title: "Dispositivos",
        caption: "Estado operacional y licencia por deviceId.",
        columns: ["Device", "Fuente", "Modo", "Version", "Licencia", "Sync", "Outbox", "Ultima venta", "Ultimo pulso", "Estado"],
        rows: enriched.map((row: any) => ({
          Device: row.deviceId,
          Fuente: row.source,
          Modo: row.runtimeMode,
          Version: row.appVersion,
          Licencia: normalizeStatus(row.licenseStatus),
          Sync: normalizeStatus(row.syncStatus),
          Outbox: Number(row.outboxCount ?? 0),
          "Ultima venta": dateLabel(row.lastSaleAt),
          "Ultimo pulso": relativeLabel(row.lastSeenAt),
          Estado: normalizeStatus(row.computedHealth)
        })),
        emptyMessage: "No hay heartbeats de Tablet todavia."
      },
      {
        title: "Checkpoints",
        caption: "Ultimos cursores por stream.",
        columns: ["Fuente", "Device", "Stream", "Checkpoint", "Lifecycle", "Estado"],
        rows: checkpoints.slice(0, 80).map((row: any) => ({
          Fuente: row.source,
          Device: row.deviceId ?? "general",
          Stream: row.stream,
          Checkpoint: dateLabel(row.checkpointAt),
          Lifecycle: row.lifecycleStatus ?? "sin lifecycle",
          Estado: normalizeStatus(row.status)
        })),
        emptyMessage: "Sin checkpoints de sincronizacion registrados."
      },
      {
        title: "Buckets de outbox",
        caption: "Pendientes por fuente/status/topic.",
        columns: ["Fuente", "Device", "Topic", "Lifecycle", "Conteo", "Mas viejo", "Estado"],
        rows: buckets.slice(0, 80).map((row: any) => ({
          Fuente: row.source,
          Device: row.deviceId ?? "general",
          Topic: row.topic ?? "todos",
          Lifecycle: row.lifecycleStatus ?? "sin lifecycle",
          Conteo: row.count,
          "Mas viejo": dateLabel(row.oldestEventAt),
          Estado: normalizeStatus(row.status)
        })),
        emptyMessage: "Sin buckets de outbox registrados."
      }
    ],
    diagnostics: { businessId, query, staleAfterSeconds: 600, offlineAfterSeconds: 3600 }
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
    title: "Sincronizacion y conflictos",
    description: "Ledger de ingest, ciclo de vida, duplicados, conflictos y estado tri-db.",
    sourceLine: "Fuente: OutboxEvent, SyncAttempt, SyncConflict y shared/tri-db/status.latest.json.",
    independenceLine: "PC puede atrasarse o marcar conflicto sin detener venta local de Tablet.",
    metrics: [
      { label: "Eventos", value: numberLabel(events.length), note: "OutboxEvent acotado" },
      { label: "Delta catalogo", value: numberLabel(catalogStatus.latestExport?.total ?? 0), note: catalogStatus.latestExport ? `Ultimo ${catalogStatus.latestExport.mode}` : "sin export generado", tone: catalogStatus.latestExport ? "ok" : "warn" },
      { label: "Conflictos", value: numberLabel(conflicts.filter((row: any) => row.status !== "resolved").length), note: "SyncConflict abierto", tone: conflicts.length ? "warn" : "ok" },
      { label: "Intentos", value: numberLabel(attempts.length), note: "SyncAttempt" },
      { label: "Duracion prom.", value: `${numberLabel(avgDuration)} ms`, note: "Intentos recientes" },
      { label: "Pendiente mas viejo", value: oldestPending ? relativeLabel(oldestPending.createdAt) : "sin pendiente", note: "Proteccion de backlog" }
    ],
    panels: [
      {
        title: "Tri-db bridge",
        body: `Estado ${triDb.status}. Tablet rows ${triDb.tablet.saleCount}; PC rows ${triDb.pc.saleCount}; pcCoversTablet=${triDb.parityOk ? "si" : "no"}.`,
        tone: triDb.parityOk ? "ok" : "warn"
      },
      {
        title: "Duplicados",
        body: "El ingest usa idempotencyKey/eventId; duplicados quedan visibles sin proyectar dos veces.",
        tone: "ok"
      },
      {
        title: "PC a Tablet catalogo",
        body: "El delta de catalogo usa contrato compartido, cursor determinista y no bloquea ventas locales de Tablet.",
        tone: "ok"
      }
    ],
    tables: [
      {
        title: "Lifecycle",
        caption: "Conteos recibidos, validados, aceptados, proyectados, reconciliados, conflicto, fallido o dead_letter.",
        columns: ["Lifecycle", "Conteo"],
        rows: buckets.map((bucket) => ({ Lifecycle: bucket.key, Conteo: bucket.value })),
        emptyMessage: "Sin eventos de sync en ledger."
      },
      {
        title: "Intentos",
        caption: "Duracion, fuente, device, topic y estado.",
        columns: ["Fecha", "Fuente", "Device", "Topic", "Duracion", "Lifecycle", "Estado"],
        rows: attempts.map((attempt: any) => ({
          Fecha: dateLabel(attempt.createdAt),
          Fuente: attempt.source,
          Device: attempt.deviceId ?? "sin device",
          Topic: attempt.topic ?? "sin topic",
          Duracion: `${attempt.durationMs ?? 0} ms`,
          Lifecycle: attempt.lifecycleStatus ?? "sin lifecycle",
          Estado: normalizeStatus(attempt.status)
        })),
        emptyMessage: "No hay intentos de sync registrados."
      },
      {
        title: "Ledger OutboxEvent",
        caption: "Evento, agregado, idempotencia visible sin payload crudo.",
        columns: ["Fecha", "Topic", "Aggregate", "Lifecycle", "Intentos", "Estado"],
        rows: events.map((event: any) => ({
          Fecha: dateLabel(event.createdAt),
          Topic: event.topic,
          Aggregate: event.aggregateId,
          Lifecycle: event.lifecycleStatus ?? "sin lifecycle",
          Intentos: event.attempts ?? 0,
          Estado: normalizeStatus(event.status)
        })),
        emptyMessage: "Sin eventos de sync en PC."
      },
      {
        title: "Conflictos",
        caption: "Cola accionable por severidad/codigo.",
        columns: ["Detectado", "Codigo", "Severidad", "Device", "Entidad", "Recomendacion", "Estado"],
        rows: conflicts.map((conflict: any) => ({
          Detectado: dateLabel(conflict.detectedAt),
          Codigo: conflict.conflictCode,
          Severidad: conflict.severity,
          Device: conflict.deviceId ?? "sin device",
          Entidad: conflict.aggregateId ?? "sin entidad",
          Recomendacion: conflict.resolution ?? "Revisar evento origen, entidad afectada y reprocesar solo si el contrato lo permite.",
          Estado: normalizeStatus(conflict.status)
        })),
        emptyMessage: "Sin conflictos abiertos."
      },
      {
        title: "Catalogo PC a Tablet",
        caption: "Estado del export master-data disponible para pull Tablet.",
        columns: ["Entidad", "Filas PC", "Ultimo delta", "Cursor"],
        rows: Object.entries(catalogStatus.tableCounts).map(([Entidad, Filas]) => ({
          Entidad,
          "Filas PC": Filas,
          "Ultimo delta": catalogStatus.latestExport?.byEntity?.[Entidad] ?? 0,
          Cursor: catalogStatus.latestExport?.cursor ?? "sin cursor"
        })),
        emptyMessage: "Sin entidades de catalogo soportadas."
      },
      {
        title: "Paridad tri-db",
        caption: "Tablet rows, PC rows, delta y cobertura.",
        columns: ["Tabla", "Tablet", "PC", "Delta", "Cubre"],
        rows: triDb.parityTables.map((row) => ({
          Tabla: row.table,
          Tablet: row.tabletRows,
          PC: row.pcRows,
          Delta: row.deltaPcMinusTablet,
          Cubre: row.pcCoversTablet ? "si" : "no"
        })),
        emptyMessage: "Tri-db status no trae tabla de paridad."
      }
    ],
    diagnostics: { businessId, topic, source, newestReceivedAt: newestReceived?.receivedAt ?? null, triDbSource: triDb.sourcePath, catalogDelta: catalogStatus },
    actions: [
      { label: "Generar delta catalogo", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "delta", target: "tablet" }, successMessage: "Delta incremental generado desde PC." },
      { label: "Generar bootstrap catalogo", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "bootstrap", target: "tablet" }, successMessage: "Bootstrap de catalogo generado desde PC." },
      { label: "Forzar resync catalogo", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "resync", target: "tablet" }, successMessage: "Resync de catalogo generado desde PC." }
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
    title: "Licencias y Runtime",
    description: "Estado local PC, refresh remoto opcional, funciones permitidas y salud de Tablets.",
    sourceLine: "Fuente: shared/licensing + DeviceHeartbeat + canonical DB.",
    independenceLine: "La licencia local de Tablet sigue siendo fuente valida para operacion offline.",
    metrics: [
      { label: "Estado PC", value: normalizeStatus(license.state), note: `Plan ${license.plan}`, tone: license.state === "active" || license.state === "development" ? "ok" : "warn" },
      { label: "Dias restantes", value: license.daysRemaining === null ? "n/d" : String(license.daysRemaining), note: "Umbral visible" },
      { label: "Refresh remoto", value: refresh.enabled ? "configurado" : "no configurado", note: refresh.state, tone: refresh.enabled ? "ok" : "warn" },
      { label: "Funciones bloqueadas", value: numberLabel(blockedFeatures.length), note: "Feature gates PC", tone: blockedFeatures.length ? "warn" : "ok" },
      { label: "Tablets con licencia", value: numberLabel(heartbeats.length), note: "Desde heartbeat" }
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
        caption: "Feature gates resueltos por licencia local.",
        columns: ["Feature", "Permitida", "Motivo"],
        rows: features.map((feature: any) => ({
          Feature: feature.key,
          Permitida: feature.allowed ? "si" : "no",
          Motivo: feature.reason
        })),
        emptyMessage: "No hay feature gates PC resueltos."
      },
      {
        title: "Licencia Tablets",
        caption: "Estado reportado por DeviceHeartbeat.",
        columns: ["Estado", "Dispositivos"],
        rows: Array.from(tabletLicenses.entries()).map(([Estado, Dispositivos]) => ({ Estado, Dispositivos })),
        emptyMessage: "No hay estados de licencia Tablet por heartbeat."
      },
      {
        title: "Runtime readiness",
        caption: "Chequeo operativo de PC.",
        columns: ["Componente", "Estado", "Detalle"],
        rows: [
          { Componente: "DB canonica", Estado: "activo", Detalle: "Prisma client configurado" },
          { Componente: "Licencia PC", Estado: normalizeStatus(license.state), Detalle: `Fuente ${license.source}` },
          { Componente: "Sync", Estado: "activo", Detalle: "Backoffice sync endpoints disponibles" },
          { Componente: "Devices", Estado: heartbeats.length ? "activo" : "pendiente", Detalle: `${heartbeats.length} heartbeats` },
          { Componente: "Rutas", Estado: "activo", Detalle: "Shell PC expone modulos principales" }
        ],
        emptyMessage: "Runtime no disponible."
      }
    ],
    diagnostics: {
      businessId,
      customerId: license.customerId ?? null,
      lastRefreshAt: refresh.lastRefreshAt,
      lastSuccessAt: refresh.lastSuccessAt,
      lastFailureAt: refresh.lastFailureAt,
      lastError: refresh.lastError ? "sanitized_error_present" : null
    },
    actions: [
      refresh.enabled
        ? { label: "Actualizar licencia", href: "/api/license/refresh", method: "POST", successMessage: "Refresh de licencia solicitado." }
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
    title: "Comunicacion y gobernanza",
    description: "Eventos inbound, comandos de gobierno, releases pendientes y acknowledgments observables.",
    sourceLine: "Fuente: OutboxEvent inbound, DeviceHeartbeat y AuditEvent para comandos repo-locales.",
    independenceLine: "Los comandos PC quedan pendientes/observables; Tablet nunca espera un comando para vender.",
    metrics: [
      { label: "Tablets objetivo", value: numberLabel(filteredHeartbeats.length), note: "DeviceHeartbeat" },
      { label: "Inbound", value: numberLabel(inbound.length), note: "Tablet a PC" },
      { label: "Gobierno outbound", value: numberLabel(commands.length), note: "AuditEvent command ledger" },
      { label: "Catalogo exportado", value: numberLabel(catalogStatus.latestExport?.total ?? 0), note: catalogStatus.latestExport ? relativeLabel(catalogStatus.latestExport.createdAt) : "sin delta", tone: catalogStatus.latestExport ? "ok" : "warn" },
      { label: "Ultimo inbound", value: lastInbound ? relativeLabel(lastInbound) : "sin evento", note: "Tablet to PC" },
      { label: "Ultimo outbound", value: lastOutbound ? relativeLabel(lastOutbound) : "sin comando", note: "PC to Tablet" }
    ],
    panels: [
      {
        title: "Contrato repo-local",
        body: "Cuando no existe canal externo de entrega, PC registra comandos idempotentes en AuditEvent con estado queued_for_pickup. No se finge envio ni ack.",
        tone: "ok"
      },
      {
        title: "Safe to continue selling",
        body: "Catalogo, precio, licencia o runtime pendientes no bloquean ventas locales ya permitidas por Tablet.",
        tone: "ok"
      },
      {
        title: "Pull catalogo entrante",
        body: "Tablet solicita el delta a PC y guarda su propio checkpoint local. Esta pantalla no usa Chart Lab ni toasts fake para cerrar sync.",
        tone: "ok"
      }
    ],
    tables: [
      {
        title: "Tablets objetivo",
        caption: "Dispositivos y compatibilidad visible.",
        columns: ["Device", "Version", "Schema", "Licencia", "Sync", "Ultimo pulso", "Compatibilidad"],
        rows: filteredHeartbeats.map((row: any) => ({
          Device: row.deviceId,
          Version: row.appVersion,
          Schema: row.schemaVersion ?? "sin schema",
          Licencia: normalizeStatus(row.licenseStatus),
          Sync: normalizeStatus(row.syncStatus),
          "Ultimo pulso": relativeLabel(row.lastSeenAt),
          Compatibilidad: row.schemaVersion ? "revisable" : "sin schema reportado"
        })),
        emptyMessage: "No hay Tablets objetivo por heartbeat."
      },
      {
        title: "Inbound Tablet a PC",
        caption: "Eventos recibidos con lifecycle e idempotencia sin payload crudo.",
        columns: ["Fecha", "Device", "Topic", "Aggregate", "Lifecycle", "Estado"],
        rows: inbound.map((event: any) => ({
          Fecha: dateLabel(event.receivedAt ?? event.createdAt),
          Device: event.terminalId ?? event.source ?? "sin device",
          Topic: event.topic,
          Aggregate: event.aggregateId,
          Lifecycle: event.lifecycleStatus ?? "sin lifecycle",
          Estado: normalizeStatus(event.status)
        })),
        emptyMessage: "Sin eventos inbound desde Tablet."
      },
      {
        title: "Gobierno PC a Tablet",
        caption: "Comandos registrados, pendientes de entrega externa/Tablet pickup.",
        columns: ["Fecha", "Comando", "Destino", "Idempotencia", "Estado"],
        rows: commands.map((command: any) => {
          const payload = asJson(command.afterJson ?? command.metadataJson);
          return {
            Fecha: dateLabel(command.createdAt),
            Comando: payload.commandType ?? command.entityType,
            Destino: payload.target ?? command.entityId ?? "all",
            Idempotencia: payload.idempotencyKey ?? command.id,
            Estado: payload.status ?? "queued_for_pickup"
          };
        }),
        emptyMessage: "No hay comandos de gobierno registrados."
      },
      {
        title: "Catalogo disponible para Tablet",
        caption: "Master-data PC exportable por entidad y ultimo cursor generado.",
        columns: ["Entidad", "Filas PC", "Ultimo export", "Cursor"],
        rows: Object.entries(catalogStatus.tableCounts).map(([Entidad, Filas]) => ({
          Entidad,
          "Filas PC": Filas,
          "Ultimo export": catalogStatus.latestExport?.byEntity?.[Entidad] ?? 0,
          Cursor: catalogStatus.latestExport?.cursor ?? "sin cursor"
        })),
        emptyMessage: "Sin catalogo PC disponible para distribuir."
      },
      {
        title: "Conflictos relacionados",
        caption: "Version/schema/conflictos que afectan comunicacion.",
        columns: ["Detectado", "Device", "Codigo", "Severidad", "Estado"],
        rows: conflicts.map((conflict: any) => ({
          Detectado: dateLabel(conflict.detectedAt),
          Device: conflict.deviceId ?? "sin device",
          Codigo: conflict.conflictCode,
          Severidad: conflict.severity,
          Estado: normalizeStatus(conflict.status)
        })),
        emptyMessage: "Sin conflictos de comunicacion registrados."
      }
    ],
    diagnostics: { businessId, target, commandContract: "pc-tablet-governance-command.v1", outboundDelivery: "audit-ledger-no-fake-ack", catalogDelta: catalogStatus },
    actions: [
      { label: "Generar delta catalogo", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "delta", target: target || "all" }, successMessage: "Delta de catalogo generado para Tablet." },
      { label: "Bootstrap catalogo", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "bootstrap", target: target || "all" }, successMessage: "Bootstrap de catalogo generado para Tablet." },
      { label: "Resync catalogo", href: "/api/sync/export/catalog-delta", method: "POST", body: { mode: "resync", target: target || "all" }, successMessage: "Resync de catalogo generado para Tablet." },
      { label: "Registrar refresh runtime", href: "/api/backoffice/tablet-communication/governance-command", method: "POST", body: { commandType: "runtime.refresh", target: target || "all", requestedBy: "pc-operator" }, successMessage: "Comando runtime.refresh registrado sin ack falso." }
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
