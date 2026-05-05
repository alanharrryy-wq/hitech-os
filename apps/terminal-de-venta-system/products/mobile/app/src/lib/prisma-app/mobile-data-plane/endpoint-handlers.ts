import { noStoreJsonInit, okMobileResponse, type PrismaMobileEndpointId } from "../prisma-app-api-contracts";
import { okMobileSnapshotResponse } from "../prisma-mobile-snapshot-contract";
import { loadMobileDataPlaneState } from "./state-loader";
import { buildAlertsPayload, buildBranchesPayload, buildCashCurrentPayload, buildHealthPayload, buildInventoryWatchlistPayload, buildReportsDailyPayload, buildSalesTodayPayload, buildSnapshotPayload, buildSummaryPayload } from "./payload-builders";

function sourceFromMode(mode: "connected" | "partial" | "offline") {
  return mode === "offline" ? "unavailable" : "connected-data-plane";
}

export async function mobileDataPlaneJson(endpoint: PrismaMobileEndpointId) {
  const state = await loadMobileDataPlaneState();
  const payloadByEndpoint = {
    summary: buildSummaryPayload,
    sales_today: buildSalesTodayPayload,
    cash_current: buildCashCurrentPayload,
    inventory_watchlist: buildInventoryWatchlistPayload,
    alerts: buildAlertsPayload,
    reports_daily: buildReportsDailyPayload,
    branches: buildBranchesPayload,
    health: buildHealthPayload
  } satisfies Record<PrismaMobileEndpointId, (state: Awaited<ReturnType<typeof loadMobileDataPlaneState>>) => unknown>;
  return Response.json(okMobileResponse(endpoint, payloadByEndpoint[endpoint](state), { source: sourceFromMode(state.runtimeMode), runtimeMode: state.runtimeMode, upstreams: state.probes }), noStoreJsonInit());
}

export async function mobileDataPlaneSnapshotJson() {
  const state = await loadMobileDataPlaneState();
  return Response.json(okMobileSnapshotResponse(buildSnapshotPayload(state), sourceFromMode(state.runtimeMode), state.runtimeMode, state.probes), noStoreJsonInit());
}
