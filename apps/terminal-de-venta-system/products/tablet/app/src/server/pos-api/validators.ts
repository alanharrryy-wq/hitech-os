/* PRISMA_DARK_PACKSHOTS_197 */

import type { CompleteLocalSaleInput, PosCartLineInput, PosModifierSelectionInput, PosPaymentMethod, PosSalePaymentMethod, SalePaymentTenderInput } from "../pos-engine/types";
import { PRISMA_ORIGINAL_CUSTOMER, normalizePrismaOriginalBusinessId, normalizePrismaOriginalTerminalId } from "../../../../../../shared/customer/prisma-original-customer";

export const DEFAULT_POS_API_BUSINESS_ID = process.env.PRISMA_SYNC_BUSINESS_ID?.trim() || process.env.PRISMA_TABLET_BUSINESS_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_SYNC_BUSINESS_ID?.trim() || PRISMA_ORIGINAL_CUSTOMER.businessId;
export const DEFAULT_POS_API_TERMINAL_ID = process.env.PRISMA_TABLET_TERMINAL_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TABLET_TERMINAL_ID?.trim() || PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId;
export const DEFAULT_POS_API_CASHIER = process.env.PRISMA_TABLET_CASHIER?.trim() || "tablet-cashier";

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

export type SalesHistoryInput = {
  businessId: string;
  terminalId?: string;
  preset: "today" | "yesterday" | "7d" | "30d" | "custom";
  from?: string;
  to?: string;
  query?: string;
  limit: number;
};

export type PosListInput = {
  businessId: string;
  terminalId?: string;
  date?: string;
  limit: number;
  status?: string;
  threshold: number;
};

export type PosExportInput = PosListInput & {
  format: "json" | "csv";
};

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value.trim() : fallback;
}

function normalizeBusinessId(value: unknown) {
  const incoming = normalizePrismaOriginalBusinessId(value);
  return incoming === PRISMA_ORIGINAL_CUSTOMER.businessId ? DEFAULT_POS_API_BUSINESS_ID : incoming;
}

function normalizeTerminalId(value: unknown) {
  const incoming = normalizePrismaOriginalTerminalId(value);
  return incoming === PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId ? DEFAULT_POS_API_TERMINAL_ID : incoming;
}

function asPositiveInteger(value: unknown, fallback: number, max = 100) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return fallback;
  return Math.min(parsed, max);
}

function asOptionalNonNegativeInteger(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 0) throw new Error("INVALID_PAYMENT_AMOUNT");
  return parsed;
}

function asOptionalCustomerId(value: unknown) {
  const customerId = asString(value);
  if (!customerId) return null;
  if (customerId.length > 160) throw new Error("INVALID_SALE_CUSTOMER_ID");
  return customerId;
}

function asBoolean(value: unknown, fallback = false) {
  if (value === true || value === "true" || value === "1") return true;
  if (value === false || value === "false" || value === "0") return false;
  return fallback;
}

function readPaymentMethod(value: unknown): PosSalePaymentMethod {
  const method = asString(value, "cash").toLowerCase();
  if (method === "cash" || method === "card" || method === "transfer" || method === "mixed") return method;
  throw new Error("INVALID_PAYMENT_METHOD");
}

function readTenderType(value: unknown, index: number): PosPaymentMethod {
  const method = asString(value).toLowerCase();
  if (method === "cash" || method === "card" || method === "transfer") return method;
  throw new Error(`INVALID_PAYMENT_TENDER_METHOD:${index}`);
}

function readPaymentTenders(value: unknown): SalePaymentTenderInput[] | undefined {
  if (value === null || value === undefined || value === "") return undefined;
  if (!Array.isArray(value)) throw new Error("INVALID_PAYMENT_TENDERS");
  const tenders = value.map((raw: any, index) => {
    const tenderType = readTenderType(raw?.tenderType ?? raw?.method ?? raw?.paymentMethod, index);
    const amountCents = asOptionalNonNegativeInteger(raw?.amountCents ?? raw?.amount);
    if (amountCents === null) throw new Error(`INVALID_PAYMENT_TENDER_AMOUNT:${index}`);
    const reference = asString(raw?.reference ?? raw?.authorization ?? raw?.folio, "") || null;
    return { tenderType, amountCents, reference };
  });
  return tenders.length ? tenders : undefined;
}

export function readProductSearchInput(searchParams: URLSearchParams): ProductSearchInput {
  return {
    q: asString(searchParams.get("q")),
    businessId: normalizeBusinessId(searchParams.get("businessId")),
    limit: asPositiveInteger(searchParams.get("limit"), 5000, 5000),
    includeInactive: asBoolean(searchParams.get("includeInactive"), false)
  };
}

export function readProductResolveInput(searchParams: URLSearchParams): ProductResolveInput {
  const code = asString(searchParams.get("code"));
  if (!code) throw new Error("MISSING_PRODUCT_CODE");
  return { code, businessId: normalizeBusinessId(searchParams.get("businessId")) };
}

export function readSalesTodayInput(searchParams: URLSearchParams): SalesTodayInput {
  return {
    businessId: normalizeBusinessId(searchParams.get("businessId")),
    terminalId: asString(searchParams.get("terminalId"), "") || undefined,
    date: asString(searchParams.get("date"), "") || undefined
  };
}

export function readSalesHistoryInput(searchParams: URLSearchParams): SalesHistoryInput {
  const rawPreset = asString(searchParams.get("preset"), "7d").toLowerCase();
  const preset = rawPreset === "today" || rawPreset === "yesterday" || rawPreset === "30d" || rawPreset === "custom" ? rawPreset : "7d";
  return {
    businessId: normalizeBusinessId(searchParams.get("businessId")),
    terminalId: asString(searchParams.get("terminalId"), "") || undefined,
    preset,
    from: asString(searchParams.get("from"), "") || undefined,
    to: asString(searchParams.get("to"), "") || undefined,
    query: asString(searchParams.get("q"), "") || undefined,
    limit: asPositiveInteger(searchParams.get("limit"), 120, 200)
  };
}

export function readPosListInput(searchParams: URLSearchParams, defaultLimit = 50, maxLimit = 200): PosListInput {
  return {
    businessId: normalizeBusinessId(searchParams.get("businessId")),
    terminalId: asString(searchParams.get("terminalId"), "") || undefined,
    date: asString(searchParams.get("date"), "") || undefined,
    limit: asPositiveInteger(searchParams.get("limit"), defaultLimit, maxLimit),
    status: asString(searchParams.get("status"), "") || undefined,
    threshold: asPositiveInteger(searchParams.get("threshold"), 5, 9999)
  };
}

export function readPosExportInput(searchParams: URLSearchParams): PosExportInput {
  const format = asString(searchParams.get("format"), "json").toLowerCase();
  if (format !== "json" && format !== "csv") throw new Error("INVALID_EXPORT_FORMAT");
  return { ...readPosListInput(searchParams, 500, 1000), format };
}

function readModifierSelections(value: unknown, index: number): PosModifierSelectionInput[] | undefined {
  if (value === null || value === undefined) return undefined;
  if (!Array.isArray(value)) throw new Error(`INVALID_LINE_MODIFIERS:${index}`);
  const seenGroups = new Set<string>();
  const selections = value.map((raw: any, selectionIndex: number) => {
    const modifierGroupId = asString(raw?.modifierGroupId);
    const optionSource: unknown[] = Array.isArray(raw?.optionIds) ? raw.optionIds : Array.isArray(raw?.options) ? raw.options : [];
    const optionIds: string[] = Array.from(new Set<string>(optionSource.map((optionId) => asString(optionId)).filter((optionId): optionId is string => Boolean(optionId))));
    if (!modifierGroupId || modifierGroupId.length > 160 || !optionIds.length || optionIds.length > 24 || optionIds.some((optionId) => optionId.length > 160)) {
      throw new Error(`INVALID_LINE_MODIFIERS:${index}:${selectionIndex}`);
    }
    if (seenGroups.has(modifierGroupId)) throw new Error(`DUPLICATE_LINE_MODIFIER_GROUP:${index}`);
    seenGroups.add(modifierGroupId);
    return { modifierGroupId, optionIds };
  });
  return selections.length ? selections : undefined;
}

function normalizeLine(raw: any, index: number): PosCartLineInput {
  const qty = Number(raw?.qty ?? raw?.quantity);
  if (!Number.isInteger(qty) || qty <= 0) throw new Error(`INVALID_LINE_QUANTITY:${index}`);

  const productId = asString(raw?.productId);
  const sku = asString(raw?.sku);
  const barcode = asString(raw?.barcode ?? raw?.code);

  if (!productId && !sku && !barcode) throw new Error(`MISSING_LINE_PRODUCT_REF:${index}`);
  const modifierSelections = readModifierSelections(raw?.modifierSelections ?? raw?.modifiers, index);
  return { ...(productId ? { productId } : {}), ...(sku ? { sku } : {}), ...(barcode ? { barcode } : {}), qty, ...(modifierSelections ? { modifierSelections } : {}) };
}

export async function readCompleteSaleInput(request: Request): Promise<CompleteLocalSaleInput> {
  const body = await request.json().catch(() => {
    throw new Error("INVALID_JSON_BODY");
  });

  const linesSource = Array.isArray(body?.lines) ? body.lines : Array.isArray(body?.items) ? body.items : [];
  if (!linesSource.length) throw new Error("EMPTY_CART");

  const paymentMethod = readPaymentMethod(body?.paymentMethod);
  const cashReceivedCents = asOptionalNonNegativeInteger(body?.cashReceivedCents);
  const changeCents = asOptionalNonNegativeInteger(body?.changeCents) ?? 0;
  const paymentTenders = readPaymentTenders(body?.paymentTenders ?? body?.tenders);

  if (paymentMethod === "cash" && cashReceivedCents === null && !paymentTenders?.length) throw new Error("CASH_RECEIVED_REQUIRED");

  return {
    businessId: normalizeBusinessId(body?.businessId),
    terminalId: normalizeTerminalId(body?.terminalId),
    cashSessionId: asString(body?.cashSessionId, "") || null,
    customerId: asOptionalCustomerId(body?.customerId),
    cashier: asString(body?.cashier ?? body?.operatorId, DEFAULT_POS_API_CASHIER),
    location: asString(body?.location, "tablet-floor"),
    allowNegativeStock: asBoolean(body?.allowNegativeStock, false),
    lowStockThreshold: asPositiveInteger(body?.lowStockThreshold, 5, 9999),
    clientRequestId: asString(body?.clientRequestId, "") || undefined,
    paymentMethod,
    cashReceivedCents,
    changeCents,
    paymentTenders,
    lines: linesSource.map((line: any, index: number) => normalizeLine(line, index))
  };
}

export function validatorErrorToMessage(error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  if (message === "INVALID_JSON_BODY") return { code: "INVALID_JSON_BODY", message: "El cuerpo JSON no es válido." };
  if (message === "EMPTY_CART") return { code: "EMPTY_CART", message: "El carrito está vacío." };
  if (message === "MISSING_PRODUCT_CODE") return { code: "MISSING_PRODUCT_CODE", message: "Falta el parámetro code para resolver producto." };
  if (message === "INVALID_EXPORT_FORMAT") return { code: "INVALID_EXPORT_FORMAT", message: "Usa format=json o format=csv." };
  if (message === "INVALID_PAYMENT_METHOD") return { code: "INVALID_PAYMENT_METHOD", message: "Método de pago inválido." };
  if (message === "INVALID_PAYMENT_AMOUNT") return { code: "INVALID_PAYMENT_AMOUNT", message: "Monto de pago inválido." };
  if (message === "INVALID_PAYMENT_TENDERS") return { code: "INVALID_PAYMENT_TENDERS", message: "El desglose de pago no es válido." };
  if (message.startsWith("INVALID_PAYMENT_TENDER_METHOD:")) return { code: "INVALID_PAYMENT_METHOD", message: "Cada pago debe usar efectivo, tarjeta o transferencia." };
  if (message.startsWith("INVALID_PAYMENT_TENDER_AMOUNT:")) return { code: "INVALID_PAYMENT_AMOUNT", message: "Cada pago debe traer importe válido." };
  if (message === "CASH_RECEIVED_REQUIRED") return { code: "CASH_RECEIVED_REQUIRED", message: "Captura efectivo recibido para cerrar pago en efectivo." };
  if (message === "INVALID_SALE_CUSTOMER_ID") return { code: "INVALID_SALE_CUSTOMER_ID", message: "El cliente seleccionado no es válido." };
  if (message.startsWith("INVALID_LINE_QUANTITY:")) return { code: "INVALID_QUANTITY", message: "Cada línea debe traer cantidad entera mayor a cero." };
  if (message.startsWith("MISSING_LINE_PRODUCT_REF:")) return { code: "PRODUCT_REF_REQUIRED", message: "Cada línea debe traer productId, sku o barcode." };
  if (message.startsWith("INVALID_LINE_MODIFIERS:")) return { code: "INVALID_LINE_MODIFIERS", message: "Los modificadores de la línea no son válidos." };
  if (message.startsWith("DUPLICATE_LINE_MODIFIER_GROUP:")) return { code: "DUPLICATE_LINE_MODIFIER_GROUP", message: "Una línea no puede repetir el mismo grupo de modificadores." };
  return { code: "POS_API_VALIDATION_ERROR", message: "Solicitud POS inválida." };
}
