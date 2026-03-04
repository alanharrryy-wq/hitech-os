import type { DirectorCapabilityMode } from "../contracts/program-types.js";
import type { DirectorSequence } from "./sequence-types.js";
import { canonicalizeSequence } from "./sequence-serializer.js";

export type PerformanceProfile = "high" | "balanced" | "low";

export interface DegradeContext {
  readonly requestedMode: DirectorCapabilityMode;
  readonly reducedMotion: boolean;
  readonly performanceProfile: PerformanceProfile;
}

export interface DegradeReason {
  readonly code:
    | "requested-off"
    | "perf-low"
    | "reduced-motion"
    | "lite-drop-motion-track"
    | "lite-reduce-layer-intensity";
  readonly message: string;
}

export interface DegradeResult {
  readonly requested: DirectorCapabilityMode;
  readonly applied: DirectorCapabilityMode;
  readonly reasons: readonly DegradeReason[];
  readonly sequence: DirectorSequence;
}

function reduceLayerValue(value: unknown): unknown {
  if (typeof value === "number") {
    return Number((value * 0.5).toFixed(4));
  }

  if (value && typeof value === "object" && !Array.isArray(value) && "value" in value) {
    const raw = (value as { value: unknown }).value;
    if (typeof raw === "number") {
      return {
        ...(value as Record<string, unknown>),
        value: Number((raw * 0.5).toFixed(4))
      };
    }
  }

  return value;
}

function applyJumpToFinal(sequence: DirectorSequence): DirectorSequence {
  const latestByTrackAndKey = new Map<string, (typeof sequence.timelineDSL.keyframes)[number]>();

  for (const keyframe of sequence.timelineDSL.keyframes) {
    latestByTrackAndKey.set(`${keyframe.track}:${keyframe.key}`, keyframe);
  }

  const finalKeyframes = [...latestByTrackAndKey.values()]
    .map((keyframe) => ({
      ...keyframe,
      tMs: 0,
      easing: "linear" as const
    }))
    .sort((left, right) => {
      if (left.track !== right.track) {
        return left.track.localeCompare(right.track);
      }
      return left.key.localeCompare(right.key);
    });

  return {
    ...sequence,
    timelineDSL: {
      ...sequence.timelineDSL,
      keyframes: finalKeyframes,
      markers: sequence.timelineDSL.markers.map((marker) => ({
        ...marker,
        tMs: 0
      }))
    }
  };
}

function applyLiteProfile(sequence: DirectorSequence): DirectorSequence {
  const tracks = sequence.timelineDSL.tracks.filter((track) => track !== "motion");
  const keyframes = sequence.timelineDSL.keyframes
    .filter((keyframe) => keyframe.track !== "motion")
    .map((keyframe) => {
      if (keyframe.track !== "layers") {
        return keyframe;
      }

      return {
        ...keyframe,
        value: reduceLayerValue(keyframe.value)
      };
    });

  return {
    ...sequence,
    timelineDSL: {
      ...sequence.timelineDSL,
      tracks,
      keyframes
    }
  };
}

function applyOffProfile(sequence: DirectorSequence): DirectorSequence {
  return {
    ...sequence,
    timelineDSL: {
      tracks: [],
      keyframes: [],
      markers: []
    }
  };
}

export function degradeSequence(sequence: DirectorSequence, context: DegradeContext): DegradeResult {
  const reasons: DegradeReason[] = [];
  let applied: DirectorCapabilityMode = context.requestedMode;
  let degraded = canonicalizeSequence(sequence);

  if (context.requestedMode === "off") {
    reasons.push({
      code: "requested-off",
      message: "Requested mode is off; sequence timeline disabled"
    });
    degraded = applyOffProfile(degraded);
    return {
      requested: context.requestedMode,
      applied,
      reasons,
      sequence: degraded
    };
  }

  if (context.performanceProfile === "low" && (applied === "full" || applied === "debug")) {
    applied = "lite";
    reasons.push({
      code: "perf-low",
      message: "Performance profile is low, forcing lite mode"
    });
  }

  if (context.reducedMotion && applied !== "off") {
    if (applied === "full" || applied === "debug") {
      applied = "lite";
    }

    reasons.push({
      code: "reduced-motion",
      message: "Reduced motion enabled; sequence jumps to final keyframes"
    });
    degraded = applyJumpToFinal(degraded);
  }

  if (applied === "lite") {
    degraded = applyLiteProfile(degraded);
    reasons.push(
      {
        code: "lite-drop-motion-track",
        message: "Lite mode drops motion track keyframes"
      },
      {
        code: "lite-reduce-layer-intensity",
        message: "Lite mode reduces layers intensity deterministically"
      }
    );
  }

  return {
    requested: context.requestedMode,
    applied,
    reasons,
    sequence: canonicalizeSequence(degraded)
  };
}

export function applyReducedMotion(sequence: DirectorSequence): DirectorSequence {
  return degradeSequence(sequence, {
    requestedMode: "full",
    reducedMotion: true,
    performanceProfile: "high"
  }).sequence;
}

export function applyPerfDegrade(sequence: DirectorSequence): DirectorSequence {
  return degradeSequence(sequence, {
    requestedMode: "full",
    reducedMotion: false,
    performanceProfile: "low"
  }).sequence;
}
