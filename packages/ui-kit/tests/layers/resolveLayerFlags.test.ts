import { describe, expect, it } from "vitest";
import { ALL_LAYERS } from "../../src/layers/layerIds.js";
import {
  createLayerFlagsQueryFromResolved,
  createResolvedFromLayers,
  createResolvedFromProfile,
  encodeLayersParam,
  parseLayersQueryValue,
  resolveLayerFlags,
  toLayerFlagPairs
} from "../../src/layers/resolveLayerFlags.js";

describe("resolveLayerFlags", () => {
  it("defaults to neutral profile with all layers off", () => {
    const resolved = resolveLayerFlags({});
    expect(resolved.source).toBe("default");
    expect(resolved.profile).toBe("neutral");
    expect(resolved.debug).toBe(false);
    expect(resolved.unknownTokens).toEqual([]);

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

  it("parses list layers and reports unknown tokens", () => {
    const parsed = parseLayersQueryValue(
      "stage.noise,card.innerStroke,card.innerStroke,motion.enabled,unknown.layer"
    );

    expect(parsed.layerIds).toEqual(["stage.noise", "card.innerStroke"]);
    expect(parsed.motionAliasOn).toBe(true);
    expect(parsed.unknownTokens).toEqual(["unknown.layer"]);
  });

  it("ignores unknown layer tokens while surfacing them", () => {
    const resolved = resolveLayerFlags({
      layers: "stage.noise,card.innerStroke,unknown.layer"
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.flags["stage.noise"]).toBe(true);
    expect(resolved.flags["card.innerStroke"]).toBe(true);
    expect(resolved.flags["card.blur"]).toBe(false);
    expect(resolved.flags["motion.enabled"]).toBe(false);
    expect(resolved.unknownTokens).toEqual(["unknown.layer"]);
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

  it("supports motion query override and motion.enabled alias", () => {
    const withAlias = resolveLayerFlags({ layers: "stage.scanlines,motion.enabled" });
    const withMotionParam = resolveLayerFlags({ layerProfile: "perf", motion: "on" });
    const motionOffWins = resolveLayerFlags({
      layers: "stage.scanlines,motion.enabled",
      motion: "off"
    });

    expect(withAlias.flags["motion.enabled"]).toBe(true);
    expect(withAlias.motionSource).toBe("layers");
    expect(withMotionParam.flags["motion.enabled"]).toBe(true);
    expect(withMotionParam.motionSource).toBe("motion");
    expect(withMotionParam.source).toBe("mixed");
    expect(motionOffWins.flags["motion.enabled"]).toBe(false);
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
      motion: ["on"],
      debug: ["1"]
    });

    expect(resolved.source).toBe("layers");
    expect(resolved.debug).toBe(true);
    expect(resolved.flags["card.grain"]).toBe(true);
    expect(resolved.flags["stage.haze"]).toBe(true);
    expect(resolved.flags["stage.vignette"]).toBe(false);
    expect(resolved.flags["motion.enabled"]).toBe(true);
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
    expect(next.get("motion")).toBeNull();
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
    expect(next.get("motion")).toBeNull();
  });

  it("keeps motion in canonical query when enabled", () => {
    const resolved = resolveLayerFlags({ layerProfile: "fx", motion: "on" });
    const next = createLayerFlagsQueryFromResolved(
      resolved,
      new URLSearchParams("foo=bar&layerProfile=fx")
    );

    expect(next.toString()).toBe("layerProfile=fx&motion=on&foo=bar");
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
