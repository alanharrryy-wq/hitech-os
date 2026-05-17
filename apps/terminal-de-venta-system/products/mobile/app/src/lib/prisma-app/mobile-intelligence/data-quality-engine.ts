import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { DataQualityReport, MobileRuntimeMode, SourceQuality } from "./contracts";
import { DataQualityReportSchema } from "./contracts";
import { sanitizeEvidenceText } from "./evidence";

function toSourceQuality(source: MobileDataPlaneState["sourceStatuses"][number]): SourceQuality {
  return {
    id: source.id,
    label: source.label,
    status: source.status,
    lastSeenAt: source.lastSeenAt,
    freshnessSeconds: source.freshnessSeconds,
    latencyMs: source.latencyMs,
    errorCount: source.errorCount,
    lastError: source.lastError ? sanitizeEvidenceText(source.lastError) : null,
    warnings: source.warnings.map(sanitizeEvidenceText)
  };
}

function runtimeMode(state: MobileDataPlaneState, sources: SourceQuality[]): MobileRuntimeMode {
  if (state.runtimeMode === "demo-disabled" || state.runtimeMode === "stale") return state.runtimeMode;
  if (state.runtimeMode === "live" && state.warnings.length === 0) return "live";
  const tablet = sources.find((source) => source.id === "tablet");
  const pc = sources.find((source) => source.id === "pc");
  const coreSources = [tablet, pc].filter(Boolean) as SourceQuality[];
  const okCore = coreSources.filter((source) => source.status === "ok").length;
  const configuredSources = sources.filter((source) => source.status !== "unknown");
  const anyOk = sources.some((source) => source.status === "ok");
  const allConfiguredFailed = configuredSources.length > 0 && configuredSources.every((source) => source.status === "offline" || source.status === "error");

  if (process.env.PRISMA_MOBILE_DEMO_DATA_MODE === "disabled") return "demo-disabled";
  if (okCore === coreSources.length && coreSources.length >= 2 && state.warnings.length === 0) return "live";
  if (okCore > 0 || anyOk) return "partial";
  if (allConfiguredFailed) return "offline";
  return "unknown";
}

function scoreSources(sources: SourceQuality[]): number {
  const weighted = sources.map((source) => {
    const weight = source.id === "tablet" ? 0.4 : source.id === "pc" ? 0.25 : source.id === "control" ? 0.15 : source.id === "blackbox" ? 0.15 : 0.05;
    const score = source.status === "ok" ? 1 : source.status === "stale" ? 0.68 : source.status === "unknown" ? 0.28 : 0;
    return { weight, score };
  });
  const totalWeight = weighted.reduce((sum, item) => sum + item.weight, 0) || 1;
  return weighted.reduce((sum, item) => sum + item.weight * item.score, 0) / totalWeight;
}

function clampUnit(value: number): number {
  return Math.max(0, Math.min(1, Number(value.toFixed(2))));
}

export function evaluateDataQuality(state: MobileDataPlaneState): DataQualityReport {
  const generatedAt = new Date().toISOString();
  const sources = state.sourceStatuses.map(toSourceQuality);
  const missingSources = sources.filter((source) => source.id !== "local" && (source.status === "offline" || source.status === "error" || source.status === "unknown")).map((source) => source.id);
  const staleSources = sources.filter((source) => source.status === "stale").map((source) => source.id);
  const warnings = [
    ...state.warnings.map(sanitizeEvidenceText),
    ...sources.flatMap((source) => source.warnings.map((warning) => `${source.label}: ${warning}`))
  ].slice(0, 12);
  const mode = runtimeMode(state, sources);
  const completeness = clampUnit(scoreSources(sources));
  const confidencePenalty = warnings.length > 0 ? Math.min(0.25, warnings.length * 0.03) : 0;
  const confidence = clampUnit(completeness - confidencePenalty);
  const freshnessCandidates = sources.flatMap((source) => typeof source.freshnessSeconds === "number" ? [source.freshnessSeconds] : []);
  const freshnessSeconds = freshnessCandidates.length > 0 ? Math.max(...freshnessCandidates) : null;

  return DataQualityReportSchema.parse({
    runtimeMode: mode,
    confidence,
    completeness,
    generatedAt,
    freshnessSeconds,
    missingSources,
    staleSources,
    warnings,
    sources
  });
}
