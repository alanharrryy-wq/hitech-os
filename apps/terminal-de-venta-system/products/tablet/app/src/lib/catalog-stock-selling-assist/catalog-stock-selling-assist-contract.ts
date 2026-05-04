import type { PosProduct } from "@/lib/pos/cart-state";

export type CatalogStockSellingAssistMode = "catalog" | "stock";

export type CatalogStockSellingAssistProduct = PosProduct & {
  businessId?: string;
  costCents?: number;
  updatedAt?: string;
};

export type CatalogStockSignal =
  | "available"
  | "low_stock"
  | "out_of_stock"
  | "inactive";

export type CatalogStockFilter =
  | "all"
  | "available"
  | "low_stock"
  | "out_of_stock"
  | "inactive";

export type CatalogStockTone = "ok" | "warn" | "danger" | "neutral";

export type CatalogStockMetric = {
  id: string;
  label: string;
  value: string;
  note: string;
  tone: CatalogStockTone;
};

export type CatalogStockSearchState =
  | "idle"
  | "loading"
  | "ready"
  | "empty"
  | "error"
  | "offline";

export type CatalogStockCartHandoffResult = {
  ok: true;
  cartLines: number;
  cartUnits: number;
  productName: string;
  message: string;
} | {
  ok: false;
  code: "PRODUCT_INACTIVE" | "OUT_OF_STOCK" | "LOCAL_STORAGE_UNAVAILABLE" | "INVALID_PRODUCT";
  message: string;
};

export type CatalogStockScreenCopy = {
  currentPath: string;
  title: string;
  subtitle: string;
  kicker: string;
  searchPlaceholder: string;
  primaryAction: string;
  emptyTitle: string;
  emptyDescription: string;
};

export const CATALOG_STOCK_SELLING_ASSIST_VERSION = "03J_03K";

export const CATALOG_STOCK_SCREEN_COPY: Record<CatalogStockSellingAssistMode, CatalogStockScreenCopy> = {
  catalog: {
    currentPath: "/catalog",
    title: "Catálogo que sí vende",
    subtitle: "Busca producto, revisa precio, código, existencia y mándalo directo a venta sin abrir otra libreta mental.",
    kicker: "Catálogo + venta asistida",
    searchPlaceholder: "Buscar por nombre, SKU, categoría o código",
    primaryAction: "Agregar a venta",
    emptyTitle: "No hay productos en este filtro",
    emptyDescription: "Cambia la búsqueda o revisa si el producto está inactivo. La Tablet no adivina, todavía no le pagan de vidente."
  },
  stock: {
    currentPath: "/stock",
    title: "Existencias para vender",
    subtitle: "Revisa bajo stock, sin stock e inactivos, y manda productos vendibles al carrito local de /pos.",
    kicker: "Stock operativo + venta asistida",
    searchPlaceholder: "Buscar existencias por producto, SKU o código",
    primaryAction: "Mandar a venta",
    emptyTitle: "Sin existencias que mostrar",
    emptyDescription: "El filtro actual no encontró productos. Ajusta la búsqueda antes de culpar al inventario, pobre condenado."
  }
};

export const CATALOG_STOCK_VISIBLE_FORBIDDEN_COPY = [
  "demo",
  "payload",
  "outbox",
  "runtime",
  "fixture",
  "mock",
  "lorem",
  "todo"
] as const;
