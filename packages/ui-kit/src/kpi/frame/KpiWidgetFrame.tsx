"use client";

import type { CSSProperties, HTMLAttributes, PropsWithChildren } from "react";
import { cn } from "../../lib/cn.js";
import { useReducedMotion } from "../motion/useReducedMotion.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type {
  Density,
  KpiStyleId,
  KpiSurfaceId,
  PerfProfile,
  SemanticIntent,
  SizeVariant,
  WidgetId,
  WidgetState
} from "../types.js";

export interface KpiWidgetFrameProps
  extends PropsWithChildren,
    Omit<HTMLAttributes<HTMLElement>, "style"> {
  readonly widgetId: WidgetId;
  readonly styleId?: KpiStyleId | undefined;
  readonly surface?: KpiSurfaceId | undefined;
  readonly size?: SizeVariant | undefined;
  readonly density?: Density | undefined;
  readonly intent?: SemanticIntent | undefined;
  readonly perfProfile?: PerfProfile | undefined;
  readonly state?: WidgetState | undefined;
  readonly hero?: boolean | undefined;
  readonly heroSlot?: "primary" | "support" | undefined;
  readonly style?: CSSProperties | undefined;
}

const MIN_HEIGHT: Readonly<Record<SizeVariant, number>> = {
  xs: 124,
  s: 152,
  m: 188,
  l: 228
};

function resolveHeroMode(hero: boolean | undefined, density: Density, slot: "primary" | "support"): boolean {
  if (!hero) {
    return false;
  }

  // Budget contract: only the designated primary hero keeps elevated treatment.
  return density === "hero" && slot === "primary";
}

export function KpiWidgetFrame({
  widgetId,
  styleId,
  surface,
  size = "m",
  density = "normal",
  intent = "neutral",
  perfProfile = "balanced",
  state = "ready",
  hero,
  heroSlot = "support",
  className,
  style,
  children,
  ...props
}: KpiWidgetFrameProps) {
  const theme = useKpiTheme({ styleId, surface, size, density, intent, perfProfile });
  const motion = useReducedMotion({ perfProfile });
  const heroMode = resolveHeroMode(hero, density, heroSlot);

  return (
    <article
      className={cn("kpi-widget-frame relative isolate overflow-hidden", className)}
      data-kpi-widget={widgetId}
      data-kpi-style={theme.styleId}
      data-kpi-surface={theme.surface}
      data-kpi-perf={theme.perfProfile}
      data-kpi-density={theme.density}
      data-kpi-state={state}
      data-kpi-hero={heroMode ? "on" : "off"}
      aria-busy={state === "loading"}
      style={{
        minHeight: MIN_HEIGHT[size],
        paddingInline: theme.frame.paddingInline,
        paddingBlock: theme.frame.paddingBlock,
        borderRadius: theme.frame.radius,
        border: `1px solid ${theme.frame.hairline}`,
        background:
          theme.styleId === "LIQUID_GLASS"
            ? `linear-gradient(180deg, ${theme.frame.background}, ${theme.frame.tint})`
            : theme.frame.background,
        boxShadow: heroMode
          ? `${theme.frame.shadow}, 0 0 0 1px ${theme.frame.highlight}`
          : theme.frame.shadow,
        color: theme.text.primary,
        transform: motion.allowMicroMotion ? "translateY(0)" : "none",
        transition: motion.allowMicroMotion
          ? `transform ${theme.fx.motionDuration} ease, box-shadow ${theme.fx.motionDuration} ease`
          : "none",
        ...style
      }}
      {...props}
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            theme.styleId === "GRAPHITE_PRISM_ISO"
              ? "linear-gradient(160deg, hsl(var(--ui-surface-1) / 0.06), transparent 44%)"
              : "linear-gradient(160deg, hsl(var(--ui-surface-1) / 0.18), transparent 48%)",
          opacity: theme.fx.allowGlow ? (heroMode ? 0.34 : 0.18) : 0.12
        }}
      />
      <div className="relative z-[1]">{children}</div>
    </article>
  );
}
