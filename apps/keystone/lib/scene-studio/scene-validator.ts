import { LAYER_DATA_ATTRIBUTES, type LayerId } from "@hitech/ui-kit";
import type { SceneDiagnosticsPayload } from "./scene-bridge";
import type { SceneRecord } from "./scene-schema";

export interface SceneValidationWarning {
  readonly code:
    | "UNKNOWN_LAYER_TOKENS"
    | "MISSING_DATA_ATTRIBUTES"
    | "PROFILE_MISMATCH"
    | "SOURCE_MISMATCH"
    | "MOTION_MISMATCH"
    | "EXPECTATION_FAILED";
  readonly message: string;
}

export interface SceneValidationReport {
  readonly valid: boolean;
  readonly warnings: readonly SceneValidationWarning[];
}

function expectedLayerIds(scene: SceneRecord): readonly LayerId[] {
  if (scene.layers.mode === "all") {
    return Object.keys(LAYER_DATA_ATTRIBUTES) as LayerId[];
  }

  if (scene.layers.mode === "none") {
    return [];
  }

  return scene.layers.layerIds;
}

function collectMissingDomAttributes(
  expectedLayers: readonly LayerId[],
  diagnostics: SceneDiagnosticsPayload
): string[] {
  const missing: string[] = [];

  for (const layerId of expectedLayers) {
    const attr = LAYER_DATA_ATTRIBUTES[layerId];
    if (diagnostics.domDataAttributes[attr] !== "1") {
      missing.push(attr);
    }
  }

  return missing;
}

export function validateSceneDiagnostics(
  scene: SceneRecord,
  diagnostics: SceneDiagnosticsPayload
): SceneValidationReport {
  const warnings: SceneValidationWarning[] = [];

  if (diagnostics.unknownTokens.length > 0) {
    warnings.push({
      code: "UNKNOWN_LAYER_TOKENS",
      message: `Unknown layer tokens: ${diagnostics.unknownTokens.join(", ")}`
    });
  }

  const missingAttrs = collectMissingDomAttributes(expectedLayerIds(scene), diagnostics);
  if (missingAttrs.length > 0) {
    warnings.push({
      code: "MISSING_DATA_ATTRIBUTES",
      message: `Missing expected DOM attributes: ${missingAttrs.join(", ")}`
    });
  }

  if (scene.layerProfile !== diagnostics.resolved.profile && scene.layers.mode !== "list") {
    warnings.push({
      code: "PROFILE_MISMATCH",
      message: `Scene profile (${scene.layerProfile}) differs from resolved profile (${diagnostics.resolved.profile}).`
    });
  }

  if (scene.motion !== (diagnostics.resolved.flags["motion.enabled"] ? "on" : "off")) {
    warnings.push({
      code: "MOTION_MISMATCH",
      message: `Scene motion (${scene.motion}) differs from resolved motion.`
    });
  }

  if (scene.expectations?.expectedSource && diagnostics.resolved.source !== scene.expectations.expectedSource) {
    warnings.push({
      code: "SOURCE_MISMATCH",
      message: `Expected source ${scene.expectations.expectedSource}, got ${diagnostics.resolved.source}.`
    });
  }

  if (scene.expectations?.minEnabledLayers !== undefined) {
    const enabledCount = diagnostics.enabledLayerIds.length;
    if (enabledCount < scene.expectations.minEnabledLayers) {
      warnings.push({
        code: "EXPECTATION_FAILED",
        message: `Expected at least ${scene.expectations.minEnabledLayers} enabled layers, got ${enabledCount}.`
      });
    }
  }

  return {
    valid: warnings.length === 0,
    warnings
  };
}
