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
  description: string;
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
    description: "Default product surface profile."
  },
  neutral: {
    id: "neutral",
    label: "Neutral",
    description: "Balanced brand profile for generic contexts."
  },
  signal: {
    id: "signal",
    label: "Signal",
    description: "High-signal profile for status-heavy surfaces."
  },
  graphite: {
    id: "graphite",
    label: "Graphite",
    description: "Subdued profile for dense analytical surfaces."
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
  const areaResult = areaSchema.safeParse(input.area);
  const area: UiArea = areaResult.success ? areaResult.data : "generic";
  const defaults = areaDefaults[area];

  const densityResult = densitySchema.safeParse(input.density);
  const presetResult = presetSchema.safeParse(input.preset);
  const roleResult = roleSchema.safeParse(input.role);
  const motionResult = motionSchema.safeParse(input.motion);
  const contrastResult = contrastSchema.safeParse(input.contrast);

  return {
    area,
    density: densityResult.success ? densityResult.data : defaults.density,
    preset: presetResult.success ? presetResult.data : defaults.preset,
    role: roleResult.success ? roleResult.data : "operator",
    motion: motionResult.success ? motionResult.data : "full",
    contrast: contrastResult.success ? contrastResult.data : "normal",
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
  return `${runtimeMotionClass(context)} ${runtimeContrastClass(context)}`;
}
