import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_CASHIER, DEFAULT_POS_API_TERMINAL_ID } from "@/server/pos-api/validators";
import type { RuntimeSnapshotInput } from "./types";

function readEnv(name: string, fallback: string) {
  const value = process.env[name]?.trim();
  return value || fallback;
}

export function readRuntimeSnapshotInput(searchParams?: URLSearchParams): RuntimeSnapshotInput {
  const businessId = searchParams?.get("businessId")?.trim() || readEnv("TABLET_BUSINESS_ID", DEFAULT_POS_API_BUSINESS_ID);
  const terminalId = searchParams?.get("terminalId")?.trim() || readEnv("TABLET_TERMINAL_ID", DEFAULT_POS_API_TERMINAL_ID);
  const operatorId = searchParams?.get("operatorId")?.trim() || readEnv("TABLET_OPERATOR_ID", DEFAULT_POS_API_CASHIER);
  const operatorName = searchParams?.get("operatorName")?.trim() || readEnv("TABLET_OPERATOR_NAME", "Operador");
  const date = searchParams?.get("date")?.trim() || undefined;
  return { businessId, terminalId, operatorId, operatorName, date };
}

export function getRuntimeConnectionOverride() {
  const value = process.env.TABLET_CONNECTION_STATE?.trim().toLowerCase();
  if (value === "offline" || value === "online" || value === "pending" || value === "review") return value;
  return null;
}
