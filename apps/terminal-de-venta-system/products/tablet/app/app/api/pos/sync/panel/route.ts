import{toPosApiError}from"@/server/pos-api/errors";import{ok}from"@/server/pos-api/responses";import{readPosListInput}from"@/server/pos-api/validators";import{buildPendingOfflineSyncPanel}from"@/server/pos-sync-panel";export const runtime="nodejs";export const dynamic="force-dynamic";async function __prismaTabboom1OriginalGET(request:Request){try{const input=readPosListInput(new URL(request.url).searchParams,80,200);const panel=await buildPendingOfflineSyncPanel(input);return ok(panel,undefined,{endpoint:"GET /api/pos/sync/panel",businessId:input.businessId})}catch(error){return toPosApiError(error)}}


// PRISMA_TABBOOM1_CACHE_BEGIN
type PrismaTabboom1CacheEntry = {
  at: number;
  status: number;
  body: string;
  headers: [string, string][];
};

type PrismaTabboom1State = {
  cache?: PrismaTabboom1CacheEntry;
  inflight?: Promise<Response>;
};

const PRISMA_TABBOOM1_CACHE_KEY = "__prismaTabboom1_tablet_sync_panel";
const PRISMA_TABBOOM1_TTL_MS = Number(process.env.PRISMA_TABBOOM1_SYNC_CACHE_TTL_MS ?? "750");
const PRISMA_TABBOOM1_TIMEOUT_MS = Number(process.env.PRISMA_TABBOOM1_SYNC_TIMEOUT_MS ?? "1050");

function prismaTabboom1State(): PrismaTabboom1State {
  const globalStore = globalThis as unknown as Record<string, PrismaTabboom1State>;
  globalStore[PRISMA_TABBOOM1_CACHE_KEY] ??= {};
  return globalStore[PRISMA_TABBOOM1_CACHE_KEY];
}

function prismaTabboom1Clone(entry: PrismaTabboom1CacheEntry, cacheState: "hit" | "stale"): Response {
  const headers = new Headers(entry.headers);
  headers.set("x-prisma-tabboom1-cache", cacheState);
  headers.set("x-prisma-tabboom1-route", "tablet_sync_panel");
  return new Response(entry.body, { status: entry.status, headers });
}

function prismaTabboom1Fallback(state: PrismaTabboom1State): Response {
  if (state.cache) {
    return prismaTabboom1Clone(state.cache, "stale");
  }
  return Response.json({ ok: true, data: { summary: { total: 0, pending: 0, failed: 0, sent: 0, acked: 0, conflict: 0, risk: "unknown", headline: "Sync panel bounded fallback", operatorMessage: "Panel protegido por timeout/cache; no se disparo envio automatico.", offlineVisible: false, lastCheckedAt: new Date().toISOString() }, items: [], diagnostics: ["PRISMA_TABBOOM1_TIMEOUT_FALLBACK"] }, meta: { endpoint: "GET /api/pos/sync/panel", source: "PRISMA_TABBOOM1_TIMEOUT_FALLBACK" } }, {
    status: 200,
    headers: {
      "cache-control": "no-store",
      "x-prisma-tabboom1-cache": "timeout-fallback",
      "x-prisma-tabboom1-route": "tablet_sync_panel",
    },
  });
}

async function prismaTabboom1OriginalBounded(runOriginal: () => Promise<Response>): Promise<Response> {
  const state = prismaTabboom1State();
  const timeout = new Promise<Response>((resolve) => {
    setTimeout(() => resolve(prismaTabboom1Fallback(state)), PRISMA_TABBOOM1_TIMEOUT_MS);
  });
  const response = await Promise.race([Promise.resolve().then(runOriginal), timeout]);
  const body = await response.clone().text();
  const headers = Array.from(response.headers.entries());
  if (response.status < 500 && body.length > 0) {
    state.cache = { at: Date.now(), status: response.status, body, headers };
  }
  const finalHeaders = new Headers(headers);
  finalHeaders.set("x-prisma-tabboom1-cache", finalHeaders.get("x-prisma-tabboom1-cache") ?? "miss");
  finalHeaders.set("x-prisma-tabboom1-route", "tablet_sync_panel");
  return new Response(body, { status: response.status, headers: finalHeaders });
}

export async function GET(request:Request) {
  const state = prismaTabboom1State();
  const now = Date.now();
  if (state.cache && now - state.cache.at <= PRISMA_TABBOOM1_TTL_MS) {
    return prismaTabboom1Clone(state.cache, "hit");
  }
  if (state.inflight) {
    return Promise.race([
      state.inflight.then((response) => response.clone()),
      new Promise<Response>((resolve) => {
        setTimeout(() => resolve(prismaTabboom1Fallback(state)), PRISMA_TABBOOM1_TIMEOUT_MS);
      }),
    ]);
  }
  state.inflight = prismaTabboom1OriginalBounded(() => __prismaTabboom1OriginalGET(request));
  try {
    return await state.inflight;
  } finally {
    state.inflight = undefined;
  }
}
// PRISMA_TABBOOM1_CACHE_END
