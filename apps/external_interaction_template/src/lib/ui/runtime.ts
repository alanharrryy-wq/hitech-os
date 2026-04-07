import { z } from "zod";

export const UI_AREAS = ["launcher", "inbox", "flow", "record", "sync", "system", "generic"] as const;
export type UiArea = (typeof UI_AREAS)[number];

export const UI_DENSITIES = ["compact", "comfortable", "spacious"] as const;
export type UiDensity = (typeof UI_DENSITIES)[number];

export const UI_PRESETS = ["immersive", "balanced", "analytical", "operational"] as const;
export type UiPreset = (typeof UI_PRESETS)[number];

export const UI_ROLES = ["guest", "external_user", "reviewer", "approver", "operator", "system"] as const;
export type UiRole = (typeof UI_ROLES)[number];

export const UI_MOTION_PREFERENCES = ["full", "reduced", "none"] as const;
export type UiMotionPreference = (typeof UI_MOTION_PREFERENCES)[number];

export const UI_CONTRAST_PREFERENCES = ["normal", "more", "max"] as const;
export type UiContrastPreference = (typeof UI_CONTRAST_PREFERENCES)[number];

export interface BrandProfile {
  id: "aurora" | "neutral" | "signal" | "graphite";
  label: string;
  accentClass: string;
  surfaceClass: string;
  ringClass: string;
  glowClass: string;
}

export interface RuntimeUiContext {
  area: UiArea;
  density: UiDensity;
  preset: UiPreset;
  role: UiRole;
  motion: UiMotionPreference;
  contrast: UiContrastPreference;
  brandProfile: BrandProfile;
}

export interface RuntimeUiContextInput extends Partial<Omit<RuntimeUiContext, "brandProfile">> {
  brandProfile?: BrandProfile | BrandProfile["id"];
}

const areaSchema = z.enum(UI_AREAS);
const densitySchema = z.enum(UI_DENSITIES);
const presetSchema = z.enum(UI_PRESETS);
const roleSchema = z.enum(UI_ROLES);
const motionSchema = z.enum(UI_MOTION_PREFERENCES);
const contrastSchema = z.enum(UI_CONTRAST_PREFERENCES);

export const BRAND_PROFILES: Record<BrandProfile["id"], BrandProfile> = {
  aurora: {
    id: "aurora",
    label: "Aurora",
    accentClass: "text-accent",
    surfaceClass: "bg-surface/58",
    ringClass: "ring-accent/55",
    glowClass: "shadow-[0_0_36px_rgba(128,226,255,0.16)]"
  },
  neutral: {
    id: "neutral",
    label: "Neutral",
    accentClass: "text-text",
    surfaceClass: "bg-surface/52",
    ringClass: "ring-white/20",
    glowClass: "shadow-glass"
  },
  signal: {
    id: "signal",
    label: "Signal",
    accentClass: "text-success",
    surfaceClass: "bg-surface/60",
    ringClass: "ring-success/35",
    glowClass: "shadow-[0_0_30px_rgba(121,231,178,0.14)]"
  },
  graphite: {
    id: "graphite",
    label: "Graphite",
    accentClass: "text-muted",
    surfaceClass: "bg-canvas/36",
    ringClass: "ring-white/15",
    glowClass: "shadow-[0_10px_36px_rgba(0,0,0,0.24)]"
  }
};

const areaDefaults: Record<UiArea, Pick<RuntimeUiContext, "density" | "preset">> = {
  launcher: { density: "comfortable", preset: "balanced" },
  inbox: { density: "comfortable", preset: "operational" },
  flow: { density: "spacious", preset: "immersive" },
  record: { density: "comfortable", preset: "analytical" },
  sync: { density: "compact", preset: "operational" },
  system: { density: "compact", preset: "balanced" },
  generic: { density: "comfortable", preset: "balanced" }
};

export function resolveBrandProfile(profile: RuntimeUiContextInput["brandProfile"]): BrandProfile {
  if (!profile) return BRAND_PROFILES.aurora;
  if (typeof profile === "string") return BRAND_PROFILES[profile] ?? BRAND_PROFILES.aurora;
  return BRAND_PROFILES[profile.id] ?? profile;
}

export function createRuntimeUiContext(input: RuntimeUiContextInput = {}): RuntimeUiContext {
  const parsedArea = areaSchema.safeParse(input.area);
  const area: UiArea = parsedArea.success ? parsedArea.data : "generic";
  const defaults = areaDefaults[area];

  const parsedDensity = densitySchema.safeParse(input.density);
  const parsedPreset = presetSchema.safeParse(input.preset);
  const parsedRole = roleSchema.safeParse(input.role);
  const parsedMotion = motionSchema.safeParse(input.motion);
  const parsedContrast = contrastSchema.safeParse(input.contrast);

  return {
    area,
    density: parsedDensity.success ? parsedDensity.data : defaults.density,
    preset: parsedPreset.success ? parsedPreset.data : defaults.preset,
    role: parsedRole.success ? parsedRole.data : "operator",
    motion: parsedMotion.success ? parsedMotion.data : "full",
    contrast: parsedContrast.success ? parsedContrast.data : "normal",
    brandProfile: resolveBrandProfile(input.brandProfile)
  };
}

export function mergeRuntimeUiContext(base: RuntimeUiContext, patch: RuntimeUiContextInput = {}): RuntimeUiContext {
  return createRuntimeUiContext({ ...base, ...patch, brandProfile: patch.brandProfile ?? base.brandProfile });
}

export function runtimeDataAttributes(context: RuntimeUiContext): Record<string, string> {
  return {
    "data-ui-area": context.area,
    "data-ui-density": context.density,
    "data-ui-preset": context.preset,
    "data-ui-role": context.role,
    "data-ui-motion": context.motion,
    "data-ui-contrast": context.contrast,
    "data-ui-brand": context.brandProfile.id
  };
}

export function runtimeSpacing(context: RuntimeUiContext): { sectionGap: string; cardPadding: string } {
  if (context.density === "compact") return { sectionGap: "gap-3", cardPadding: "p-3" };
  if (context.density === "spacious") return { sectionGap: "gap-6", cardPadding: "p-5" };
  return { sectionGap: "gap-4", cardPadding: "p-4" };
}

export function runtimeMotionClass(context: RuntimeUiContext): string {
  if (context.motion === "none") return "transition-none motion-reduce:transform-none motion-reduce:animate-none";
  if (context.motion === "reduced") return "transition duration-150 motion-reduce:transform-none motion-reduce:animate-none";
  return "transition duration-200";
}

export function runtimeContrastClass(context: RuntimeUiContext): string {
  if (context.contrast === "max") return "contrast-125 saturate-[1.06]";
  if (context.contrast === "more") return "contrast-110";
  return "contrast-100";
}

export function runtimeShellClass(context: RuntimeUiContext): string {
  return `${context.brandProfile.surfaceClass} ${context.brandProfile.glowClass} ${runtimeMotionClass(context)} ${runtimeContrastClass(context)}`;
}
