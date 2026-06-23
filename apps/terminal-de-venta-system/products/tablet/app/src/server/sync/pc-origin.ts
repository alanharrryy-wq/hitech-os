import { resolveRuntimeContext } from "../../../../../../shared/runtime";

const DEFAULT_CONNECT_TIMEOUT_MS = 2500;
const DEFAULT_PC_ORIGIN = "http://127.0.0.1:3130";
const DEFAULT_PC_INGEST_PATH = "/api/backoffice/sync/ingest";
const DEFAULT_PC_HEALTH_PATH = "/api/health";
const DEFAULT_SYNC_BATCH_SIZE = 10;

export type PrismaTabletPcOriginConfig = {
  enabled: boolean;
  origin: string | null;
  ingestPath: string;
  healthPath: string;
  timeoutMs: number;
  automaticDispatch: boolean;
  ackStrict: boolean;
  batchSize: number;
  maxAttempts: number;
};

function readFlag(name: string, fallback = false): boolean {
  const raw = process.env[name];
  if (!raw) return fallback;
  return ["1", "true", "yes", "on"].includes(raw.trim().toLowerCase());
}

function asBoolean(value: unknown, fallback = false): boolean {
  if (typeof value === "boolean") return value;
  if (typeof value === "string") return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
  return fallback;
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizePcIngestPath(value: string | null): string {
  const path = value?.trim();
  if (!path || path === "/api/sync/ingest") return DEFAULT_PC_INGEST_PATH;
  return path.startsWith("/") ? path : `/${path}`;
}

function normalizePcHealthPath(value: string | null): string {
  const path = value?.trim();
  if (!path || path === "/api/sync/ingest" || path === DEFAULT_PC_INGEST_PATH) return DEFAULT_PC_HEALTH_PATH;
  return path.startsWith("/") ? path : `/${path}`;
}

function readInt(name: string, fallback: number, min: number, max: number): number {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}

export function loadPrismaTabletPcOriginConfig(): PrismaTabletPcOriginConfig {
  const runtime = resolveRuntimeContext();
  const sync = runtime.config?.sync ?? {};
  const runtimeSyncEnabled = asBoolean(sync.enabled, runtime.packageType === "TABLET_PC_MANAGED");
  const origin = sanitizePcOrigin(process.env.PRISMA_TABLET_PC_ORIGIN ?? process.env.PC_ORIGIN ?? asString(sync.pcOrigin) ?? asString(sync.origin) ?? (runtimeSyncEnabled ? DEFAULT_PC_ORIGIN : ""));
  // Default-off by env: the tablet never dispatches to PC unless the operator explicitly enables it.
  // Runtime/package config can still prefill origin, timeout, batch size and health paths.
  const enabled = readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", false) && Boolean(origin);
  return {
    enabled,
    origin,
    ingestPath: normalizePcIngestPath(process.env.PRISMA_TABLET_PC_INGEST_PATH || asString(sync.ingestPath)),
    healthPath: normalizePcHealthPath(process.env.PRISMA_TABLET_PC_HEALTH_PATH || asString(sync.healthPath)),
    timeoutMs: readInt("PRISMA_TABLET_PC_TIMEOUT_MS", Number(sync.timeoutMs) || DEFAULT_CONNECT_TIMEOUT_MS, 250, 15000),
    automaticDispatch: enabled && readFlag("PRISMA_TABLET_SYNC_AUTODISPATCH", asBoolean(sync.automaticDispatch, false)),
    ackStrict: readFlag("PRISMA_TABLET_SYNC_ACK_STRICT", asBoolean(sync.ackStrict, true)),
    batchSize: readInt("PRISMA_TABLET_SYNC_BATCH_SIZE", Number(sync.batchSize) || DEFAULT_SYNC_BATCH_SIZE, 1, 100),
    maxAttempts: readInt("PRISMA_TABLET_SYNC_MAX_ATTEMPTS", Number(sync.maxAttempts) || 8, 1, 30)
  };
}

export function sanitizePcOrigin(raw: string): string | null {
  const trimmed = raw.trim().replace(/\/$/, "");
  if (!trimmed) return null;
  let parsed: URL;
  try {
    parsed = new URL(trimmed);
  } catch {
    return null;
  }
  if (!["http:", "https:"].includes(parsed.protocol)) return null;
  if (parsed.username || parsed.password) return null;
  return parsed.origin;
}

export function pcUrl(config: PrismaTabletPcOriginConfig, path: string): string | null {
  if (!config.origin) return null;
  return `${config.origin}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function checkPrismaPcHealth(config = loadPrismaTabletPcOriginConfig()) {
  const url = pcUrl(config, config.healthPath);
  if (!config.enabled || !url) {
    return { ok: false, enabled: config.enabled, status: "disabled" as const, url: null, error: null };
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), config.timeoutMs);
  try {
    const response = await fetch(url, { method: "GET", signal: controller.signal, cache: "no-store" });
    return { ok: response.ok, enabled: config.enabled, status: response.ok ? "online" as const : "degraded" as const, url, httpStatus: response.status, error: null };
  } catch (error) {
    return { ok: false, enabled: config.enabled, status: "offline" as const, url, error: error instanceof Error ? error.message : String(error) };
  } finally {
    clearTimeout(timer);
  }
}
