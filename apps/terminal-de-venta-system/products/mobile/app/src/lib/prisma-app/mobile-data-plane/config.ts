import type { MobileDataPlaneConfig } from "./types";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../../../shared/customer/prisma-original-customer";

function readInt(name: string, fallback: number, min = 0, max = Number.MAX_SAFE_INTEGER): number {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(max, Math.max(min, parsed));
}

function readString(name: string, fallback: string): string {
  const raw = process.env[name];
  return raw && raw.trim().length > 0 ? raw.trim() : fallback;
}

function readOrigin(name: string, fallback: string | null): string | null {
  const raw = process.env[name];
  const value = raw && raw.trim().length > 0 ? raw.trim() : fallback;
  if (!value) return null;
  try {
    const url = new URL(value);
    url.pathname = url.pathname.replace(/\/+$/, "");
    url.search = "";
    url.hash = "";
    return url.toString().replace(/\/$/, "");
  } catch {
    return fallback;
  }
}

export function getMobileDataPlaneConfig(): MobileDataPlaneConfig {
  return {
    businessId: readString("PRISMA_MOBILE_BUSINESS_ID", PRISMA_ORIGINAL_CUSTOMER.businessId),
    terminalId: readString("PRISMA_MOBILE_TERMINAL_ID", PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId),
    businessName: readString("PRISMA_MOBILE_BUSINESS_NAME", PRISMA_ORIGINAL_CUSTOMER.displayName),
    customerId: readString("PRISMA_MOBILE_CUSTOMER_ID", PRISMA_ORIGINAL_CUSTOMER.customerId),
    tenantId: readString("PRISMA_MOBILE_TENANT_ID", PRISMA_ORIGINAL_CUSTOMER.tenantId),
    licenseId: readString("PRISMA_MOBILE_LICENSE_ID", PRISMA_ORIGINAL_CUSTOMER.licenseId),
    planLabel: readString("PRISMA_MOBILE_PLAN_LABEL", PRISMA_ORIGINAL_CUSTOMER.planLabel),
    licenseStateLabel: readString("PRISMA_MOBILE_LICENSE_STATE_LABEL", "Licencia local pendiente de confirmacion"),
    authorizationLabel: readString("PRISMA_MOBILE_AUTHORIZATION_LABEL", "Mobile vinculado a la cuenta"),
    pcDeviceId: readString("PRISMA_MOBILE_PC_DEVICE_ID", PRISMA_ORIGINAL_CUSTOMER.pcDeviceId),
    tabletDeviceId: readString("PRISMA_MOBILE_TABLET_DEVICE_ID", PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId),
    mobileDeviceId: readString("PRISMA_MOBILE_DEVICE_ID", PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId),
    tabletOrigin: readOrigin("PRISMA_MOBILE_TABLET_ORIGIN", "http://127.0.0.1:3120"),
    pcOrigin: readOrigin("PRISMA_MOBILE_PC_ORIGIN", "http://127.0.0.1:3130"),
    controlOrigin: readOrigin("PRISMA_MOBILE_CONTROL_ORIGIN", null),
    blackBoxOrigin: readOrigin("PRISMA_MOBILE_BLACKBOX_ORIGIN", null),
    requestTimeoutMs: readInt("PRISMA_MOBILE_SOURCE_TIMEOUT_MS", readInt("PRISMA_MOBILE_REQUEST_TIMEOUT_MS", 2500, 250, 15000), 250, 15000),
    tabletTimeoutMs: readInt("PRISMA_MOBILE_TABLET_TIMEOUT_MS", 2500, 250, 15000),
    pcTimeoutMs: readInt("PRISMA_MOBILE_PC_TIMEOUT_MS", 2500, 250, 15000),
    controlTimeoutMs: readInt("PRISMA_MOBILE_CONTROL_TIMEOUT_MS", 2000, 250, 15000),
    blackBoxTimeoutMs: readInt("PRISMA_MOBILE_BLACKBOX_TIMEOUT_MS", 2000, 250, 15000),
    retryCount: readInt("PRISMA_MOBILE_RETRY_COUNT", 1, 0, 4),
    staleAfterMs: readInt("PRISMA_MOBILE_STALE_AFTER_MS", 90000, 15000, 86400000),
    lowStockDefaultThreshold: readInt("PRISMA_MOBILE_LOW_STOCK_THRESHOLD", 4, 0, 999999),
    overstockDefaultThreshold: readInt("PRISMA_MOBILE_OVERSTOCK_THRESHOLD", 72, 1, 999999),
    cashDifferenceWarningCents: readInt("PRISMA_MOBILE_CASH_WARNING_CENTS", 5000, 0, 99999999),
    cashDifferenceCriticalCents: readInt("PRISMA_MOBILE_CASH_CRITICAL_CENTS", 20000, 0, 99999999)
  };
}

export function getMobileDataPlaneConfigDiagnostics(config = getMobileDataPlaneConfig()): string[] {
  const warnings: string[] = [];
  if (!config.tabletOrigin) warnings.push("PRISMA_MOBILE_TABLET_ORIGIN no está configurado; ventas e inventario Tablet quedarán no disponibles.");
  if (!config.pcOrigin) warnings.push("PRISMA_MOBILE_PC_ORIGIN no está configurado; dashboard/backoffice quedará no disponible.");
  if (!config.controlOrigin) warnings.push("PRISMA_MOBILE_CONTROL_ORIGIN no está configurado; auditoría Control queda no disponible.");
  if (!config.blackBoxOrigin) warnings.push("PRISMA_MOBILE_BLACKBOX_ORIGIN no está configurado; caja negra queda no disponible.");
  if (config.cashDifferenceCriticalCents < config.cashDifferenceWarningCents) warnings.push("El umbral crítico de efectivo es menor que el umbral de advertencia.");
  return warnings;
}
