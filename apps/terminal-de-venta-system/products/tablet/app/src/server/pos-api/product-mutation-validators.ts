import { DEFAULT_POS_API_BUSINESS_ID } from "./validators";

export type ProductMutationInput = {
  id?: string;
  businessId: string;
  sku: string;
  name: string;
  category: string;
  barcode: string | null;
  priceCents: number;
  costCents: number;
  stockOnHand: number;
  isActive: boolean;
};

export type BarcodeAvailabilityInput = {
  businessId: string;
  code: string;
  productId?: string;
};

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value.trim() : fallback;
}

function asBoolean(value: unknown, fallback = true) {
  if (value === true || value === "true" || value === "1") return true;
  if (value === false || value === "false" || value === "0") return false;
  return fallback;
}

function asInteger(value: unknown, fallback: number, min: number, max: number) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || !Number.isInteger(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}

function asCents(value: unknown, fallback = 0) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(0, Math.round(parsed));
}

function priceToCents(value: unknown, fallback = 0) {
  const parsed = Number(typeof value === "string" ? value.replace(/,/g, "").trim() : value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(0, Math.round(parsed * 100));
}

function normalizeSku(value: string) {
  return value.trim().replace(/\s+/g, "-").toUpperCase();
}

function requireLength(value: string, min: number, max: number, code: string) {
  if (value.length < min || value.length > max) throw new Error(code);
  return value;
}

export function readProductCreateInput(raw: any): ProductMutationInput {
  const sku = normalizeSku(asString(raw?.sku));
  const name = asString(raw?.name);
  const category = asString(raw?.category, "General") || "General";
  const barcode = asString(raw?.barcode ?? raw?.code, "") || null;
  const priceCents = raw?.priceCents !== undefined ? asCents(raw.priceCents, 0) : priceToCents(raw?.price, 0);
  const costCents = raw?.costCents !== undefined ? asCents(raw.costCents, 0) : priceToCents(raw?.cost, 0);
  const stockOnHand = asInteger(raw?.stockOnHand ?? raw?.initialStock, 0, 0, 999999);

  requireLength(sku, 2, 64, "INVALID_PRODUCT_SKU");
  requireLength(name, 2, 160, "INVALID_PRODUCT_NAME");
  requireLength(category, 2, 80, "INVALID_PRODUCT_CATEGORY");
  if (priceCents <= 0) throw new Error("INVALID_PRODUCT_PRICE");
  if (barcode && (barcode.length < 3 || barcode.length > 64)) throw new Error("INVALID_PRODUCT_BARCODE");

  return {
    businessId: asString(raw?.businessId, DEFAULT_POS_API_BUSINESS_ID),
    sku,
    name,
    category,
    barcode,
    priceCents,
    costCents,
    stockOnHand,
    isActive: asBoolean(raw?.isActive, true)
  };
}

export function readProductUpdateInput(raw: any): ProductMutationInput {
  const input = readProductCreateInput(raw);
  const id = asString(raw?.id ?? raw?.productId);
  requireLength(id, 8, 80, "MISSING_PRODUCT_ID");
  return { ...input, id };
}

export function readBarcodeAvailabilityInput(raw: any): BarcodeAvailabilityInput {
  const code = asString(raw?.code ?? raw?.barcode);
  if (!code) throw new Error("MISSING_BARCODE");
  if (code.length < 3 || code.length > 64) throw new Error("INVALID_PRODUCT_BARCODE");
  return {
    code,
    businessId: asString(raw?.businessId, DEFAULT_POS_API_BUSINESS_ID),
    productId: asString(raw?.productId, "") || undefined
  };
}
