import type { MaterialId, StyleId } from "../types.js";
import { getLuxuryTokens } from "../tokens/index.js";

export type MaterialLayer = "card" | "inset" | "drawer" | "hero";
export type TextureKind = "grain" | "grid";

export interface MaterialSurfaceVars {
  readonly base: string;
  readonly tint: string;
  readonly overlay: string;
}

export interface MaterialHairlineVars {
  readonly color: string;
  readonly widthPx: number;
}

export interface MaterialInnerStrokeVars {
  readonly color: string;
  readonly insetPx: number;
}

export interface MaterialBlurVars {
  readonly radiusPx: number;
  readonly saturation: number;
  readonly fallbackSurface: string;
}

export interface MaterialSpecularVars {
  readonly opacity: number;
  readonly angleDeg: number;
  readonly widthPct: number;
}

export interface MaterialTextureVars {
  readonly kind: TextureKind;
  readonly opacity: number;
  readonly scale: number;
  readonly bounded: boolean;
}

export interface LuxuryMaterialRecipe {
  readonly id: MaterialId;
  readonly styleId: StyleId;
  readonly layer: MaterialLayer;
  readonly derivesFrom?: MaterialId;
  readonly surface: MaterialSurfaceVars;
  readonly borderHairline: MaterialHairlineVars;
  readonly innerStroke: MaterialInnerStrokeVars;
  readonly blur?: MaterialBlurVars;
  readonly specular: MaterialSpecularVars;
  readonly texture?: MaterialTextureVars;
  readonly elevationLevel: 0 | 1 | 2 | 3;
  readonly governanceTags: readonly string[];
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function withBoundedTextureOpacity(styleId: StyleId, kind: TextureKind, opacity: number): number {
  const tokens = getLuxuryTokens(styleId);
  const maxOpacity = kind === "grain" ? tokens.texture.grainMaxOpacity : tokens.texture.gridMaxOpacity;
  return clamp(opacity, 0, maxOpacity);
}

function deriveMaterial(
  base: LuxuryMaterialRecipe,
  overrides: {
    readonly id: MaterialId;
    readonly layer?: MaterialLayer;
    readonly styleId?: StyleId;
    readonly derivesFrom?: MaterialId;
    readonly surface?: Partial<MaterialSurfaceVars>;
    readonly borderHairline?: Partial<MaterialHairlineVars>;
    readonly innerStroke?: Partial<MaterialInnerStrokeVars>;
    readonly blur?: MaterialBlurVars | null;
    readonly specular?: Partial<MaterialSpecularVars>;
    readonly texture?: MaterialTextureVars | null;
    readonly elevationLevel?: 0 | 1 | 2 | 3;
    readonly governanceTags?: readonly string[];
  }
): LuxuryMaterialRecipe {
  const blurValue =
    overrides.blur === null ? undefined : (overrides.blur ?? base.blur);
  const textureValue =
    overrides.texture === null ? undefined : (overrides.texture ?? base.texture);

  return {
    id: overrides.id,
    layer: overrides.layer ?? base.layer,
    styleId: overrides.styleId ?? base.styleId,
    derivesFrom: overrides.derivesFrom ?? base.id,
    surface: {
      ...base.surface,
      ...(overrides.surface ?? {})
    },
    borderHairline: {
      ...base.borderHairline,
      ...(overrides.borderHairline ?? {})
    },
    innerStroke: {
      ...base.innerStroke,
      ...(overrides.innerStroke ?? {})
    },
    ...(blurValue ? { blur: blurValue } : {}),
    specular: {
      ...base.specular,
      ...(overrides.specular ?? {})
    },
    ...(textureValue ? { texture: textureValue } : {}),
    elevationLevel: overrides.elevationLevel ?? base.elevationLevel,
    governanceTags: overrides.governanceTags ?? base.governanceTags
  };
}

function createRegistry(): Readonly<Record<MaterialId, LuxuryMaterialRecipe>> {
  const liquid = getLuxuryTokens("LIQUID_GLASS");
  const noir = getLuxuryTokens("GOLD_NOIR_TERMINAL");
  const graphite = getLuxuryTokens("GRAPHITE_PRISM_ISO");

  const glassCard: LuxuryMaterialRecipe = {
    id: "glass/card",
    styleId: "LIQUID_GLASS",
    layer: "card",
    surface: {
      base: liquid.neutral.panel,
      tint: liquid.neutral.pearl,
      overlay: "linear-gradient(180deg, hsl(214 88% 99% / 0.3), transparent 48%)"
    },
    borderHairline: {
      color: liquid.hairline.strong,
      widthPx: liquid.hairline.widthPx
    },
    innerStroke: {
      color: liquid.innerStroke.subtle,
      insetPx: 1
    },
    blur: {
      radiusPx: liquid.glowBudget.maxBlurPx,
      saturation: 1.16,
      fallbackSurface: "hsl(214 58% 96% / 0.94)"
    },
    specular: {
      opacity: 0.12,
      angleDeg: 158,
      widthPct: 42
    },
    texture: {
      kind: "grain",
      opacity: withBoundedTextureOpacity("LIQUID_GLASS", "grain", 0.03),
      scale: 1,
      bounded: true
    },
    elevationLevel: 1,
    governanceTags: ["derive-only", "legibility-first", "no-neon"]
  };

  const glassInset = deriveMaterial(glassCard, {
    id: "glass/inset",
    layer: "inset",
    surface: {
      base: liquid.neutral.panelRaised,
      tint: "hsl(214 54% 98% / 0.56)",
      overlay: "linear-gradient(180deg, hsl(214 92% 99% / 0.22), transparent 45%)"
    },
    innerStroke: {
      color: liquid.innerStroke.strong,
      insetPx: 1
    },
    blur: {
      radiusPx: Math.max(8, liquid.glowBudget.maxBlurPx - 8),
      saturation: 1.08,
      fallbackSurface: "hsl(214 50% 95% / 0.92)"
    },
    specular: {
      opacity: 0.08,
      angleDeg: 162,
      widthPct: 36
    },
    elevationLevel: 0,
    governanceTags: ["derived-from-glass-card", "inset-control", "micro-depth"]
  });

  const glassDrawer = deriveMaterial(glassCard, {
    id: "glass/drawer",
    layer: "drawer",
    surface: {
      base: "linear-gradient(172deg, hsl(214 56% 97% / 0.84), hsl(216 30% 90% / 0.72))",
      tint: "hsl(214 60% 98% / 0.7)",
      overlay: "linear-gradient(180deg, hsl(214 94% 99% / 0.32), transparent 46%)"
    },
    borderHairline: {
      color: liquid.hairline.subtle,
      widthPx: liquid.hairline.widthPx
    },
    blur: {
      radiusPx: liquid.glowBudget.maxBlurPx,
      saturation: 1.2,
      fallbackSurface: "hsl(214 42% 95% / 0.95)"
    },
    specular: {
      opacity: 0.1,
      angleDeg: 168,
      widthPct: 44
    },
    texture: {
      kind: "grain",
      opacity: withBoundedTextureOpacity("LIQUID_GLASS", "grain", 0.024),
      scale: 1.2,
      bounded: true
    },
    elevationLevel: 2,
    governanceTags: ["derived-from-glass-card", "drawer-shell", "bounded-blur"]
  });

  const glassHero = deriveMaterial(glassCard, {
    id: "glass/hero",
    layer: "hero",
    surface: {
      base: "linear-gradient(162deg, hsl(214 72% 99% / 0.8), hsl(217 36% 92% / 0.66))",
      tint: "hsl(214 82% 99% / 0.74)",
      overlay: "linear-gradient(180deg, hsl(214 98% 99% / 0.4), transparent 50%)"
    },
    blur: {
      radiusPx: liquid.glowBudget.maxBlurPx,
      saturation: 1.24,
      fallbackSurface: "hsl(214 62% 97% / 0.95)"
    },
    specular: {
      opacity: 0.16,
      angleDeg: 164,
      widthPct: 48
    },
    elevationLevel: 3,
    governanceTags: ["derived-from-glass-card", "hero-only", "one-per-screen"]
  });

  const inkCard: LuxuryMaterialRecipe = {
    id: "ink/card",
    styleId: "GOLD_NOIR_TERMINAL",
    layer: "card",
    surface: {
      base: noir.neutral.panel,
      tint: "hsl(42 44% 68% / 0.06)",
      overlay: "linear-gradient(180deg, hsl(42 42% 72% / 0.06), transparent 48%)"
    },
    borderHairline: {
      color: noir.hairline.strong,
      widthPx: noir.hairline.widthPx
    },
    innerStroke: {
      color: noir.innerStroke.subtle,
      insetPx: 1
    },
    specular: {
      opacity: 0.04,
      angleDeg: 178,
      widthPct: 34
    },
    texture: {
      kind: "grain",
      opacity: withBoundedTextureOpacity("GOLD_NOIR_TERMINAL", "grain", 0.016),
      scale: 1,
      bounded: true
    },
    elevationLevel: 1,
    governanceTags: ["derive-only", "matte-black", "gold-budgeted"]
  };

  const inkDrawer = deriveMaterial(inkCard, {
    id: "ink/drawer",
    layer: "drawer",
    surface: {
      base: noir.neutral.panelRaised,
      tint: "hsl(42 42% 70% / 0.08)",
      overlay: "linear-gradient(180deg, hsl(42 50% 74% / 0.08), transparent 52%)"
    },
    innerStroke: {
      color: noir.innerStroke.strong,
      insetPx: 1
    },
    specular: {
      opacity: 0.03,
      angleDeg: 180,
      widthPct: 30
    },
    elevationLevel: 2,
    governanceTags: ["derived-from-ink-card", "drawer-shell", "minimal-glow"]
  });

  const graphiteCard: LuxuryMaterialRecipe = {
    id: "graphite/card",
    styleId: "GRAPHITE_PRISM_ISO",
    layer: "card",
    surface: {
      base: graphite.neutral.panel,
      tint: "hsl(196 46% 70% / 0.08)",
      overlay: "linear-gradient(180deg, hsl(198 46% 76% / 0.08), transparent 52%)"
    },
    borderHairline: {
      color: graphite.hairline.strong,
      widthPx: graphite.hairline.widthPx
    },
    innerStroke: {
      color: graphite.innerStroke.subtle,
      insetPx: 1
    },
    specular: {
      opacity: 0.05,
      angleDeg: 170,
      widthPct: 38
    },
    texture: {
      kind: "grid",
      opacity: withBoundedTextureOpacity("GRAPHITE_PRISM_ISO", "grid", 0.024),
      scale: 1,
      bounded: true
    },
    elevationLevel: 1,
    governanceTags: ["derive-only", "graphite-petrol", "chart-gradient-only"]
  };

  const graphiteInset = deriveMaterial(graphiteCard, {
    id: "graphite/inset",
    layer: "inset",
    surface: {
      base: graphite.neutral.panelRaised,
      tint: "hsl(196 40% 70% / 0.06)",
      overlay: "linear-gradient(180deg, hsl(198 40% 72% / 0.06), transparent 50%)"
    },
    innerStroke: {
      color: graphite.innerStroke.strong,
      insetPx: 1
    },
    texture: {
      kind: "grid",
      opacity: withBoundedTextureOpacity("GRAPHITE_PRISM_ISO", "grid", 0.02),
      scale: 1.12,
      bounded: true
    },
    elevationLevel: 0,
    governanceTags: ["derived-from-graphite-card", "subtle-grid", "no-surface-gradients"]
  });

  return Object.freeze({
    "glass/card": glassCard,
    "glass/inset": glassInset,
    "glass/drawer": glassDrawer,
    "glass/hero": glassHero,
    "ink/card": inkCard,
    "ink/drawer": inkDrawer,
    "graphite/card": graphiteCard,
    "graphite/inset": graphiteInset
  });
}

export const LUXURY_MATERIAL_REGISTRY = createRegistry();

export function getLuxuryMaterialRecipe(materialId: MaterialId): LuxuryMaterialRecipe {
  return LUXURY_MATERIAL_REGISTRY[materialId];
}
