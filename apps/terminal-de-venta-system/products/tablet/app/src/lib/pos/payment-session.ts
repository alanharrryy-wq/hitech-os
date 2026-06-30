import type { CartLine } from "./cart-state";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../../shared/customer/prisma-original-customer";

const LEGACY_BUSINESS_ID = "biz_tablet_standalone";
const LEGACY_TERMINAL_ID = "terminal_tablet_local_01";
const LEGACY_CASHIER = "tablet-cashier";
const DEFAULT_LOCATION = "tablet-floor";

function readPublicEnv(...names: string[]) {
  for (const name of names) {
    const value = process.env[name]?.trim();
    if (value) return value;
  }
  return "";
}

const CONFIGURED_BUSINESS_ID = readPublicEnv("NEXT_PUBLIC_PRISMA_SYNC_BUSINESS_ID", "NEXT_PUBLIC_PRISMA_TABLET_BUSINESS_ID") || PRISMA_ORIGINAL_CUSTOMER.businessId;
const CONFIGURED_TERMINAL_ID = readPublicEnv("NEXT_PUBLIC_PRISMA_TABLET_TERMINAL_ID") || PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId;
const CONFIGURED_CASHIER = readPublicEnv("NEXT_PUBLIC_PRISMA_TABLET_CASHIER") || LEGACY_CASHIER;

function readLocalStorage(key: string) {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(key)?.trim() ?? "";
}

function preferConfigured(value: string | null | undefined, legacyValue: string, configuredValue: string) {
  const clean = value?.trim() ?? "";
  if (!clean || clean === legacyValue) return configuredValue;
  return clean;
}

export function resolvePaymentSessionContext(lines: CartLine[]) {
  const businessId = preferConfigured(lines[0]?.product.businessId, LEGACY_BUSINESS_ID, CONFIGURED_BUSINESS_ID);
  const terminalId = CONFIGURED_TERMINAL_ID || preferConfigured(readLocalStorage("prisma.tablet.terminalId"), LEGACY_TERMINAL_ID, CONFIGURED_TERMINAL_ID);
  const cashier = readLocalStorage("prisma.tablet.cashier") || CONFIGURED_CASHIER;
  const cashSessionId = readLocalStorage("prisma.tablet.cashSessionId") || undefined;
  const location = readLocalStorage("prisma.tablet.location") || DEFAULT_LOCATION;

  return {
    businessId,
    terminalId,
    cashier,
    cashSessionId,
    location
  };
}
