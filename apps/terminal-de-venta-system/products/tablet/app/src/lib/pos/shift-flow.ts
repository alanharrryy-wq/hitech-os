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

async function openZeroFloatShift(): Promise<ShiftSummary> {
  const response = await requestJson<{ shift: ShiftSummary }>("/api/pos/shift/open", {
    method: "POST",
    body: JSON.stringify({ cashier: "tablet-cashier", cashierId: "tablet-cashier", cashStartCents: 0 })
  });
  return response.data.shift;
}

export async function ensureLocalShiftOpenForSale(): Promise<ShiftSummary | null> {
  const current = await readCurrentShift();
  if (current?.canSell) return current;

  try {
    return await openZeroFloatShift();
  } catch (error) {
    if (apiErrorCode(error) === "SHIFT_ALREADY_OPEN") return readCurrentShift();
    throw error;
  }
}
