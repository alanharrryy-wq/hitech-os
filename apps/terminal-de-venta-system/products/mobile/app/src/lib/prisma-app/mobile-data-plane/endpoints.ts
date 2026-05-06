import type { MobileDataPlaneConfig } from "./types";

function join(origin: string | null, path: string): string | null {
  if (!origin) return null;
  return `${origin.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}

export function tabletEndpoint(config: MobileDataPlaneConfig, path: string): string | null {
  return join(config.tabletOrigin, path);
}

export function pcEndpoint(config: MobileDataPlaneConfig, path: string): string | null {
  return join(config.pcOrigin, path);
}

export function mobileDataPlaneEndpointRegistry(config: MobileDataPlaneConfig) {
  return {
    tabletHealth: tabletEndpoint(config, "/api/health"),
    tabletSalesToday: tabletEndpoint(config, "/api/pos/sales/today"),
    tabletLowStock: tabletEndpoint(config, "/api/pos/inventory/low-stock"),
    tabletOutbox: tabletEndpoint(config, "/api/pos/events/outbox"),
    tabletRecentEvents: tabletEndpoint(config, "/api/pos/events/recent"),
    tabletOperationalToday: tabletEndpoint(config, "/api/pos/reports/operational-today"),
    pcHealth: pcEndpoint(config, "/api/health"),
    pcDashboard: pcEndpoint(config, "/api/backoffice/dashboard"),
    pcSyncStatus: pcEndpoint(config, "/api/backoffice/sync/status"),
    pcBranches: pcEndpoint(config, "/api/backoffice/branches")
  };
}
