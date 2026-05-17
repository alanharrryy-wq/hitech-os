import type { MobileDataPlaneConfig } from "../mobile-data-plane/types";
import { blackBoxEndpoint, controlEndpoint, pcEndpoint, tabletEndpoint } from "../mobile-data-plane/endpoints";

export const TabletConnector = {
  id: "tablet",
  label: "Tablet POS",
  timeoutMs: 2500,
  endpoints(config: MobileDataPlaneConfig) {
    return {
      health: tabletEndpoint(config, "/api/health"),
      salesToday: tabletEndpoint(config, "/api/pos/sales/today"),
      salesDetail: tabletEndpoint(config, "/api/pos/sales/detail"),
      lowStock: tabletEndpoint(config, "/api/pos/inventory/low-stock"),
      outbox: tabletEndpoint(config, "/api/pos/events/outbox"),
      recentEvents: tabletEndpoint(config, "/api/pos/events/recent"),
      currentShift: tabletEndpoint(config, "/api/pos/shift/current"),
      syncPanel: tabletEndpoint(config, "/api/pos/sync/panel")
    };
  }
} as const;

export const PcConnector = {
  id: "pc",
  label: "PC Backoffice",
  timeoutMs: 2500,
  endpoints(config: MobileDataPlaneConfig) {
    return {
      health: pcEndpoint(config, "/api/health"),
      dashboard: pcEndpoint(config, "/api/backoffice/dashboard"),
      inventory: pcEndpoint(config, "/api/backoffice/inventory"),
      purchases: pcEndpoint(config, "/api/backoffice/purchases"),
      suppliers: pcEndpoint(config, "/api/backoffice/suppliers"),
      reorder: pcEndpoint(config, "/api/backoffice/reorder"),
      audit: pcEndpoint(config, "/api/backoffice/audit")
    };
  }
} as const;

export const ControlConnector = {
  id: "control",
  label: "Control Audit",
  timeoutMs: 2000,
  endpoints(config: MobileDataPlaneConfig) {
    return {
      health: controlEndpoint(config, "/api/health"),
      incidents: controlEndpoint(config, "/api/incidents"),
      timeline: controlEndpoint(config, "/api/incidents/timeline"),
      reports: controlEndpoint(config, "/api/reports")
    };
  }
} as const;

export const BlackBoxConnector = {
  id: "blackbox",
  label: "Black-box",
  timeoutMs: 2000,
  endpoints(config: MobileDataPlaneConfig) {
    return {
      health: blackBoxEndpoint(config, "/api/health"),
      incidents: blackBoxEndpoint(config, "/api/incidents"),
      activeIncidents: blackBoxEndpoint(config, "/api/incidents?status=active"),
      resolvedIncidents: blackBoxEndpoint(config, "/api/incidents?status=resolved")
    };
  }
} as const;

export const LocalSnapshotConnector = {
  id: "local",
  label: "Local snapshot",
  timeoutMs: 0,
  endpoints() {
    return { snapshot: "/api/mobile/snapshot" };
  }
} as const;

