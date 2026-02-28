import { describe, expect, it } from "vitest";
import { ALL_LAYERS } from "../../src/layers/layerIds.js";
import {
  createLayerFlagsQueryFromResolved,
  createResolvedFromLayers,
  createResolvedFromProfile,
  encodeLayersParam,
  resolveLayerFlags,
  toLayerFlagPairs
} from "../../src/layers/resolveLayerFlags.js";

describe("resolveLayerFlags", () => {
  it("defaults to neutral profile with all layers off", () => {
    const resolved = resolveLayerFlags({});
    expect(resolved.source).toBe("default");
    expect(resolved.profile).toBe("neutral");
    expect(resolved.debug).toBe(false);

    for (const id of ALL_LAYERS) {
      expect(resolved.flags[id]).toBe(false);
    }
  });

  it("applies layers=none as panic switch", () => {
    const resolved = resolveLayerFlags({ layers: "none" });
    expect(resolved.source).toBe("layers");
    expect(resolved.raw.layers).toBe("none");

    for (const id of ALL_LAYERS) {
      expect(resolved.flags[id]).toBe(false);
    }
  });

  it("applies layers=all with every flag enabled", () => {
    const resolved = resolveLayerFlags({ layers: "all" });
    expect(resolved.source).toBe("layers");
    expect(resolved.raw.layers).toBe("all");

    for (const id of ALL_LAYERS) {
      expect(resolved.flags[id]).toBe(true);
    }
  });

  it("applies explicit allowlist from layers=list", () => {
    const resolved = resolveLayerFlags({
      layers: "stage.noise,card.innerStroke,card.innerStroke,unknown.layer"
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.flags["stage.noise"]).toBe(true);
    expect(resolved.flags["card.innerStroke"]).toBe(true);
    expect(resolved.flags["card.blur"]).toBe(false);
    expect(resolved.flags["motion.enabled"]).toBe(false);
  });

  it("applies layerProfile=neutral", () => {
    const resolved = resolveLayerFlags({ layerProfile: "neutral" });
    expect(resolved.source).toBe("profile");
    expect(resolved.profile).toBe("neutral");

    for (const id of ALL_LAYERS) {
      expect(resolved.flags[id]).toBe(false);
    }
  });

  it("applies layerProfile=fx safe subset", () => {
    const resolved = resolveLayerFlags({ layerProfile: "fx" });
    expect(resolved.source).toBe("profile");
    expect(resolved.profile).toBe("fx");
    expect(resolved.flags["stage.haze"]).toBe(true);
    expect(resolved.flags["stage.vignette"]).toBe(true);
    expect(resolved.flags["stage.horizon"]).toBe(true);
    expect(resolved.flags["stage.noise"]).toBe(true);
    expect(resolved.flags["card.innerStroke"]).toBe(true);
    expect(resolved.flags["card.shadowAmbient"]).toBe(true);
    expect(resolved.flags["card.specular"]).toBe(true);
    expect(resolved.flags["card.grain"]).toBe(true);
    expect(resolved.flags["inset.shadow"]).toBe(true);

    expect(resolved.flags["card.blur"]).toBe(false);
    expect(resolved.flags["motion.enabled"]).toBe(false);
  });

  it("applies layerProfile=perf with blur and motion off", () => {
    const resolved = resolveLayerFlags({ layerProfile: "perf" });
    expect(resolved.source).toBe("profile");
    expect(resolved.profile).toBe("perf");
    expect(resolved.flags["stage.vignette"]).toBe(true);
    expect(resolved.flags["card.innerStroke"]).toBe(true);
    expect(resolved.flags["card.blur"]).toBe(false);
    expect(resolved.flags["motion.enabled"]).toBe(false);
  });

  it("enforces precedence: layers wins over layerProfile", () => {
    const resolved = resolveLayerFlags({
      layers: "stage.scanlines",
      layerProfile: "fx"
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.profile).toBe("fx");
    expect(resolved.flags["stage.scanlines"]).toBe(true);
    expect(resolved.flags["stage.haze"]).toBe(false);
    expect(resolved.flags["card.innerStroke"]).toBe(false);
  });

  it("enables debug only for debug=1", () => {
    expect(resolveLayerFlags({ debug: "1" }).debug).toBe(true);
    expect(resolveLayerFlags({ debug: "0" }).debug).toBe(false);
    expect(resolveLayerFlags({ debug: "true" }).debug).toBe(false);
    expect(resolveLayerFlags({}).debug).toBe(false);
  });

  it("handles array-based search params", () => {
    const resolved = resolveLayerFlags({
      layers: ["card.grain,stage.haze"],
      layerProfile: ["perf"],
      debug: ["1"]
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.debug).toBe(true);
    expect(resolved.flags["card.grain"]).toBe(true);
    expect(resolved.flags["stage.haze"]).toBe(true);
    expect(resolved.flags["stage.vignette"]).toBe(false);
  });

  it("encodes query params from resolved layers mode", () => {
    const resolved = createResolvedFromLayers(["stage.noise", "card.innerStroke"], true);
    const next = createLayerFlagsQueryFromResolved(
      resolved,
      new URLSearchParams("layerProfile=fx")
    );

    expect(next.get("layers")).toBe("stage.noise,card.innerStroke");
    expect(next.get("layerProfile")).toBeNull();
    expect(next.get("debug")).toBe("1");
  });

  it("encodes query params from resolved profile mode", () => {
    const resolved = createResolvedFromProfile("perf", false);
    const next = createLayerFlagsQueryFromResolved(
      resolved,
      new URLSearchParams("layers=all&debug=1")
    );

    expect(next.get("layers")).toBeNull();
    expect(next.get("layerProfile")).toBe("perf");
    expect(next.get("debug")).toBeNull();
  });

  it("encodes full-on and full-off layers as shortcuts", () => {
    const allOn = resolveLayerFlags({ layers: "all" });
    const allOff = resolveLayerFlags({ layers: "none" });

    expect(encodeLayersParam(allOn.flags)).toBe("all");
    expect(encodeLayersParam(allOff.flags)).toBe("none");
  });

  it("returns stable flag pairs order", () => {
    const resolved = resolveLayerFlags({ layers: "card.grain,stage.haze" });
    const pairs = toLayerFlagPairs(resolved.flags);

    expect(pairs).toHaveLength(ALL_LAYERS.length);
    expect(pairs[0]?.id).toBe("stage.haze");
    expect(pairs[pairs.length - 1]?.id).toBe("motion.enabled");
  });
});
