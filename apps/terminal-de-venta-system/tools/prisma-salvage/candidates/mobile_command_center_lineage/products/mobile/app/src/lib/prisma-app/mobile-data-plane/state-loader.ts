import { getMobileDataPlaneConfig, getMobileDataPlaneConfigDiagnostics } from "./config";
import { mobileDataPlaneEndpointRegistry } from "./endpoints";
import { fetchJsonWithRetry, probeFromFetchResult } from "./http";
import { deriveCashState } from "./cash-policy";
import { emptyInventoryWatchlist, normalizeInventoryWatchlist } from "./inventory-adapter";
import { emptyOutboxState, normalizeOutboxState } from "./outbox-adapter";
import { normalizePcDashboard, offlinePcDashboard } from "./pc-adapter";
import { emptySalesToday, normalizeSalesToday } from "./sales-adapter";
import type { DataPlaneRuntimeMode, MobileDataPlaneState } from "./types";

function runtimeMode(tabletOk: boolean, pcOk: boolean): DataPlaneRuntimeMode {
  if (tabletOk && pcOk) return "connected";
  if (tabletOk || pcOk) return "partial";
  return "offline";
}

export async function loadMobileDataPlaneState(): Promise<MobileDataPlaneState> {
  const config = getMobileDataPlaneConfig();
  const endpoints = mobileDataPlaneEndpointRegistry(config);
  const [salesResult, inventoryResult, outboxResult, pcResult, tabletHealthResult, pcHealthResult] = await Promise.all([
    fetchJsonWithRetry<unknown>(endpoints.tabletSalesToday, { upstream: "tablet", role: "sales", timeoutMs: config.requestTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.tabletLowStock, { upstream: "tablet", role: "inventory", timeoutMs: config.requestTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.tabletOutbox, { upstream: "tablet", role: "events", timeoutMs: config.requestTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.pcDashboard, { upstream: "pc", role: "dashboard", timeoutMs: config.requestTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.tabletHealth, { upstream: "tablet", role: "health", timeoutMs: config.requestTimeoutMs, retryCount: 0 }),
    fetchJsonWithRetry<unknown>(endpoints.pcHealth, { upstream: "pc", role: "health", timeoutMs: config.requestTimeoutMs, retryCount: 0 })
  ]);

  const warnings = getMobileDataPlaneConfigDiagnostics(config);
  for (const result of [salesResult, inventoryResult, outboxResult, pcResult]) {
    if (result.status !== "ok") warnings.push(`${result.upstream}/${result.role}: ${result.error ?? result.status}`);
  }

  const salesToday = salesResult.status === "ok" ? normalizeSalesToday(salesResult.data, config) : emptySalesToday();
  const inventory = inventoryResult.status === "ok" ? normalizeInventoryWatchlist(inventoryResult.data, config) : emptyInventoryWatchlist();
  const outbox = outboxResult.status === "ok" ? normalizeOutboxState(outboxResult.data) : emptyOutboxState();
  const pc = pcResult.status === "ok" ? normalizePcDashboard(pcResult.data) : offlinePcDashboard();
  const cash = deriveCashState(salesToday, config);
  const probes = [salesResult, inventoryResult, outboxResult, pcResult, tabletHealthResult, pcHealthResult].map(probeFromFetchResult);
  const mode = runtimeMode(salesResult.status === "ok" || tabletHealthResult.status === "ok", pcResult.status === "ok" || pcHealthResult.status === "ok");
  return { config, probes, salesToday, inventory, outbox, cash, pc, warnings, runtimeMode: mode };
}
