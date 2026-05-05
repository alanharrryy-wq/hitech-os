import { formatMoney } from "@/lib/pos/cart-state";
import type {
  CatalogStockFilter,
  CatalogStockMetric,
  CatalogStockSellingAssistMode,
  CatalogStockSellingAssistProduct,
  CatalogStockSignal,
  CatalogStockTone
} from "./catalog-stock-selling-assist-contract";

export function normalizeSearch(value: string) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

export function getProductBarcode(product: CatalogStockSellingAssistProduct) {
  return product.barcode || product.barcodes?.[0] || "";
}

export function getProductLowStockThreshold(product: CatalogStockSellingAssistProduct) {
  return Math.max(1, product.lowStockThreshold ?? 5);
}

export function getCatalogStockSignal(product: CatalogStockSellingAssistProduct): CatalogStockSignal {
  if (!product || !product.id) return "inactive";
  if (!product.isActive) return "inactive";
  if ((product.stockOnHand ?? 0) <= 0) return "out_of_stock";
  if ((product.stockOnHand ?? 0) <= getProductLowStockThreshold(product)) return "low_stock";
  return "available";
}

export function getCatalogStockTone(signal: CatalogStockSignal): CatalogStockTone {
  if (signal === "available") return "ok";
  if (signal === "low_stock") return "warn";
  if (signal === "out_of_stock" || signal === "inactive") return "danger";
  return "neutral";
}

export function getCatalogStockLabel(signal: CatalogStockSignal) {
  if (signal === "available") return "Disponible";
  if (signal === "low_stock") return "Stock bajo";
  if (signal === "out_of_stock") return "Sin stock";
  return "Inactivo";
}

export function canSendProductToSale(product: CatalogStockSellingAssistProduct) {
  const signal = getCatalogStockSignal(product);
  return signal === "available" || signal === "low_stock";
}

export function getBlockedSaleReason(product: CatalogStockSellingAssistProduct) {
  const signal = getCatalogStockSignal(product);
  if (signal === "inactive") return "Producto inactivo: no se manda a venta hasta reactivarlo.";
  if (signal === "out_of_stock") return "Sin stock: evita vender aire premium, eso ni el marketing lo salva.";
  return "";
}

export function describeProductSignal(product: CatalogStockSellingAssistProduct) {
  const signal = getCatalogStockSignal(product);
  const threshold = getProductLowStockThreshold(product);
  if (signal === "available") return `Listo para vender. Existencia actual: ${product.stockOnHand} unidades.`;
  if (signal === "low_stock") return `Vendible, pero bajo vigilancia: ${product.stockOnHand} unidades y umbral ${threshold}.`;
  if (signal === "out_of_stock") return "No vendible desde esta pantalla porque la existencia local está en cero.";
  return "No vendible porque el producto está inactivo en el catálogo local.";
}

export function productMatchesFilter(product: CatalogStockSellingAssistProduct, filter: CatalogStockFilter) {
  if (filter === "all") return true;
  return getCatalogStockSignal(product) === filter;
}

export function productMatchesQuery(product: CatalogStockSellingAssistProduct, query: string) {
  const q = normalizeSearch(query);
  if (!q) return true;
  const haystack = [
    product.name,
    product.sku,
    product.category,
    getProductBarcode(product),
    ...(product.barcodes ?? [])
  ].map((value) => normalizeSearch(String(value ?? ""))).join(" ");
  return haystack.includes(q);
}

export function sortProductsForSellingAssist(products: CatalogStockSellingAssistProduct[], mode: CatalogStockSellingAssistMode) {
  const signalOrder: Record<CatalogStockSignal, number> = {
    low_stock: mode === "stock" ? 0 : 1,
    out_of_stock: mode === "stock" ? 1 : 3,
    available: mode === "stock" ? 2 : 0,
    inactive: 4
  };
  return [...products].sort((a, b) => {
    const signalDiff = signalOrder[getCatalogStockSignal(a)] - signalOrder[getCatalogStockSignal(b)];
    if (signalDiff !== 0) return signalDiff;
    const stockDiff = (a.stockOnHand ?? 0) - (b.stockOnHand ?? 0);
    if (mode === "stock" && stockDiff !== 0) return stockDiff;
    return String(a.name).localeCompare(String(b.name), "es-MX");
  });
}

export function filterProductsForSellingAssist(
  products: CatalogStockSellingAssistProduct[],
  query: string,
  filter: CatalogStockFilter,
  mode: CatalogStockSellingAssistMode
) {
  return sortProductsForSellingAssist(
    products.filter((product) => productMatchesQuery(product, query)).filter((product) => productMatchesFilter(product, filter)),
    mode
  );
}

export function buildCatalogStockMetrics(products: CatalogStockSellingAssistProduct[]): CatalogStockMetric[] {
  const active = products.filter((product) => product.isActive);
  const available = products.filter((product) => getCatalogStockSignal(product) === "available");
  const lowStock = products.filter((product) => getCatalogStockSignal(product) === "low_stock");
  const outOfStock = products.filter((product) => getCatalogStockSignal(product) === "out_of_stock");
  const inactive = products.filter((product) => getCatalogStockSignal(product) === "inactive");
  return [
    {
      id: "active",
      label: "Activos",
      value: String(active.length),
      note: "productos habilitados en catálogo local",
      tone: active.length ? "ok" : "neutral"
    },
    {
      id: "available",
      label: "Vendibles",
      value: String(available.length + lowStock.length),
      note: "se pueden mandar al carrito de /pos",
      tone: available.length + lowStock.length ? "ok" : "warn"
    },
    {
      id: "low_stock",
      label: "Stock bajo",
      value: String(lowStock.length),
      note: "vendibles, pero requieren vigilancia",
      tone: lowStock.length ? "warn" : "ok"
    },
    {
      id: "blocked",
      label: "Bloqueados",
      value: String(outOfStock.length + inactive.length),
      note: "sin stock o inactivos",
      tone: outOfStock.length + inactive.length ? "danger" : "ok"
    }
  ];
}

export function buildProductDetailRows(product: CatalogStockSellingAssistProduct) {
  const barcode = getProductBarcode(product) || "Sin código";
  return [
    { label: "Precio", value: formatMoney(product.priceCents) },
    { label: "SKU", value: product.sku || "Sin SKU" },
    { label: "Código", value: barcode },
    { label: "Categoría", value: product.category || "General" },
    { label: "Existencia", value: `${product.stockOnHand ?? 0} unidades` },
    { label: "Umbral bajo", value: `${getProductLowStockThreshold(product)} unidades` }
  ];
}

export function buildStockRiskSummary(products: CatalogStockSellingAssistProduct[]) {
  const low = products.filter((product) => getCatalogStockSignal(product) === "low_stock");
  const zero = products.filter((product) => getCatalogStockSignal(product) === "out_of_stock");
  const inactive = products.filter((product) => getCatalogStockSignal(product) === "inactive");
  if (!products.length) return "Sin productos cargados todavía.";
  if (!low.length && !zero.length && !inactive.length) return "Catálogo operativo sin bloqueos visibles para venta.";
  const parts = [];
  if (low.length) parts.push(`${low.length} con stock bajo`);
  if (zero.length) parts.push(`${zero.length} sin stock`);
  if (inactive.length) parts.push(`${inactive.length} inactivos`);
  return `Atención: ${parts.join(", ")}.`;
}

export function buildProductSearchUrl(query: string, includeInactive = true) {
  const params = new URLSearchParams({ q: query, limit: "50", includeInactive: includeInactive ? "true" : "false" });
  return `/api/pos/products/search?${params.toString()}`;
}
