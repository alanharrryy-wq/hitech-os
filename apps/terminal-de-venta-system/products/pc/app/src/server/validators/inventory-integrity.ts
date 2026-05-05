import type { AuditCountView, InventoryFinding, StockLedgerEntry, StockSnapshotView } from "@/modules/inventory/types";

export function inventoryAccuracy(okCounts: number, totalCounts: number) {
  return totalCounts <= 0 ? null : okCounts / totalCounts;
}

export function stockState(available: number, daysCover: number) {
  if (available <= 0 || daysCover < 2) return "critical" as const;
  if (daysCover < 5) return "low" as const;
  return "ok" as const;
}

export function signedMovementDelta(movement: string, qty: number) {
  const normalized = movement.toLowerCase();
  if (["out", "sale", "decrement", "salida", "venta"].some((token) => normalized.includes(token))) return -Math.abs(qty);
  if (["adjust_down", "merma", "loss", "baja"].some((token) => normalized.includes(token))) return -Math.abs(qty);
  return Math.abs(qty);
}

export function buildInventoryFindings(input: {
  snapshots: StockSnapshotView[];
  ledger: StockLedgerEntry[];
  counts: AuditCountView[];
}): InventoryFinding[] {
  const findings: InventoryFinding[] = [];

  for (const snapshot of input.snapshots) {
    if (snapshot.available < 0) {
      findings.push({
        id: `stock-negative-${snapshot.id}`,
        severity: "CRÍTICO",
        type: "stock_negativo",
        title: "Stock negativo",
        entityLabel: `${snapshot.sku} · ${snapshot.location}`,
        detail: `Disponible ${snapshot.available}. La foto de inventario contradice operación normal.`,
        recommendedAction: "Bloquear ajuste automático y abrir revisión de movimientos."
      });
    } else if (snapshot.state === "critical") {
      findings.push({
        id: `stock-critical-${snapshot.id}`,
        severity: "ALTO",
        type: "stock_critico",
        title: "Stock crítico",
        entityLabel: `${snapshot.sku} · ${snapshot.location}`,
        detail: `Cobertura ${snapshot.daysCoverLabel}; riesgo de quiebre operativo.`,
        recommendedAction: "Revisar reabasto y último movimiento antes de prometer venta."
      });
    }
  }

  for (const entry of input.ledger) {
    if (!entry.reason || entry.reason.trim().length < 3) {
      findings.push({
        id: `movement-no-reason-${entry.id}`,
        severity: "ALTO",
        type: "movimiento_sin_motivo",
        title: "Movimiento sin motivo claro",
        entityLabel: `${entry.sku} · ${entry.location}`,
        detail: "El movimiento no trae motivo suficiente para auditoría.",
        recommendedAction: "Exigir razón operativa antes de aprobar ajustes o conciliaciones."
      });
    }
    if (entry.beforeQty === null || entry.afterQty === null) {
      findings.push({
        id: `movement-derived-ledger-${entry.id}`,
        severity: "MEDIO",
        type: "ledger_derivado",
        title: "Before/after derivado",
        entityLabel: `${entry.sku} · ${entry.location}`,
        detail: "El schema actual no trae beforeQty/afterQty nativo; se calcula desde stock actual y deltas recientes.",
        recommendedAction: "En una fase posterior, persistir beforeQty/afterQty nativo para auditoría fuerte."
      });
    }
  }

  for (const count of input.counts) {
    if (Math.abs(count.variance) >= 10) {
      findings.push({
        id: `count-high-variance-${count.id}`,
        severity: "ALTO",
        type: "conteo_variacion_alta",
        title: "Conteo con variación alta",
        entityLabel: `${count.location} · ${count.countedBy}`,
        detail: `Variación absoluta ${Math.abs(count.variance)} unidades.`,
        recommendedAction: "Recontar o exigir aprobación antes de ajustar inventario."
      });
    }
  }

  return findings;
}
