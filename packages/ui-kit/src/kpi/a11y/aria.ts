import type { ChartId, KpiBreakdownDatum, KpiHeatmapCell, KpiSeries } from "../types.js";

function sanitizeIdToken(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function createAriaId(chartId: ChartId, suffix: string): string {
  return `${sanitizeIdToken(chartId)}-${sanitizeIdToken(suffix)}`;
}

export function buildAriaLabel(input: {
  readonly title: string;
  readonly value?: string | number | undefined;
  readonly unit?: string | undefined;
  readonly context?: string | undefined;
}): string {
  const valuePart = input.value === undefined ? "" : ` ${input.value}${input.unit ? ` ${input.unit}` : ""}`;
  const contextPart = input.context ? `. ${input.context}` : "";
  return `${input.title}${valuePart}${contextPart}`.trim();
}

export function buildAriaDescribedBy(chartId: ChartId, section = "summary"): string {
  return createAriaId(chartId, section);
}

export function summarizeSeries(series: readonly KpiSeries[]): string {
  if (series.length === 0) {
    return "No series available.";
  }

  const hero = series.find((entry) => entry.hero) ?? series[0];
  if (hero === undefined) {
    return "No series available.";
  }
  const values = hero.values.filter((value) => Number.isFinite(value));

  if (values.length === 0) {
    return `${hero.label} has no numeric observations.`;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const first = values[0];
  const last = values[values.length - 1];
  if (first === undefined || last === undefined) {
    return `${hero.label} has no numeric observations.`;
  }
  const trend = last > first ? "up" : last < first ? "down" : "flat";

  return `${hero.label} trend ${trend}. Range ${min.toFixed(2)} to ${max.toFixed(2)}.`;
}

export function summarizeBreakdown(items: readonly KpiBreakdownDatum[]): string {
  if (items.length === 0) {
    return "No segments available.";
  }

  const total = items.reduce((sum, item) => sum + Math.max(item.value, 0), 0);
  if (total <= 0) {
    return "All segment values are zero.";
  }

  const first = items[0];
  if (first === undefined) {
    return "No segments available.";
  }
  const dominant = items
    .slice(1)
    .reduce((current, item) => (item.value > current.value ? item : current), first);
  const dominantShare = ((dominant.value / total) * 100).toFixed(1);

  return `${dominant.label} leads at ${dominantShare} percent of total ${total.toFixed(2)}.`;
}

export function summarizeMatrix(input: {
  readonly cells: readonly KpiHeatmapCell[];
  readonly rowLabels: readonly string[];
  readonly colLabels: readonly string[];
}): string {
  const values = input.cells.map((cell) => cell.value).filter((value) => Number.isFinite(value));

  if (values.length === 0) {
    return "No matrix values available.";
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  return `${input.rowLabels.length} rows by ${input.colLabels.length} columns. Value range ${min.toFixed(2)} to ${max.toFixed(2)}.`;
}
