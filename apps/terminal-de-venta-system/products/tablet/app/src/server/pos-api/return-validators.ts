import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_CASHIER } from "./validators";

function clean(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function positiveInt(value: unknown) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : null;
}

export async function readCreateSaleReturnInput(request: Request) {
  const body = await request.json().catch(() => {
    throw new Error("INVALID_JSON_BODY");
  });
  if (!body?.saleFolio) throw new Error("RETURN_SALE_FOLIO_REQUIRED");
  const amountCents = positiveInt(body?.amountCents);
  if (amountCents === null) throw new Error("INVALID_RETURN_AMOUNT");
  const lines = Array.isArray(body?.lines) ? body.lines : [];
  if (!lines.length) throw new Error("RETURN_LINES_REQUIRED");
  return {
    businessId: clean(body.businessId) || DEFAULT_POS_API_BUSINESS_ID,
    terminalId: clean(body.terminalId),
    cashSessionId: clean(body.cashSessionId),
    actorId: clean(body.actorId ?? body.cashier),
    saleId: clean(body.saleId),
    saleFolio: clean(body.saleFolio),
    reason: clean(body.reason) || "other",
    reasonLabel: clean(body.reasonLabel) || "Otro motivo",
    notes: String(body.notes || "").slice(0, 500),
    amountCents,
    cashier: clean(body.cashier) || DEFAULT_POS_API_CASHIER,
    lines
  };
}

export function returnValidatorErrorToMessage(error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  if (message === "RETURN_LINES_REQUIRED") return { code: message, message: "Selecciona productos para devolver." };
  if (message === "INVALID_RETURN_AMOUNT") return { code: message, message: "El importe de devolución no es válido." };
  if (message === "RETURN_SALE_FOLIO_REQUIRED") return { code: message, message: "La devolución necesita folio origen." };
  if (message === "RETURN_SALE_NOT_FOUND") return { code: message, message: "No encontré el ticket origen para registrar la devolución." };
  if (message === "RETURN_QTY_EXCEEDS_AVAILABLE") return { code: message, message: "La cantidad a devolver excede lo vendido o ya devuelto en ese ticket." };
  if (message === "RETURN_AMOUNT_MISMATCH") return { code: message, message: "El importe de devolución no coincide con las líneas seleccionadas." };
  return { code: "RETURN_VALIDATION_ERROR", message: "Revisa los datos de la devolución." };
}
