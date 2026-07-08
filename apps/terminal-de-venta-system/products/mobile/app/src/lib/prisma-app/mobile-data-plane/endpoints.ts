import type { MobileDataPlaneConfig } from "./types";

function join(origin: string | null, path: string): string | null {
  if (!origin) return null;
  return `${origin.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}

function preferExternal(endpoint: string | null, localFallback: string): string {
  return endpoint ?? localFallback;
}

function scoped(path: string, config: MobileDataPlaneConfig, options: { terminal?: boolean; date?: boolean; limit?: number } = {}) {
  const url = new URL(path, "http://prisma.local");
  url.searchParams.set("businessId", config.businessId);
  if (options.terminal) url.searchParams.set("terminalId", config.terminalId);
  if (options.date && config.salesDate) url.searchParams.set("date", config.salesDate);
  if (options.limit) url.searchParams.set("limit", String(options.limit));
  return `${url.pathname}${url.search}`;
}

export function tabletEndpoint(config: MobileDataPlaneConfig, path: string): string | null {
  return join(config.tabletOrigin, path);
}

export function pcEndpoint(config: MobileDataPlaneConfig, path: string): string | null {
  return join(config.pcOrigin, path);
}

export function controlEndpoint(config: MobileDataPlaneConfig, path: string): string | null {
  return join(config.controlOrigin, path);
}

export function blackBoxEndpoint(config: MobileDataPlaneConfig, path: string): string | null {
  return join(config.blackBoxOrigin, path);
}

export function mobileDataPlaneEndpointRegistry(config: MobileDataPlaneConfig) {
  const pcSalesControlPath = config.salesDate
    ? `/api/backoffice/sales-control?preset=custom&from=${encodeURIComponent(config.salesDate)}&to=${encodeURIComponent(config.salesDate)}`
    : "/api/backoffice/sales-control?preset=30d";
  return {
    tabletHealth: tabletEndpoint(config, "/api/health"),
    tabletSalesToday: tabletEndpoint(config, scoped("/api/pos/sales/today", config, { terminal: true, date: true })),
    tabletLowStock: tabletEndpoint(config, scoped("/api/pos/inventory/low-stock", config)),
    tabletOutbox: tabletEndpoint(config, scoped("/api/pos/events/outbox", config, { limit: 200 })),
    tabletRecentEvents: tabletEndpoint(config, "/api/pos/events/recent"),
    tabletOperationalToday: tabletEndpoint(config, "/api/pos/reports/operational-today"),
    pcHealth: pcEndpoint(config, "/api/health"),
    pcDashboard: pcEndpoint(config, scoped(pcSalesControlPath, config)),
    pcSyncStatus: pcEndpoint(config, "/api/backoffice/sync/status"),
    pcBranches: pcEndpoint(config, "/api/backoffice/branches"),
    controlHealth: controlEndpoint(config, "/api/health"),
    controlIncidents: preferExternal(controlEndpoint(config, "/api/incidents"), "/api/mobile/alerts"),
    blackBoxHealth: blackBoxEndpoint(config, "/api/health"),
    blackBoxIncidents: preferExternal(blackBoxEndpoint(config, "/api/incidents"), "/api/mobile/alerts")
  };
}
