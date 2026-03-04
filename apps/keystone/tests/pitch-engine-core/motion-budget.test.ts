import { describe, expect, it } from "vitest";
import { assertMotionBudget, evaluateMotionBudget } from "../../lib/pitch-engine/index.js";
import { createSequence } from "./fixtures.js";

describe("motion-budget", () => {
  it("passes for default sequence budget", () => {
    const audit = evaluateMotionBudget(createSequence());

    expect(audit.ok).toBe(true);
    expect(audit.violations).toHaveLength(0);
  });

  it("tracks keyframe counts by track", () => {
    const audit = evaluateMotionBudget(createSequence());

    expect(audit.trackKeyframeCounts.camera).toBeGreaterThanOrEqual(1);
    expect(audit.trackKeyframeCounts.overlay).toBeGreaterThanOrEqual(1);
    expect(audit.trackKeyframeCounts.motion).toBeGreaterThanOrEqual(1);
    expect(audit.trackKeyframeCounts.layers).toBeGreaterThanOrEqual(1);
  });

  it("counts hero motion keyframes", () => {
    const audit = evaluateMotionBudget(createSequence());

    expect(audit.heroMotionCount).toBe(2);
  });

  it("violates when hero motion exceeds limit", () => {
    const sequence = createSequence({
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 1,
          maxTrackKeyframes: 10
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);

    expect(audit.ok).toBe(false);
    expect(audit.violations.some((violation) => violation.code === "hero-motion-limit")).toBe(true);
  });

  it("violates when any track exceeds keyframe limit", () => {
    const sequence = createSequence({
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 2,
          maxTrackKeyframes: 1
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);

    expect(audit.ok).toBe(false);
    expect(audit.violations.some((violation) => violation.code === "track-keyframe-limit")).toBe(true);
  });

  it("assertMotionBudget throws on violation", () => {
    const sequence = createSequence({
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 0,
          maxTrackKeyframes: 10
        }
      }
    });

    expect(() => assertMotionBudget(sequence)).toThrow(/Hero motion/);
  });

  it("assertMotionBudget does not throw when compliant", () => {
    const sequence = createSequence();

    expect(() => assertMotionBudget(sequence)).not.toThrow();
  });

  const heroCases: ReadonlyArray<{
    readonly maxHeroMotions: number;
    readonly expectOk: boolean;
  }> = [
    { maxHeroMotions: 0, expectOk: false },
    { maxHeroMotions: 1, expectOk: false },
    { maxHeroMotions: 2, expectOk: true },
    { maxHeroMotions: 3, expectOk: true },
    { maxHeroMotions: 4, expectOk: true }
  ];

  it.each(heroCases)("hero motion limit $maxHeroMotions", ({ maxHeroMotions, expectOk }) => {
    const sequence = createSequence({
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions,
          maxTrackKeyframes: 20
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);
    expect(audit.ok).toBe(expectOk);
  });

  const trackLimitCases: ReadonlyArray<{
    readonly maxTrackKeyframes: number;
    readonly expectOk: boolean;
  }> = [
    { maxTrackKeyframes: 0, expectOk: false },
    { maxTrackKeyframes: 1, expectOk: false },
    { maxTrackKeyframes: 2, expectOk: true },
    { maxTrackKeyframes: 3, expectOk: true },
    { maxTrackKeyframes: 4, expectOk: true },
    { maxTrackKeyframes: 10, expectOk: true }
  ];

  it.each(trackLimitCases)("track keyframe limit $maxTrackKeyframes", ({ maxTrackKeyframes, expectOk }) => {
    const sequence = createSequence({
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 2,
          maxTrackKeyframes
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);
    expect(audit.ok).toBe(expectOk);
  });

  const perTrackCases: ReadonlyArray<{
    readonly name: string;
    readonly keyframes: ReturnType<typeof createSequence>["timelineDSL"]["keyframes"];
    readonly maxTrackKeyframes: number;
    readonly expectedTrack: "camera" | "overlay" | "motion" | "layers";
  }> = [
    {
      name: "camera overflow",
      keyframes: [
        { tMs: 0, track: "camera", key: "zoom", value: 1, easing: "linear" },
        { tMs: 1, track: "camera", key: "panX", value: 1, easing: "linear" },
        { tMs: 2, track: "camera", key: "panY", value: 1, easing: "linear" }
      ],
      maxTrackKeyframes: 2,
      expectedTrack: "camera"
    },
    {
      name: "overlay overflow",
      keyframes: [
        { tMs: 0, track: "overlay", key: "headline", value: "a", easing: "linear" },
        { tMs: 1, track: "overlay", key: "subhead", value: "b", easing: "linear" },
        { tMs: 2, track: "overlay", key: "cta", value: "c", easing: "linear" }
      ],
      maxTrackKeyframes: 2,
      expectedTrack: "overlay"
    },
    {
      name: "motion overflow",
      keyframes: [
        { tMs: 0, track: "motion", key: "heroEntrance", value: "x", easing: "linear" },
        { tMs: 1, track: "motion", key: "parallax", value: "y", easing: "linear" },
        { tMs: 2, track: "motion", key: "drift", value: "z", easing: "linear" }
      ],
      maxTrackKeyframes: 2,
      expectedTrack: "motion"
    },
    {
      name: "layers overflow",
      keyframes: [
        { tMs: 0, track: "layers", key: "intensity", value: 1, easing: "linear" },
        { tMs: 1, track: "layers", key: "highlight", value: 1, easing: "linear" },
        { tMs: 2, track: "layers", key: "mask", value: 1, easing: "linear" }
      ],
      maxTrackKeyframes: 2,
      expectedTrack: "layers"
    }
  ];

  it.each(perTrackCases)("detects $name", ({ keyframes, maxTrackKeyframes, expectedTrack }) => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes
      },
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 10,
          maxTrackKeyframes
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);
    const violation = audit.violations.find((item) => item.code === "track-keyframe-limit");

    expect(violation?.track).toBe(expectedTrack);
  });

  it("hero count ignores non-hero motion keys", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          { tMs: 0, track: "motion", key: "drift", value: 1, easing: "linear" },
          { tMs: 1, track: "motion", key: "pulse", value: 1, easing: "linear" },
          { tMs: 2, track: "motion", key: "shake", value: 1, easing: "linear" }
        ]
      }
    });

    const audit = evaluateMotionBudget(sequence);

    expect(audit.heroMotionCount).toBe(0);
  });

  it("hero count includes only heroEntrance and parallax", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          { tMs: 0, track: "motion", key: "heroEntrance", value: 1, easing: "linear" },
          { tMs: 1, track: "motion", key: "parallax", value: 1, easing: "linear" },
          { tMs: 2, track: "motion", key: "drift", value: 1, easing: "linear" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 2,
          maxTrackKeyframes: 10
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);
    expect(audit.heroMotionCount).toBe(2);
    expect(audit.ok).toBe(true);
  });

  it("multiple violations are reported together", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [
          { tMs: 0, track: "motion", key: "heroEntrance", value: 1, easing: "linear" },
          { tMs: 1, track: "motion", key: "parallax", value: 1, easing: "linear" },
          { tMs: 2, track: "motion", key: "heroEntrance", value: 1, easing: "linear" },
          { tMs: 3, track: "camera", key: "zoom", value: 1, easing: "linear" },
          { tMs: 4, track: "camera", key: "panX", value: 1, easing: "linear" },
          { tMs: 5, track: "camera", key: "panY", value: 1, easing: "linear" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: 1,
          maxTrackKeyframes: 2
        }
      }
    });

    const audit = evaluateMotionBudget(sequence);

    expect(audit.violations.length).toBeGreaterThan(1);
    expect(audit.violations.some((violation) => violation.code === "hero-motion-limit")).toBe(true);
    expect(audit.violations.some((violation) => violation.code === "track-keyframe-limit")).toBe(true);
  });

  it("audit payload includes allowed thresholds", () => {
    const sequence = createSequence();
    const audit = evaluateMotionBudget(sequence);

    expect(audit.allowedHeroMotions).toBe(sequence.rules.motionBudget.maxHeroMotions);
    expect(audit.allowedTrackKeyframes).toBe(sequence.rules.motionBudget.maxTrackKeyframes);
  });

  it("audit is deterministic across repeated calls", () => {
    const sequence = createSequence();

    const first = evaluateMotionBudget(sequence);
    const second = evaluateMotionBudget(sequence);

    expect(first).toEqual(second);
  });
});
