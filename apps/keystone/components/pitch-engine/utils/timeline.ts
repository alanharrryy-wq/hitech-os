import type {
  DirectorTimeline,
  MarkerType,
  PitchScene,
  PitchSequence,
  SequenceCreateInput,
  TimelineMarker,
  TimelinePresetScript,
  TimelineTrack,
  TimelineTrackType
} from "../types";
import { buildStableId, nowIso } from "./id";

const TRACK_ORDER: TimelineTrackType[] = [
  "camera",
  "overlay",
  "motion",
  "layers",
  "lighting",
  "subtitle",
  "audio",
  "annotation"
];

export function createEmptyTimeline(durationMs = 8000): DirectorTimeline {
  return {
    durationMs,
    tracks: TRACK_ORDER.map((kind) => ({
      id: `track-${kind}`,
      label: kind.toUpperCase(),
      kind,
      enabled: true,
      keyframes: []
    })),
    markers: [],
    transitions: []
  };
}

export function createMarker(
  sequenceId: string,
  existingMarkers: readonly TimelineMarker[],
  input: {
    readonly type: MarkerType;
    readonly label: string;
    readonly t: number;
    readonly note: string;
  }
): TimelineMarker {
  const id = buildStableId(`marker-${sequenceId}`, input.label, existingMarkers.map((it) => it.id));

  return {
    id,
    label: input.label,
    type: input.type,
    t: Math.max(0, input.t),
    note: input.note
  };
}

export function applyPresetToTimeline(script: TimelinePresetScript): DirectorTimeline {
  return {
    durationMs: script.durationMs,
    markers: script.markers.map((marker, index) => ({
      id: `marker-${script.id}-${index + 1}`,
      label: marker.label,
      note: marker.note,
      t: marker.t,
      type: marker.type
    })),
    transitions: [],
    tracks: script.tracks.map((track, trackIndex) => ({
      id: `track-${script.id}-${track.kind}-${trackIndex + 1}`,
      kind: track.kind,
      label: track.label,
      enabled: track.enabled,
      keyframes: track.keyframes.map((keyframe, keyframeIndex) => ({
        id: `kf-${script.id}-${track.kind}-${keyframeIndex + 1}`,
        t: keyframe.t,
        easing: keyframe.easing,
        values: keyframe.values
      }))
    }))
  };
}

export function createSequenceFromPreset(input: {
  readonly scene: PitchScene;
  readonly existingSequences: readonly PitchSequence[];
  readonly create: SequenceCreateInput;
  readonly preset: TimelinePresetScript;
}): PitchSequence {
  const now = nowIso();
  const sequenceId = buildStableId(
    `seq-${input.scene.id}`,
    input.create.name,
    input.existingSequences.map((item) => item.id)
  );

  return {
    id: sequenceId,
    sceneId: input.create.baseSceneId,
    name: input.create.name,
    description: input.create.description,
    cinematicPresetId: input.preset.id,
    createdAt: now,
    updatedAt: now,
    timeline: applyPresetToTimeline(input.preset),
    diagnostics: {
      renderCost: "medium",
      qualityWarnings: [],
      lastRenderAt: null,
      lastRenderId: null
    }
  };
}

export function summarizeProgram(program: {
  readonly scenes: readonly PitchScene[];
  readonly sequences: readonly PitchSequence[];
}): {
  readonly scenes: number;
  readonly sequences: number;
  readonly markers: number;
  readonly keyframes: number;
} {
  let markerCount = 0;
  let keyframeCount = 0;

  for (const sequence of program.sequences) {
    markerCount += sequence.timeline.markers.length;
    for (const track of sequence.timeline.tracks) {
      keyframeCount += track.keyframes.length;
    }
  }

  return {
    scenes: program.scenes.length,
    sequences: program.sequences.length,
    markers: markerCount,
    keyframes: keyframeCount
  };
}

export function clampMs(value: number, min = 0, max = Number.POSITIVE_INFINITY): number {
  if (Number.isNaN(value)) {
    return min;
  }

  return Math.min(max, Math.max(min, value));
}

export function getSequenceDuration(sequence: PitchSequence | null): number {
  if (!sequence) {
    return 0;
  }

  return sequence.timeline.durationMs;
}

export function patchTrack(
  tracks: readonly TimelineTrack[],
  trackId: string,
  updater: (track: TimelineTrack) => TimelineTrack
): TimelineTrack[] {
  return tracks.map((track) => (track.id === trackId ? updater(track) : track));
}
