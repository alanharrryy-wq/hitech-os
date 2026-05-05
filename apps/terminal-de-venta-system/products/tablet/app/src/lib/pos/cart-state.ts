export type UiState = "idle" | "loading" | "ready" | "empty" | "error" | "success";

export type ApiOk<T> = { ok: true; data: T; meta: Record<string, unknown> };
export type ApiFail = { ok: false; code: string; message: string; details: Record<string, unknown> };
export type ApiResponse<T> = ApiOk<T> | ApiFail;

export type PosProduct = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  category?: string;
  barcode?: string | null;
  barcodes?: string[];
  priceCents: number;
  stockOnHand: number;
  lowStockThreshold?: number;
  isActive: boolean;
};

export type CartLine = {
  product: PosProduct;
  qty: number;
};

export type CompletedSale = {
  saleId: string;
  folio: string;
  businessId: string;
  terminalId: string;
  cashier: string;
  totalCents: number;
  status: string;
  createdAt: string;
  lines: Array<{ productId: string; sku: string; productName: string; qty: number; totalCents: number }>;
  events: Array<{ topic: string }>;
};

export const POS_CART_STORAGE_KEY = "prisma.tablet.pos.activeCart.v2";

export function formatMoney(cents: number | null | undefined) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format((cents ?? 0) / 100);
}

export function cartTotalCents(lines: CartLine[]) {
  return lines.reduce((sum, line) => sum + line.product.priceCents * line.qty, 0);
}

export function cartTotalQty(lines: CartLine[]) {
  return lines.reduce((sum, line) => sum + line.qty, 0);
}

export function makeClientRequestId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `sale_${Date.now()}_${Math.random().toString(36).slice(2)}`;
}

export function readCartFromStorage(): CartLine[] {
  if (typeof window === "undefined") return [];
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

export function writeCartToStorage(lines: CartLine[]) {
  if (typeof window === "undefined") return;
  if (!lines.length) {
    window.localStorage.removeItem(POS_CART_STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(POS_CART_STORAGE_KEY, JSON.stringify(lines));
}

export function clearCartStorage() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(POS_CART_STORAGE_KEY);
}

export async function requestJson<T>(url: string, init?: RequestInit): Promise<ApiOk<T>> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...(init?.headers ?? {})
    }
  });

  let payload: ApiResponse<T> | null = null;
  try {
    payload = (await response.json()) as ApiResponse<T>;
  } catch {
    payload = null;
  }

  if (!payload) {
    throw {
      ok: false,
      code: response.ok ? "POS_API_INVALID_RESPONSE" : "POS_API_HTTP_ERROR",
      message: response.ok ? "La respuesta del punto de venta no fue JSON valido." : `El punto de venta respondio HTTP ${response.status}.`,
      details: { status: response.status, url }
    } satisfies ApiFail;
  }

  if (!payload.ok) throw payload;

  if (!response.ok) {
    throw {
      ok: false,
      code: "POS_API_HTTP_ERROR",
      message: `El punto de venta respondio HTTP ${response.status}.`,
      details: { status: response.status, url }
    } satisfies ApiFail;
  }

  return payload;
}

export type CompletedSaleReceipt = CompletedSale & { paymentMethod?: string; cashReceivedCents?: number; changeCents?: number; clientRequestId?: string };
