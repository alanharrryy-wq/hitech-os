// PRISMA_CHART_LAB_TARGET_PROFILES_V3
import type { LabChartPreviewFrame } from "./chart-lab-types";

export type ChartLabTargetProfile = {
  id: LabChartPreviewFrame;
  label: string;
  purpose: string;
  maxLabelDensity: number;
  animationScale: number;
  shadowScale: number;
  tooltipMode: "rich" | "touch" | "compact";
  interactionLevel: "full" | "touch" | "minimal";
  preferredHeight: number;
};

export const CHART_LAB_TARGET_PROFILES: Record<LabChartPreviewFrame, ChartLabTargetProfile> = {
  pc: {
    id: "pc",
    label: "PC",
    purpose: "Full detail, rich tooltips, brush/dataZoom, dense but readable labels.",
    maxLabelDensity: 100,
    animationScale: 1,
    shadowScale: 1,
    tooltipMode: "rich",
    interactionLevel: "full",
    preferredHeight: 680
  },
  tablet: {
    id: "tablet",
    label: "Tablet",
    purpose: "Touch-friendly controls, larger targets, fewer micro labels.",
    maxLabelDensity: 72,
    animationScale: 0.82,
    shadowScale: 0.72,
    tooltipMode: "touch",
    interactionLevel: "touch",
    preferredHeight: 620
  },
  mobile: {
    id: "mobile",
    label: "Mobile",
    purpose: "Extreme legibility, compact tooltip, critical labels only.",
    maxLabelDensity: 42,
    animationScale: 0.55,
    shadowScale: 0.42,
    tooltipMode: "compact",
    interactionLevel: "minimal",
    preferredHeight: 560
  }
};

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function asRecords(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) return [];
  return value.map(asRecord).filter((item): item is Record<string, unknown> => Boolean(item));
}

export function getChartLabTargetProfile(target: LabChartPreviewFrame): ChartLabTargetProfile {
  return CHART_LAB_TARGET_PROFILES[target] ?? CHART_LAB_TARGET_PROFILES.pc;
}

export function applyTargetProfileToOption(option: Record<string, unknown>, target: LabChartPreviewFrame): Record<string, unknown> {
  const profile = getChartLabTargetProfile(target);
  const next = option;
  const tooltip = asRecord(next.tooltip) ?? {};
  tooltip.trigger = tooltip.trigger ?? "item";
  tooltip.confine = true;
  tooltip.enterable = target !== "mobile";
  tooltip.extraCssText = `${typeof tooltip.extraCssText === "string" ? tooltip.extraCssText : ""};max-width:${target === "mobile" ? 260 : target === "tablet" ? 360 : 520}px;`;
  next.tooltip = tooltip;

  for (const series of asRecords(next.series)) {
    const label = asRecord(series.label) ?? {};
    if (target === "mobile" && label.show === true) label.show = false;
    if (target === "tablet" && label.show === true) label.fontSize = Math.max(11, Number(label.fontSize ?? 11));
    series.label = label;
    const itemStyle = asRecord(series.itemStyle) ?? {};
    if (typeof itemStyle.shadowBlur === "number") itemStyle.shadowBlur = Math.round(itemStyle.shadowBlur * profile.shadowScale);
    series.itemStyle = itemStyle;
  }

  if (typeof next.animationDuration === "number") next.animationDuration = Math.round(next.animationDuration * profile.animationScale);
  if (typeof next.animationDurationUpdate === "number") next.animationDurationUpdate = Math.round(next.animationDurationUpdate * profile.animationScale);
  return next;
}

export function validateChartLabTargetProfiles(): string[] {
  const errors: string[] = [];
  for (const target of ["pc", "tablet", "mobile"] as const) {
    const profile = CHART_LAB_TARGET_PROFILES[target];
    if (!profile) errors.push(`Missing target profile: ${target}`);
    if (profile && profile.maxLabelDensity < 0) errors.push(`Invalid label density for ${target}`);
    if (profile && profile.preferredHeight < 320) errors.push(`Preferred height too small for ${target}`);
  }
  return errors;
}
