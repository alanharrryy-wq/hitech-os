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

