import type { FetchResult, MobileSourceStatus, UpstreamId } from "../mobile-data-plane/types";
import { sanitizeEvidenceText } from "./evidence";

const SOURCE_LABELS: Record<UpstreamId, string> = {
  tablet: "Tablet POS",
  pc: "PC Backoffice",
  control: "Control Audit",
  blackbox: "Black-box",
  local: "Local snapshot"
};

function sourceStatus(id: UpstreamId, results: FetchResult<unknown>[], nowIso: string): MobileSourceStatus {
  if (results.length === 0) {
    return {
      id,
      label: SOURCE_LABELS[id],
      status: "unknown",
      lastSeenAt: null,
      freshnessSeconds: null,
      latencyMs: null,
      errorCount: 0,
      lastError: null,
      warnings: ["Fuente sin probes registrados."]
    };
  }

  const okResults = results.filter((result) => result.status === "ok");
  const disabled = results.every((result) => result.status === "disabled");
  const errors = results.filter((result) => result.status !== "ok" && result.status !== "disabled");
  const latencyMs = okResults.length > 0
    ? Math.round(okResults.reduce((sum, result) => sum + result.latencyMs, 0) / okResults.length)
    : errors[0]?.latencyMs ?? null;
  const lastError = errors[0]?.error ?? (disabled ? "Origen no configurado" : null);
  const lastSeenAt = okResults.length > 0 ? nowIso : null;

  return {
    id,
    label: SOURCE_LABELS[id],
    status: okResults.length > 0 ? "ok" : disabled ? "unknown" : errors.some((result) => result.status === "timeout" || result.status === "network_error") ? "offline" : "error",
    lastSeenAt,
    freshnessSeconds: lastSeenAt ? 0 : null,
    latencyMs,
    errorCount: errors.length,
    lastError: lastError ? sanitizeEvidenceText(lastError) : null,
    warnings: errors.map((result) => `${result.role}: ${sanitizeEvidenceText(result.error ?? result.status)}`).slice(0, 4)
  };
}

export function buildMobileSourceStatuses(results: FetchResult<unknown>[], nowIso = new Date().toISOString()): MobileSourceStatus[] {
  const ids: UpstreamId[] = ["tablet", "pc", "control", "blackbox", "local"];
  return ids.map((id) => sourceStatus(id, results.filter((result) => result.upstream === id), nowIso));
}



type FreshnessOverlayRow = Record<string, unknown>;

function asRecord(value: unknown): FreshnessOverlayRow {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as FreshnessOverlayRow : {};
}

function asSourceId(value: unknown): UpstreamId | null {
  if (value === "tablet" || value === "pc" || value === "control" || value === "blackbox" || value === "local") return value;
  return null;
}

function asStatus(value: unknown): MobileSourceStatus["status"] | null {
  if (value === "ok" || value === "stale" || value === "offline" || value === "error" || value === "unknown") return value;
  if (value === "partial") return "stale";
  return null;
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asIso(value: unknown): string | null {
  if (value instanceof Date) return value.toISOString();
  if (typeof value !== "string" || !value.trim()) return null;
  const time = Date.parse(value);
  return Number.isNaN(time) ? null : new Date(time).toISOString();
}

function parseWarnings(value: unknown): string[] {
  if (Array.isArray(value)) return value.map((item) => sanitizeEvidenceText(String(item))).slice(0, 4);
  if (typeof value !== "string" || !value.trim()) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed.map((item) => sanitizeEvidenceText(String(item.detail ?? item.code ?? item))).slice(0, 4) : [];
  } catch {
    return [sanitizeEvidenceText(value)].slice(0, 4);
  }
}

export function applyDataSourceFreshness(statuses: MobileSourceStatus[], payload: unknown): MobileSourceStatus[] {
  const data = asRecord(payload);
  const sync = asRecord(data.sync ?? data.syncStatus);
  const rows = Array.isArray(sync.dataSourceFreshness)
    ? sync.dataSourceFreshness
    : Array.isArray(data.dataSourceFreshness)
      ? data.dataSourceFreshness
      : Array.isArray(data.sourceFreshness)
        ? data.sourceFreshness
        : [];
  if (rows.length === 0) return statuses;

  const byId = new Map<UpstreamId, MobileSourceStatus>(statuses.map((status) => [status.id, status]));
  for (const raw of rows) {
    const row = asRecord(raw);
    const id = asSourceId(row.source ?? row.sourceId ?? row.id);
    if (!id || !byId.has(id)) continue;
    const current = byId.get(id)!;
    const status = asStatus(row.status) ?? current.status;
    byId.set(id, {
      ...current,
      status,
      lastSeenAt: asIso(row.lastSeenAt ?? row.observedAt ?? row.updatedAt) ?? current.lastSeenAt,
      freshnessSeconds: asNumber(row.freshnessSeconds) ?? current.freshnessSeconds,
      latencyMs: asNumber(row.latencyMs) ?? current.latencyMs,
      errorCount: asNumber(row.errorCount) ?? current.errorCount,
      lastError: typeof row.lastError === "string" ? sanitizeEvidenceText(row.lastError) : current.lastError,
      warnings: parseWarnings(row.warningsJson ?? row.warnings).length ? parseWarnings(row.warningsJson ?? row.warnings) : current.warnings
    });
  }
  return statuses.map((status) => byId.get(status.id) ?? status);
}
