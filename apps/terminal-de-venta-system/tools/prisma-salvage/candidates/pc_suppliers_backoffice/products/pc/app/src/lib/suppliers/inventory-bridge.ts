import { prisma } from "@/server/prisma/client";
import type { SupplierInventoryBridgeItem, SupplierInventoryBridgeSnapshot, SupplierProductLink } from "./types";

const DEFAULT_NOW = "2026-05-02T16:30:00.000Z";

type InventoryBridgeInput = {
  now?: string;
  productLinks: SupplierProductLink[];
};

type InventoryRecord = {
  productId: string;
  sku: string;
  productName: string;
  category: string;
  stockOnHand: number;
  costCents: number;
  isActive: boolean;
  availableUnits?: number;
  daysCover?: number;
  suggestedQty?: number;
  priority?: string;
};

export async function loadSupplierInventoryBridge(input: InventoryBridgeInput): Promise<SupplierInventoryBridgeSnapshot> {
  const now = input.now ?? DEFAULT_NOW;
  const productIds = [...new Set(input.productLinks.map((link) => link.productId))];

  if (productIds.length === 0) {
    return buildFallbackBridge(input.productLinks, now, ["No hay productos asociados a proveedores."]);
  }

  try {
    const records = await loadInventoryRecords(productIds);
    if (records.size === 0) {
      return buildFallbackBridge(input.productLinks, now, ["Inventario consolidado sin coincidencias para productos de proveedores; usando datos de Proveedores."]);
    }
    return buildBridgeFromRecords(input.productLinks, records, now);
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Inventario consolidado no disponible.";
    return buildFallbackBridge(input.productLinks, now, [`Inventario consolidado no disponible; usando datos de Proveedores. Detalle: ${cleanTechnicalReason(reason)}`]);
  }
}

export function mergeSupplierProductLinksWithInventory(productLinks: SupplierProductLink[], bridge: SupplierInventoryBridgeSnapshot): SupplierProductLink[] {
  const byProduct = new Map(bridge.items.map((item) => [item.productId, item]));
  return productLinks.map((link) => {
    const inventory = byProduct.get(link.productId);
    if (!inventory || inventory.source !== "inventario_consolidado") return link;
    const averageDailySalesUnits = inventory.coverageDays > 0 ? Math.max(0.1, inventory.availableUnits / inventory.coverageDays) : link.averageDailySalesUnits;
    return {
      ...link,
      currentStockUnits: inventory.availableUnits,
      lowStockThresholdUnits: inventory.lowStockThresholdUnits,
      averageDailySalesUnits: round1(averageDailySalesUnits)
    };
  });
}

async function loadInventoryRecords(productIds: string[]): Promise<Map<string, InventoryRecord>> {
  const [products, snapshots, replenishmentSignals] = await Promise.all([
    prisma.product.findMany({
      where: { id: { in: productIds } },
      select: { id: true, sku: true, name: true, category: true, stockOnHand: true, costCents: true, isActive: true }
    }),
    prisma.stockSnapshot.findMany({
      where: { productId: { in: productIds } },
      orderBy: { snapshotAt: "desc" },
      select: { productId: true, available: true, onHand: true, daysCover: true, snapshotAt: true }
    }),
    prisma.replenishmentSignal.findMany({
      where: { productId: { in: productIds } },
      orderBy: [{ priority: "asc" }, { createdAt: "desc" }],
      select: { productId: true, suggestedQty: true, priority: true, createdAt: true }
    })
  ]);

  const latestSnapshot = new Map<string, { productId: string; available: number; onHand: number; daysCover: number }>();
  for (const snapshot of snapshots) {
    if (!latestSnapshot.has(snapshot.productId)) latestSnapshot.set(snapshot.productId, snapshot);
  }

  const latestSignal = new Map<string, { productId: string; suggestedQty: number; priority: string }>();
  for (const signal of replenishmentSignals) {
    if (!latestSignal.has(signal.productId)) latestSignal.set(signal.productId, signal);
  }

  const records = new Map<string, InventoryRecord>();
  for (const product of products) {
    const snapshot = latestSnapshot.get(product.id);
    const signal = latestSignal.get(product.id);
    records.set(product.id, {
      productId: product.id,
      sku: product.sku,
      productName: product.name,
      category: product.category,
      stockOnHand: product.stockOnHand,
      costCents: product.costCents,
      isActive: product.isActive,
      availableUnits: snapshot?.available ?? product.stockOnHand,
      daysCover: snapshot?.daysCover,
      suggestedQty: signal?.suggestedQty,
      priority: signal?.priority
    });
  }
  return records;
}

function buildBridgeFromRecords(productLinks: SupplierProductLink[], records: Map<string, InventoryRecord>, now: string): SupplierInventoryBridgeSnapshot {
  const warnings: string[] = [];
  const items: SupplierInventoryBridgeItem[] = productLinks.map((link) => {
    const record = records.get(link.productId);
    if (!record) return buildFallbackItem(link);
    const availableUnits = normalizeNumber(record.availableUnits, record.stockOnHand);
    const coverageDays = normalizeNumber(record.daysCover, calculateCoverageDays(availableUnits, link.averageDailySalesUnits));
    const suggestedQty = Math.max(0, normalizeNumber(record.suggestedQty, Math.max(0, link.lowStockThresholdUnits - availableUnits)));
    const priority = resolvePriority(availableUnits, coverageDays, suggestedQty, record.priority);
    return {
      id: `inventory-${link.productId}`,
      productId: link.productId,
      sku: record.sku || link.sku,
      productName: record.productName || link.name,
      supplierId: link.supplierId,
      supplierName: link.supplierName,
      currentStockUnits: normalizeNumber(record.stockOnHand, link.currentStockUnits),
      availableUnits,
      lowStockThresholdUnits: link.lowStockThresholdUnits,
      coverageDays,
      suggestedQty,
      priority,
      source: "inventario_consolidado",
      evidence: buildEvidence(availableUnits, coverageDays, suggestedQty, "inventario consolidado"),
      actionLabel: priority === "critical" ? "Priorizar compra" : priority === "high" ? "Revisar pedido" : "Vigilar cobertura",
      tone: priorityToTone(priority)
    };
  });
  const missing = items.filter((item) => item.source !== "inventario_consolidado").length;
  if (missing > 0) warnings.push(`${missing} productos aún usan datos de Proveedores porque no aparecieron en inventario consolidado.`);
  return summarizeBridge(items, now, "inventario_consolidado", "Inventario consolidado", productLinks.length, warnings);
}

function buildFallbackBridge(productLinks: SupplierProductLink[], now: string, warnings: string[]): SupplierInventoryBridgeSnapshot {
  const items = productLinks.map(buildFallbackItem);
  return summarizeBridge(items, now, "datos_de_proveedores", "Datos cargados en Proveedores", productLinks.length, warnings);
}

function buildFallbackItem(link: SupplierProductLink): SupplierInventoryBridgeItem {
  const coverageDays = calculateCoverageDays(link.currentStockUnits, link.averageDailySalesUnits);
  const suggestedQty = Math.max(0, link.lowStockThresholdUnits - link.currentStockUnits);
  const priority = resolvePriority(link.currentStockUnits, coverageDays, suggestedQty);
  return {
    id: `inventory-${link.productId}`,
    productId: link.productId,
    sku: link.sku,
    productName: link.name,
    supplierId: link.supplierId,
    supplierName: link.supplierName,
    currentStockUnits: link.currentStockUnits,
    availableUnits: link.currentStockUnits,
    lowStockThresholdUnits: link.lowStockThresholdUnits,
    coverageDays,
    suggestedQty,
    priority,
    source: "datos_de_proveedores",
    evidence: buildEvidence(link.currentStockUnits, coverageDays, suggestedQty, "datos de Proveedores"),
    actionLabel: priority === "critical" ? "Priorizar compra" : priority === "high" ? "Revisar pedido" : "Vigilar cobertura",
    tone: priorityToTone(priority)
  };
}

function summarizeBridge(items: SupplierInventoryBridgeItem[], now: string, source: SupplierInventoryBridgeSnapshot["source"], sourceLabel: string, linkedProducts: number, warnings: string[]): SupplierInventoryBridgeSnapshot {
  const connectedProducts = items.filter((item) => item.source === "inventario_consolidado").length;
  const averageCoverageDays = items.length ? round1(items.reduce((sum, item) => sum + item.coverageDays, 0) / items.length) : 0;
  return {
    generatedAt: now,
    source,
    sourceLabel,
    connectedProducts,
    linkedProducts,
    criticalProducts: items.filter((item) => item.priority === "critical").length,
    lowStockProducts: items.filter((item) => item.priority === "high").length,
    overstockProducts: items.filter((item) => item.coverageDays >= 14).length,
    averageCoverageDays,
    warnings,
    items: items.sort(sortInventoryItems).slice(0, 12)
  };
}

function resolvePriority(stock: number, coverageDays: number, suggestedQty: number, rawPriority?: string): SupplierInventoryBridgeItem["priority"] {
  const normalized = String(rawPriority ?? "").toLowerCase();
  if (normalized.includes("critical") || stock <= 0 || coverageDays < 1.5) return "critical";
  if (normalized.includes("high") || suggestedQty > 0 || coverageDays < 3) return "high";
  if (coverageDays >= 14) return "low";
  return "medium";
}

function priorityToTone(priority: SupplierInventoryBridgeItem["priority"]): SupplierInventoryBridgeItem["tone"] {
  if (priority === "critical") return "urgent";
  if (priority === "high") return "high";
  if (priority === "low") return "ok";
  return "warn";
}

function sortInventoryItems(a: SupplierInventoryBridgeItem, b: SupplierInventoryBridgeItem): number {
  const weight = { critical: 4, high: 3, medium: 2, low: 1 };
  return weight[b.priority] - weight[a.priority] || a.coverageDays - b.coverageDays || b.suggestedQty - a.suggestedQty;
}

function calculateCoverageDays(stock: number, averageDailySalesUnits: number): number {
  if (!Number.isFinite(averageDailySalesUnits) || averageDailySalesUnits <= 0) return stock > 0 ? 99 : 0;
  return round1(Math.max(0, stock / averageDailySalesUnits));
}

function buildEvidence(availableUnits: number, coverageDays: number, suggestedQty: number, source: string): string {
  const parts = [`${availableUnits} piezas disponibles`, `${coverageDays} días de cobertura`, `fuente: ${source}`];
  if (suggestedQty > 0) parts.splice(2, 0, `${suggestedQty} piezas sugeridas`);
  return parts.join(" · ");
}

function normalizeNumber(value: unknown, fallback: number): number {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
}

function round1(value: number): number {
  return Math.round(value * 10) / 10;
}

function cleanTechnicalReason(value: string): string {
  return value.replace(/\s+/g, " ").slice(0, 140);
}
