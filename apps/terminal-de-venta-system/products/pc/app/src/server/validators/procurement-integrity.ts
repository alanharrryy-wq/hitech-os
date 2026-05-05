import type { PurchaseRow, ReceiptRow, ReplenishmentRow, OperationAlert } from "@/modules/operations/types";

export function suggestedReplenishment(current: number, min: number | null, max: number | null) {
  if (min == null || current > min) return 0;
  return Math.max(0, (max ?? min * 2) - current);
}

export function classifyPurchaseRisk(row: Pick<PurchaseRow, "status" | "expectedAt" | "linesCount" | "pendingQty">): PurchaseRow["risk"] {
  if (row.linesCount <= 0) return "SIN_LINEAS";
  const expected = new Date(row.expectedAt);
  if (!Number.isNaN(expected.getTime()) && expected.getTime() < Date.now() && row.pendingQty > 0) return "VENCIDA";
  if (row.pendingQty > 0 || ["partial", "partially_received", "parcial"].includes(row.status.toLowerCase())) return "PARCIAL";
  return "OK";
}

export function classifyReceiptDiscrepancy(expectedQty: number, receivedQty: number) {
  const delta = receivedQty - expectedQty;
  if (expectedQty === 0 && receivedQty > 0) return { label: "No esperado", severity: "ALTO" as const, delta };
  if (delta < 0) return { label: "Faltante", severity: "ALTO" as const, delta };
  if (delta > 0) return { label: "Sobrante", severity: "MEDIO" as const, delta };
  return { label: "Sin diferencia", severity: "BAJO" as const, delta };
}

export function validateReplenishmentSignal(row: ReplenishmentRow) {
  const findings: string[] = [];
  if (row.suggestedQty < 0) findings.push("Sugerido negativo");
  if (row.currentStock < 0) findings.push("Stock negativo");
  if (row.maxStock < row.minStock) findings.push("Máximo menor al mínimo");
  if (!row.sku.trim()) findings.push("SKU vacío");
  return findings;
}

export function buildOperationAlerts(input: {
  purchases: PurchaseRow[];
  receipts: ReceiptRow[];
  replenishment: ReplenishmentRow[];
}): OperationAlert[] {
  const alerts: OperationAlert[] = [];
  for (const order of input.purchases.filter((row) => row.risk !== "OK").slice(0, 6)) {
    alerts.push({
      severity: order.risk === "VENCIDA" ? "ALTO" : "MEDIO",
      module: "Compras",
      title: `Orden ${order.folio}: ${order.risk.toLowerCase()}`,
      detail: `${order.supplier} tiene ${order.pendingQty} unidades pendientes.`,
      href: "/purchasing"
    });
  }
  for (const receipt of input.receipts.filter((row) => row.discrepancyCount > 0).slice(0, 6)) {
    alerts.push({
      severity: Math.abs(receipt.discrepancyQty) > 5 ? "ALTO" : "MEDIO",
      module: "Recepción",
      title: `Recepción ${receipt.folio} con diferencia`,
      detail: `${receipt.discrepancyLabel}: diferencia neta ${receipt.discrepancyQty}.`,
      href: "/receiving"
    });
  }
  for (const signal of input.replenishment.filter((row) => row.priority.toLowerCase().includes("high") || row.priority.toLowerCase().includes("alta")).slice(0, 6)) {
    alerts.push({
      severity: "ALTO",
      module: "Reabasto",
      title: `${signal.sku} requiere reabasto`,
      detail: `${signal.name}: sugerido ${signal.suggestedQty} en ${signal.location}.`,
      href: "/replenishment"
    });
  }
  return alerts;
}
