export const coreTokens = {
  radius: {
    none: "var(--ui-core-radius-none)",
    sm: "var(--ui-core-radius-sm)",
    md: "var(--ui-core-radius-md)",
    lg: "var(--ui-core-radius-lg)",
    xl: "var(--ui-core-radius-xl)"
  },
  space: {
    1: "var(--ui-core-space-1)",
    2: "var(--ui-core-space-2)",
    3: "var(--ui-core-space-3)",
    4: "var(--ui-core-space-4)",
    5: "var(--ui-core-space-5)",
    6: "var(--ui-core-space-6)",
    8: "var(--ui-core-space-8)",
    10: "var(--ui-core-space-10)",
    12: "var(--ui-core-space-12)"
  },
  duration: {
    fast: "var(--ui-core-duration-fast)",
    base: "var(--ui-core-duration-base)",
    slow: "var(--ui-core-duration-slow)"
  }
} as const;

export const semanticTokens = {
  background: "hsl(var(--ui-bg))",
  backgroundSoft: "hsl(var(--ui-bg-soft))",
  surface1: "hsl(var(--ui-surface-1))",
  surface2: "hsl(var(--ui-surface-2))",
  textPrimary: "hsl(var(--ui-text-1))",
  textSecondary: "hsl(var(--ui-text-2))",
  textMuted: "hsl(var(--ui-text-3))",
  border: "hsl(var(--ui-border-1))",
  accent: "hsl(var(--ui-accent))",
  success: "hsl(var(--ui-success))",
  warning: "hsl(var(--ui-warning))",
  danger: "hsl(var(--ui-danger))"
} as const;

export const fxTokens = {
  noiseOpacity: "var(--ui-fx-noise-opacity)",
  scanlineOpacity: "var(--ui-fx-scanline-opacity)",
  hazeOpacity: "var(--ui-fx-haze-opacity)",
  vignetteOpacity: "var(--ui-fx-vignette-opacity)",
  blurSoft: "var(--ui-fx-blur-sm)",
  blurMedium: "var(--ui-fx-blur-md)",
  blurMax: "var(--ui-fx-blur-max)",
  shadow1: "var(--ui-shadow-1)",
  shadow2: "var(--ui-shadow-2)",
  shadow3: "var(--ui-shadow-3)",
  shadowMax: "var(--ui-shadow-max)"
} as const;

export type CoreTokens = typeof coreTokens;
export type SemanticTokens = typeof semanticTokens;
export type FxTokens = typeof fxTokens;

export function getTokenVar(name: string): string {
  return `var(${name})`;
}

export function resolveSemanticToken(name: keyof typeof semanticTokens): string {
  return semanticTokens[name];
}
