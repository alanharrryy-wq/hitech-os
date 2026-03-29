"use client";

import { useMemo } from "react";
import { coreTokens, semanticTokens } from "../../lib/tokens.js";
import type {
  Density,
  KpiStyleId,
  KpiSurfaceId,
  PerfProfile,
  SemanticIntent,
  SizeVariant
} from "../types.js";

const INTENT_SERIES_TOKENS: Readonly<Record<SemanticIntent, readonly string[]>> = {
  deal: [semanticTokens.accent, semanticTokens.success, semanticTokens.warning, semanticTokens.textSecondary],
  cash: [semanticTokens.success, semanticTokens.accent, semanticTokens.warning, semanticTokens.textSecondary],
  evidence: [semanticTokens.accent, semanticTokens.textSecondary, semanticTokens.textMuted, semanticTokens.success],
  outcome: [semanticTokens.success, semanticTokens.accent, semanticTokens.warning, semanticTokens.textSecondary],
  governance: [semanticTokens.textSecondary, semanticTokens.accent, semanticTokens.success, semanticTokens.warning],
  risk: [semanticTokens.danger, semanticTokens.warning, semanticTokens.textSecondary, semanticTokens.accent],
  neutral: [semanticTokens.accent, semanticTokens.textSecondary, semanticTokens.success, semanticTokens.warning]
};

export interface KpiThemeOptions {
  readonly styleId?: KpiStyleId | undefined;
  readonly surface?: KpiSurfaceId | undefined;
  readonly intent?: SemanticIntent | undefined;
  readonly perfProfile?: PerfProfile | undefined;
  readonly density?: Density | undefined;
  readonly size?: SizeVariant | undefined;
}

export interface KpiTheme {
  readonly styleId: KpiStyleId;
  readonly surface: KpiSurfaceId;
  readonly intent: SemanticIntent;
  readonly perfProfile: PerfProfile;
  readonly density: Density;
  readonly size: SizeVariant;
  readonly text: {
    readonly primary: string;
    readonly secondary: string;
    readonly muted: string;
    readonly emphasis: string;
  };
  readonly frame: {
    readonly background: string;
    readonly tint: string;
    readonly hairline: string;
    readonly highlight: string;
    readonly shadow: string;
    readonly radius: string;
    readonly paddingInline: string;
    readonly paddingBlock: string;
  };
  readonly chart: {
    readonly grid: string;
    readonly series: readonly string[];
    readonly heroSeries: string;
    readonly positive: string;
    readonly caution: string;
    readonly negative: string;
    readonly neutral: string;
    readonly prismGradient: string;
  };
  readonly fx: {
    readonly allowBlur: boolean;
    readonly allowGlow: boolean;
    readonly allowShimmer: boolean;
    readonly hoverScale: number;
    readonly motionDuration: string;
  };
}

function resolvePadding(size: SizeVariant, density: Density): { inline: string; block: string } {
  const table: Readonly<Record<SizeVariant, { inline: string; block: string }>> = {
    xs: { inline: "0.65rem", block: "0.55rem" },
    s: { inline: "0.8rem", block: "0.7rem" },
    m: { inline: "1rem", block: "0.9rem" },
    l: { inline: "1.2rem", block: "1.05rem" }
  };

  const selected = table[size];
  if (density === "dense") {
    return {
      inline: `calc(${selected.inline} - 0.12rem)`,
      block: `calc(${selected.block} - 0.08rem)`
    };
  }

  if (density === "hero") {
    return {
      inline: `calc(${selected.inline} + 0.18rem)`,
      block: `calc(${selected.block} + 0.14rem)`
    };
  }

  return selected;
}

export function useKpiTheme(options: KpiThemeOptions = {}): KpiTheme {
  return useMemo(() => {
    const styleId: KpiStyleId = options.styleId ?? "LIQUID_GLASS";
    const intent: SemanticIntent = options.intent ?? "neutral";
    const perfProfile: PerfProfile = options.perfProfile ?? "balanced";
    const density: Density = options.density ?? "normal";
    const size: SizeVariant = options.size ?? "m";

    const inferredSurface: KpiSurfaceId =
      options.surface ??
      (styleId === "GOLD_NOIR_TERMINAL" ? "matte" : styleId === "GRAPHITE_PRISM_ISO" ? "graphite" : "glass");

    const series = INTENT_SERIES_TOKENS[intent];
    const heroSeries = series[0] ?? semanticTokens.accent;
    const padding = resolvePadding(size, density);

    const liquidPalette = {
      textPrimary: semanticTokens.textPrimary,
      textSecondary: semanticTokens.textSecondary,
      textMuted: semanticTokens.textMuted,
      frameBackground: "hsl(var(--ui-surface-1) / 0.7)",
      frameTint: "hsl(var(--ui-surface-2) / 0.64)",
      frameHairline: "hsl(var(--ui-border-1) / 0.88)",
      frameHighlight: "hsl(var(--ui-surface-1) / 0.54)",
      frameShadow: "var(--ui-shadow-2)",
      grid: "hsl(var(--ui-border-1) / 0.4)"
    };

    const goldNoirPalette = {
      textPrimary: semanticTokens.textSecondary,
      textSecondary: "hsl(var(--ui-text-inverse) / 0.9)",
      textMuted: "hsl(var(--ui-text-inverse) / 0.68)",
      frameBackground: "hsl(var(--ui-text-1) / 0.95)",
      frameTint: "hsl(var(--ui-text-1) / 0.86)",
      frameHairline: "hsl(var(--ui-warning) / 0.52)",
      frameHighlight: "hsl(var(--ui-warning) / 0.2)",
      frameShadow: "0 10px 24px hsl(var(--ui-text-1) / 0.32)",
      grid: "hsl(var(--ui-warning) / 0.22)"
    };

    const graphitePalette = {
      textPrimary: "hsl(var(--ui-text-inverse) / 0.96)",
      textSecondary: "hsl(var(--ui-text-inverse) / 0.84)",
      textMuted: "hsl(var(--ui-text-inverse) / 0.62)",
      frameBackground: "hsl(var(--ui-text-1) / 0.9)",
      frameTint: "hsl(var(--ui-text-1) / 0.82)",
      frameHairline: "hsl(var(--ui-border-2) / 0.42)",
      frameHighlight: "hsl(var(--ui-surface-1) / 0.14)",
      frameShadow: "0 12px 26px hsl(var(--ui-text-1) / 0.28)",
      grid: "hsl(var(--ui-border-2) / 0.34)"
    };

    const palette =
      styleId === "GOLD_NOIR_TERMINAL"
        ? goldNoirPalette
        : styleId === "GRAPHITE_PRISM_ISO"
          ? graphitePalette
          : liquidPalette;

    const allowHighFx = perfProfile === "quality";

    return {
      styleId,
      surface: inferredSurface,
      intent,
      perfProfile,
      density,
      size,
      text: {
        primary: palette.textPrimary,
        secondary: palette.textSecondary,
        muted: palette.textMuted,
        emphasis: styleId === "GOLD_NOIR_TERMINAL" ? "hsl(var(--ui-warning))" : semanticTokens.accent
      },
      frame: {
        background: palette.frameBackground,
        tint: palette.frameTint,
        hairline: palette.frameHairline,
        highlight: palette.frameHighlight,
        shadow: palette.frameShadow,
        radius: "var(--ui-core-radius-lg)",
        paddingInline: padding.inline,
        paddingBlock: padding.block
      },
      chart: {
        grid: palette.grid,
        series,
        heroSeries,
        positive: semanticTokens.success,
        caution: semanticTokens.warning,
        negative: semanticTokens.danger,
        neutral: semanticTokens.textSecondary,
        prismGradient:
          "linear-gradient(135deg, hsl(var(--ui-accent)) 0%, hsl(var(--ui-warning)) 45%, hsl(var(--ui-success)) 100%)"
      },
      fx: {
        allowBlur: inferredSurface === "glass" && perfProfile !== "performance",
        allowGlow: styleId !== "GOLD_NOIR_TERMINAL" && allowHighFx,
        allowShimmer: allowHighFx,
        hoverScale: perfProfile === "performance" ? 1 : 1.006,
        motionDuration: perfProfile === "quality" ? coreTokens.duration.base : coreTokens.duration.fast
      }
    };
  }, [options.density, options.intent, options.perfProfile, options.size, options.styleId, options.surface]);
}
