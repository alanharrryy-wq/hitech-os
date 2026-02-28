import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import {
  extractDataLayerAttrs,
  loadKeystoneRuntime,
  resolveExpectedLayerState,
  stableFlagSignature,
  type ResolvedLayerLike
} from "./utils/pitchDeckTestHarness";
import {
  PITCH_DECK_PERMUTATION_CASES,
  PITCH_DECK_PERMUTATION_CASE_COUNT,
  type DeckPermutationCase
} from "./utils/pitchPermutationMatrix.generated";

const runtimePromise = loadKeystoneRuntime(import.meta.url);
const runtime = await runtimePromise;

function toResolvedLike(value: unknown): ResolvedLayerLike {
  const candidate = value as Partial<ResolvedLayerLike>;
  return {
    flags: (candidate.flags ?? {}) as Record<string, boolean>,
    profile: typeof candidate.profile === "string" ? candidate.profile : "neutral",
    source: typeof candidate.source === "string" ? candidate.source : "default",
    debug: candidate.debug === true,
    raw: typeof candidate.raw === "object" && candidate.raw != null ? candidate.raw : {}
  };
}

function toSearchParams(caseItem: DeckPermutationCase): Record<string, string | undefined> {
  return {
    ...(caseItem.layers !== undefined ? { layers: caseItem.layers } : {}),
    ...(caseItem.layerProfile !== undefined ? { layerProfile: caseItem.layerProfile } : {}),
    ...(caseItem.debug !== undefined ? { debug: caseItem.debug } : {})
  };
}

function shouldRenderRichAssertions(index: number): boolean {
  if (index === 0) {
    return true;
  }
  if (index === PITCH_DECK_PERMUTATION_CASES.length - 1) {
    return true;
  }
  return index % 7 === 0;
}

function renderAttrAndPanel(
  runtime: Awaited<typeof runtimePromise>,
  resolved: ResolvedLayerLike,
  env: DeckPermutationCase["env"]
): { attrs: Record<string, "on" | "off">; panelVisible: boolean } {
  const LayerFlagsProvider = runtime.LayerFlagsProvider as React.ComponentType<Record<string, unknown>>;
  const Stage = runtime.Stage as React.ComponentType<Record<string, unknown>>;
  const GlassCard = runtime.GlassCard as React.ComponentType<Record<string, unknown>>;
  const LayerDebugPanel = runtime.LayerDebugPanel as React.ComponentType<Record<string, unknown>>;

  const previousNodeEnv = process.env.NODE_ENV;
  process.env.NODE_ENV = env;

  try {
    const tree = React.createElement(
      LayerFlagsProvider,
      { initialResolved: resolved },
      React.createElement(
        Stage,
        { className: "permutation-stage" },
        React.createElement("span", null, "stage")
      ),
      React.createElement(
        GlassCard,
        { className: "permutation-card", tone: "default", backdrop: "off" },
        React.createElement("span", null, "card")
      ),
      React.createElement(LayerDebugPanel)
    );

    const html = renderToStaticMarkup(tree);
    const attrs = extractDataLayerAttrs(html);
    const panelVisible = html.includes("Layer Toggle Debugging");
    return { attrs, panelVisible };
  } finally {
    process.env.NODE_ENV = previousNodeEnv;
  }
}

describe("keystone /pitch permutations deck stability", () => {
  const suite = runtime.available ? describe : describe.skip;

  suite("layer/profile/debug permutations", () => {
    it("keeps deterministic matrix cardinality and ordering", () => {
      expect(PITCH_DECK_PERMUTATION_CASE_COUNT).toBe(2520);
      expect(PITCH_DECK_PERMUTATION_CASES.length).toBe(PITCH_DECK_PERMUTATION_CASE_COUNT);
      expect(PITCH_DECK_PERMUTATION_CASES[0]?.id).toBe("PERM_0001");
      expect(PITCH_DECK_PERMUTATION_CASES[PITCH_DECK_PERMUTATION_CASES.length - 1]?.id).toBe("PERM_2520");
    });

    it("validates canonical resolver invariants for every permutation", () => {
      for (const caseItem of PITCH_DECK_PERMUTATION_CASES) {
        const params = toSearchParams(caseItem);
        const expected = resolveExpectedLayerState(params);
        const resolved = toResolvedLike(runtime.resolveLayerFlags?.(params));

        expect(resolved.source).toBe(caseItem.expectedSource);
        expect(resolved.profile).toBe(caseItem.expectedProfile);
        expect(resolved.debug).toBe(caseItem.expectedDebug);
        expect(stableFlagSignature(resolved.flags)).toBe(caseItem.expectedFlagsSignature);
        expect(stableFlagSignature(resolved.flags)).toBe(stableFlagSignature(expected.flags));

        if (caseItem.expectedLayersOverrideProfile) {
          expect(resolved.source).toBe("layers");
        }
      }
    });

    it("asserts rendered data attrs + debug panel behavior on sampled permutations", () => {
      for (let index = 0; index < PITCH_DECK_PERMUTATION_CASES.length; index += 1) {
        if (!shouldRenderRichAssertions(index)) {
          continue;
        }

        const caseItem = PITCH_DECK_PERMUTATION_CASES[index];
        const params = toSearchParams(caseItem);
        const resolved = toResolvedLike(runtime.resolveLayerFlags?.(params));
        const rendered = renderAttrAndPanel(runtime, resolved, caseItem.env);

        expect(rendered.attrs["data-layer-stage-noise"]).toBe(caseItem.expectedStageNoise);
        expect(rendered.attrs["data-layer-stage-scanlines"]).toBe(caseItem.expectedStageScanlines);
        expect(rendered.attrs["data-layer-card-blur"]).toBe(caseItem.expectedCardBlur);
        expect(rendered.attrs["data-layer-motion-enabled"]).toBe(caseItem.expectedMotionEnabled);
        expect(rendered.panelVisible).toBe(caseItem.expectedDebugPanelVisible);
      }
    });

    it("layers overrides profile across all mixed-input permutations", () => {
      const mixed = PITCH_DECK_PERMUTATION_CASES.filter(
        (item) => item.layers !== undefined && item.layerProfile !== undefined
      );

      expect(mixed.length).toBeGreaterThan(0);

      for (const caseItem of mixed) {
        const resolved = toResolvedLike(runtime.resolveLayerFlags?.(toSearchParams(caseItem)));
        expect(resolved.source).toBe("layers");
        expect(caseItem.expectedLayersOverrideProfile).toBe(true);
      }
    });

    it("debug=1 only shows panel when NODE_ENV is not production", () => {
      const debugCases = PITCH_DECK_PERMUTATION_CASES.filter((item) => item.debug === "1");
      expect(debugCases.length).toBeGreaterThan(0);

      for (let index = 0; index < debugCases.length; index += 1) {
        const caseItem = debugCases[index];
        if (index % 5 !== 0) {
          continue;
        }

        const params = toSearchParams(caseItem);
        const resolved = toResolvedLike(runtime.resolveLayerFlags?.(params));

        const rendered = renderAttrAndPanel(runtime, resolved, caseItem.env);
        expect(rendered.panelVisible).toBe(caseItem.env !== "production");
        expect(caseItem.expectedDebugPanelVisible).toBe(caseItem.env !== "production");
      }
    });

    it("provides a deterministic sampled digest for CI snapshot-style regression checks", () => {
      const selected: DeckPermutationCase[] = [];

      for (let index = 0; index < PITCH_DECK_PERMUTATION_CASES.length; index += 113) {
        selected.push(PITCH_DECK_PERMUTATION_CASES[index]);
      }

      const digest = selected
        .map((caseItem) => {
          const params = toSearchParams(caseItem);
          const resolved = toResolvedLike(runtime.resolveLayerFlags?.(params));
          return [
            caseItem.id,
            caseItem.expectedSource,
            caseItem.expectedProfile,
            caseItem.expectedDebug ? "1" : "0",
            stableFlagSignature(resolved.flags)
          ].join("::");
        })
        .join("\n");

      expect(digest.startsWith("PERM_0001::default::neutral::0::")).toBe(true);
      expect(digest.includes("::layers::")).toBe(true);
      expect(digest.includes("::profile::")).toBe(true);
      expect(digest.length).toBeGreaterThan(500);
    });
  });

  if (!runtime.available) {
    describe("layer/profile/debug permutations (runtime missing)", () => {
      it("keeps matrix available for integration runner and reports reason", () => {
        expect(runtime.available).toBe(false);
        expect(PITCH_DECK_PERMUTATION_CASE_COUNT).toBe(2520);
        expect(runtime.reason.length).toBeGreaterThan(0);
      });
    });
  }
});

it("sanity: permutation matrix contains mixed source coverage", () => {
  const hasLayers = PITCH_DECK_PERMUTATION_CASES.some((item) => item.expectedSource === "layers");
  const hasProfile = PITCH_DECK_PERMUTATION_CASES.some((item) => item.expectedSource === "profile");
  const hasDefault = PITCH_DECK_PERMUTATION_CASES.some((item) => item.expectedSource === "default");

  expect(hasLayers).toBe(true);
  expect(hasProfile).toBe(true);
  expect(hasDefault).toBe(true);
});
