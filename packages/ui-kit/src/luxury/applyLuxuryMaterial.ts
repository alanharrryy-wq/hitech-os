import type { ApplyLuxuryMaterialInput, PerfProfile } from "./types.js";
import { getLuxuryTokens } from "./tokens/index.js";
import {
  materialRuntimeToCssVars,
  resolveMaterialRuntime,
  type MaterialRuntimeFlags
} from "./materials/materialEngine.js";

export interface AppliedLuxuryMaterial {
  readonly materialId: ApplyLuxuryMaterialInput["materialId"];
  readonly styleId: ReturnType<typeof resolveMaterialRuntime>["recipe"]["styleId"];
  readonly perfProfile: PerfProfile;
  readonly cssVars: Readonly<Record<string, string>>;
  readonly dataAttributes: Readonly<Record<string, string>>;
  readonly runtimeFlags: MaterialRuntimeFlags;
  readonly safeguards: readonly string[];
}

function normalizePerfProfile(perfProfile?: PerfProfile): PerfProfile {
  return perfProfile === "perf" ? "perf" : "default";
}

export function applyLuxuryMaterial(
  input: ApplyLuxuryMaterialInput & { readonly blurSupported?: boolean }
): AppliedLuxuryMaterial {
  const perfProfile = normalizePerfProfile(input.perfProfile);
  const runtime = resolveMaterialRuntime(input.materialId, perfProfile, input.blurSupported);
  const tokens = getLuxuryTokens(runtime.recipe.styleId);

  const safeguards: string[] = [];
  if (!runtime.flags.blurEnabled && runtime.recipe.blur) {
    safeguards.push("blur-fallback-surface-enabled");
  }

  if (perfProfile === "perf") {
    safeguards.push("perf-profile-disables-expensive-effects");
  }

  if (runtime.flags.specularEnabled && runtime.recipe.specular.opacity > tokens.glowBudget.maxAlpha) {
    safeguards.push("specular-opacity-clamped-to-glow-budget");
  }

  return {
    materialId: input.materialId,
    styleId: runtime.recipe.styleId,
    perfProfile,
    cssVars: {
      ...materialRuntimeToCssVars(runtime),
      "--lux-glow-max-alpha": String(tokens.glowBudget.maxAlpha),
      "--lux-glow-max-blur": `${tokens.glowBudget.maxBlurPx}px`,
      "--lux-gold-max-coverage": String(tokens.goldUsage.maxCoverageRatio),
      "--lux-gold-max-accents": String(tokens.goldUsage.maxAccentsPerSurface)
    },
    dataAttributes: {
      "data-lux-style": runtime.recipe.styleId,
      "data-lux-material": runtime.recipe.id,
      "data-lux-layer": runtime.recipe.layer,
      "data-lux-perf": perfProfile,
      "data-lux-blur": runtime.flags.blurMode,
      "data-lux-texture": runtime.flags.textureEnabled ? "on" : "off",
      "data-lux-specular": runtime.flags.specularEnabled ? "on" : "off"
    },
    runtimeFlags: runtime.flags,
    safeguards
  };
}
