
import type { CartLine } from "./cart-state";

const DEFAULT_TERMINAL_ID = "terminal_tablet_local_01";
const DEFAULT_CASHIER = "tablet-cashier";
const DEFAULT_LOCATION = "tablet-floor";

function readLocalStorage(key: string) {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(key)?.trim() ?? "";
}

export function resolvePaymentSessionContext(lines: CartLine[]) {
  const businessId = lines[0]?.product.businessId;
  const terminalId = readLocalStorage("prisma.tablet.terminalId") || DEFAULT_TERMINAL_ID;
  const cashier = readLocalStorage("prisma.tablet.cashier") || DEFAULT_CASHIER;
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
