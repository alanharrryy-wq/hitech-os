import { KPI_WIDGET_CATALOG, type CatalogEntry } from "../registry/catalog.js";
import type { ChartId, Maturity, PerfCost } from "../types.js";

export interface MaturitySignal {
  readonly hasAriaLabel: boolean;
  readonly hasSummary: boolean;
  readonly supportsLoading: boolean;
  readonly supportsEmpty: boolean;
  readonly supportsReducedMotion: boolean;
  readonly supportsPerfProfile: boolean;
  readonly perfCost: PerfCost;
  readonly isAlienTech?: boolean;
}

export interface MaturityScore {
  readonly chartId: ChartId;
  readonly score: number;
  readonly maturity: Maturity;
  readonly reasons: readonly string[];
}

function perfPenalty(cost: PerfCost): number {
  if (cost === "high") {
    return 0.18;
  }

  if (cost === "med") {
    return 0.08;
  }

  return 0;
}

export function classifyMaturity(chartId: ChartId, signal: MaturitySignal): MaturityScore {
  const reasons: string[] = [];
  let score = 1;

  if (!signal.hasAriaLabel) {
    score -= 0.24;
    reasons.push("Missing aria-label contract");
  }

  if (!signal.hasSummary) {
    score -= 0.16;
    reasons.push("Missing textual summary");
  }

  if (!signal.supportsLoading) {
    score -= 0.12;
    reasons.push("No loading state");
  }

  if (!signal.supportsEmpty) {
    score -= 0.12;
    reasons.push("No empty state");
  }

  if (!signal.supportsReducedMotion) {
    score -= 0.16;
    reasons.push("No reduced-motion final state");
  }

  if (!signal.supportsPerfProfile) {
    score -= 0.12;
    reasons.push("No perf profile support");
  }

  score -= perfPenalty(signal.perfCost);
  if (signal.perfCost === "high") {
    reasons.push("High paint/composition cost");
  }

  score = Math.max(0, Math.min(score, 1));

  let maturity: Maturity;
  if (signal.isAlienTech) {
    maturity = "AlienTech";
  } else if (score >= 0.82) {
    maturity = "Mature";
  } else {
    maturity = "NeedsLove";
  }

  return {
    chartId,
    score,
    maturity,
    reasons
  };
}

export function scoreCatalog(entries: readonly CatalogEntry[] = KPI_WIDGET_CATALOG): readonly MaturityScore[] {
  return entries.map((entry) =>
    classifyMaturity(entry.id, {
      hasAriaLabel: true,
      hasSummary: true,
      supportsLoading: true,
      supportsEmpty: true,
      supportsReducedMotion: true,
      supportsPerfProfile: true,
      perfCost: entry.perfCost,
      isAlienTech: entry.maturity === "AlienTech"
    })
  );
}

export function deriveCatalogMaturity(entries: readonly CatalogEntry[] = KPI_WIDGET_CATALOG): readonly CatalogEntry[] {
  const scored = new Map<ChartId, MaturityScore>();
  for (const item of scoreCatalog(entries)) {
    scored.set(item.chartId, item);
  }

  return entries.map((entry) => {
    const score = scored.get(entry.id);
    if (!score) {
      return entry;
    }

    return {
      ...entry,
      maturity: score.maturity
    };
  });
}
