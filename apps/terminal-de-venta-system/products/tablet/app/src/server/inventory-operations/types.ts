import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID } from "../pos-api/validators";

export type InventoryOperationAction = "adjust" | "count" | "receive";
type InventoryOperationBase = {
  action: InventoryOperationAction;
  businessId: string;
  terminalId: string;
  actorId: string;
  clientRequestId: string;
  location: string;
};
export type InventoryAdjustInput = InventoryOperationBase & { action: "adjust"; productId: string; targetQty: number; reason: string };
export type InventoryCountInput = InventoryOperationBase & { action: "count"; lines: Array<{ productId: string; countedQty: number }>; reason: string };
export type InventoryReceiveInput = InventoryOperationBase & { action: "receive"; purchaseOrderId: string; lines: Array<{ purchaseOrderLineId: string; qtyReceived: number }>; reference: string | null };
export type InventoryOperationInput = InventoryAdjustInput | InventoryCountInput | InventoryReceiveInput;

export type InventoryOperationResult = {
  operationId: string;
  action: InventoryOperationAction;
  businessId: string;
  terminalId: string;
  actorId: string;
  clientRequestId: string;
  createdAt: string;
  deduplicated: boolean;
  affectedProducts: Array<{ productId: string; sku: string; name: string; beforeQty: number; afterQty: number; deltaQty: number }>;
  receipt?: { id: string; folio: string; purchaseOrderId: string; status: string; subtotalCents: number; taxCents: number; totalCents: number };
  count?: { id: string; lineCount: number; variance: number };
};

export type InventoryOperationsSnapshot = {
  purchaseOrders: Array<{
    id: string;
    folio: string;
    supplierId: string;
    supplierName: string;
    status: string;
    lines: Array<{ id: string; productId: string; sku: string; name: string; qtyOrdered: number; qtyReceived: number; qtyRemaining: number }>;
  }>;
  recentCounts: Array<{ id: string; location: string; countedBy: string; variance: number; status: string; countedAt: string }>;
};

export class InventoryOperationError extends Error {
  constructor(readonly code: string, message: string, readonly status = 400, readonly details: Record<string, unknown> = {}) {
    super(message);
    this.name = "InventoryOperationError";
  }
}

function text(value: unknown, fallback = "") {
  return typeof value === "string" ? value.trim() : fallback;
}

function nonNegativeInt(value: unknown, field: string) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 0) throw new InventoryOperationError("INVALID_INVENTORY_QUANTITY", `${field} debe ser entero mayor o igual a cero.`, 400, { field });
  return parsed;
}

function positiveInt(value: unknown, field: string) {
  const parsed = nonNegativeInt(value, field);
  if (parsed <= 0) throw new InventoryOperationError("INVALID_INVENTORY_QUANTITY", `${field} debe ser mayor a cero.`, 400, { field });
  return parsed;
}

function common(body: any) {
  const actorId = text(body?.actorId);
  if (!actorId) throw new InventoryOperationError("ACTOR_REQUIRED", "Falta el responsable de la operación.");
  const clientRequestId = text(body?.clientRequestId);
  if (clientRequestId.length < 8 || clientRequestId.length > 120) throw new InventoryOperationError("INVALID_CLIENT_REQUEST_ID", "El identificador idempotente debe tener entre 8 y 120 caracteres.");
  return {
    businessId: text(body?.businessId, DEFAULT_POS_API_BUSINESS_ID),
    terminalId: text(body?.terminalId, DEFAULT_POS_API_TERMINAL_ID),
    actorId,
    clientRequestId,
    location: text(body?.location, "tablet-floor")
  };
}

export async function readInventoryOperationInput(request: Request): Promise<InventoryOperationInput> {
  const body = await request.json().catch(() => { throw new InventoryOperationError("INVALID_JSON_BODY", "El cuerpo JSON no es válido."); });
  const action = text(body?.action).toLowerCase();
  const base = common(body);
  if (action === "adjust") {
    const productId = text(body?.productId);
    const reason = text(body?.reason);
    if (!productId) throw new InventoryOperationError("PRODUCT_REQUIRED", "Selecciona un producto.");
    if (reason.length < 3 || reason.length > 180) throw new InventoryOperationError("INVALID_INVENTORY_REASON", "Captura un motivo de 3 a 180 caracteres.");
    return { ...base, action, productId, targetQty: nonNegativeInt(body?.targetQty, "targetQty"), reason };
  }
  if (action === "count") {
    if (!Array.isArray(body?.lines) || !body.lines.length || body.lines.length > 80) throw new InventoryOperationError("INVALID_COUNT_LINES", "El conteo requiere entre 1 y 80 productos.");
    const seen = new Set<string>();
    const lines = body.lines.map((line: any, index: number) => {
      const productId = text(line?.productId);
      if (!productId || seen.has(productId)) throw new InventoryOperationError("INVALID_COUNT_LINES", "El conteo contiene productos vacíos o duplicados.", 400, { index });
      seen.add(productId);
      return { productId, countedQty: nonNegativeInt(line?.countedQty, `lines[${index}].countedQty`) };
    });
    const reason = text(body?.reason, "Conteo físico Tablet");
    return { ...base, action, lines, reason };
  }
  if (action === "receive") {
    const purchaseOrderId = text(body?.purchaseOrderId);
    if (!purchaseOrderId) throw new InventoryOperationError("PURCHASE_ORDER_REQUIRED", "Selecciona una orden de compra.");
    if (!Array.isArray(body?.lines) || !body.lines.length || body.lines.length > 80) throw new InventoryOperationError("INVALID_RECEIPT_LINES", "La recepción requiere entre 1 y 80 líneas.");
    const seen = new Set<string>();
    const lines = body.lines.map((line: any, index: number) => {
      const purchaseOrderLineId = text(line?.purchaseOrderLineId);
      if (!purchaseOrderLineId || seen.has(purchaseOrderLineId)) throw new InventoryOperationError("INVALID_RECEIPT_LINES", "La recepción contiene líneas vacías o duplicadas.", 400, { index });
      seen.add(purchaseOrderLineId);
      return { purchaseOrderLineId, qtyReceived: positiveInt(line?.qtyReceived, `lines[${index}].qtyReceived`) };
    });
    return { ...base, action, purchaseOrderId, lines, reference: text(body?.reference) || null };
  }
  throw new InventoryOperationError("INVALID_INVENTORY_ACTION", "Usa adjust, count o receive.");
}

export function readInventorySnapshotInput(searchParams: URLSearchParams) {
  return { businessId: text(searchParams.get("businessId"), DEFAULT_POS_API_BUSINESS_ID), terminalId: text(searchParams.get("terminalId"), DEFAULT_POS_API_TERMINAL_ID) };
}
