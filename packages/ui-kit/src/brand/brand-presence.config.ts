import type { CSSProperties } from "react";
import type { LayerProfile } from "../layers/layerIds.js";

export type BrandPresenceMode = "watermark" | "corner-seal" | "header-mark";
export type BrandPresenceIntensity = "subtle" | "medium";

export interface BrandPresenceConfig {
  readonly enableGlobalWatermark: boolean;
  readonly enableCornerSeal: boolean;
  readonly enableHeaderMark: boolean;
  readonly enableFooterSignature: boolean;
  readonly watermarkOpacityNeutral: number;
  readonly watermarkOpacityFx: number;
  readonly sealOpacity: number;
  readonly sealSize: number;
  readonly headerHaloIntensity: number;
  readonly phoenixAssetPath: string;
}

export const brandPresenceConfig: BrandPresenceConfig = {
  enableGlobalWatermark: true,
  enableCornerSeal: true,
  enableHeaderMark: true,
  enableFooterSignature: true,
  watermarkOpacityNeutral: 0.04,
  watermarkOpacityFx: 0.06,
  sealOpacity: 0.05,
  sealSize: 34,
  headerHaloIntensity: 0.1,
  phoenixAssetPath: "/brand/hitech-phoenix.svg"
};

const INTENSITY_MULTIPLIER: Record<BrandPresenceIntensity, number> = {
  subtle: 1,
  medium: 1.3
};

function clampOpacity(value: number): number {
  if (value < 0) {
    return 0;
  }

  if (value > 0.3) {
    return 0.3;
  }

  return value;
}

export function resolveBrandModeEnabled(mode: BrandPresenceMode, profile: LayerProfile): boolean {
  if (mode === "watermark") {
    return brandPresenceConfig.enableGlobalWatermark && profile !== "perf";
  }

  if (mode === "corner-seal") {
    return brandPresenceConfig.enableCornerSeal;
  }

  return brandPresenceConfig.enableHeaderMark;
}

export function resolveBrandModeOpacity(
  mode: BrandPresenceMode,
  profile: LayerProfile,
  intensity: BrandPresenceIntensity = "subtle"
): number {
  const intensityScale = INTENSITY_MULTIPLIER[intensity];

  if (mode === "watermark") {
    const base = profile === "fx" ? brandPresenceConfig.watermarkOpacityFx : brandPresenceConfig.watermarkOpacityNeutral;
    return clampOpacity(base * intensityScale);
  }

  if (mode === "corner-seal") {
    return clampOpacity(brandPresenceConfig.sealOpacity * intensityScale);
  }

  return clampOpacity(brandPresenceConfig.headerHaloIntensity * intensityScale);
}

export function resolveBrandSealSize(intensity: BrandPresenceIntensity = "subtle"): number {
  return Math.round(brandPresenceConfig.sealSize * INTENSITY_MULTIPLIER[intensity]);
}

export function createBrandPresenceRootStyle(
  profile: LayerProfile,
  intensity: BrandPresenceIntensity = "subtle"
): CSSProperties {
  return {
    "--hitech-brand-watermark-opacity": String(resolveBrandModeOpacity("watermark", profile, intensity)),
    "--hitech-brand-seal-opacity": String(resolveBrandModeOpacity("corner-seal", profile, intensity)),
    "--hitech-brand-header-halo-opacity": String(resolveBrandModeOpacity("header-mark", profile, intensity)),
    "--hitech-brand-seal-size": `${resolveBrandSealSize(intensity)}px`,
    "--hitech-brand-phoenix-url": `url('${brandPresenceConfig.phoenixAssetPath}')`
  } as CSSProperties;
}
