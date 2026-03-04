import type { SceneRecord } from "../contracts/program-types.js";
import { computeDerived } from "../sequence/capture-plan.js";
import { canonicalizeSequence } from "../sequence/sequence-serializer.js";
import type { DirectorSequence } from "../sequence/sequence-types.js";
import { degradeSequence, type DegradeContext, type DegradeResult } from "../sequence/degrade.js";
import type { SceneAdapter, SceneRuntimeConfig } from "./scene-adapter.js";

export interface SequenceResolution {
  readonly timestampMs: number;
  readonly runtime: SceneRuntimeConfig;
  readonly capturePlanTimestamps: readonly number[];
  readonly degrade: Pick<DegradeResult, "requested" | "applied" | "reasons">;
}

function resolveBaseScene(sequence: DirectorSequence, adapter: SceneAdapter): SceneRecord {
  const ref = sequence.baseSceneRef;

  if (ref.type === "inlineScene") {
    return adapter.canonicalizeScene(ref.scene);
  }

  const found = adapter.getSceneById(ref.sceneId);
  if (!found) {
    throw new Error(`Unknown sceneId '${ref.sceneId}' for sequence '${sequence.sequenceId}'`);
  }

  return adapter.canonicalizeScene(found);
}

function applyKeyframes(
  sequence: DirectorSequence,
  timestampMs: number
): Pick<SceneRuntimeConfig, "camera" | "overlay" | "motion" | "layers"> {
  const camera: Record<string, unknown> = {};
  const overlay: Record<string, unknown> = {};
  const motion: Record<string, unknown> = {};
  const layers: Record<string, unknown> = {};

  const eligible = sequence.timelineDSL.keyframes
    .filter((keyframe) => keyframe.tMs <= timestampMs)
    .sort((left, right) => {
      if (left.tMs !== right.tMs) {
        return left.tMs - right.tMs;
      }
      if (left.track !== right.track) {
        return left.track.localeCompare(right.track);
      }
      return left.key.localeCompare(right.key);
    });

  for (const keyframe of eligible) {
    switch (keyframe.track) {
      case "camera": {
        camera[keyframe.key] = keyframe.value;
        break;
      }

      case "overlay": {
        overlay[keyframe.key] = keyframe.value;
        break;
      }

      case "motion": {
        motion[keyframe.key] = keyframe.value;
        break;
      }

      case "layers": {
        layers[keyframe.key] = keyframe.value;
        break;
      }

      default: {
        break;
      }
    }
  }

  return {
    camera,
    overlay,
    motion,
    layers
  };
}

export function resolveSequenceAtTime(input: {
  readonly sequence: DirectorSequence;
  readonly timestampMs: number;
  readonly adapter: SceneAdapter;
  readonly degradeContext?: DegradeContext;
}): SequenceResolution {
  const canonical = canonicalizeSequence(input.sequence);
  const degrade = degradeSequence(canonical, input.degradeContext ?? {
    requestedMode: "off",
    reducedMotion: false,
    performanceProfile: "high"
  });
  const baseScene = resolveBaseScene(degrade.sequence, input.adapter);

  const clampedTimestamp = Math.max(0, Math.floor(input.timestampMs));
  const patches = applyKeyframes(degrade.sequence, clampedTimestamp);

  const capturePlan = computeDerived(degrade.sequence);

  return {
    timestampMs: clampedTimestamp,
    runtime: {
      scene: baseScene,
      camera: patches.camera,
      overlay: patches.overlay,
      motion: patches.motion,
      layers: patches.layers
    },
    capturePlanTimestamps: capturePlan.timestamps,
    degrade: {
      requested: degrade.requested,
      applied: degrade.applied,
      reasons: degrade.reasons
    }
  };
}

export function resolveSequenceTimeline(input: {
  readonly sequence: DirectorSequence;
  readonly adapter: SceneAdapter;
  readonly degradeContext?: DegradeContext;
}): readonly SequenceResolution[] {
  const canonical = canonicalizeSequence(input.sequence);
  const degraded = degradeSequence(canonical, input.degradeContext ?? {
    requestedMode: "off",
    reducedMotion: false,
    performanceProfile: "high"
  });

  const timestamps = computeDerived(degraded.sequence).timestamps;

  return timestamps.map((timestamp) =>
    resolveSequenceAtTime({
      sequence: degraded.sequence,
      timestampMs: timestamp,
      adapter: input.adapter,
      degradeContext: {
        requestedMode: degraded.applied,
        reducedMotion: false,
        performanceProfile: "high"
      }
    })
  );
}
