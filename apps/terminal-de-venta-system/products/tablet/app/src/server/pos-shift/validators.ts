import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID, DEFAULT_POS_API_CASHIER } from "../pos-api/validators";
import type { CloseShiftInput, OpenShiftInput, RecordCashMovementInput } from "./types";
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

function asPositiveCents(value: unknown, field: string) {
  const cents = asCents(value, field);
  if (cents <= 0) throw new ShiftError("INVALID_CASH_AMOUNT", `${field} debe ser mayor a cero.`, 400, { field });
  return cents;
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

export async function readCashMovementInput(request: Request): Promise<RecordCashMovementInput> {
  const body = await request.json().catch(() => {
    throw new ShiftError("INVALID_JSON_BODY", "El cuerpo JSON no es valido.", 400);
  });
  const movement = asString(body?.movement).toUpperCase();
  if (movement !== "CASH_IN" && movement !== "CASH_OUT") {
    throw new ShiftError("INVALID_CASH_MOVEMENT", "Usa CASH_IN o CASH_OUT.", 400, { movement });
  }
  const actorId = asString(body?.actorId ?? body?.cashierId);
  if (!actorId) throw new ShiftError("ACTOR_REQUIRED", "Falta el responsable del movimiento.", 400);
  const clientRequestId = asString(body?.clientRequestId);
  if (clientRequestId.length < 8 || clientRequestId.length > 120) {
    throw new ShiftError("INVALID_CLIENT_REQUEST_ID", "El identificador idempotente debe tener entre 8 y 120 caracteres.", 400);
  }
  const reason = asString(body?.reason);
  if (reason.length < 3 || reason.length > 180) {
    throw new ShiftError("INVALID_CASH_REASON", "Captura un motivo de 3 a 180 caracteres.", 400);
  }
  return {
    businessId: normalizeBusinessId(body?.businessId),
    terminalId: normalizeTerminalId(body?.terminalId),
    actorId,
    clientRequestId,
    movement,
    amountCents: asPositiveCents(body?.amountCents, "amountCents"),
    reason
  };
}
