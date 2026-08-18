import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { readPosListInput } from "@/server/pos-api/validators";
import { buildPendingOfflineSyncPanel } from "@/server/pos-sync-panel";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type SyncPanelInput = ReturnType<typeof readPosListInput>;

type PrismaTabboom1CacheEntry = {
  at: number;
  status: number;
  body: string;
  headers: [string, string][];
};

type PrismaTabboom1State = {
  cache?: PrismaTabboom1CacheEntry;
  inflight?: Promise<Response>;
  touchedAt: number;
};

type PrismaTabboom1Store = {
  states: Map<string, PrismaTabboom1State>;
};

const PRISMA_TABBOOM1_CACHE_KEY = "__prismaTabboom1_tablet_sync_panel";
const PRISMA_TABBOOM1_TTL_MS = Number(process.env.PRISMA_TABBOOM1_SYNC_CACHE_TTL_MS ?? "750");
const PRISMA_TABBOOM1_TIMEOUT_MS = Number(process.env.PRISMA_TABBOOM1_SYNC_TIMEOUT_MS ?? "1050");
const PRISMA_TABBOOM1_MAX_QUERY_STATES = 128;

async function prismaTabboom1OriginalGET(input: SyncPanelInput) {
  try {
    const panel = await buildPendingOfflineSyncPanel(input);
    return ok(panel, undefined, {
      endpoint: "GET /api/pos/sync/panel",
      businessId: input.businessId
    });
  } catch (error) {
    return toPosApiError(error);
  }
}

function prismaTabboom1QueryKey(input: SyncPanelInput) {
  return JSON.stringify({
    businessId: input.businessId,
    limit: input.limit,
    status: input.status?.trim().toLowerCase() ?? ""
  });
}

function prismaTabboom1Store(): PrismaTabboom1Store {
  const globalStore = globalThis as unknown as Record<string, PrismaTabboom1Store>;
  globalStore[PRISMA_TABBOOM1_CACHE_KEY] ??= { states: new Map() };
  return globalStore[PRISMA_TABBOOM1_CACHE_KEY];
}

function prismaTabboom1PruneStore(store: PrismaTabboom1Store, keepKey: string) {
  if (store.states.size < PRISMA_TABBOOM1_MAX_QUERY_STATES) return;
  const candidates = [...store.states.entries()]
    .filter(([key, state]) => key !== keepKey && !state.inflight)
    .sort((left, right) => left[1].touchedAt - right[1].touchedAt);
  const excess = store.states.size - PRISMA_TABBOOM1_MAX_QUERY_STATES + 1;
  for (const [key] of candidates.slice(0, Math.max(1, excess))) {
    store.states.delete(key);
  }
}

function prismaTabboom1State(cacheKey: string): PrismaTabboom1State {
  const store = prismaTabboom1Store();
  const existing = store.states.get(cacheKey);
  if (existing) {
    existing.touchedAt = Date.now();
    return existing;
  }
  prismaTabboom1PruneStore(store, cacheKey);
  const created: PrismaTabboom1State = { touchedAt: Date.now() };
  store.states.set(cacheKey, created);
  return created;
}

function prismaTabboom1Clone(entry: PrismaTabboom1CacheEntry, cacheState: "hit"): Response {
  const headers = new Headers(entry.headers);
  headers.set("x-prisma-tabboom1-cache", cacheState);
  headers.set("x-prisma-tabboom1-route", "tablet_sync_panel");
  return new Response(entry.body, { status: entry.status, headers });
}

function prismaTabboom1UnverifiedTimeout(): Response {
  const response = fail(
    "SYNC_PANEL_UNVERIFIED",
    "No se pudo confirmar el estado de pendientes a tiempo. La venta local sigue disponible; vuelve a revisar el panel.",
    503,
    {
      source: "PRISMA_TABBOOM1_TIMEOUT_FALLBACK",
      reason: "bounded_timeout",
      localSalesBlocked: false
    }
  );
  response.headers.set("cache-control", "no-store");
  response.headers.set("x-prisma-tabboom1-cache", "timeout-unverified");
  response.headers.set("x-prisma-tabboom1-route", "tablet_sync_panel");
  return response;
}

async function prismaTabboom1OriginalBounded(
  state: PrismaTabboom1State,
  runOriginal: () => Promise<Response>
): Promise<Response> {
  const timeout = new Promise<Response>((resolve) => {
    setTimeout(() => resolve(prismaTabboom1UnverifiedTimeout()), PRISMA_TABBOOM1_TIMEOUT_MS);
  });
  const response = await Promise.race([Promise.resolve().then(runOriginal), timeout]);
  const body = await response.clone().text();
  const headers = Array.from(response.headers.entries());
  if (response.status < 500 && body.length > 0) {
    state.cache = { at: Date.now(), status: response.status, body, headers };
  }
  state.touchedAt = Date.now();
  const finalHeaders = new Headers(headers);
  finalHeaders.set("x-prisma-tabboom1-cache", finalHeaders.get("x-prisma-tabboom1-cache") ?? "miss");
  finalHeaders.set("x-prisma-tabboom1-route", "tablet_sync_panel");
  return new Response(body, { status: response.status, headers: finalHeaders });
}

export async function GET(request: Request) {
  try {
    const input = readPosListInput(new URL(request.url).searchParams, 80, 200);
    const cacheKey = prismaTabboom1QueryKey(input);
    const state = prismaTabboom1State(cacheKey);
    const now = Date.now();

    if (state.cache && now - state.cache.at <= PRISMA_TABBOOM1_TTL_MS) {
      return prismaTabboom1Clone(state.cache, "hit");
    }

    if (state.inflight) {
      return Promise.race([
        state.inflight.then((response) => response.clone()),
        new Promise<Response>((resolve) => {
          setTimeout(() => resolve(prismaTabboom1UnverifiedTimeout()), PRISMA_TABBOOM1_TIMEOUT_MS);
        })
      ]);
    }

    state.inflight = prismaTabboom1OriginalBounded(state, () => prismaTabboom1OriginalGET(input));
    try {
      return await state.inflight;
    } finally {
      state.inflight = undefined;
      state.touchedAt = Date.now();
    }
  } catch (error) {
    return toPosApiError(error);
  }
}
