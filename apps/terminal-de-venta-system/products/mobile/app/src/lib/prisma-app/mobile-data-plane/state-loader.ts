import { getMobileDataPlaneConfig, getMobileDataPlaneConfigDiagnostics } from "./config";
import { mobileDataPlaneEndpointRegistry } from "./endpoints";
import { fetchJsonWithRetry, probeFromFetchResult } from "./http";
import { deriveCashState } from "./cash-policy";
import { emptyInventoryWatchlist, normalizeInventoryWatchlist } from "./inventory-adapter";
import { emptyOutboxState, normalizeOutboxState } from "./outbox-adapter";
import { normalizePcDashboard, offlinePcDashboard } from "./pc-adapter";
import { emptySalesToday, normalizeSalesToday } from "./sales-adapter";
import { applyDataSourceFreshness, buildMobileSourceStatuses } from "../mobile-intelligence/source-status";
import type { DataPlaneRuntimeMode, MobileDataPlaneState } from "./types";

function secondsSince(value: string | null): number | null {
  if (!value) return null;
  const time = Date.parse(value);
  if (Number.isNaN(time)) return null;
  return Math.max(0, Math.round((Date.now() - time) / 1000));
}

function runtimeMode(input: { tabletOk: boolean; pcOk: boolean; staleAfterMs: number; oldestPendingAt: string | null; lastSyncedAt: string | null; warnings: string[] }): DataPlaneRuntimeMode {
  if (process.env.PRISMA_MOBILE_DEMO_DATA_MODE === "disabled") return "demo-disabled";
  const oldestPendingAge = secondsSince(input.oldestPendingAt);
  const lastSyncAge = secondsSince(input.lastSyncedAt);
  const staleAfterSeconds = Math.max(1, Math.round(input.staleAfterMs / 1000));
  const staleByPending = oldestPendingAge !== null && oldestPendingAge > staleAfterSeconds;
  const staleBySync = lastSyncAge !== null && lastSyncAge > staleAfterSeconds;
  if (input.tabletOk && input.pcOk && (staleByPending || staleBySync)) return "stale";
  if (input.tabletOk && input.pcOk && input.warnings.length === 0) return "live";
  if (input.tabletOk || input.pcOk) return "partial";
  if (input.warnings.length > 0) return "offline";
  return "unknown";
}

export async function loadMobileDataPlaneState(): Promise<MobileDataPlaneState> {
  const config = getMobileDataPlaneConfig();
  const endpoints = mobileDataPlaneEndpointRegistry(config);
  const [
    salesResult,
    inventoryResult,
    outboxResult,
    pcResult,
    tabletHealthResult,
    pcHealthResult,
    controlHealthResult,
    controlIncidentsResult,
    blackBoxHealthResult,
    blackBoxIncidentsResult
  ] = await Promise.all([
    fetchJsonWithRetry<unknown>(endpoints.tabletSalesToday, { upstream: "tablet", role: "sales", timeoutMs: config.tabletTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.tabletLowStock, { upstream: "tablet", role: "inventory", timeoutMs: config.tabletTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.tabletOutbox, { upstream: "tablet", role: "events", timeoutMs: config.tabletTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.pcDashboard, { upstream: "pc", role: "dashboard", timeoutMs: config.pcTimeoutMs, retryCount: config.retryCount }),
    fetchJsonWithRetry<unknown>(endpoints.tabletHealth, { upstream: "tablet", role: "health", timeoutMs: config.tabletTimeoutMs, retryCount: 0 }),
    fetchJsonWithRetry<unknown>(endpoints.pcHealth, { upstream: "pc", role: "health", timeoutMs: config.pcTimeoutMs, retryCount: 0 }),
    fetchJsonWithRetry<unknown>(endpoints.controlHealth, { upstream: "control", role: "health", timeoutMs: config.controlTimeoutMs, retryCount: 0 }),
    fetchJsonWithRetry<unknown>(endpoints.controlIncidents, { upstream: "control", role: "incidents", timeoutMs: config.controlTimeoutMs, retryCount: 0 }),
    fetchJsonWithRetry<unknown>(endpoints.blackBoxHealth, { upstream: "blackbox", role: "health", timeoutMs: config.blackBoxTimeoutMs, retryCount: 0 }),
    fetchJsonWithRetry<unknown>(endpoints.blackBoxIncidents, { upstream: "blackbox", role: "incidents", timeoutMs: config.blackBoxTimeoutMs, retryCount: 0 })
  ]);

  const warnings = getMobileDataPlaneConfigDiagnostics(config);
  for (const result of [salesResult, inventoryResult, outboxResult, pcResult, controlHealthResult, controlIncidentsResult, blackBoxHealthResult, blackBoxIncidentsResult]) {
    if (result.status !== "ok") warnings.push(`${result.upstream}/${result.role}: ${result.error ?? result.status}`);
  }

  const salesToday = salesResult.status === "ok" ? normalizeSalesToday(salesResult.data, config) : emptySalesToday();
  const inventory = inventoryResult.status === "ok" ? normalizeInventoryWatchlist(inventoryResult.data, config) : emptyInventoryWatchlist();
  const outbox = outboxResult.status === "ok" ? normalizeOutboxState(outboxResult.data) : emptyOutboxState();
  const pc = pcResult.status === "ok" ? normalizePcDashboard(pcResult.data) : offlinePcDashboard();
  const cash = deriveCashState(salesToday, config);
  const fetchResults = [salesResult, inventoryResult, outboxResult, pcResult, tabletHealthResult, pcHealthResult, controlHealthResult, controlIncidentsResult, blackBoxHealthResult, blackBoxIncidentsResult];
  const probes = fetchResults.map(probeFromFetchResult);
  const sourceStatuses = applyDataSourceFreshness(buildMobileSourceStatuses(fetchResults), pcResult.status === "ok" ? pcResult.data : null);
  const mode = runtimeMode({
    tabletOk: salesResult.status === "ok" || tabletHealthResult.status === "ok",
    pcOk: pcResult.status === "ok" || pcHealthResult.status === "ok",
    staleAfterMs: config.staleAfterMs,
    oldestPendingAt: outbox.oldestPendingAt,
    lastSyncedAt: outbox.lastSyncedAt,
    warnings
  });
  return { config, probes, sourceStatuses, salesToday, inventory, outbox, cash, pc, warnings, runtimeMode: mode };
}
