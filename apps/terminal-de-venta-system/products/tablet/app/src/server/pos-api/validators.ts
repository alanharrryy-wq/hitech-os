import type { CompleteLocalSaleInput, PosCartLineInput } from "../pos-engine/types";

export const DEFAULT_POS_API_BUSINESS_ID = "biz_tablet_standalone";
export const DEFAULT_POS_API_TERMINAL_ID = "terminal_tablet_001";
export const DEFAULT_POS_API_CASHIER = "tablet-cashier";

export type ProductSearchInput = {
  q: string;
  businessId: string;
  limit: number;
  includeInactive: boolean;
};

export type ProductResolveInput = {
  code: string;
  businessId: string;
};

export type SalesTodayInput = {
  businessId: string;
  terminalId?: string;
  date?: string;
};

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value.trim() : fallback;
}

function asPositiveInteger(value: unknown, fallback: number, max = 100) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return fallback;
  return Math.min(parsed, max);
}

function asBoolean(value: unknown, fallback = false) {
  if (value === true || value === "true" || value === "1") return true;
  if (value === false || value === "false" || value === "0") return false;
  return fallback;
}

export function readProductSearchInput(searchParams: URLSearchParams): ProductSearchInput {
  return {
    q: asString(searchParams.get("q")),
    businessId: asString(searchParams.get("businessId"), DEFAULT_POS_API_BUSINESS_ID),
    limit: asPositiveInteger(searchParams.get("limit"), 20, 50),
    includeInactive: asBoolean(searchParams.get("includeInactive"), false)
  };
}

export function readProductResolveInput(searchParams: URLSearchParams): ProductResolveInput {
  const code = asString(searchParams.get("code"));
  if (!code) {
    throw new Error("MISSING_PRODUCT_CODE");
  }
  return {
    code,
    businessId: asString(searchParams.get("businessId"), DEFAULT_POS_API_BUSINESS_ID)
  };
}

export function readSalesTodayInput(searchParams: URLSearchParams): SalesTodayInput {
  return {
    businessId: asString(searchParams.get("businessId"), DEFAULT_POS_API_BUSINESS_ID),
    terminalId: asString(searchParams.get("terminalId"), "") || undefined,
    date: asString(searchParams.get("date"), "") || undefined
  };
}

function normalizeLine(raw: any, index: number): PosCartLineInput {
  const qty = Number(raw?.qty ?? raw?.quantity);
  if (!Number.isInteger(qty) || qty <= 0) {
    throw new Error(`INVALID_LINE_QUANTITY:${index}`);
  }

  const productId = asString(raw?.productId);
  const sku = asString(raw?.sku);
  const barcode = asString(raw?.barcode ?? raw?.code);

  if (!productId && !sku && !barcode) {
    throw new Error(`MISSING_LINE_PRODUCT_REF:${index}`);
  }

  return {
    ...(productId ? { productId } : {}),
    ...(sku ? { sku } : {}),
    ...(barcode ? { barcode } : {}),
    qty
  };
}

export async function readCompleteSaleInput(request: Request): Promise<CompleteLocalSaleInput> {
  const body = await request.json().catch(() => {
    throw new Error("INVALID_JSON_BODY");
  });

  const linesSource = Array.isArray(body?.lines) ? body.lines : Array.isArray(body?.items) ? body.items : [];
  if (!linesSource.length) {
    throw new Error("EMPTY_CART");
  }

  return {
    businessId: asString(body?.businessId, DEFAULT_POS_API_BUSINESS_ID),
    terminalId: asString(body?.terminalId, DEFAULT_POS_API_TERMINAL_ID),
    cashSessionId: asString(body?.cashSessionId, "") || null,
    cashier: asString(body?.cashier ?? body?.operatorId, DEFAULT_POS_API_CASHIER),
    location: asString(body?.location, "tablet-floor"),
    allowNegativeStock: asBoolean(body?.allowNegativeStock, false),
    lowStockThreshold: asPositiveInteger(body?.lowStockThreshold, 5, 9999),
    clientRequestId: asString(body?.clientRequestId, "") || undefined,
    lines: linesSource.map((line: any, index: number) => normalizeLine(line, index))
  };
}

export function validatorErrorToMessage(error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  if (message === "INVALID_JSON_BODY") return { code: "INVALID_JSON_BODY", message: "El cuerpo JSON no es valido." };
  if (message === "EMPTY_CART") return { code: "EMPTY_CART", message: "El carrito esta vacio." };
  if (message === "MISSING_PRODUCT_CODE") return { code: "MISSING_PRODUCT_CODE", message: "Falta el parametro code para resolver producto." };
  if (message.startsWith("INVALID_LINE_QUANTITY:")) return { code: "INVALID_QUANTITY", message: "Cada linea debe traer cantidad entera mayor a cero." };
  if (message.startsWith("MISSING_LINE_PRODUCT_REF:")) return { code: "PRODUCT_REF_REQUIRED", message: "Cada linea debe traer productId, sku o barcode." };
  return { code: "POS_API_VALIDATION_ERROR", message: "Solicitud POS invalida." };
}
