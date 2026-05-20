import { requestJson } from "./cart-state";

export type ShiftSummary = {
  id: string;
  businessId: string;
  terminalId: string;
  cashier: string;
  status: "OPEN" | "CLOSED";
  canSell: boolean;
};

export function apiErrorCode(error: unknown): string {
  if (!error || typeof error !== "object") return "";
  if ("code" in error) return String((error as { code?: unknown }).code ?? "").toUpperCase();
  return "";
}

async function readCurrentShift(): Promise<ShiftSummary | null> {
  const response = await requestJson<{ shift: ShiftSummary | null }>("/api/pos/shift/current");
  return response.data.shift ?? null;
}

export async function readLocalShiftForSale(): Promise<ShiftSummary | null> {
  return readCurrentShift();
}

/**
 * Deprecated compatibility surface. Manual shift open lives in /shift only.
 * Sale completion must surface SHIFT_NOT_OPEN instead of mutating cash state.
 */
export async function ensureLocalShiftOpenForSale(): Promise<ShiftSummary | null> {
  return readCurrentShift();
}
