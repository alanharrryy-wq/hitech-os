import type { PrismaChartConfidence, PrismaChartDataSource, PrismaChartDataStatus, PrismaChartFreshness, PrismaChartQuality } from "./prismaChartContracts";

export function confidenceLevel(score: number): PrismaChartConfidence["level"] {
  if (score >= 80) return "high";
  if (score >= 55) return "medium";
  return "low";
}

export function buildConfidence(score: number, reasons: string[]): PrismaChartConfidence {
  const normalized = Math.max(0, Math.min(100, Math.round(score)));
  return { score: normalized, level: confidenceLevel(normalized), reasons };
}

export function buildFreshness(generatedAt: string, maxStaleMinutes: number, staleSources: string[] = []): PrismaChartFreshness {
  return { generatedAt, maxStaleMinutes, staleSources };
}

export function buildMockQuality(generatedAt: string, sourceLabel: string, todo: string): PrismaChartQuality {
  return {
    source: "mock",
    dataStatus: "mock",
    sourceLabel,
    freshness: buildFreshness(generatedAt, 15, ["mock-fallback"]),
    confidence: buildConfidence(30, ["Deterministic mock fallback", "Real adapter not wired yet"]),
    emptyState: "No hay datos suficientes. Ultima actualizacion: --. Confianza: baja.",
    fallbackReason: "Deterministic mock fallback is active.",
    todo
  };
}

export function buildAdapterQuality(
  generatedAt: string,
  source: PrismaChartDataSource,
  sourceLabel: string,
  confidence: number,
  staleSources: string[] = [],
  dataStatus: PrismaChartDataStatus = "partial",
  fallbackReason?: string
): PrismaChartQuality {
  return {
    source,
    dataStatus,
    sourceLabel,
    freshness: buildFreshness(generatedAt, 15, staleSources),
    confidence: buildConfidence(confidence, staleSources.length ? ["Partial or stale source coverage"] : ["Adapter data available"]),
    emptyState: dataStatus === "real" ? "Sin registros para el rango seleccionado." : "Datos parciales o fuente incompleta; se conserva fallback deterministico.",
    fallbackReason
  };
}
