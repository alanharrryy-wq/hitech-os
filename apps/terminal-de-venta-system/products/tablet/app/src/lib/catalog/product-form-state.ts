export type CatalogProduct = {
  id: string;
  businessId?: string;
  sku: string;
  name: string;
  category: string;
  barcode?: string | null;
  barcodes?: string[];
  priceCents: number;
  costCents?: number;
  stockOnHand: number;
  isActive: boolean;
};

export type CatalogProductFormState = {
  id?: string;
  sku: string;
  name: string;
  category: string;
  barcode: string;
  price: string;
  cost: string;
  stockOnHand: string;
  isActive: boolean;
};

export type CatalogApiOk<T> = { ok: true; data: T; meta: Record<string, unknown> };
export type CatalogApiFail = { ok: false; code: string; message: string; details: Record<string, unknown> };
export type CatalogApiResponse<T> = CatalogApiOk<T> | CatalogApiFail;

export const emptyProductForm: CatalogProductFormState = {
  sku: "",
  name: "",
  category: "General",
  barcode: "",
  price: "",
  cost: "",
  stockOnHand: "0",
  isActive: true
};

export function formatMoney(cents: number | null | undefined) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format((cents ?? 0) / 100);
}

export function productToForm(product: CatalogProduct): CatalogProductFormState {
  return {
    id: product.id,
    sku: product.sku,
    name: product.name,
    category: product.category || "General",
    barcode: product.barcode || product.barcodes?.[0] || "",
    price: String((product.priceCents ?? 0) / 100),
    cost: String((product.costCents ?? 0) / 100),
    stockOnHand: String(product.stockOnHand ?? 0),
    isActive: product.isActive
  };
}

export function formToPayload(form: CatalogProductFormState) {
  return {
    ...(form.id ? { id: form.id } : {}),
    sku: form.sku.trim(),
    name: form.name.trim(),
    category: form.category.trim() || "General",
    barcode: form.barcode.trim() || null,
    price: Number(form.price),
    cost: Number(form.cost || 0),
    stockOnHand: Number.parseInt(form.stockOnHand || "0", 10),
    isActive: form.isActive
  };
}

export async function catalogRequest<T>(url: string, init?: RequestInit): Promise<CatalogApiOk<T>> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...(init?.headers ?? {})
    }
  });
  const payload = (await response.json()) as CatalogApiResponse<T>;
  if (!payload.ok) throw payload;
  return payload;
}
