"use client";

import type { CSSProperties, ReactNode } from "react";
import { cn } from "../../lib/cn.js";
import { buildAriaDescribedBy, buildAriaLabel } from "../a11y/aria.js";
import { KpiFooter } from "../frame/KpiFooter.js";
import { KpiHeader } from "../frame/KpiHeader.js";
import { KpiWidgetFrame } from "../frame/KpiWidgetFrame.js";
import { useReducedMotion } from "../motion/useReducedMotion.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type { KpiChartPropsBase, PerfProfile } from "../types.js";

export const CHART_WIDTH = 360;
export const CHART_HEIGHT = 180;
export const CHART_PADDING = 18;

const SR_ONLY_STYLE: CSSProperties = {
  position: "absolute",
  width: 1,
  height: 1,
  padding: 0,
  margin: -1,
  overflow: "hidden",
  clip: "rect(0, 0, 0, 0)",
  border: 0,
  whiteSpace: "nowrap"
};

export interface ChartRenderContext {
  readonly width: number;
  readonly height: number;
  readonly padding: number;
  readonly reducedMotion: boolean;
  readonly perfProfile: PerfProfile;
  readonly canAnimate: boolean;
}

export interface KpiChartSurfaceProps extends KpiChartPropsBase {
  readonly footerNote?: string;
  readonly footerChange?: string;
  readonly emptyMessage?: string;
  readonly loadingMessage?: string;
  readonly children?: ReactNode;
  readonly className?: string;
}

export function KpiChartSurface({
  chartId,
  title,
  subtitle,
  value,
  unit,
  note,
  styleId,
  surface,
  size,
  density,
  intent,
  perfProfile = "balanced",
  state = "ready",
  hero,
  heroSlot,
  className = "",
  ariaLabel,
  summary,
  footerNote,
  footerChange,
  emptyMessage,
  loadingMessage,
  children
}: KpiChartSurfaceProps) {
  const theme = useKpiTheme({ styleId, surface, size, density, intent, perfProfile });
  const motion = useReducedMotion({ perfProfile });
  const describedById = buildAriaDescribedBy(chartId, "summary");
  const resolvedLabel =
    ariaLabel ??
    buildAriaLabel({
      title,
      value,
      unit,
      context: subtitle
    });

  const body =
    state === "loading" ? (
      <KpiLoadingStateSvg
        animate={motion.allowShimmer && theme.fx.allowShimmer}
        label={loadingMessage ?? "Loading chart"}
      />
    ) : state === "empty" ? (
      <KpiEmptyState message={emptyMessage ?? "No data in current filter window."} />
    ) : (
      children
    );

  return (
    <KpiWidgetFrame
      widgetId={chartId}
      styleId={theme.styleId}
      surface={theme.surface}
      size={theme.size}
      density={theme.density}
      intent={theme.intent}
      perfProfile={theme.perfProfile}
      hero={hero}
      heroSlot={heroSlot}
      state={state}
      className={className ?? ""}
      aria-label={resolvedLabel}
      aria-describedby={describedById}
    >
      <KpiHeader
        title={title}
        subtitle={subtitle}
        value={value}
        unit={unit}
        styleId={theme.styleId}
        surface={theme.surface}
        intent={theme.intent}
        perfProfile={theme.perfProfile}
      />

      <div className="mt-3">{body}</div>

      <span id={describedById} style={SR_ONLY_STYLE}>
        {summary ?? note ?? "Chart loaded."}
      </span>

      <KpiFooter
        note={footerNote ?? note}
        change={footerChange}
        styleId={theme.styleId}
        surface={theme.surface}
        intent={theme.intent}
        perfProfile={theme.perfProfile}
      />
    </KpiWidgetFrame>
  );
}

export function createRenderContext(perfProfile: PerfProfile, reducedMotion: boolean): ChartRenderContext {
  return {
    width: CHART_WIDTH,
    height: CHART_HEIGHT,
    padding: CHART_PADDING,
    reducedMotion,
    perfProfile,
    canAnimate: !reducedMotion && perfProfile !== "performance"
  };
}

interface LoadingStateProps {
  readonly animate: boolean;
  readonly label: string;
}

function KpiLoadingStateSvg({ animate, label }: LoadingStateProps) {
  return (
    <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-label={label} className="h-auto w-full">
      <title>{label}</title>
      <rect x="14" y="18" width="332" height="146" rx="10" fill="hsl(var(--ui-surface-2))" />
      <rect x="24" y="40" width="180" height="8" rx="4" fill="hsl(var(--ui-surface-3))">
        {animate ? (
          <animate attributeName="opacity" values="0.35;0.75;0.35" dur="1.2s" repeatCount="indefinite" />
        ) : null}
      </rect>
      <rect x="24" y="64" width="300" height="8" rx="4" fill="hsl(var(--ui-surface-3))">
        {animate ? (
          <animate attributeName="opacity" values="0.3;0.65;0.3" dur="1.4s" repeatCount="indefinite" />
        ) : null}
      </rect>
      <rect x="24" y="102" width="146" height="8" rx="4" fill="hsl(var(--ui-surface-3))">
        {animate ? (
          <animate attributeName="opacity" values="0.25;0.58;0.25" dur="1.1s" repeatCount="indefinite" />
        ) : null}
      </rect>
    </svg>
  );
}

interface EmptyStateProps {
  readonly message: string;
}

function KpiEmptyState({ message }: EmptyStateProps) {
  return (
    <div
      className="grid min-h-[132px] place-items-center rounded-md border border-dashed p-4 text-center"
      style={{ borderColor: "hsl(var(--ui-border-2))", color: "hsl(var(--ui-text-3))" }}
    >
      <p className="m-0 text-sm">{message}</p>
    </div>
  );
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function finiteValues(values: readonly number[]): number[] {
  return values.filter((value) => Number.isFinite(value));
}

export function sum(values: readonly number[]): number {
  return finiteValues(values).reduce((acc, value) => acc + value, 0);
}

export function extent(values: readonly number[]): { min: number; max: number } {
  const clean = finiteValues(values);
  if (clean.length === 0) {
    return { min: 0, max: 1 };
  }

  const min = Math.min(...clean);
  const max = Math.max(...clean);

  if (min === max) {
    return { min: min - 1, max: max + 1 };
  }

  return { min, max };
}

export function xScale(index: number, count: number, width: number, padding = CHART_PADDING): number {
  const span = Math.max(width - padding * 2, 1);
  if (count <= 1) {
    return padding;
  }

  return padding + (index / (count - 1)) * span;
}

export function yScale(value: number, min: number, max: number, height: number, padding = CHART_PADDING): number {
  const span = Math.max(height - padding * 2, 1);
  const normalized = (value - min) / Math.max(max - min, 1e-9);
  return height - padding - normalized * span;
}

export function linePath(
  values: readonly number[],
  width = CHART_WIDTH,
  height = CHART_HEIGHT,
  padding = CHART_PADDING
): string {
  const clean = finiteValues(values);
  if (clean.length === 0) {
    return "";
  }

  const { min, max } = extent(clean);

  return clean
    .map((value, index) => {
      const x = xScale(index, clean.length, width, padding);
      const y = yScale(value, min, max, height, padding);
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function areaPath(
  values: readonly number[],
  width = CHART_WIDTH,
  height = CHART_HEIGHT,
  padding = CHART_PADDING
): string {
  const clean = finiteValues(values);
  if (clean.length === 0) {
    return "";
  }

  const { min, max } = extent(clean);
  const baseline = height - padding;

  const line = clean
    .map((value, index) => {
      const x = xScale(index, clean.length, width, padding);
      const y = yScale(value, min, max, height, padding);
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");

  const firstX = xScale(0, clean.length, width, padding);
  const lastX = xScale(clean.length - 1, clean.length, width, padding);

  return `${line} L${lastX.toFixed(2)} ${baseline.toFixed(2)} L${firstX.toFixed(2)} ${baseline.toFixed(2)} Z`;
}

export function polarToCartesian(centerX: number, centerY: number, radius: number, angle: number): { x: number; y: number } {
  return {
    x: centerX + radius * Math.cos(angle),
    y: centerY + radius * Math.sin(angle)
  };
}

export function arcPath(
  centerX: number,
  centerY: number,
  radius: number,
  startAngle: number,
  endAngle: number
): string {
  const start = polarToCartesian(centerX, centerY, radius, startAngle);
  const end = polarToCartesian(centerX, centerY, radius, endAngle);
  const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;

  return `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${radius.toFixed(2)} ${radius.toFixed(2)} 0 ${largeArc} 1 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
}

export function formatCompact(value: number): string {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function dashedGrid(count: number, width = CHART_WIDTH, height = CHART_HEIGHT): ReactNode {
  return Array.from({ length: count }, (_, index) => {
    const y = CHART_PADDING + ((height - CHART_PADDING * 2) / Math.max(count - 1, 1)) * index;
    return (
      <line
        key={`grid-${index}`}
        x1={CHART_PADDING}
        x2={width - CHART_PADDING}
        y1={y}
        y2={y}
        stroke="hsl(var(--ui-border-1) / 0.35)"
        strokeDasharray="3 4"
      />
    );
  });
}

export function chartClassName(extra?: string): string {
  return cn("h-auto w-full", extra);
}
