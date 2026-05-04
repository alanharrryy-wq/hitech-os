import type { CanonicalInventoryItem, CanonicalInventoryWatchlist, MobileDataPlaneConfig } from "./types";
import { asRecord, pickArray, readNonNegativeInt, readString, unwrapOkData, uniqueStable } from "./extractors";

function normalizeInventoryItem(raw: unknown, index: number, config: MobileDataPlaneConfig): CanonicalInventoryItem {
  const record = asRecord(raw);
  const stockQty = readNonNegativeInt(record, ["stockQty", "stockOnHand", "stock", "qty", "quantity"], 0);
  const lowStockThreshold = readNonNegativeInt(record, ["lowStockThreshold", "min", "minimum"], config.lowStockDefaultThreshold);
  const overstockThreshold = readNonNegativeInt(record, ["overstockThreshold", "max", "maximum"], config.overstockDefaultThreshold);
  return {
    productId: readString(record, ["productId", "id"], `product_${index}`),
    sku: readString(record, ["sku", "barcode", "code"], `SKU-${index + 1}`),
    name: readString(record, ["name", "productName", "title"], "Producto sin nombre recibido"),
    category: readString(record, ["category", "family", "department"], "General"),
    stockQty,
    lowStockThreshold,
    overstockThreshold,
    weeklyUnitsSold: readNonNegativeInt(record, ["weeklyUnitsSold", "unitsSold7d", "soldLast7Days"], 0),
    lastMovementLabel: readString(record, ["movement", "lastMovement", "lastMovementLabel"], stockQty <= lowStockThreshold ? "Reponer pronto" : "Sin movimiento reciente")
  };
}

export function classifyInventoryState(item: CanonicalInventoryItem): "critico" | "reponer" | "normal" | "sobrestock" {
  if (item.stockQty <= 0) return "critico";
  if (item.stockQty <= item.lowStockThreshold) return "reponer";
  if (item.stockQty >= item.overstockThreshold) return "sobrestock";
  return "normal";
}

export function normalizeInventoryWatchlist(payload: unknown, config: MobileDataPlaneConfig): CanonicalInventoryWatchlist {
  const data = unwrapOkData(payload);
  const rawItems = pickArray(data, ["items", "products", "stock", "rows", "watchlist", "lowStock"]);
  const items = uniqueStable(rawItems.map((item, index) => normalizeInventoryItem(item, index, config)), (item) => `${item.productId}:${item.sku}`)
    .sort((a, b) => {
      const order = { critico: 0, reponer: 1, normal: 2, sobrestock: 3 } as const;
      return order[classifyInventoryState(a)] - order[classifyInventoryState(b)] || a.stockQty - b.stockQty;
    });
  return {
    items,
    critical: items.filter((item) => classifyInventoryState(item) === "critico").length,
    reorder: items.filter((item) => classifyInventoryState(item) === "reponer").length,
    normal: items.filter((item) => classifyInventoryState(item) === "normal").length,
    overstock: items.filter((item) => classifyInventoryState(item) === "sobrestock").length
  };
}

export function emptyInventoryWatchlist(): CanonicalInventoryWatchlist {
  return { items: [], critical: 0, reorder: 0, normal: 0, overstock: 0 };
}
