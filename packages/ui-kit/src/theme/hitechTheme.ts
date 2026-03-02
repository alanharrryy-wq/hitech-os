export const HITECH_BRAND_COLORS = {
  bronze: "#AB7B26",
  tealDeep: "#026F86",
  cyan: "#02A7CA",
  umber: "#553E13"
} as const;

export type HitechBrandColorId = keyof typeof HITECH_BRAND_COLORS;

export const HITECH_COLOR_SCALE = {
  bronze: {
    50: "#FCF7EA",
    100: "#F6E8C7",
    200: "#EFD38E",
    300: "#E0B45A",
    400: "#C48F34",
    500: "#AB7B26",
    600: "#8D631D",
    700: "#6E4B17",
    800: "#553A15",
    900: "#3B280F"
  },
  teal: {
    50: "#E9F8FB",
    100: "#C7EEF4",
    200: "#91DDE9",
    300: "#59C7DB",
    400: "#22A9C3",
    500: "#026F86",
    600: "#025D70",
    700: "#02495A",
    800: "#033947",
    900: "#032835"
  },
  cyan: {
    50: "#E8FAFE",
    100: "#C4F2FC",
    200: "#8FE7F8",
    300: "#57D9F2",
    400: "#21C2E3",
    500: "#02A7CA",
    600: "#0287A4",
    700: "#02687F",
    800: "#024C5D",
    900: "#013241"
  },
  umber: {
    50: "#F4EEE2",
    100: "#E4D6B9",
    200: "#CBAE79",
    300: "#B28749",
    400: "#8D632A",
    500: "#553E13",
    600: "#4A360F",
    700: "#3D2C0D",
    800: "#30220B",
    900: "#221808"
  },
  graphite: {
    50: "#F4F6F8",
    100: "#E6EBF0",
    200: "#CCD5DE",
    300: "#A7B4C3",
    400: "#7B8DA2",
    500: "#546577",
    600: "#3E4B59",
    700: "#2D3741",
    800: "#1C232B",
    900: "#11161D"
  }
} as const;

export type HitechGradientId =
  | "bronzeToTeal"
  | "tealToCyan"
  | "cyanToTeal"
  | "bronzeToUmber"
  | "tealToGraphite"
  | "cyanToGraphite"
  | "auroraLine"
  | "horizonDeep"
  | "screenSheen"
  | "panelHalo"
  | "surfaceL0"
  | "surfaceL1"
  | "surfaceL2"
  | "surfaceL3"
  | "surfaceL4"
  | "surfaceL5"
  | "accentArc"
  | "warningHot"
  | "successCool"
  | "criticalPulse"
  | "overlayFog"
  | "overlayScan"
  | "overlayBezel";

export const HITECH_GRADIENT_RECIPES: Record<HitechGradientId, string> = {
  bronzeToTeal: "linear-gradient(120deg, #AB7B26 0%, #026F86 100%)",
  tealToCyan: "linear-gradient(120deg, #026F86 0%, #02A7CA 100%)",
  cyanToTeal: "linear-gradient(120deg, #02A7CA 0%, #026F86 100%)",
  bronzeToUmber: "linear-gradient(140deg, #AB7B26 0%, #553E13 100%)",
  tealToGraphite: "linear-gradient(140deg, #026F86 0%, #1C232B 100%)",
  cyanToGraphite: "linear-gradient(140deg, #02A7CA 0%, #1C232B 100%)",
  auroraLine: "linear-gradient(90deg, rgba(171, 123, 38, 0) 0%, rgba(171, 123, 38, 0.9) 32%, rgba(2, 111, 134, 0.9) 68%, rgba(2, 167, 202, 0) 100%)",
  horizonDeep: "linear-gradient(180deg, rgba(17, 22, 29, 0) 0%, rgba(17, 22, 29, 0.65) 100%)",
  screenSheen: "linear-gradient(122deg, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0.04) 38%, rgba(2,167,202,0.08) 68%, rgba(255,255,255,0) 100%)",
  panelHalo: "radial-gradient(circle at 50% -24%, rgba(2,167,202,0.44) 0%, rgba(2,111,134,0.14) 42%, rgba(2,111,134,0) 78%)",
  surfaceL0: "linear-gradient(170deg, rgba(255,255,255,0.94) 0%, rgba(244,246,248,0.92) 100%)",
  surfaceL1: "linear-gradient(170deg, rgba(246,250,251,0.93) 0%, rgba(227,236,241,0.9) 100%)",
  surfaceL2: "linear-gradient(170deg, rgba(233,241,245,0.9) 0%, rgba(208,221,229,0.88) 100%)",
  surfaceL3: "linear-gradient(170deg, rgba(219,232,239,0.86) 0%, rgba(186,205,217,0.84) 100%)",
  surfaceL4: "linear-gradient(170deg, rgba(36,50,62,0.86) 0%, rgba(23,31,39,0.9) 100%)",
  surfaceL5: "linear-gradient(170deg, rgba(21,28,35,0.96) 0%, rgba(12,16,22,0.98) 100%)",
  accentArc: "conic-gradient(from 220deg at 50% 50%, rgba(171,123,38,0) 0deg, rgba(171,123,38,0.8) 95deg, rgba(2,167,202,0.7) 210deg, rgba(2,111,134,0) 360deg)",
  warningHot: "linear-gradient(140deg, rgba(171,123,38,0.98) 0%, rgba(255,170,64,0.96) 100%)",
  successCool: "linear-gradient(140deg, rgba(2,111,134,0.95) 0%, rgba(2,167,202,0.88) 100%)",
  criticalPulse: "linear-gradient(140deg, rgba(160,48,28,0.95) 0%, rgba(220,90,68,0.9) 100%)",
  overlayFog: "radial-gradient(circle at 20% 20%, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.06) 36%, rgba(255,255,255,0) 72%)",
  overlayScan: "linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(2,167,202,0.08) 49%, rgba(255,255,255,0) 100%)",
  overlayBezel: "linear-gradient(145deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.04) 32%, rgba(2,111,134,0.08) 68%, rgba(0,0,0,0.18) 100%)"
};

export type HitechGlowId =
  | "bronzeSoft"
  | "bronzeMedium"
  | "bronzeHard"
  | "tealSoft"
  | "tealMedium"
  | "tealHard"
  | "cyanSoft"
  | "cyanMedium"
  | "cyanHard"
  | "alert"
  | "critical"
  | "ambient"
  | "panel"
  | "button"
  | "focus";

export const HITECH_GLOW_RECIPES: Record<HitechGlowId, string> = {
  bronzeSoft: "0 0 0 1px rgba(171,123,38,0.3), 0 6px 20px rgba(171,123,38,0.16)",
  bronzeMedium: "0 0 0 1px rgba(171,123,38,0.42), 0 12px 28px rgba(171,123,38,0.24)",
  bronzeHard: "0 0 0 1px rgba(171,123,38,0.62), 0 16px 40px rgba(171,123,38,0.3)",
  tealSoft: "0 0 0 1px rgba(2,111,134,0.34), 0 6px 20px rgba(2,111,134,0.16)",
  tealMedium: "0 0 0 1px rgba(2,111,134,0.5), 0 12px 30px rgba(2,111,134,0.24)",
  tealHard: "0 0 0 1px rgba(2,111,134,0.68), 0 20px 44px rgba(2,111,134,0.34)",
  cyanSoft: "0 0 0 1px rgba(2,167,202,0.34), 0 6px 20px rgba(2,167,202,0.15)",
  cyanMedium: "0 0 0 1px rgba(2,167,202,0.52), 0 12px 32px rgba(2,167,202,0.25)",
  cyanHard: "0 0 0 1px rgba(2,167,202,0.74), 0 22px 50px rgba(2,167,202,0.36)",
  alert: "0 0 0 1px rgba(171,123,38,0.56), 0 0 24px rgba(171,123,38,0.52)",
  critical: "0 0 0 1px rgba(224,82,70,0.66), 0 0 30px rgba(224,82,70,0.46)",
  ambient: "0 16px 50px rgba(15,24,34,0.3)",
  panel: "0 18px 38px rgba(14,20,28,0.26), 0 0 0 1px rgba(255,255,255,0.07)",
  button: "0 8px 24px rgba(2,111,134,0.22), 0 0 0 1px rgba(2,167,202,0.4)",
  focus: "0 0 0 2px rgba(255,255,255,0.88), 0 0 0 4px rgba(2,167,202,0.76), 0 0 22px rgba(2,167,202,0.4)"
};

export type HitechStrokeId =
  | "hairline"
  | "soft"
  | "medium"
  | "hard"
  | "accent"
  | "accentBright"
  | "warning"
  | "critical"
  | "inset"
  | "bezel"
  | "inner"
  | "outer";

export const HITECH_STROKE_RECIPES: Record<HitechStrokeId, string> = {
  hairline: "1px solid rgba(255,255,255,0.12)",
  soft: "1px solid rgba(103,127,146,0.35)",
  medium: "1px solid rgba(95,122,146,0.48)",
  hard: "1px solid rgba(83,116,145,0.68)",
  accent: "1px solid rgba(2,111,134,0.62)",
  accentBright: "1px solid rgba(2,167,202,0.76)",
  warning: "1px solid rgba(171,123,38,0.7)",
  critical: "1px solid rgba(220,90,68,0.74)",
  inset: "1px solid rgba(255,255,255,0.24)",
  bezel: "1px solid rgba(140,160,176,0.36)",
  inner: "1px solid rgba(255,255,255,0.34)",
  outer: "1px solid rgba(28,44,58,0.5)"
};

export type HitechTextureId =
  | "none"
  | "grainFine"
  | "grainMedium"
  | "grainCoarse"
  | "noiseBlue"
  | "noiseWarm"
  | "carbon"
  | "etched";

export interface HitechTextureRecipe {
  readonly image: string;
  readonly size: string;
  readonly opacity: number;
  readonly blendMode: "normal" | "overlay" | "multiply" | "soft-light" | "screen";
}

export const HITECH_TEXTURE_RECIPES: Record<HitechTextureId, HitechTextureRecipe> = {
  none: {
    image: "none",
    size: "auto",
    opacity: 0,
    blendMode: "normal"
  },
  grainFine: {
    image: "radial-gradient(rgba(28,41,56,0.52) 0.4px, transparent 0.4px)",
    size: "2px 2px",
    opacity: 0.12,
    blendMode: "overlay"
  },
  grainMedium: {
    image: "radial-gradient(rgba(20,36,50,0.54) 0.55px, transparent 0.55px)",
    size: "3px 3px",
    opacity: 0.15,
    blendMode: "overlay"
  },
  grainCoarse: {
    image: "radial-gradient(rgba(18,28,38,0.62) 0.75px, transparent 0.75px)",
    size: "4px 4px",
    opacity: 0.2,
    blendMode: "overlay"
  },
  noiseBlue: {
    image: "radial-gradient(rgba(2,111,134,0.58) 0.6px, transparent 0.6px)",
    size: "3px 3px",
    opacity: 0.13,
    blendMode: "soft-light"
  },
  noiseWarm: {
    image: "radial-gradient(rgba(171,123,38,0.56) 0.6px, transparent 0.6px)",
    size: "3px 3px",
    opacity: 0.13,
    blendMode: "soft-light"
  },
  carbon: {
    image: "linear-gradient(45deg, rgba(255,255,255,0.06) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.06) 75%, transparent 75%, transparent)",
    size: "8px 8px",
    opacity: 0.12,
    blendMode: "multiply"
  },
  etched: {
    image: "linear-gradient(180deg, rgba(255,255,255,0.15), rgba(255,255,255,0.02)), linear-gradient(90deg, rgba(2,167,202,0.08), rgba(171,123,38,0.08))",
    size: "100% 100%, 100% 100%",
    opacity: 0.35,
    blendMode: "overlay"
  }
};

export interface HitechMaterialRecipe {
  readonly base: string;
  readonly stroke: HitechStrokeId;
  readonly glow: HitechGlowId;
  readonly texture: HitechTextureId;
  readonly blur: string;
}

export type HitechMaterialId =
  | "glass.micro"
  | "glass.soft"
  | "glass.deep"
  | "glass.halo"
  | "panel.standard"
  | "panel.deep"
  | "panel.critical"
  | "control.primary"
  | "control.secondary"
  | "control.ghost"
  | "chip.pass"
  | "chip.block"
  | "chip.hold"
  | "chip.critical";

export const HITECH_MATERIAL_RECIPES: Record<HitechMaterialId, HitechMaterialRecipe> = {
  "glass.micro": {
    base: HITECH_GRADIENT_RECIPES.surfaceL0,
    stroke: "inner",
    glow: "ambient",
    texture: "grainFine",
    blur: "blur(8px)"
  },
  "glass.soft": {
    base: HITECH_GRADIENT_RECIPES.surfaceL1,
    stroke: "soft",
    glow: "panel",
    texture: "grainMedium",
    blur: "blur(10px)"
  },
  "glass.deep": {
    base: HITECH_GRADIENT_RECIPES.surfaceL2,
    stroke: "medium",
    glow: "tealSoft",
    texture: "grainMedium",
    blur: "blur(12px)"
  },
  "glass.halo": {
    base: `${HITECH_GRADIENT_RECIPES.surfaceL0}, ${HITECH_GRADIENT_RECIPES.panelHalo}`,
    stroke: "accent",
    glow: "cyanMedium",
    texture: "noiseBlue",
    blur: "blur(14px)"
  },
  "panel.standard": {
    base: HITECH_GRADIENT_RECIPES.surfaceL3,
    stroke: "bezel",
    glow: "ambient",
    texture: "carbon",
    blur: "none"
  },
  "panel.deep": {
    base: HITECH_GRADIENT_RECIPES.surfaceL4,
    stroke: "outer",
    glow: "tealSoft",
    texture: "carbon",
    blur: "none"
  },
  "panel.critical": {
    base: HITECH_GRADIENT_RECIPES.criticalPulse,
    stroke: "critical",
    glow: "critical",
    texture: "etched",
    blur: "none"
  },
  "control.primary": {
    base: HITECH_GRADIENT_RECIPES.tealToCyan,
    stroke: "accentBright",
    glow: "button",
    texture: "noiseBlue",
    blur: "none"
  },
  "control.secondary": {
    base: HITECH_GRADIENT_RECIPES.bronzeToTeal,
    stroke: "warning",
    glow: "bronzeMedium",
    texture: "noiseWarm",
    blur: "none"
  },
  "control.ghost": {
    base: HITECH_GRADIENT_RECIPES.surfaceL1,
    stroke: "soft",
    glow: "ambient",
    texture: "grainFine",
    blur: "none"
  },
  "chip.pass": {
    base: HITECH_GRADIENT_RECIPES.successCool,
    stroke: "accent",
    glow: "tealSoft",
    texture: "grainFine",
    blur: "none"
  },
  "chip.block": {
    base: HITECH_GRADIENT_RECIPES.warningHot,
    stroke: "warning",
    glow: "bronzeSoft",
    texture: "grainFine",
    blur: "none"
  },
  "chip.hold": {
    base: HITECH_GRADIENT_RECIPES.surfaceL3,
    stroke: "bezel",
    glow: "ambient",
    texture: "etched",
    blur: "none"
  },
  "chip.critical": {
    base: HITECH_GRADIENT_RECIPES.criticalPulse,
    stroke: "critical",
    glow: "critical",
    texture: "noiseWarm",
    blur: "none"
  }
};

export const HITECH_THEME_CSS_VARIABLES = {
  "--hk-brand-bronze": HITECH_BRAND_COLORS.bronze,
  "--hk-brand-teal": HITECH_BRAND_COLORS.tealDeep,
  "--hk-brand-cyan": HITECH_BRAND_COLORS.cyan,
  "--hk-brand-umber": HITECH_BRAND_COLORS.umber,
  "--hk-gradient-bronze-teal": HITECH_GRADIENT_RECIPES.bronzeToTeal,
  "--hk-gradient-teal-cyan": HITECH_GRADIENT_RECIPES.tealToCyan,
  "--hk-gradient-bronze-umber": HITECH_GRADIENT_RECIPES.bronzeToUmber,
  "--hk-gradient-screen-sheen": HITECH_GRADIENT_RECIPES.screenSheen,
  "--hk-gradient-panel-halo": HITECH_GRADIENT_RECIPES.panelHalo,
  "--hk-gradient-overlay-fog": HITECH_GRADIENT_RECIPES.overlayFog,
  "--hk-gradient-overlay-scan": HITECH_GRADIENT_RECIPES.overlayScan,
  "--hk-gradient-overlay-bezel": HITECH_GRADIENT_RECIPES.overlayBezel,
  "--hk-glow-bronze-soft": HITECH_GLOW_RECIPES.bronzeSoft,
  "--hk-glow-bronze-medium": HITECH_GLOW_RECIPES.bronzeMedium,
  "--hk-glow-teal-soft": HITECH_GLOW_RECIPES.tealSoft,
  "--hk-glow-teal-medium": HITECH_GLOW_RECIPES.tealMedium,
  "--hk-glow-cyan-soft": HITECH_GLOW_RECIPES.cyanSoft,
  "--hk-glow-cyan-medium": HITECH_GLOW_RECIPES.cyanMedium,
  "--hk-glow-focus": HITECH_GLOW_RECIPES.focus,
  "--hk-stroke-soft": HITECH_STROKE_RECIPES.soft,
  "--hk-stroke-medium": HITECH_STROKE_RECIPES.medium,
  "--hk-stroke-accent": HITECH_STROKE_RECIPES.accent,
  "--hk-stroke-warning": HITECH_STROKE_RECIPES.warning,
  "--hk-stroke-critical": HITECH_STROKE_RECIPES.critical,
  "--hk-texture-fine-image": HITECH_TEXTURE_RECIPES.grainFine.image,
  "--hk-texture-fine-size": HITECH_TEXTURE_RECIPES.grainFine.size,
  "--hk-texture-fine-opacity": `${HITECH_TEXTURE_RECIPES.grainFine.opacity}`,
  "--hk-texture-blue-image": HITECH_TEXTURE_RECIPES.noiseBlue.image,
  "--hk-texture-blue-size": HITECH_TEXTURE_RECIPES.noiseBlue.size,
  "--hk-texture-blue-opacity": `${HITECH_TEXTURE_RECIPES.noiseBlue.opacity}`,
  "--hk-motion-fast": "120ms",
  "--hk-motion-base": "220ms",
  "--hk-motion-slow": "420ms",
  "--hk-ease-standard": "cubic-bezier(0.2, 0.7, 0, 1)",
  "--hk-ease-glass": "cubic-bezier(0.16, 0.8, 0.18, 1)",
  "--hk-radius-2xs": "4px",
  "--hk-radius-xs": "8px",
  "--hk-radius-sm": "12px",
  "--hk-radius-md": "16px",
  "--hk-radius-lg": "22px",
  "--hk-radius-xl": "30px"
} as const;

export type HitechThemeVarName = keyof typeof HITECH_THEME_CSS_VARIABLES;

export function createHitechCssVars(
  overrides?: Partial<Record<HitechThemeVarName, string>>
): Record<string, string> {
  return {
    ...HITECH_THEME_CSS_VARIABLES,
    ...(overrides ?? {})
  };
}

export function resolveHitechGradient(id: HitechGradientId): string {
  return HITECH_GRADIENT_RECIPES[id];
}

export function resolveHitechGlow(id: HitechGlowId): string {
  return HITECH_GLOW_RECIPES[id];
}

export function resolveHitechStroke(id: HitechStrokeId): string {
  return HITECH_STROKE_RECIPES[id];
}

export function resolveHitechTexture(id: HitechTextureId): HitechTextureRecipe {
  return HITECH_TEXTURE_RECIPES[id];
}

export function resolveHitechMaterial(id: HitechMaterialId): HitechMaterialRecipe {
  return HITECH_MATERIAL_RECIPES[id];
}

export function listHitechMaterialIds(): HitechMaterialId[] {
  return Object.keys(HITECH_MATERIAL_RECIPES) as HitechMaterialId[];
}

export function listHitechGradientIds(): HitechGradientId[] {
  return Object.keys(HITECH_GRADIENT_RECIPES) as HitechGradientId[];
}

export function listHitechGlowIds(): HitechGlowId[] {
  return Object.keys(HITECH_GLOW_RECIPES) as HitechGlowId[];
}

export function listHitechStrokeIds(): HitechStrokeId[] {
  return Object.keys(HITECH_STROKE_RECIPES) as HitechStrokeId[];
}

export function listHitechTextureIds(): HitechTextureId[] {
  return Object.keys(HITECH_TEXTURE_RECIPES) as HitechTextureId[];
}
