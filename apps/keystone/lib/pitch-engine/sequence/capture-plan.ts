import type { SequenceCapturePlan, DirectorSequence, CapturePlanEntry } from "./sequence-types.js";

function uniqueSorted(values: readonly number[]): readonly number[] {
  return [...new Set(values)].sort((left, right) => left - right);
}

export interface CapturePlanOptions {
  readonly includeEndPaddingMs?: number;
  readonly explicitEndMs?: number;
}

export function computeDerived(sequence: DirectorSequence, options: CapturePlanOptions = {}): SequenceCapturePlan {
  const entries: CapturePlanEntry[] = [];

  entries.push({
    tMs: 0,
    reason: "start"
  });

  for (const keyframe of sequence.timelineDSL.keyframes) {
    entries.push({
      tMs: keyframe.tMs,
      reason: "keyframe",
      track: keyframe.track,
      key: keyframe.key
    });
  }

  for (const marker of sequence.timelineDSL.markers) {
    entries.push({
      tMs: marker.tMs,
      reason: "marker",
      markerLabel: marker.label
    });
  }

  const rawLast = Math.max(
    0,
    ...sequence.timelineDSL.keyframes.map((keyframe) => keyframe.tMs),
    ...sequence.timelineDSL.markers.map((marker) => marker.tMs)
  );

  const endMs = Math.max(options.explicitEndMs ?? rawLast, rawLast) + (options.includeEndPaddingMs ?? 0);

  entries.push({
    tMs: endMs,
    reason: "end"
  });

  const timestamps = uniqueSorted(entries.map((entry) => entry.tMs));

  const sortedEntries = [...entries].sort((left, right) => {
    if (left.tMs !== right.tMs) {
      return left.tMs - right.tMs;
    }

    const order = {
      start: 0,
      keyframe: 1,
      marker: 2,
      end: 3
    } as const;

    if (order[left.reason] !== order[right.reason]) {
      return order[left.reason] - order[right.reason];
    }

    const leftTrack = left.track ?? "";
    const rightTrack = right.track ?? "";
    if (leftTrack !== rightTrack) {
      return leftTrack.localeCompare(rightTrack);
    }

    const leftKey = left.key ?? "";
    const rightKey = right.key ?? "";
    if (leftKey !== rightKey) {
      return leftKey.localeCompare(rightKey);
    }

    return (left.markerLabel ?? "").localeCompare(right.markerLabel ?? "");
  });

  return {
    sequenceId: sequence.sequenceId,
    timestamps,
    entries: sortedEntries
  };
}

export function computeCapturePlanTimestamps(
  sequence: DirectorSequence,
  options: CapturePlanOptions = {}
): readonly number[] {
  return computeDerived(sequence, options).timestamps;
}
