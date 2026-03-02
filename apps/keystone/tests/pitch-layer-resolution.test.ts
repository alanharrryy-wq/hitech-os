import { ALL_LAYERS, PROFILE_PRESETS } from "@hitech/ui-kit";
import { describe, expect, it } from "vitest";
import { resolvePitchLayerFlags } from "../lib/pitch/layer-resolution";

function enabledLayerIds(resolved: ReturnType<typeof resolvePitchLayerFlags>): readonly string[] {
  return ALL_LAYERS.filter((id) => resolved.flags[id]);
}

describe("pitch layer resolution precedence", () => {
  it("uses neutral defaults with all layers disabled when params are empty", () => {
    const resolved = resolvePitchLayerFlags({});

    expect(resolved.source).toBe("default");
    expect(resolved.profile).toBe("neutral");
    expect(resolved.debug).toBe(false);

    for (const id of ALL_LAYERS) {
      expect(resolved.flags[id]).toBe(false);
    }
  });

  it("treats layerProfile when layers param is absent", () => {
    const resolved = resolvePitchLayerFlags({ layerProfile: "fx" });

    expect(resolved.source).toBe("profile");
    expect(resolved.profile).toBe("fx");
    expect(new Set(enabledLayerIds(resolved))).toEqual(new Set(PROFILE_PRESETS.fx));
  });

  it("keeps default mode for invalid profile names", () => {
    const resolved = resolvePitchLayerFlags({ layerProfile: "experimental" });
    expect(resolved.source).toBe("default");
    expect(resolved.profile).toBe("neutral");
    expect(enabledLayerIds(resolved)).toEqual([]);
  });

  it("prioritizes explicit layers=none over layerProfile", () => {
    const resolved = resolvePitchLayerFlags({
      layers: "none",
      layerProfile: "fx",
      debug: "1"
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.profile).toBe("fx");
    expect(resolved.debug).toBe(true);
    expect(enabledLayerIds(resolved)).toEqual([]);
  });

  it("prioritizes explicit layers=all over layerProfile", () => {
    const resolved = resolvePitchLayerFlags({
      layers: "all",
      layerProfile: "perf"
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.profile).toBe("perf");

    for (const id of ALL_LAYERS) {
      expect(resolved.flags[id]).toBe(true);
    }
  });

  it("accepts explicit layer lists and ignores unknown entries", () => {
    const resolved = resolvePitchLayerFlags({
      layers: "stage.noise,invalid.layer,stage.vignette,stage.noise",
      layerProfile: "fx"
    });

    expect(resolved.source).toBe("layers");
    expect(enabledLayerIds(resolved)).toEqual(["stage.vignette", "stage.noise"]);
  });

  it("only enables debug when debug=1", () => {
    expect(resolvePitchLayerFlags({ debug: "1" }).debug).toBe(true);
    expect(resolvePitchLayerFlags({ debug: "0" }).debug).toBe(false);
    expect(resolvePitchLayerFlags({ debug: "true" }).debug).toBe(false);
    expect(resolvePitchLayerFlags({}).debug).toBe(false);
  });

  it("reads only the first value when array-like params are provided", () => {
    const resolved = resolvePitchLayerFlags({
      layers: ["none", "all"],
      layerProfile: ["perf", "fx"],
      debug: ["1", "0"]
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.profile).toBe("perf");
    expect(resolved.debug).toBe(true);
    expect(enabledLayerIds(resolved)).toEqual([]);
  });
});
