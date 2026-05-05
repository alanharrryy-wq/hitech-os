import { InventoryRepository } from "@/server/repositories/inventory.repository";
import { buildInventoryFindings, inventoryAccuracy, signedMovementDelta, stockState } from "@/server/validators/inventory-integrity";
import type { AuditCountView, InventoryAuditSeverityFilter, InventoryCountStatusFilter, InventoryFilters, InventoryStateFilter, InventoryWorkspace, StockLedgerEntry, StockSnapshotView } from "@/modules/inventory/types";

const repository = new InventoryRepository();

function normalizeState(value: string): InventoryStateFilter {
  return value === "critical" || value === "low" || value === "ok" ? value : "all";
}

function normalizeCountStatus(value: string): InventoryCountStatusFilter {
  return value === "open" || value === "review" || value === "closed" ? value : "all";
}

function normalizeSeverity(value: string): InventoryAuditSeverityFilter {
  return value === "CRÍTICO" || value === "ALTO" || value === "MEDIO" ? value : "all";
}

function normalizeFilters(input: Partial<Record<keyof InventoryFilters, string>>): InventoryFilters {
  return {
    q: String(input.q ?? "").trim().slice(0, 80),
    location: String(input.location ?? "all") || "all",
    state: normalizeState(String(input.state ?? "all")),
    countStatus: normalizeCountStatus(String(input.countStatus ?? "all")),
    auditSeverity: normalizeSeverity(String(input.auditSeverity ?? "all"))
  };
}

function dateLabel(value: Date | string | null | undefined) {
  if (!value) return "No disponible";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function iso(value: Date | string | null | undefined) {
  if (!value) return new Date(0).toISOString();
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return new Date(0).toISOString();
  return date.toISOString();
}

function daysLabel(value: number) {
  if (value < 0) return "sin cobertura";
  if (value < 1) return "menos de 1 día";
  return `${value.toFixed(1)} días`;
}

function mapSnapshot(row: any): StockSnapshotView {
  const state = stockState(Number(row.available ?? 0), Number(row.daysCover ?? 0));
  return {
    id: row.id,
    sku: row.product?.sku ?? "SIN-SKU",
    productName: row.product?.name ?? "Producto sin nombre",
    location: row.location,
    onHand: Number(row.onHand ?? 0),
    reserved: Number(row.reserved ?? 0),
    available: Number(row.available ?? 0),
    daysCover: Number(row.daysCover ?? 0),
    daysCoverLabel: daysLabel(Number(row.daysCover ?? 0)),
    state,
    stateLabel: state === "critical" ? "crítico" : state === "low" ? "bajo" : "ok",
    snapshotAt: iso(row.snapshotAt),
    snapshotAtLabel: dateLabel(row.snapshotAt)
  };
}

function mapCount(row: any): AuditCountView {
  const variance = Number(row.variance ?? 0);
  return {
    id: row.id,
    location: row.location,
    countedBy: row.countedBy || "sin actor",
    variance,
    status: row.status,
    countedAt: iso(row.countedAt),
    countedAtLabel: dateLabel(row.countedAt),
    accuracy: Math.abs(variance) === 0 ? 1 : 0,
    accuracyLabel: Math.abs(variance) === 0 ? "100%" : "requiere revisión"
  };
}

function buildLedger(rows: any[], snapshots: StockSnapshotView[]): StockLedgerEntry[] {
  const currentByProductLocation = new Map<string, number>();
  for (const snapshot of snapshots) {
    currentByProductLocation.set(`${snapshot.sku}::${snapshot.location}`, snapshot.onHand);
  }

  const grouped = new Map<string, any[]>();
  for (const row of rows) {
    const sku = row.product?.sku ?? row.productId;
    const key = `${sku}::${row.location}`;
    const list = grouped.get(key) ?? [];
    list.push(row);
    grouped.set(key, list);
  }

  const ledger: StockLedgerEntry[] = [];
  for (const [key, groupRows] of grouped.entries()) {
    const current = currentByProductLocation.get(key) ?? null;
    let afterCursor = current;
    for (const row of groupRows) {
      const delta = signedMovementDelta(String(row.movement ?? "adjust"), Number(row.qty ?? 0));
      const afterQty = afterCursor;
      const beforeQty = afterCursor === null ? null : afterCursor - delta;
      afterCursor = beforeQty;
      ledger.push({
        id: row.id,
        sku: row.product?.sku ?? "SIN-SKU",
        productName: row.product?.name ?? "Producto sin nombre",
        movement: row.movement ?? "adjust",
        quantityDelta: delta,
        reason: row.reason || "sin motivo",
        location: row.location || "sin ubicación",
        source: "StockMovement",
        sourceId: row.id,
        actor: "system:canonical-db",
        beforeQty,
        afterQty,
        createdAt: iso(row.createdAt),
        createdAtLabel: dateLabel(row.createdAt),
        confidence: beforeQty === null || afterQty === null ? "missing" : "derived"
      });
    }
  }
  return ledger.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}

function summarize(snapshots: StockSnapshotView[], ledger: StockLedgerEntry[], counts: AuditCountView[]) {
  const okCounts = counts.filter((count) => Math.abs(count.variance) === 0).length;
  return {
    stockedSkuCount: new Set(snapshots.map((snapshot) => snapshot.sku)).size,
    criticalStockCount: snapshots.filter((snapshot) => snapshot.state === "critical").length,
    lowStockCount: snapshots.filter((snapshot) => snapshot.state === "low").length,
    movementCount: ledger.length,
    countCount: counts.length,
    openCountCount: counts.filter((count) => ["open", "review"].includes(count.status)).length,
    varianceAbsoluteTotal: counts.reduce((acc, count) => acc + Math.abs(count.variance), 0),
    inventoryAccuracy: inventoryAccuracy(okCounts, counts.length)
  };
}

export async function getInventoryWorkspace(input: Partial<Record<keyof InventoryFilters, string>>): Promise<InventoryWorkspace> {
  const filters = normalizeFilters(input);
  const generatedAt = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date());

  try {
    const [snapshotRows, movementRows, countRows] = await Promise.all([
      repository.listSnapshots(filters),
      repository.listMovements(filters),
      repository.listCounts(filters)
    ]);

    const snapshots = snapshotRows.map(mapSnapshot);
    const ledger = buildLedger(movementRows, snapshots);
    const counts = countRows.map(mapCount);
    const allFindings = buildInventoryFindings({ snapshots, ledger, counts });
    const auditFindings = filters.auditSeverity === "all" ? allFindings : allFindings.filter((finding) => finding.severity === filters.auditSeverity);
    const countFindings = auditFindings.filter((finding) => finding.type.startsWith("conteo"));
    const locations = Array.from(new Set([...snapshots.map((row) => row.location), ...ledger.map((row) => row.location), ...counts.map((row) => row.location)])).sort();

    return {
      filters,
      locations,
      snapshots,
      ledger,
      counts,
      auditFindings,
      countFindings,
      summary: summarize(snapshots, ledger, counts),
      meta: {
        source: "canonical_prisma",
        confidence: "derived",
        persistence: "available",
        ledgerMode: "derived_from_stock_movement",
        generatedAt,
        warnings: ["El schema actual no persiste beforeQty/afterQty ni actor nativo; I03 calcula una vista derivada y marca actor como system:canonical-db."]
      }
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Error desconocido leyendo Prisma.";
    return {
      filters,
      locations: [],
      snapshots: [],
      ledger: [],
      counts: [],
      auditFindings: [],
      countFindings: [],
      summary: {
        stockedSkuCount: 0,
        criticalStockCount: 0,
        lowStockCount: 0,
        movementCount: 0,
        countCount: 0,
        openCountCount: 0,
        varianceAbsoluteTotal: 0,
        inventoryAccuracy: null
      },
      meta: {
        source: "fallback_empty",
        confidence: "blocked",
        persistence: "unavailable",
        ledgerMode: "unavailable",
        generatedAt,
        warnings: [`Persistencia no disponible: ${message}`]
      }
    };
  }
}
