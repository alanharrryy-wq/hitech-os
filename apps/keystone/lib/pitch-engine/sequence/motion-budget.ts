import type { DirectorSequence, SequenceTrack } from "./sequence-types.js";
import { isHeroMotionKey } from "./dsl.js";

export interface MotionBudgetViolation {
  readonly code: "hero-motion-limit" | "track-keyframe-limit";
  readonly message: string;
  readonly track?: SequenceTrack;
  readonly actual: number;
  readonly allowed: number;
}

export interface MotionBudgetAudit {
  readonly sequenceId: string;
  readonly heroMotionCount: number;
  readonly trackKeyframeCounts: Readonly<Record<SequenceTrack, number>>;
  readonly allowedHeroMotions: number;
  readonly allowedTrackKeyframes: number;
  readonly violations: readonly MotionBudgetViolation[];
  readonly ok: boolean;
}

function emptyTrackCounts(): Record<SequenceTrack, number> {
  return {
    camera: 0,
    overlay: 0,
    motion: 0,
    layers: 0
  };
}

export function evaluateMotionBudget(sequence: DirectorSequence): MotionBudgetAudit {
  const trackCounts = emptyTrackCounts();
  let heroMotionCount = 0;

  for (const keyframe of sequence.timelineDSL.keyframes) {
    trackCounts[keyframe.track] += 1;

    if (keyframe.track === "motion" && isHeroMotionKey(keyframe.key)) {
      heroMotionCount += 1;
    }
  }

  const violations: MotionBudgetViolation[] = [];

  const allowedHeroMotions = sequence.rules.motionBudget.maxHeroMotions;
  const allowedTrackKeyframes = sequence.rules.motionBudget.maxTrackKeyframes;

  if (heroMotionCount > allowedHeroMotions) {
    violations.push({
      code: "hero-motion-limit",
      message: `Hero motion keyframes exceeded limit (${heroMotionCount} > ${allowedHeroMotions})`,
      actual: heroMotionCount,
      allowed: allowedHeroMotions
    });
  }

  const orderedTracks: readonly SequenceTrack[] = ["camera", "overlay", "motion", "layers"];
  for (const track of orderedTracks) {
    const count = trackCounts[track];
    if (count > allowedTrackKeyframes) {
      violations.push({
        code: "track-keyframe-limit",
        message: `Track '${track}' keyframes exceeded limit (${count} > ${allowedTrackKeyframes})`,
        track,
        actual: count,
        allowed: allowedTrackKeyframes
      });
    }
  }

  return {
    sequenceId: sequence.sequenceId,
    heroMotionCount,
    trackKeyframeCounts: trackCounts,
    allowedHeroMotions,
    allowedTrackKeyframes,
    violations,
    ok: violations.length === 0
  };
}

export function assertMotionBudget(sequence: DirectorSequence): void {
  const audit = evaluateMotionBudget(sequence);
  if (!audit.ok) {
    const [firstViolation] = audit.violations;
    throw new Error(firstViolation ? firstViolation.message : "Motion budget violation");
  }
}
