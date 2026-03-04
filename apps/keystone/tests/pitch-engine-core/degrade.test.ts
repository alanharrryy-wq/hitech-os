import { describe, expect, it } from "vitest";
import {
  applyPerfDegrade,
  applyReducedMotion,
  degradeSequence,
  type DegradeContext
} from "../../lib/pitch-engine/index.js";
import { createSequence } from "./fixtures.js";

describe("degrade", () => {
  it("requested off disables all timeline tracks", () => {
    const sequence = createSequence();

    const degraded = degradeSequence(sequence, {
      requestedMode: "off",
      reducedMotion: false,
      performanceProfile: "high"
    });

    expect(degraded.applied).toBe("off");
    expect(degraded.sequence.timelineDSL.tracks).toEqual([]);
    expect(degraded.sequence.timelineDSL.keyframes).toHaveLength(0);
    expect(degraded.reasons[0]?.code).toBe("requested-off");
  });

  const modeCases: ReadonlyArray<{
    readonly name: string;
    readonly context: DegradeContext;
    readonly expectedApplied: "off" | "lite" | "full" | "debug";
    readonly expectedCodes: readonly string[];
  }> = [
    {
      name: "full + high perf keeps full",
      context: {
        requestedMode: "full",
        reducedMotion: false,
        performanceProfile: "high"
      },
      expectedApplied: "full",
      expectedCodes: []
    },
    {
      name: "full + balanced perf keeps full",
      context: {
        requestedMode: "full",
        reducedMotion: false,
        performanceProfile: "balanced"
      },
      expectedApplied: "full",
      expectedCodes: []
    },
    {
      name: "full + low perf degrades to lite",
      context: {
        requestedMode: "full",
        reducedMotion: false,
        performanceProfile: "low"
      },
      expectedApplied: "lite",
      expectedCodes: ["perf-low", "lite-drop-motion-track", "lite-reduce-layer-intensity"]
    },
    {
      name: "debug + low perf degrades to lite",
      context: {
        requestedMode: "debug",
        reducedMotion: false,
        performanceProfile: "low"
      },
      expectedApplied: "lite",
      expectedCodes: ["perf-low", "lite-drop-motion-track", "lite-reduce-layer-intensity"]
    },
    {
      name: "lite + high perf stays lite",
      context: {
        requestedMode: "lite",
        reducedMotion: false,
        performanceProfile: "high"
      },
      expectedApplied: "lite",
      expectedCodes: ["lite-drop-motion-track", "lite-reduce-layer-intensity"]
    },
    {
      name: "debug + high perf stays debug",
      context: {
        requestedMode: "debug",
        reducedMotion: false,
        performanceProfile: "high"
      },
      expectedApplied: "debug",
      expectedCodes: []
    },
    {
      name: "full + reduced motion degrades to lite",
      context: {
        requestedMode: "full",
        reducedMotion: true,
        performanceProfile: "high"
      },
      expectedApplied: "lite",
      expectedCodes: ["reduced-motion", "lite-drop-motion-track", "lite-reduce-layer-intensity"]
    },
    {
      name: "debug + reduced motion degrades to lite",
      context: {
        requestedMode: "debug",
        reducedMotion: true,
        performanceProfile: "high"
      },
      expectedApplied: "lite",
      expectedCodes: ["reduced-motion", "lite-drop-motion-track", "lite-reduce-layer-intensity"]
    },
    {
      name: "lite + reduced motion stays lite",
      context: {
        requestedMode: "lite",
        reducedMotion: true,
        performanceProfile: "high"
      },
      expectedApplied: "lite",
      expectedCodes: ["reduced-motion", "lite-drop-motion-track", "lite-reduce-layer-intensity"]
    },
    {
      name: "off + reduced motion remains off",
      context: {
        requestedMode: "off",
        reducedMotion: true,
        performanceProfile: "low"
      },
      expectedApplied: "off",
      expectedCodes: ["requested-off"]
    }
  ];

  it.each(modeCases)("$name", ({ context, expectedApplied, expectedCodes }) => {
    const sequence = createSequence();
    const degraded = degradeSequence(sequence, context);

    expect(degraded.applied).toBe(expectedApplied);

    const codes = degraded.reasons.map((reason) => reason.code);
    for (const code of expectedCodes) {
      expect(codes).toContain(code);
    }
  });

  it("lite mode drops motion track", () => {
    const sequence = createSequence();

    const degraded = degradeSequence(sequence, {
      requestedMode: "lite",
      reducedMotion: false,
      performanceProfile: "high"
    });

    expect(degraded.sequence.timelineDSL.tracks).not.toContain("motion");
    expect(degraded.sequence.timelineDSL.keyframes.every((keyframe) => keyframe.track !== "motion")).toBe(true);
  });

  it("lite mode reduces layer intensity numeric values", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          {
            tMs: 100,
            track: "layers",
            key: "intensity",
            value: 0.8,
            easing: "linear"
          }
        ]
      }
    });

    const degraded = degradeSequence(sequence, {
      requestedMode: "lite",
      reducedMotion: false,
      performanceProfile: "high"
    });

    expect(degraded.sequence.timelineDSL.keyframes[0]?.value).toBe(0.4);
  });

  it("lite mode reduces nested layer intensity object values", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          {
            tMs: 100,
            track: "layers",
            key: "intensity",
            value: {
              value: 0.6,
              unit: "ratio"
            },
            easing: "linear"
          }
        ]
      }
    });

    const degraded = degradeSequence(sequence, {
      requestedMode: "lite",
      reducedMotion: false,
      performanceProfile: "high"
    });

    expect(degraded.sequence.timelineDSL.keyframes[0]?.value).toEqual({
      value: 0.3,
      unit: "ratio"
    });
  });

  it("reduced motion jumpToFinal keeps latest per track/key", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          {
            tMs: 0,
            track: "camera",
            key: "zoom",
            value: 1,
            easing: "linear"
          },
          {
            tMs: 1_000,
            track: "camera",
            key: "zoom",
            value: 1.4,
            easing: "easeOut"
          },
          {
            tMs: 2_000,
            track: "overlay",
            key: "headline",
            value: "Final",
            easing: "easeInOut"
          }
        ]
      }
    });

    const degraded = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "high"
    });

    const cameraZoom = degraded.sequence.timelineDSL.keyframes.find(
      (keyframe) => keyframe.track === "camera" && keyframe.key === "zoom"
    );

    expect(cameraZoom?.value).toBe(1.4);
    expect(cameraZoom?.tMs).toBe(0);
  });

  it("reduced motion sets all markers to zero", () => {
    const degraded = degradeSequence(createSequence(), {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "high"
    });

    expect(degraded.sequence.timelineDSL.markers.every((marker) => marker.tMs === 0)).toBe(true);
  });

  it("applyReducedMotion helper matches reduce context behavior", () => {
    const sequence = createSequence();
    const helper = applyReducedMotion(sequence);
    const manual = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "high"
    }).sequence;

    expect(helper).toEqual(manual);
  });

  it("applyPerfDegrade helper matches low perf context behavior", () => {
    const sequence = createSequence();
    const helper = applyPerfDegrade(sequence);
    const manual = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: false,
      performanceProfile: "low"
    }).sequence;

    expect(helper).toEqual(manual);
  });

  it("deterministic output for same input and context", () => {
    const sequence = createSequence();

    const a = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "low"
    });

    const b = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "low"
    });

    expect(a).toEqual(b);
  });

  const intensityCases: ReadonlyArray<{
    readonly input: number;
    readonly expected: number;
  }> = [
    { input: 1, expected: 0.5 },
    { input: 0.9, expected: 0.45 },
    { input: 0.75, expected: 0.375 },
    { input: 0.5, expected: 0.25 },
    { input: 0.25, expected: 0.125 },
    { input: 0.1, expected: 0.05 },
    { input: 0, expected: 0 }
  ];

  it.each(intensityCases)("lite halves layer intensity $input", ({ input, expected }) => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          {
            tMs: 100,
            track: "layers",
            key: "intensity",
            value: input,
            easing: "linear"
          }
        ]
      }
    });

    const degraded = degradeSequence(sequence, {
      requestedMode: "lite",
      reducedMotion: false,
      performanceProfile: "high"
    });

    expect(degraded.sequence.timelineDSL.keyframes[0]?.value).toBe(expected);
  });

  it("lite degrade leaves non-layer keyframe values unchanged", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          {
            tMs: 100,
            track: "camera",
            key: "zoom",
            value: 1.2,
            easing: "linear"
          },
          {
            tMs: 150,
            track: "overlay",
            key: "headline",
            value: "hello",
            easing: "linear"
          }
        ]
      }
    });

    const degraded = degradeSequence(sequence, {
      requestedMode: "lite",
      reducedMotion: false,
      performanceProfile: "high"
    });

    expect(degraded.sequence.timelineDSL.keyframes[0]?.value).toBe(1.2);
    expect(degraded.sequence.timelineDSL.keyframes[1]?.value).toBe("hello");
  });

  it("reduced motion then lite still deterministic keyframe order", () => {
    const sequence = createSequence();

    const degradedA = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "low"
    });

    const degradedB = degradeSequence(sequence, {
      requestedMode: "full",
      reducedMotion: true,
      performanceProfile: "low"
    });

    const idsA = degradedA.sequence.timelineDSL.keyframes.map(
      (keyframe) => `${keyframe.track}:${keyframe.key}:${keyframe.tMs}`
    );
    const idsB = degradedB.sequence.timelineDSL.keyframes.map(
      (keyframe) => `${keyframe.track}:${keyframe.key}:${keyframe.tMs}`
    );

    expect(idsA).toEqual(idsB);
  });
});
