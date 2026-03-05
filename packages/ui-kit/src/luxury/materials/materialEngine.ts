import type { MaterialId, PerfProfile, StyleId, SurfaceId } from "../types.js";
import { getLuxuryTokens } from "../tokens/index.js";
import {
  getLuxuryMaterialRecipe,
  type LuxuryMaterialRecipe,
  type MaterialTextureVars
} from "./materialRegistry.js";

const SURFACE_MATERIAL_MAP: Readonly<Record<StyleId, Readonly<Record<SurfaceId, MaterialId>>>> = {
  LIQUID_GLASS: {
    controlRoomHud: "glass/hero",
    pitchCard: "glass/card",
    pitchPanel: "glass/inset",
    kpiWidget: "glass/card",
    tableDense: "glass/inset",
    drawer: "glass/drawer",
    rail: "glass/inset",
    popover: "glass/card"
  },
  GOLD_NOIR_TERMINAL: {
    controlRoomHud: "ink/card",
    pitchCard: "ink/card",
    pitchPanel: "ink/card",
    kpiWidget: "ink/card",
    tableDense: "ink/card",
    drawer: "ink/drawer",
    rail: "ink/card",
    popover: "ink/card"
  },
  GRAPHITE_PRISM_ISO: {
    controlRoomHud: "graphite/card",
    pitchCard: "graphite/card",
    pitchPanel: "graphite/inset",
    kpiWidget: "graphite/card",
    tableDense: "graphite/inset",
    drawer: "graphite/card",
    rail: "graphite/inset",
    popover: "graphite/card"
  }
};

export interface MaterialRuntimeFlags {
  readonly blurEnabled: boolean;
  readonly specularEnabled: boolean;
  readonly textureEnabled: boolean;
  readonly blurMode: "backdrop-filter" | "fallback";
}

export interface ResolvedMaterialRuntime {
  readonly recipe: LuxuryMaterialRecipe;
  readonly flags: MaterialRuntimeFlags;
}

function getCssApiSupports(): ((property: string, value?: string) => boolean) | undefined {
  const cssApi = (globalThis as unknown as { CSS?: { supports?: (property: string, value?: string) => boolean } }).CSS;
  if (!cssApi || typeof cssApi.supports !== "function") {
    return undefined;
  }

  return cssApi.supports.bind(cssApi);
}

export function supportsBackdropBlur(): boolean {
  const supports = getCssApiSupports();
  if (!supports) {
    return false;
  }

  return supports("backdrop-filter", "blur(1px)") || supports("-webkit-backdrop-filter", "blur(1px)");
}

function withPerfTexture(texture: MaterialTextureVars | undefined, perfProfile: PerfProfile): MaterialTextureVars | undefined {
  if (!texture) {
    return undefined;
  }

  if (perfProfile !== "perf") {
    return texture;
  }

  return {
    ...texture,
    opacity: Math.min(texture.opacity, 0.01)
  };
}

export function resolveMaterialIdForSurface(styleId: StyleId, surfaceId: SurfaceId): MaterialId {
  return SURFACE_MATERIAL_MAP[styleId][surfaceId];
}

export function resolveMaterialRuntime(
  materialId: MaterialId,
  perfProfile: PerfProfile,
  blurSupportedOverride?: boolean
): ResolvedMaterialRuntime {
  const recipe = getLuxuryMaterialRecipe(materialId);
  const tokens = getLuxuryTokens(recipe.styleId);
  const blurSupported = blurSupportedOverride ?? supportsBackdropBlur();

  const blurEnabled = perfProfile === "default" && Boolean(recipe.blur) && blurSupported;
  const blurMode: MaterialRuntimeFlags["blurMode"] = blurEnabled ? "backdrop-filter" : "fallback";

  const specularEnabled = perfProfile === "default" && recipe.specular.opacity > 0;
  const texture = withPerfTexture(recipe.texture, perfProfile);
  const textureEnabled = Boolean(texture && texture.opacity > 0);
  const nextSpecularOpacity = specularEnabled
    ? Math.min(recipe.specular.opacity, tokens.glowBudget.maxAlpha)
    : 0;

  const nextRecipe: LuxuryMaterialRecipe = {
    id: recipe.id,
    styleId: recipe.styleId,
    layer: recipe.layer,
    ...(recipe.derivesFrom ? { derivesFrom: recipe.derivesFrom } : {}),
    surface: recipe.surface,
    borderHairline: recipe.borderHairline,
    innerStroke: recipe.innerStroke,
    specular: {
      ...recipe.specular,
      opacity: nextSpecularOpacity
    },
    ...(blurEnabled && recipe.blur ? { blur: recipe.blur } : {}),
    ...(texture ? { texture } : {}),
    elevationLevel: recipe.elevationLevel,
    governanceTags: recipe.governanceTags
  };

  return {
    recipe: nextRecipe,
    flags: {
      blurEnabled,
      specularEnabled,
      textureEnabled,
      blurMode
    }
  };
}

export function materialRuntimeToCssVars(runtime: ResolvedMaterialRuntime): Record<string, string> {
  const { recipe, flags } = runtime;
  const elevation = getLuxuryTokens(recipe.styleId).elevation[recipe.elevationLevel];
  const blurRadius = flags.blurEnabled && recipe.blur ? `${recipe.blur.radiusPx}px` : "0px";
  const blurSaturation = flags.blurEnabled && recipe.blur ? String(recipe.blur.saturation) : "1";

  return {
    "--lux-surface-bg": recipe.surface.base,
    "--lux-surface-tint": recipe.surface.tint,
    "--lux-surface-overlay": recipe.surface.overlay,
    "--lux-border-hairline-color": recipe.borderHairline.color,
    "--lux-border-hairline-width": `${recipe.borderHairline.widthPx}px`,
    "--lux-inner-stroke-color": recipe.innerStroke.color,
    "--lux-inner-stroke-inset": `${recipe.innerStroke.insetPx}px`,
    "--lux-elevation-lift": elevation.surfaceLift,
    "--lux-elevation-shadow": elevation.shadow,
    "--lux-elevation-rim": elevation.rimLight,
    "--lux-blur-radius": blurRadius,
    "--lux-blur-saturation": blurSaturation,
    "--lux-blur-fallback-surface": recipe.blur?.fallbackSurface ?? recipe.surface.base,
    "--lux-specular-opacity": String(recipe.specular.opacity),
    "--lux-specular-angle": `${recipe.specular.angleDeg}deg`,
    "--lux-specular-width": `${recipe.specular.widthPct}%`,
    "--lux-texture-opacity": String(recipe.texture?.opacity ?? 0),
    "--lux-texture-scale": String(recipe.texture?.scale ?? 1)
  };
}

export function getStyleMaterialStack(styleId: StyleId): readonly MaterialId[] {
  if (styleId === "LIQUID_GLASS") {
    return ["glass/card", "glass/inset", "glass/drawer", "glass/hero"];
  }

  if (styleId === "GOLD_NOIR_TERMINAL") {
    return ["ink/card", "ink/drawer"];
  }

  return ["graphite/card", "graphite/inset"];
}
