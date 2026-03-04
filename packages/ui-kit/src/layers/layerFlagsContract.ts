import { ALL_LAYERS, LAYER_DATA_ATTRIBUTES, type LayerId } from "./layerIds.js";

export const LAYER_DOM_ROOT_TARGET = "html" as const;

export const LAYER_DOM_SOURCE_VALUES = ["defaults", "profile", "layers", "mixed"] as const;
export type LayerDomSourceValue = (typeof LAYER_DOM_SOURCE_VALUES)[number];

export const LAYER_RESOLUTION_PRECEDENCE = [
  "defaults",
  "profile",
  "layers",
  "motion",
  "developer-overrides"
] as const;

export interface LayerFlagsContract {
  readonly layerIds: readonly LayerId[];
  readonly attributeMap: Readonly<Record<LayerId, string>>;
  readonly domSourceValues: readonly LayerDomSourceValue[];
  readonly resolutionPrecedence: readonly string[];
}

export const LAYER_FLAGS_CONTRACT: LayerFlagsContract = {
  layerIds: ALL_LAYERS,
  attributeMap: LAYER_DATA_ATTRIBUTES,
  domSourceValues: LAYER_DOM_SOURCE_VALUES,
  resolutionPrecedence: LAYER_RESOLUTION_PRECEDENCE
};

const ATTRIBUTE_NAME_PATTERN = /^data-layer-[a-z0-9-]+$/;

export interface LayerContractValidationResult {
  readonly ok: boolean;
  readonly errors: readonly string[];
}

export function validateLayerFlagsContract(): LayerContractValidationResult {
  const errors: string[] = [];

  const ids = [...ALL_LAYERS];
  const uniqueIdCount = new Set(ids).size;
  if (uniqueIdCount !== ids.length) {
    errors.push("ALL_LAYERS contains duplicate layer ids.");
  }

  for (const id of ALL_LAYERS) {
    const attribute = LAYER_DATA_ATTRIBUTES[id];
    if (!attribute) {
      errors.push(`Missing data attribute mapping for layer "${id}".`);
      continue;
    }

    if (!ATTRIBUTE_NAME_PATTERN.test(attribute)) {
      errors.push(
        `Invalid data attribute "${attribute}" for layer "${id}". Expected format data-layer-*.`
      );
    }
  }

  const attributeValues = Object.values(LAYER_DATA_ATTRIBUTES);
  const uniqueAttributeCount = new Set(attributeValues).size;
  if (uniqueAttributeCount !== attributeValues.length) {
    errors.push("LAYER_DATA_ATTRIBUTES contains duplicate attribute names.");
  }

  return {
    ok: errors.length === 0,
    errors
  };
}

export function assertLayerFlagsContract(): void {
  const validation = validateLayerFlagsContract();
  if (validation.ok) {
    return;
  }

  throw new Error(`Layer contract invariant failed:\n- ${validation.errors.join("\n- ")}`);
}

if (process.env["NODE_ENV"] !== "production") {
  assertLayerFlagsContract();
}
