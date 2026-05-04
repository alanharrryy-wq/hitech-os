import type { CartLine } from "./cart-state";
import { calculateCartTotalCents, calculateCartTotalQty, getCartLineStockSignal, validateCartForCheckout } from "./cart-engine";

export type CartLineViewModel = {
  productId: string;
  sku: string;
  name: string;
  qty: number;
  unitPriceCents: number;
  lineTotalCents: number;
  stockLabel: string;
  stockTone: "ok" | "warn" | "danger";
  blocksCheckout: boolean;
};

export type CartPanelViewModel = {
  lines: CartLineViewModel[];
  totalCents: number;
  totalQty: number;
  checkoutReady: boolean;
  checkoutReason: string;
};

export function buildCartLineViewModel(line: CartLine): CartLineViewModel {
  const stock = getCartLineStockSignal(line);
  return {
    productId: line.product.id,
    sku: line.product.sku,
    name: line.product.name,
    qty: line.qty,
    unitPriceCents: line.product.priceCents,
    lineTotalCents: line.product.priceCents * line.qty,
    stockLabel: stock.label,
    stockTone: stock.tone,
    blocksCheckout: stock.blocksCheckout
  };
}

export function buildCartPanelViewModel(lines: CartLine[]): CartPanelViewModel {
  const readiness = validateCartForCheckout(lines);
  return {
    lines: lines.map(buildCartLineViewModel),
    totalCents: calculateCartTotalCents(lines),
    totalQty: calculateCartTotalQty(lines),
    checkoutReady: readiness.ready,
    checkoutReason: readiness.ready ? "" : readiness.reason ?? "Revisa el carrito antes de cobrar."
  };
}
