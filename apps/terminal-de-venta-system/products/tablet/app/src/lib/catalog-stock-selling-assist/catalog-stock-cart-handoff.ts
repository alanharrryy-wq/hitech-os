import type { CartLine, PosProduct } from "@/lib/pos/cart-state";
import { POS_CART_STORAGE_KEY, cartTotalQty } from "@/lib/pos/cart-state";
import { addProductToCart } from "@/lib/pos/cart-engine";
import type { CatalogStockCartHandoffResult, CatalogStockSellingAssistProduct } from "./catalog-stock-selling-assist-contract";
import { canSendProductToSale, getBlockedSaleReason } from "./catalog-stock-selling-assist-view-model";

function safeReadCart(): CartLine[] | null {
  if (typeof window === "undefined" || !window.localStorage) return null;
  const raw = window.localStorage.getItem(POS_CART_STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as CartLine[];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((line) => line?.product?.id && Number.isFinite(line.qty) && line.qty > 0);
  } catch {
    return [];
  }
}

function safeWriteCart(lines: CartLine[]) {
  if (typeof window === "undefined" || !window.localStorage) return false;
  window.localStorage.setItem(POS_CART_STORAGE_KEY, JSON.stringify(lines));
  window.dispatchEvent(new CustomEvent("prisma:tablet-cart-updated", { detail: { lines } }));
  return true;
}

function toCartProduct(product: CatalogStockSellingAssistProduct): PosProduct {
  return {
    id: product.id,
    businessId: product.businessId ?? "biz_tablet_standalone",
    sku: product.sku,
    name: product.name,
    category: product.category || "General",
    barcode: product.barcode ?? product.barcodes?.[0] ?? null,
    barcodes: product.barcodes ?? [],
    priceCents: product.priceCents,
    stockOnHand: product.stockOnHand,
    lowStockThreshold: product.lowStockThreshold,
    isActive: product.isActive
  };
}

export function addSellingAssistProductToCart(product: CatalogStockSellingAssistProduct): CatalogStockCartHandoffResult {
  if (!product?.id || !product.name) {
    return { ok: false, code: "INVALID_PRODUCT", message: "Producto inválido para mandar a venta." };
  }
  if (!canSendProductToSale(product)) {
    return {
      ok: false,
      code: product.isActive ? "OUT_OF_STOCK" : "PRODUCT_INACTIVE",
      message: getBlockedSaleReason(product)
    };
  }
  const current = safeReadCart();
  if (!current) {
    return {
      ok: false,
      code: "LOCAL_STORAGE_UNAVAILABLE",
      message: "No se pudo abrir el carrito local de la Tablet. Revisa permisos del navegador."
    };
  }
  const next = addProductToCart(current, toCartProduct(product)).lines;
  if (!safeWriteCart(next)) {
    return {
      ok: false,
      code: "LOCAL_STORAGE_UNAVAILABLE",
      message: "No se pudo guardar el carrito local de la Tablet."
    };
  }
  return {
    ok: true,
    cartLines: next.length,
    cartUnits: cartTotalQty(next),
    productName: product.name,
    message: `${product.name} agregado a venta. Carrito: ${cartTotalQty(next)} pieza(s).`
  };
}

export function readSellingAssistCartSummary() {
  const cart = safeReadCart() ?? [];
  return {
    lines: cart.length,
    units: cartTotalQty(cart),
    hasCart: cart.length > 0
  };
}
