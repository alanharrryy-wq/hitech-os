import { describe, expect, it, vi } from "vitest";
import { createAllLayersOff, mergeLayerFlags, type LayerFlags } from "../../src/layers/layerIds.js";
import {
  applyLayerFlagsToDom,
  clearLayerFlagsFromDom,
  LAYER_DOM_METADATA_PROFILE_ATTRIBUTE,
  LAYER_DOM_METADATA_SOURCE_ATTRIBUTE
} from "../../src/layers/applyLayerFlagsToDom.js";

interface FakeDomTarget {
  readonly attributes: Map<string, string>;
  readonly setAttribute: ReturnType<typeof vi.fn>;
  readonly removeAttribute: ReturnType<typeof vi.fn>;
}

function createFakeTarget(): FakeDomTarget {
  const attributes = new Map<string, string>();
  const setAttribute = vi.fn((name: string, value: string) => {
    attributes.set(name, value);
  });
  const removeAttribute = vi.fn((name: string) => {
    attributes.delete(name);
  });

  return {
    attributes,
    setAttribute,
    removeAttribute
  };
}

function withFlags(overrides?: Partial<LayerFlags>): LayerFlags {
  return mergeLayerFlags(createAllLayersOff(), overrides);
}

describe("applyLayerFlagsToDom", () => {
  it("sets enabled data-layer attributes and metadata", () => {
    const target = createFakeTarget();
    applyLayerFlagsToDom({
      target,
      source: "layers",
      profile: "fx",
      flags: withFlags({
        "stage.noise": true,
        "card.blur": true
      })
    });

    expect(target.attributes.get("data-layer-stage-noise")).toBe("1");
    expect(target.attributes.get("data-layer-card-blur")).toBe("1");
    expect(target.attributes.get(LAYER_DOM_METADATA_SOURCE_ATTRIBUTE)).toBe("layers");
    expect(target.attributes.get(LAYER_DOM_METADATA_PROFILE_ATTRIBUTE)).toBe("fx");
  });

  it("diffs updates and avoids writing unchanged attributes", () => {
    const target = createFakeTarget();
    const initialFlags = withFlags({
      "stage.noise": true
    });

    applyLayerFlagsToDom({
      target,
      source: "layers",
      profile: "neutral",
      flags: initialFlags
    });

    const setCallsAfterFirstApply = target.setAttribute.mock.calls.length;
    const removeCallsAfterFirstApply = target.removeAttribute.mock.calls.length;

    applyLayerFlagsToDom({
      target,
      source: "layers",
      profile: "neutral",
      flags: initialFlags
    });

    expect(target.setAttribute.mock.calls.length).toBe(setCallsAfterFirstApply);
    expect(target.removeAttribute.mock.calls.length).toBe(removeCallsAfterFirstApply);
  });

  it("removes disabled attributes on diffed updates", () => {
    const target = createFakeTarget();
    applyLayerFlagsToDom({
      target,
      source: "layers",
      profile: "neutral",
      flags: withFlags({
        "stage.noise": true,
        "card.blur": true
      })
    });

    applyLayerFlagsToDom({
      target,
      source: "layers",
      profile: "neutral",
      flags: withFlags({
        "card.blur": true
      })
    });

    expect(target.attributes.has("data-layer-stage-noise")).toBe(false);
    expect(target.attributes.get("data-layer-card-blur")).toBe("1");
  });

  it("clears all layer attributes and metadata", () => {
    const target = createFakeTarget();
    applyLayerFlagsToDom({
      target,
      source: "mixed",
      profile: "perf",
      flags: withFlags({
        "stage.scanlines": true
      })
    });

    clearLayerFlagsFromDom(target);

    expect(target.attributes.size).toBe(0);
  });
});
