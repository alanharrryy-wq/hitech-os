import type { MobileDataPlaneConfig } from "./types";

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
    businessId: readString("PRISMA_MOBILE_BUSINESS_ID", "biz_tablet_standalone"),
    terminalId: readString("PRISMA_MOBILE_TERMINAL_ID", "terminal_tablet_local_01"),
    businessName: readString("PRISMA_MOBILE_BUSINESS_NAME", "PRISMA Operación"),
    tabletOrigin: readOrigin("PRISMA_MOBILE_TABLET_ORIGIN", "http://127.0.0.1:3120"),
    pcOrigin: readOrigin("PRISMA_MOBILE_PC_ORIGIN", "http://127.0.0.1:3130"),
    requestTimeoutMs: readInt("PRISMA_MOBILE_REQUEST_TIMEOUT_MS", 1800, 250, 15000),
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
  if (config.cashDifferenceCriticalCents < config.cashDifferenceWarningCents) warnings.push("El umbral crítico de efectivo es menor que el umbral de advertencia.");
  return warnings;
}
