import { stableStringify, sortUniqueStrings, type JsonValue } from "../shared/deterministic.js";
import type { PitchSceneRef, SceneRecord } from "../contracts/program-types.js";
import { parseSequence } from "./sequence-schema.js";
import { SEQUENCE_TRACKS, type SequenceTrack } from "./dsl.js";
import type { DirectorSequence } from "./sequence-types.js";

export interface SequenceCanonicalizationOptions {
  readonly sceneCanonicalizer?: (scene: SceneRecord) => SceneRecord;
}

function trackOrder(track: SequenceTrack): number {
  const index = SEQUENCE_TRACKS.indexOf(track);
  return index === -1 ? Number.MAX_SAFE_INTEGER : index;
}

function normalizeScene(scene: SceneRecord, options: SequenceCanonicalizationOptions): SceneRecord {
  const base: SceneRecord = {
    sceneId: scene.sceneId,
    route: scene.route,
    query: Object.fromEntries(
      Object.entries(scene.query)
        .map(([key, value]) => [key.trim(), value.trim()] as const)
        .filter(([key]) => key.length > 0)
        .sort(([left], [right]) => left.localeCompare(right))
    ),
    viewport: {
      width: scene.viewport.width,
      height: scene.viewport.height,
      deviceScaleFactor: scene.viewport.deviceScaleFactor
    },
    profile: scene.profile,
    layers: sortUniqueStrings(scene.layers),
    motion: {
      enabled: scene.motion.enabled,
      intensity: scene.motion.intensity,
      reducedMotionPolicy: scene.motion.reducedMotionPolicy
    }
  };

  return options.sceneCanonicalizer ? options.sceneCanonicalizer(base) : base;
}

function normalizeSceneRef(ref: PitchSceneRef, options: SequenceCanonicalizationOptions): PitchSceneRef {
  if (ref.type === "sceneId") {
    return {
      type: "sceneId",
      sceneId: ref.sceneId
    };
  }

  return {
    type: "inlineScene",
    scene: normalizeScene(ref.scene, options)
  };
}

export function canonicalizeSequence(
  sequence: DirectorSequence,
  options: SequenceCanonicalizationOptions = {}
): DirectorSequence {
  return {
    sequenceId: sequence.sequenceId,
    schemaVersion: sequence.schemaVersion,
    createdAt: sequence.createdAt,
    updatedAt: sequence.updatedAt,
    baseSceneRef: normalizeSceneRef(sequence.baseSceneRef, options),
    timelineDSL: {
      tracks: [...new Set(sequence.timelineDSL.tracks)].sort((left, right) => {
        return trackOrder(left) - trackOrder(right);
      }),
      keyframes: [...sequence.timelineDSL.keyframes]
        .map((keyframe) => ({
          tMs: keyframe.tMs,
          track: keyframe.track,
          key: keyframe.key,
          value: keyframe.value,
          easing: keyframe.easing
        }))
        .sort((left, right) => {
          if (left.tMs !== right.tMs) {
            return left.tMs - right.tMs;
          }
          const byTrack = trackOrder(left.track) - trackOrder(right.track);
          if (byTrack !== 0) {
            return byTrack;
          }
          return left.key.localeCompare(right.key);
        }),
      markers: [...sequence.timelineDSL.markers]
        .map((marker) => ({
          tMs: marker.tMs,
          label: marker.label
        }))
        .sort((left, right) => {
          if (left.tMs !== right.tMs) {
            return left.tMs - right.tMs;
          }
          return left.label.localeCompare(right.label);
        })
    },
    rules: {
      motionBudget: {
        maxHeroMotions: sequence.rules.motionBudget.maxHeroMotions,
        maxTrackKeyframes: sequence.rules.motionBudget.maxTrackKeyframes
      },
      reducedMotion: {
        strategy: sequence.rules.reducedMotion.strategy
      },
      perfDegrade: {
        strategy: sequence.rules.perfDegrade.strategy
      }
    }
  };
}

export function serializeSequence(
  sequence: DirectorSequence,
  options: SequenceCanonicalizationOptions = {}
): string {
  const canonical = canonicalizeSequence(sequence, options);
  return stableStringify(canonical as unknown as JsonValue);
}

export function parseSequenceJson(input: string): DirectorSequence {
  return parseSequence(JSON.parse(input) as unknown);
}

export function deserializeSequence(
  input: string,
  options: SequenceCanonicalizationOptions = {}
): DirectorSequence {
  const parsed = parseSequenceJson(input);
  return canonicalizeSequence(parsed, options);
}
