import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID, DEFAULT_POS_API_CASHIER } from "../pos-api/validators";
import type { CloseShiftInput, OpenShiftInput } from "./types";
import { ShiftError } from "./types";

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value.trim() : fallback;
}

function normalizeBusinessId(value: unknown) {
  const incoming = asString(value, "");
  if (!incoming || incoming === "biz_tablet_standalone") return DEFAULT_POS_API_BUSINESS_ID;
  return incoming;
}

function normalizeTerminalId(value: unknown) {
  const incoming = asString(value, "");
  if (!incoming || incoming === "terminal_tablet_local_01") return DEFAULT_POS_API_TERMINAL_ID;
  return incoming;
}

function asCents(value: unknown, field: string) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) throw new ShiftError("INVALID_CASH_AMOUNT", `${field} debe ser un monto valido mayor o igual a cero.`, 400, { field });
  return Math.round(n);
}

export async function readOpenShiftInput(request: Request): Promise<OpenShiftInput> {
  const body = await request.json().catch(() => {
    throw new ShiftError("INVALID_JSON_BODY", "El cuerpo JSON no es valido.", 400);
  });
  const cashier = asString(body?.cashier ?? body?.operatorName, DEFAULT_POS_API_CASHIER);
  if (!cashier) throw new ShiftError("CASHIER_REQUIRED", "Captura el nombre del cajero para abrir turno.", 400);
  return {
    businessId: normalizeBusinessId(body?.businessId),
    terminalId: normalizeTerminalId(body?.terminalId),
    cashierId: asString(body?.cashierId ?? body?.operatorId, cashier),
    cashier,
    cashStartCents: asCents(body?.cashStartCents ?? body?.openingCashCents ?? 0, "cashStartCents")
  };
}

export async function readCloseShiftInput(request: Request): Promise<CloseShiftInput> {
  const body = await request.json().catch(() => {
    throw new ShiftError("INVALID_JSON_BODY", "El cuerpo JSON no es valido.", 400);
  });
  return {
    businessId: normalizeBusinessId(body?.businessId),
    terminalId: normalizeTerminalId(body?.terminalId),
    countedCashCents: asCents(body?.countedCashCents ?? body?.cashEndCents, "countedCashCents"),
    note: asString(body?.note, "") || undefined
  };
}

export function readCurrentShiftInput(searchParams: URLSearchParams) {
  return {
    businessId: normalizeBusinessId(searchParams.get("businessId")),
    terminalId: normalizeTerminalId(searchParams.get("terminalId"))
  };
}
