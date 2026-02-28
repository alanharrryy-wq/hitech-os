import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import {
  ALL_LAYERS,
  extractDataLayerAttrs,
  listAllKnownDataAttrs,
  loadKeystoneRuntime,
  resolveExpectedLayerState,
  stableFlagSignature,
  type ExpectedLayerState,
  type LayerId,
  type ResolvedLayerLike
} from "./utils/pitchDeckTestHarness";

const runtimePromise = loadKeystoneRuntime(import.meta.url);
const runtime = await runtimePromise;

function readResolvedShape(value: unknown): ResolvedLayerLike {
  const candidate = value as Partial<ResolvedLayerLike>;
  const flags = (candidate.flags ?? {}) as Record<string, boolean>;
  const profile = typeof candidate.profile === "string" ? candidate.profile : "neutral";
  const source = typeof candidate.source === "string" ? candidate.source : "default";
  const debug = candidate.debug === true;

  return {
    flags,
    profile,
    source,
    debug,
    raw: typeof candidate.raw === "object" && candidate.raw != null ? candidate.raw : {}
  };
}

function renderLayerMarkup(
  runtime: Awaited<typeof runtimePromise>,
  expected: ExpectedLayerState,
  resolved: ResolvedLayerLike
): string {
  const LayerFlagsProvider = runtime.LayerFlagsProvider as React.ComponentType<Record<string, unknown>>;
  const Stage = runtime.Stage as React.ComponentType<Record<string, unknown>>;
  const GlassCard = runtime.GlassCard as React.ComponentType<Record<string, unknown>>;

  const tree = React.createElement(
    LayerFlagsProvider,
    { initialResolved: resolved },
    React.createElement(
      Stage,
      { className: "test-stage" },
      React.createElement("span", null, `source=${expected.source}`)
    ),
    React.createElement(
      GlassCard,
      { tone: "default", backdrop: "off", className: "test-card" },
      React.createElement("span", null, `profile=${expected.profile}`)
    )
  );

  return renderToStaticMarkup(tree);
}

function assertSelectedAttrs(
  attrs: Record<string, "on" | "off">,
  expected: ExpectedLayerState,
  selection: readonly LayerId[]
): void {
  for (const layerId of selection) {
    const expectedValue = expected.flags[layerId] ? "on" : "off";
    const attrName =
      layerId === "stage.haze"
        ? "data-layer-stage-haze"
        : layerId === "stage.vignette"
          ? "data-layer-stage-vignette"
          : layerId === "stage.noise"
            ? "data-layer-stage-noise"
            : layerId === "stage.scanlines"
              ? "data-layer-stage-scanlines"
              : layerId === "stage.horizon"
                ? "data-layer-stage-horizon"
                : layerId === "frame.bezel"
                  ? "data-layer-frame-bezel"
                  : layerId === "card.blur"
                    ? "data-layer-card-blur"
                    : layerId === "card.innerStroke"
                      ? "data-layer-card-inner-stroke"
                      : layerId === "card.specular"
                        ? "data-layer-card-specular"
                        : layerId === "card.grain"
                          ? "data-layer-card-grain"
                          : layerId === "card.shadowAmbient"
                            ? "data-layer-card-shadow-ambient"
                            : layerId === "inset.shadow"
                              ? "data-layer-inset-shadow"
                              : "data-layer-motion-enabled";

    expect(attrs[attrName]).toBe(expectedValue);
  }
}

describe("keystone /pitch data attributes deck stability", () => {
  const suite = runtime.available ? describe : describe.skip;

  suite("layer attrs", () => {
    it("layers=none => all known layer attrs resolve to off", () => {
      const params = { layers: "none" };
      const expected = resolveExpectedLayerState(params);
      const resolved = readResolvedShape(runtime.resolveLayerFlags?.(params));

      const html = renderLayerMarkup(runtime, expected, resolved);
      const attrs = extractDataLayerAttrs(html);

      for (const attrName of listAllKnownDataAttrs()) {
        expect(attrs[attrName]).toBe("off");
      }

      expect(stableFlagSignature(resolved.flags)).toBe(stableFlagSignature(expected.flags));
      expect(resolved.source).toBe("layers");
    });

    it('layers=stage.noise => data-layer-stage-noise="on"', () => {
      const params = { layers: "stage.noise" };
      const expected = resolveExpectedLayerState(params);
      const resolved = readResolvedShape(runtime.resolveLayerFlags?.(params));

      const html = renderLayerMarkup(runtime, expected, resolved);
      const attrs = extractDataLayerAttrs(html);

      expect(attrs["data-layer-stage-noise"]).toBe("on");
      expect(attrs["data-layer-stage-scanlines"]).toBe("off");
      expect(attrs["data-layer-card-blur"]).toBe("off");
      expect(attrs["data-layer-motion-enabled"]).toBe("off");
      expect(stableFlagSignature(resolved.flags)).toBe(stableFlagSignature(expected.flags));
    });

    it("layerProfile=perf => blur/motion attrs off", () => {
      const params = { layerProfile: "perf" };
      const expected = resolveExpectedLayerState(params);
      const resolved = readResolvedShape(runtime.resolveLayerFlags?.(params));

      const html = renderLayerMarkup(runtime, expected, resolved);
      const attrs = extractDataLayerAttrs(html);

      expect(attrs["data-layer-card-blur"]).toBe("off");
      expect(attrs["data-layer-motion-enabled"]).toBe("off");
      expect(attrs["data-layer-stage-vignette"]).toBe("on");
      expect(attrs["data-layer-card-inner-stroke"]).toBe("on");
      expect(stableFlagSignature(resolved.flags)).toBe(stableFlagSignature(expected.flags));
      expect(resolved.source).toBe("profile");
    });

    it("selected attrs track deterministic canonical expectations", () => {
      const cases = [
        { layers: "all" },
        { layers: "stage.scanlines,card.blur,motion.enabled" },
        { layers: "stage.noise,unknown.layer" },
        { layerProfile: "fx" },
        { layerProfile: "neutral" },
        { layers: "none", layerProfile: "fx" }
      ];

      const selected: readonly LayerId[] = [
        "stage.noise",
        "stage.scanlines",
        "stage.vignette",
        "card.blur",
        "card.innerStroke",
        "motion.enabled"
      ];

      for (const params of cases) {
        const expected = resolveExpectedLayerState(params);
        const resolved = readResolvedShape(runtime.resolveLayerFlags?.(params));
        const html = renderLayerMarkup(runtime, expected, resolved);
        const attrs = extractDataLayerAttrs(html);

        assertSelectedAttrs(attrs, expected, selected);
        expect(stableFlagSignature(resolved.flags)).toBe(stableFlagSignature(expected.flags));
      }
    });

    it("layers source always overrides provided profile in attrs", () => {
      const cases = [
        { layers: "none", layerProfile: "fx" },
        { layers: "all", layerProfile: "perf" },
        { layers: "stage.noise", layerProfile: "perf" },
        { layers: "card.blur,motion.enabled", layerProfile: "fx" }
      ];

      for (const params of cases) {
        const expected = resolveExpectedLayerState(params);
        const resolved = readResolvedShape(runtime.resolveLayerFlags?.(params));
        const html = renderLayerMarkup(runtime, expected, resolved);
        const attrs = extractDataLayerAttrs(html);

        expect(resolved.source).toBe("layers");
        expect(stableFlagSignature(resolved.flags)).toBe(stableFlagSignature(expected.flags));
        expect(attrs["data-layer-stage-noise"]).toBe(expected.flags["stage.noise"] ? "on" : "off");
        expect(attrs["data-layer-card-blur"]).toBe(expected.flags["card.blur"] ? "on" : "off");
      }
    });
  });

  if (!runtime.available) {
    describe("layer attrs (runtime missing)", () => {
      it("documents missing keystone runtime context", () => {
        expect(runtime.available).toBe(false);
        expect(runtime.reason.length).toBeGreaterThan(0);
      });
    });
  }
});

it("sanity: canonical layer set remains deterministic for attribute tests", () => {
  expect(ALL_LAYERS).toEqual([
    "stage.haze",
    "stage.vignette",
    "stage.noise",
    "stage.scanlines",
    "stage.horizon",
    "frame.bezel",
    "card.blur",
    "card.innerStroke",
    "card.specular",
    "card.grain",
    "card.shadowAmbient",
    "inset.shadow",
    "motion.enabled"
  ]);
});
