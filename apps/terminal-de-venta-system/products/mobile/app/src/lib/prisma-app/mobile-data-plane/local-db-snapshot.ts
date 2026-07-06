import { existsSync } from "node:fs";
import path from "node:path";
import type {
  CanonicalCashState,
  CanonicalInventoryItem,
  CanonicalInventoryWatchlist,
  CanonicalOutboxState,
  CanonicalPcDashboard,
  CanonicalSale,
  CanonicalSalesToday,
  MobileDataPlaneConfig,
  UpstreamProbe
} from "./types";

type SqliteDatabase = {
  prepare(query: string): {
    all(...params: unknown[]): Record<string, unknown>[];
    get(...params: unknown[]): Record<string, unknown> | undefined;
  };
  close(): void;
};

type LocalDbSnapshot = {
  probes: UpstreamProbe[];
  salesToday: CanonicalSalesToday;
  inventory: CanonicalInventoryWatchlist;
  outbox: CanonicalOutboxState;
  cash: CanonicalCashState;
  pc: CanonicalPcDashboard;
  warnings: string[];
};

const LOCAL_SOURCE_LABEL = "Fuente local operativa";

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function sqliteStamp(date: Date) {
  return date.toISOString().slice(0, 19);
}

function looksLikeTerminalRoot(candidate: string) {
  return existsSync(path.join(candidate, "terminal_de_venta.cmd"))
    && existsSync(path.join(candidate, "products", "tablet", "app", "data", "tablet-pos.db"));
}

function findTerminalRoot(start: string) {
  let current = path.resolve(start);
  for (;;) {
    if (looksLikeTerminalRoot(current)) return current;
    const nested = path.join(current, "apps", "terminal-de-venta-system");
    if (looksLikeTerminalRoot(nested)) return nested;
    const parent = path.dirname(current);
    if (parent === current) return null;
    current = parent;
  }
}

async function openSqliteReadOnly(dbPath: string): Promise<SqliteDatabase | null> {
  try {
    const dynamicImport = new Function("specifier", "return import(specifier)") as (specifier: string) => Promise<any>;
    const sqlite = await dynamicImport("node:sqlite");
    return new sqlite.DatabaseSync(dbPath, { readOnly: true }) as SqliteDatabase;
  } catch {
    return null;
  }
}

function text(value: unknown, fallback = "") {
  const parsed = String(value ?? "").trim();
  return parsed || fallback;
}

function cents(value: unknown) {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? Math.max(0, Math.round(parsed)) : 0;
}

function intValue(value: unknown) {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? Math.max(0, Math.trunc(parsed)) : 0;
}

function salesQuery(db: SqliteDatabase, businessId: string, from: Date, toExclusive: Date) {
  return db.prepare(`
    SELECT
      id,
      folio,
      createdAt,
      completedAt,
      totalCents,
      subtotalCents,
      discountCents,
      paymentMethod,
      cashier,
      terminalId
    FROM Sale
    WHERE businessId = ?
      AND status IN ('PAID', 'COMPLETED')
      AND createdAt >= ?
      AND createdAt < ?
    ORDER BY createdAt DESC
  `).all(businessId, sqliteStamp(from), sqliteStamp(toExclusive));
}

function saleLines(db: SqliteDatabase, businessId: string, saleIds: string[]) {
  if (!saleIds.length) return new Map<string, Record<string, unknown>[]>();
  const placeholders = saleIds.map(() => "?").join(",");
  const rows = db.prepare(`
    SELECT saleId, productId, sku, productName, qty, priceCents, totalCents
    FROM SaleLine
    WHERE businessId = ? AND saleId IN (${placeholders})
  `).all(businessId, ...saleIds);
  const bySale = new Map<string, Record<string, unknown>[]>();
  for (const row of rows) {
    const saleId = text(row.saleId);
    bySale.set(saleId, [...(bySale.get(saleId) ?? []), row]);
  }
  return bySale;
}

function hourlyBuckets(sales: CanonicalSale[]) {
  const buckets = new Map<string, { hour: string; amountCents: number; tickets: number }>();
  for (const sale of sales) {
    const hour = String(new Date(sale.completedAt || sale.createdAt).getHours()).padStart(2, "0") + ":00";
    const current = buckets.get(hour) ?? { hour, amountCents: 0, tickets: 0 };
    current.amountCents += sale.totalCents;
    current.tickets += 1;
    buckets.set(hour, current);
  }
  return Array.from(buckets.values()).sort((a, b) => a.hour.localeCompare(b.hour));
}

function topCategory(sales: CanonicalSale[]) {
  const totals = new Map<string, number>();
  for (const sale of sales) {
    for (const line of sale.lines) {
      totals.set(line.category, (totals.get(line.category) ?? 0) + line.totalCents);
    }
  }
  return Array.from(totals.entries()).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "Sin categoría dominante";
}

function canonicalSales(db: SqliteDatabase, businessId: string, from: Date, toExclusive: Date): CanonicalSale[] {
  const rows = salesQuery(db, businessId, from, toExclusive);
  const linesBySale = saleLines(db, businessId, rows.map((row) => text(row.id)).filter(Boolean));
  return rows.map((row, index) => {
    const saleId = text(row.id, `sale_${index}`);
    const lines = (linesBySale.get(saleId) ?? []).map((line, lineIndex) => ({
      productId: text(line.productId, `product_${lineIndex}`),
      sku: text(line.sku, `SKU-${lineIndex + 1}`),
      name: text(line.productName, "Producto"),
      qty: intValue(line.qty),
      unitPriceCents: cents(line.priceCents),
      totalCents: cents(line.totalCents),
      category: "Operación"
    }));
    return {
      id: saleId,
      ticketNumber: text(row.folio, saleId),
      createdAt: text(row.createdAt, new Date().toISOString()),
      completedAt: text(row.completedAt, text(row.createdAt, new Date().toISOString())),
      totalCents: cents(row.totalCents),
      subtotalCents: cents(row.subtotalCents),
      discountCents: cents(row.discountCents),
      paymentMethod: text(row.paymentMethod, "cash"),
      operatorId: text(row.cashier, "operador"),
      terminalId: text(row.terminalId, "tablet"),
      lines
    };
  });
}

function buildSales(db: SqliteDatabase, config: MobileDataPlaneConfig): CanonicalSalesToday {
  const today = startOfDay(new Date());
  const tomorrow = addDays(today, 1);
  const recentFrom = addDays(today, -29);
  const todaySales = canonicalSales(db, config.businessId, today, tomorrow);
  const recentSales = canonicalSales(db, config.businessId, recentFrom, tomorrow);
  const todayTotal = todaySales.reduce((sum, sale) => sum + sale.totalCents, 0);
  const recentTotal = recentSales.reduce((sum, sale) => sum + sale.totalCents, 0);
  const recentLastSaleAt = recentSales[0]?.completedAt ?? recentSales[0]?.createdAt ?? null;

  return {
    sales: todaySales,
    totalSalesCents: todayTotal,
    tickets: todaySales.length,
    averageTicketCents: todaySales.length ? Math.round(todayTotal / todaySales.length) : 0,
    hourlyBuckets: hourlyBuckets(todaySales),
    topCategory: todaySales.length ? topCategory(todaySales) : topCategory(recentSales),
    sourceLabel: LOCAL_SOURCE_LABEL,
    recentActivity: recentSales.length
      ? {
          label: "Últimos 30 días",
          totalSalesCents: recentTotal,
          tickets: recentSales.length,
          averageTicketCents: Math.round(recentTotal / recentSales.length),
          lastSaleAt: recentLastSaleAt,
          sourceLabel: LOCAL_SOURCE_LABEL
        }
      : null
  };
}

function buildInventory(db: SqliteDatabase, config: MobileDataPlaneConfig): CanonicalInventoryWatchlist {
  const rows = db.prepare(`
    SELECT
      p.id AS productId,
      p.sku,
      p.name,
      p.category,
      COALESCE(s.available, p.stockOnHand, 0) AS stockQty
    FROM Product p
    LEFT JOIN StockSnapshot s ON s.productId = p.id AND s.businessId = p.businessId
    WHERE p.businessId = ? AND p.isActive = 1
    ORDER BY stockQty ASC, p.name ASC
    LIMIT 18
  `).all(config.businessId);
  const items: CanonicalInventoryItem[] = rows.map((row, index) => ({
    productId: text(row.productId, `product_${index}`),
    sku: text(row.sku, `SKU-${index + 1}`),
    name: text(row.name, "Producto"),
    category: text(row.category, "General"),
    stockQty: intValue(row.stockQty),
    lowStockThreshold: config.lowStockDefaultThreshold,
    overstockThreshold: config.overstockDefaultThreshold,
    weeklyUnitsSold: 0,
    lastMovementLabel: "Última actividad disponible"
  }));
  return {
    items,
    critical: items.filter((item) => item.stockQty <= 0).length,
    reorder: items.filter((item) => item.stockQty > 0 && item.stockQty <= item.lowStockThreshold).length,
    normal: items.filter((item) => item.stockQty > item.lowStockThreshold && item.stockQty < item.overstockThreshold).length,
    overstock: items.filter((item) => item.stockQty >= item.overstockThreshold).length
  };
}

function buildOutbox(db: SqliteDatabase, businessId: string): CanonicalOutboxState {
  const rows = db.prepare("SELECT status, COUNT(*) AS count FROM OutboxEvent WHERE businessId = ? GROUP BY status").all(businessId);
  const byStatus = new Map(rows.map((row) => [text(row.status).toLowerCase(), intValue(row.count)]));
  const latest = db.prepare("SELECT MAX(COALESCE(ackedAt, syncedAt, sentAt, createdAt)) AS value FROM OutboxEvent WHERE businessId = ?").get(businessId);
  const oldest = db.prepare("SELECT MIN(createdAt) AS value FROM OutboxEvent WHERE businessId = ? AND status IN ('pending','queued','sent','received')").get(businessId);
  return {
    pending: (byStatus.get("pending") ?? 0) + (byStatus.get("queued") ?? 0) + (byStatus.get("sent") ?? 0) + (byStatus.get("received") ?? 0),
    failed: (byStatus.get("failed") ?? 0) + (byStatus.get("rejected") ?? 0) + (byStatus.get("dead_letter") ?? 0),
    acked: (byStatus.get("acked") ?? 0) + (byStatus.get("synced") ?? 0),
    lastSyncedAt: text(latest?.value) || null,
    oldestPendingAt: text(oldest?.value) || null
  };
}

function buildCash(db: SqliteDatabase, businessId: string): CanonicalCashState {
  const session = db.prepare(`
    SELECT openedAt, closedAt, expectedCashCents, cashEndCents, varianceCents
    FROM CashSession
    WHERE businessId = ?
    ORDER BY openedAt DESC
    LIMIT 1
  `).get(businessId);
  const movements = db.prepare(`
    SELECT movement, SUM(amountCents) AS amount
    FROM CashMovement
    WHERE businessId = ?
    GROUP BY movement
  `).all(businessId);
  const byMovement = new Map(movements.map((row) => [text(row.movement).toLowerCase(), cents(row.amount)]));
  return {
    expectedCents: cents(session?.expectedCashCents),
    countedCents: session?.cashEndCents === null || session?.cashEndCents === undefined ? null : cents(session.cashEndCents),
    differenceCents: Number(session?.varianceCents ?? 0),
    openedAt: text(session?.openedAt) || null,
    lastCutAt: text(session?.closedAt) || null,
    cashInCents: (byMovement.get("cash_in") ?? 0) + (byMovement.get("opening_float") ?? 0),
    cashOutCents: byMovement.get("cash_out") ?? 0,
    cardCents: 0,
    transferCents: 0
  };
}

function buildPcDashboard(db: SqliteDatabase | null, config: MobileDataPlaneConfig): CanonicalPcDashboard {
  if (!db) {
    return { ok: false, branchName: "PC Backoffice", branchStatus: "revisar", consolidatedSalesCents: null, consolidatedTickets: null, syncLagMs: null, activeAlerts: 0 };
  }
  const today = startOfDay(new Date());
  const tomorrow = addDays(today, 1);
  const recentFrom = addDays(today, -29);
  const store = db.prepare("SELECT name FROM Store WHERE businessId = ? ORDER BY name ASC LIMIT 1").get(config.businessId);
  const sales = db.prepare(`
    SELECT COUNT(*) AS tickets, COALESCE(SUM(totalCents), 0) AS total
    FROM Sale
    WHERE businessId = ? AND status IN ('PAID', 'COMPLETED') AND createdAt >= ? AND createdAt < ?
  `).get(config.businessId, sqliteStamp(recentFrom), sqliteStamp(tomorrow));
  return {
    ok: true,
    branchName: text(store?.name, "PC Backoffice"),
    branchStatus: "revisar",
    consolidatedSalesCents: cents(sales?.total),
    consolidatedTickets: intValue(sales?.tickets),
    syncLagMs: null,
    activeAlerts: 0
  };
}

export async function readLocalDbSnapshot(config: MobileDataPlaneConfig): Promise<LocalDbSnapshot | null> {
  const terminalRoot = findTerminalRoot(process.cwd());
  if (!terminalRoot) return null;
  const tabletDbPath = path.join(terminalRoot, "products", "tablet", "app", "data", "tablet-pos.db");
  const pcDbPath = path.join(terminalRoot, "products", "pc", "app", "data", "canonical.db");
  if (!existsSync(tabletDbPath)) return null;

  const tabletDb = await openSqliteReadOnly(tabletDbPath);
  if (!tabletDb) return null;
  const pcDb = existsSync(pcDbPath) ? await openSqliteReadOnly(pcDbPath) : null;
  try {
    const salesToday = buildSales(tabletDb, config);
    const inventory = buildInventory(tabletDb, config);
    const outbox = buildOutbox(tabletDb, config.businessId);
    const cash = buildCash(tabletDb, config.businessId);
    const pc = buildPcDashboard(pcDb, config);
    return {
      probes: [
        { id: "local", ok: true, url: `file:${tabletDbPath}`, status: 200 },
        { id: "tablet", ok: false, url: `file:${tabletDbPath}`, error: "heartbeat no certificado; datos operativos leídos desde fuente local" },
        { id: "pc", ok: Boolean(pcDb), url: `file:${pcDbPath}`, status: pcDb ? 200 : undefined, error: pcDb ? undefined : "PC local no disponible para lectura" }
      ],
      salesToday,
      inventory,
      outbox,
      cash,
      pc,
      warnings: ["Datos operativos disponibles desde fuente local; heartbeat Tablet no certificado en esta lectura."]
    };
  } finally {
    tabletDb.close();
    pcDb?.close();
  }
}
