import { NextResponse } from "next/server";
import { checkPrismaPcHealth, loadPrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

async function __prismaTabboom1OriginalGET() {
  const config = loadPrismaTabletPcOriginConfig();
  const result = await checkPrismaPcHealth(config);
  return NextResponse.json(result, { status: 200 });
}


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

const PRISMA_TABBOOM1_CACHE_KEY = "__prismaTabboom1_tablet_pc_health";
const PRISMA_TABBOOM1_TTL_MS = Number(process.env.PRISMA_TABBOOM1_SYNC_CACHE_TTL_MS ?? "650");
const PRISMA_TABBOOM1_TIMEOUT_MS = Number(process.env.PRISMA_TABBOOM1_SYNC_TIMEOUT_MS ?? "950");

function prismaTabboom1State(): PrismaTabboom1State {
  const globalStore = globalThis as unknown as Record<string, PrismaTabboom1State>;
  globalStore[PRISMA_TABBOOM1_CACHE_KEY] ??= {};
  return globalStore[PRISMA_TABBOOM1_CACHE_KEY];
}

function prismaTabboom1Clone(entry: PrismaTabboom1CacheEntry, cacheState: "hit" | "stale"): Response {
  const headers = new Headers(entry.headers);
  headers.set("x-prisma-tabboom1-cache", cacheState);
  headers.set("x-prisma-tabboom1-route", "tablet_pc_health");
  return new Response(entry.body, { status: entry.status, headers });
}

function prismaTabboom1Fallback(state: PrismaTabboom1State): Response {
  if (state.cache) {
    return prismaTabboom1Clone(state.cache, "stale");
  }
  return Response.json({ ok: false, status: "degraded", source: "PRISMA_TABBOOM1_TIMEOUT_FALLBACK", reason: "bounded_timeout", cached: false, checkedAt: new Date().toISOString() }, {
    status: 200,
    headers: {
      "cache-control": "no-store",
      "x-prisma-tabboom1-cache": "timeout-fallback",
      "x-prisma-tabboom1-route": "tablet_pc_health",
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
  finalHeaders.set("x-prisma-tabboom1-route", "tablet_pc_health");
  return new Response(body, { status: response.status, headers: finalHeaders });
}

export async function GET() {
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
  state.inflight = prismaTabboom1OriginalBounded(() => __prismaTabboom1OriginalGET());
  try {
    return await state.inflight;
  } finally {
    state.inflight = undefined;
  }
}
// PRISMA_TABBOOM1_CACHE_END
