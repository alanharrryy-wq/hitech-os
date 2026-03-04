import type { PitchSceneRef } from "../contracts/program-types.js";
import type { SequenceEasing, SequenceKey, SequenceTrack, SequenceValue } from "./dsl.js";
import { SEQUENCE_SCHEMA_VERSION } from "./dsl.js";

export interface SequenceKeyframe {
  readonly tMs: number;
  readonly track: SequenceTrack;
  readonly key: SequenceKey;
  readonly value: SequenceValue;
  readonly easing: SequenceEasing;
}

export interface SequenceMarker {
  readonly tMs: number;
  readonly label: string;
}

export interface SequenceTimelineDsl {
  readonly tracks: readonly SequenceTrack[];
  readonly keyframes: readonly SequenceKeyframe[];
  readonly markers: readonly SequenceMarker[];
}

export interface SequenceMotionBudget {
  readonly maxHeroMotions: number;
  readonly maxTrackKeyframes: number;
}

export interface SequenceReducedMotionRule {
  readonly strategy: "jumpToFinal";
}

export interface SequencePerfDegradeRule {
  readonly strategy: "lite";
}

export interface SequenceRules {
  readonly motionBudget: SequenceMotionBudget;
  readonly reducedMotion: SequenceReducedMotionRule;
  readonly perfDegrade: SequencePerfDegradeRule;
}

export interface DirectorSequenceV1 {
  readonly sequenceId: string;
  readonly schemaVersion: typeof SEQUENCE_SCHEMA_VERSION;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly baseSceneRef: PitchSceneRef;
  readonly timelineDSL: SequenceTimelineDsl;
  readonly rules: SequenceRules;
}

export type DirectorSequence = DirectorSequenceV1;

export interface CapturePlanEntry {
  readonly tMs: number;
  readonly reason: "start" | "keyframe" | "marker" | "end";
  readonly track?: SequenceTrack;
  readonly key?: SequenceKey;
  readonly markerLabel?: string;
}

export interface SequenceCapturePlan {
  readonly sequenceId: string;
  readonly timestamps: readonly number[];
  readonly entries: readonly CapturePlanEntry[];
}

export interface SequenceValidationError {
  readonly path: string;
  readonly message: string;
  readonly code?: string;
}

export interface SequenceValidationResult {
  readonly ok: boolean;
  readonly sequence?: DirectorSequence;
  readonly errors: readonly SequenceValidationError[];
}

export interface SequenceMigrationRecord {
  readonly fromVersion: number | "unknown";
  readonly toVersion: number;
  readonly notes: readonly string[];
}

export interface SequenceMigrationResult {
  readonly sequence: DirectorSequence;
  readonly migrations: readonly SequenceMigrationRecord[];
}
