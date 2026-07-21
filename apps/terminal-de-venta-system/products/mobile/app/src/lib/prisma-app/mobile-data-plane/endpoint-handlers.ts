import {
  noStoreJsonInit,
  okMobileResponse,
  type PrismaMobileEndpointId
} from "../prisma-app-api-contracts";
import { okMobileSnapshotResponse } from "../prisma-mobile-snapshot-contract";
import { loadAuthorizedMobileState } from "../mobile-security/route-guard";
import {
  buildAlertsPayload,
  buildBranchesPayload,
  buildCashCurrentPayload,
  buildHealthPayload,
  buildInventoryWatchlistPayload,
  buildReportsDailyPayload,
  buildSalesTodayPayload,
  buildSnapshotPayload,
  buildSummaryPayload
} from "./payload-builders";
import { sourceFromRuntimeMode } from "./runtime-mode";

const ENDPOINT_PERMISSION: Record<PrismaMobileEndpointId, string> = {
  summary: "RM.BUSINESS.EXECUTIVE_SUMMARY",
  sales_today: "RM.SALES.SUMMARY",
  cash_current: "RM.CASH.SUMMARY",
  inventory_watchlist: "RM.INVENTORY.WATCHLIST",
  alerts: "RM.RISK.DETAIL",
  reports_daily: "RM.DAILY_BRIEF",
  branches: "RM.CONTEXT.ACTIVE",
  health: "RM.SYSTEM.SUMMARY"
};

function secureJsonInit(mode: string): ResponseInit {
  const init = noStoreJsonInit();
  const headers = new Headers(init.headers);
  headers.set("Vary", "Authorization, Cookie");
  headers.set("X-Prisma-Mobile-Context-Mode", mode);
  return { ...init, headers };
}

export async function mobileDataPlaneJson(
  request: Request,
  endpoint: PrismaMobileEndpointId
) {
  const guarded = await loadAuthorizedMobileState(request, ENDPOINT_PERMISSION[endpoint]);
  if (!guarded.ok) return guarded.response;

  const state = guarded.state;
  const payloadByEndpoint = {
    summary: buildSummaryPayload,
    sales_today: buildSalesTodayPayload,
    cash_current: buildCashCurrentPayload,
    inventory_watchlist: buildInventoryWatchlistPayload,
    alerts: buildAlertsPayload,
    reports_daily: buildReportsDailyPayload,
    branches: buildBranchesPayload,
    health: buildHealthPayload
  } satisfies Record<
    PrismaMobileEndpointId,
    (input: typeof state) => unknown
  >;

  return Response.json(
    okMobileResponse(endpoint, payloadByEndpoint[endpoint](state), {
      source: sourceFromRuntimeMode(state.runtimeMode),
      runtimeMode: state.runtimeMode,
      upstreams: guarded.safeProbes
    }),
    secureJsonInit(guarded.context.authorizationMode)
  );
}

export async function mobileDataPlaneSnapshotJson(request: Request) {
  const guarded = await loadAuthorizedMobileState(request, "MOBILE.SNAPSHOT.LEGACY.READ");
  if (!guarded.ok) return guarded.response;

  const state = guarded.state;
  return Response.json(
    okMobileSnapshotResponse(
      buildSnapshotPayload(state),
      sourceFromRuntimeMode(state.runtimeMode),
      state.runtimeMode,
      guarded.safeProbes
    ),
    secureJsonInit(guarded.context.authorizationMode)
  );
}
