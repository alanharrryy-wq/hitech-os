import type { CartLine, PosProduct } from "./cart-state";

export const CART_LIMITS = {
  maxLines: 120,
  maxQtyPerLine: 999
} as const;

export type CartMutationResult = {
  lines: CartLine[];
  changed: boolean;
  /** Visible, non-fatal reason for UI flows that want to show why a cart mutation did not apply. */
  warning?: string;
};

export type CartLineStockSignal = {
  label: string;
  tone: "ok" | "warn" | "danger";
  blocksCheckout: boolean;
};

export type CartCheckoutReadiness = {
  ready: boolean;
  reason: string;
  totalCents: number;
  totalQty: number;
  blockingProductIds: string[];
};

function normalizeCartQuantity(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 1;
  return Math.max(1, Math.min(CART_LIMITS.maxQtyPerLine, Math.trunc(parsed)));
}

function normalizePriceCents(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 0;
  return Math.max(0, Math.trunc(parsed));
}

function sanitizeProduct(product: PosProduct): PosProduct | null {
  if (!product?.id || !product.name || !product.sku) return null;
  if (!product.isActive) return null;
  return {
    ...product,
    priceCents: normalizePriceCents(product.priceCents),
    stockOnHand: Number.isFinite(Number(product.stockOnHand)) ? Math.trunc(Number(product.stockOnHand)) : 0,
    lowStockThreshold: product.lowStockThreshold === undefined ? product.lowStockThreshold : Math.max(0, Math.trunc(Number(product.lowStockThreshold) || 0))
  };
}

export function sanitizeCartLine(line: CartLine | null | undefined): CartLine | null {
  if (!line?.product) return null;
  const product = sanitizeProduct(line.product);
  if (!product) return null;
  return {
    product,
    qty: normalizeCartQuantity(line.qty)
  };
}

export function sanitizeCart(lines: CartLine[] | null | undefined): CartLine[] {
  if (!Array.isArray(lines)) return [];
  const byProduct = new Map<string, CartLine>();
  for (const rawLine of lines) {
    const line = sanitizeCartLine(rawLine);
    if (!line) continue;
    const current = byProduct.get(line.product.id);
    if (!current) {
      byProduct.set(line.product.id, line);
      continue;
    }
    byProduct.set(line.product.id, {
      product: current.product,
      qty: normalizeCartQuantity(current.qty + line.qty)
    });
  }
  return Array.from(byProduct.values()).slice(0, CART_LIMITS.maxLines);
}

function sameCart(a: CartLine[], b: CartLine[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((line, index) => b[index]?.product.id === line.product.id && b[index]?.qty === line.qty);
}

export function addProductToCart(lines: CartLine[], product: PosProduct): CartMutationResult {
  const current = sanitizeCart(lines);
  const cleanProduct = sanitizeProduct(product);
  if (!cleanProduct) return { lines: current, changed: false, warning: "Producto inválido o inactivo." };
  const existing = current.find((line) => line.product.id === cleanProduct.id);
  if (existing) return incrementCartLine(current, cleanProduct.id);
  if (current.length >= CART_LIMITS.maxLines) return { lines: current, changed: false, warning: "El ticket alcanzó el máximo de líneas permitidas." };
  return { lines: [...current, { product: cleanProduct, qty: 1 }], changed: true };
}

export function incrementCartLine(lines: CartLine[], productId: string): CartMutationResult {
  const current = sanitizeCart(lines);
  let changed = false;
  const next = current.map((line) => {
    if (line.product.id !== productId) return line;
    const qty = normalizeCartQuantity(line.qty + 1);
    changed = qty !== line.qty;
    return { ...line, qty };
  });
  return { lines: next, changed };
}

export function decrementCartLine(lines: CartLine[], productId: string): CartMutationResult {
  const current = sanitizeCart(lines);
  let changed = false;
  const next = current.flatMap((line) => {
    if (line.product.id !== productId) return [line];
    changed = true;
    if (line.qty <= 1) return [];
    return [{ ...line, qty: line.qty - 1 }];
  });
  return { lines: next, changed };
}

export function removeCartLine(lines: CartLine[], productId: string): CartMutationResult {
  const current = sanitizeCart(lines);
  const next = current.filter((line) => line.product.id !== productId);
  return { lines: next, changed: next.length !== current.length };
}

export function clearCart(lines: CartLine[]): CartMutationResult {
  return { lines: [], changed: sanitizeCart(lines).length > 0 };
}

export function calculateCartTotalCents(lines: CartLine[]): number {
  return sanitizeCart(lines).reduce((sum, line) => sum + line.product.priceCents * line.qty, 0);
}

export function calculateCartTotalQty(lines: CartLine[]): number {
  return sanitizeCart(lines).reduce((sum, line) => sum + line.qty, 0);
}

export function getCartLineStockSignal(line: CartLine): CartLineStockSignal {
  const cleanLine = sanitizeCartLine(line);
  if (!cleanLine) return { label: "Producto inválido", tone: "danger", blocksCheckout: true };
  const { product, qty } = cleanLine;
  if (product.stockOnHand <= 0) {
    return { label: "Sin existencia", tone: "danger", blocksCheckout: true };
  }
  if (qty > product.stockOnHand) {
    return { label: `Stock insuficiente (${product.stockOnHand} disp.)`, tone: "danger", blocksCheckout: true };
  }
  const threshold = product.lowStockThreshold ?? 0;
  if (threshold > 0 && product.stockOnHand <= threshold) {
    return { label: `Stock bajo (${product.stockOnHand} disp.)`, tone: "warn", blocksCheckout: false };
  }
  return { label: `${product.stockOnHand} disponible(s)`, tone: "ok", blocksCheckout: false };
}

export function validateCartForCheckout(lines: CartLine[]): CartCheckoutReadiness {
  const current = sanitizeCart(lines);
  const totalCents = calculateCartTotalCents(current);
  const totalQty = calculateCartTotalQty(current);
  if (!current.length) {
    return {
      ready: false,
      reason: "Agrega productos antes de cobrar.",
      totalCents,
      totalQty,
      blockingProductIds: []
    };
  }
  const blockingProductIds = current
    .filter((line) => getCartLineStockSignal(line).blocksCheckout)
    .map((line) => line.product.id);
  if (blockingProductIds.length) {
    return {
      ready: false,
      reason: "Hay productos sin existencia suficiente.",
      totalCents,
      totalQty,
      blockingProductIds
    };
  }
  if (totalCents <= 0) {
    return {
      ready: false,
      reason: "El ticket no puede cobrarse en cero.",
      totalCents,
      totalQty,
      blockingProductIds: []
    };
  }
  return {
    ready: true,
    reason: "Listo para cobrar.",
    totalCents,
    totalQty,
    blockingProductIds: []
  };
}

export function serializeCart(lines: CartLine[]): string {
  return JSON.stringify(sanitizeCart(lines));
}

export function hydrateCart(raw: string | null | undefined): CartLine[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as CartLine[];
    return sanitizeCart(parsed);
  } catch {
    return [];
  }
}

export type CheckoutPayloadInput = {
  lines: CartLine[];
  terminalId?: string;
  cashier?: string;
  clientRequestId?: string;
  paymentMethod?: string;
  cashReceivedCents?: number;
};

export type CheckoutPayload = {
  ready: boolean;
  reason: string;
  totalCents: number;
  totalQty: number;
  businessId: string | null;
  terminalId: string;
  cashier: string;
  clientRequestId: string | null;
  paymentMethod: string;
  cashReceivedCents: number;
  items: Array<{ productId: string; sku: string; qty: number; unitPriceCents: number }>;
};

function normalizeCheckoutPayloadInput(input: CartLine[] | CheckoutPayloadInput): CheckoutPayloadInput {
  if (Array.isArray(input)) {
    return { lines: input };
  }
  return input;
}

export function buildCheckoutPayload(input: CartLine[] | CheckoutPayloadInput): CheckoutPayload {
  const normalized = normalizeCheckoutPayloadInput(input);
  const lines = sanitizeCart(normalized.lines);
  const readiness = validateCartForCheckout(lines);
  return {
    ready: readiness.ready,
    reason: readiness.reason,
    totalCents: readiness.totalCents,
    totalQty: readiness.totalQty,
    businessId: lines[0]?.product.businessId ?? null,
    terminalId: normalized.terminalId ?? "terminal_tablet_local_01",
    cashier: normalized.cashier ?? "tablet-cashier",
    clientRequestId: normalized.clientRequestId ?? null,
    paymentMethod: normalized.paymentMethod ?? "cash",
    cashReceivedCents: normalized.cashReceivedCents ?? 0,
    items: lines.map((line) => ({
      productId: line.product.id,
      sku: line.product.sku,
      qty: line.qty,
      unitPriceCents: line.product.priceCents
    }))
  };
}

export function cartLinesEqual(a: CartLine[], b: CartLine[]): boolean {
  return sameCart(sanitizeCart(a), sanitizeCart(b));
}
