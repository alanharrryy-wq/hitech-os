import { describe, expect, it } from "vitest";
import { ALL_LAYERS, LAYER_DATA_ATTRIBUTES } from "../../src/layers/layerIds.js";
import {
  LAYER_FLAGS_CONTRACT,
  LAYER_RESOLUTION_PRECEDENCE,
  validateLayerFlagsContract
} from "../../src/layers/layerFlagsContract.js";

describe("layerFlagsContract", () => {
  it("keeps the declared contract valid", () => {
    const validation = validateLayerFlagsContract();
    expect(validation.ok).toBe(true);
    expect(validation.errors).toEqual([]);
  });

  it("keeps attribute coverage in sync with all layer ids", () => {
    expect(Object.keys(LAYER_DATA_ATTRIBUTES)).toHaveLength(ALL_LAYERS.length);
    expect(LAYER_FLAGS_CONTRACT.layerIds).toEqual(ALL_LAYERS);
  });

  it("exposes deterministic precedence order", () => {
    expect(LAYER_RESOLUTION_PRECEDENCE).toEqual([
      "defaults",
      "profile",
      "layers",
      "motion",
      "developer-overrides"
    ]);
  });
});
