import { ALL_LAYERS, LAYER_DATA_ATTRIBUTES, parseLayerList } from "@hitech/ui-kit";
import { describe, expect, it } from "vitest";
import { resolvePitchLayerFlags } from "../../lib/pitch/layer-resolution";
import { LAYER_RESOLUTION_SCENARIOS } from "./fixtures/layer_resolution_scenarios.generated";

function readEnabledLayers(flags: ReturnType<typeof resolvePitchLayerFlags>["flags"]): readonly string[] {
  return ALL_LAYERS.filter((id) => flags[id]);
}

function toSearchParams(scenario: (typeof LAYER_RESOLUTION_SCENARIOS)[number]) {
  return {
    ...(scenario.profile ? { layerProfile: scenario.profile } : {}),
    ...(scenario.layers !== undefined ? { layers: scenario.layers } : {}),
    ...(scenario.debug !== undefined ? { debug: scenario.debug } : {})
  };
}

describe("pitch-engine layer contract validation matrix", () => {
  it("keeps visual base contract ids deterministic and ordered", () => {
    expect(ALL_LAYERS).toHaveLength(13);
    expect(ALL_LAYERS[0]).toBe("stage.haze");
    expect(ALL_LAYERS[1]).toBe("stage.vignette");
    expect(ALL_LAYERS[2]).toBe("stage.noise");
    expect(ALL_LAYERS[3]).toBe("stage.scanlines");
    expect(ALL_LAYERS[4]).toBe("stage.horizon");
    expect(ALL_LAYERS[5]).toBe("frame.bezel");
    expect(ALL_LAYERS[6]).toBe("card.blur");
    expect(ALL_LAYERS[7]).toBe("card.innerStroke");
    expect(ALL_LAYERS[8]).toBe("card.specular");
    expect(ALL_LAYERS[9]).toBe("card.grain");
    expect(ALL_LAYERS[10]).toBe("card.shadowAmbient");
    expect(ALL_LAYERS[11]).toBe("inset.shadow");
    expect(ALL_LAYERS[12]).toBe("motion.enabled");
  });

  it("keeps DOM data-layer attribute mapping complete and metadata-safe", () => {
    const expectedAttributes: Record<string, string> = {
      "stage.haze": "data-layer-stage-haze",
      "stage.vignette": "data-layer-stage-vignette",
      "stage.noise": "data-layer-stage-noise",
      "stage.scanlines": "data-layer-stage-scanlines",
      "stage.horizon": "data-layer-stage-horizon",
      "frame.bezel": "data-layer-frame-bezel",
      "card.blur": "data-layer-card-blur",
      "card.innerStroke": "data-layer-card-inner-stroke",
      "card.specular": "data-layer-card-specular",
      "card.grain": "data-layer-card-grain",
      "card.shadowAmbient": "data-layer-card-shadow-ambient",
      "inset.shadow": "data-layer-inset-shadow",
      "motion.enabled": "data-layer-motion-enabled"
    };

    for (const layerId of ALL_LAYERS) {
      expect(LAYER_DATA_ATTRIBUTES[layerId]).toBe(expectedAttributes[layerId]);
      expect(LAYER_DATA_ATTRIBUTES[layerId].startsWith("data-layer-")).toBe(true);
      expect(LAYER_DATA_ATTRIBUTES[layerId].includes("--")).toBe(false);
    }
  });

  it("parser stays tolerant to unknown tokens and preserves canonical ordering", () => {
    expect(parseLayerList("unknown,stage.noise,invalid,stage.vignette")).toEqual([
      "stage.vignette",
      "stage.noise"
    ]);
    expect(parseLayerList("unknown.only")).toEqual([]);
  });

  for (const scenario of LAYER_RESOLUTION_SCENARIOS) {
    it(`resolves precedence/defaults/profile/url/debug for ${scenario.id}`, () => {
      const resolved = resolvePitchLayerFlags(toSearchParams(scenario));
      const enabled = readEnabledLayers(resolved.flags);
      expect(resolved.source).toBe(scenario.expected.source);
      expect(resolved.profile).toBe(scenario.expected.profile);
      expect(resolved.debug).toBe(scenario.expected.debug);
      expect(new Set(enabled)).toEqual(new Set(scenario.expected.enabled));
      expect(enabled.length).toBe(scenario.expected.enabledCount);
      expect(resolved.flags["motion.enabled"]).toBe(scenario.expected.motionEnabled);
    });
  }
});
