export interface ScreenDeterminismInput {
  readonly industrialReliability: number;
  readonly softwareCompleteness: number;
  readonly tractionStrength: number;
  readonly compliancePosture: number;
  readonly cashRunwayMonths: number;
  readonly unresolvedCriticalIssues: number;
}

export type Screen05Decision = "advance" | "hold";
export type Screen06Band = "ready" | "watch" | "blocked";
export type PitchFlowState = "draft" | "screen05-assessed" | "screen06-assessed" | "approved" | "rejected";
export type PitchFlowEvent =
  | "run-screen05"
  | "run-screen06"
  | "approve"
  | "reject"
  | "reset";

export interface Screen05Evaluation {
  readonly weightedScore: number;
  readonly penaltyScore: number;
  readonly finalScore: number;
  readonly reasons: readonly string[];
  readonly decision: Screen05Decision;
}

export interface Screen06Evaluation {
  readonly executionScore: number;
  readonly reasons: readonly string[];
  readonly band: Screen06Band;
}

export interface ScreenDeterminismEvaluation {
  readonly screen05: Screen05Evaluation;
  readonly screen06: Screen06Evaluation;
}

export interface PitchFlowTransitionResult {
  readonly previous: PitchFlowState;
  readonly event: PitchFlowEvent;
  readonly next: PitchFlowState;
  readonly lockedReason: string | null;
}

function clamp(value: number, min: number, max: number): number {
  if (value < min) {
    return min;
  }
  if (value > max) {
    return max;
  }
  return value;
}

function round(value: number): number {
  return Math.round(value);
}

function sortReasons(reasons: readonly string[]): readonly string[] {
  return [...reasons].sort((left, right) => left.localeCompare(right));
}

export function deriveScreen05Evaluation(input: ScreenDeterminismInput): Screen05Evaluation {
  const weightedScore = round(
    input.industrialReliability * 0.32 +
      input.softwareCompleteness * 0.31 +
      input.tractionStrength * 0.22 +
      input.compliancePosture * 0.15
  );

  const runwayPenalty = input.cashRunwayMonths < 6 ? (6 - input.cashRunwayMonths) * 4 : 0;
  const issuesPenalty = input.unresolvedCriticalIssues * 7;
  const penaltyScore = runwayPenalty + issuesPenalty;
  const finalScore = clamp(weightedScore - penaltyScore, 0, 100);

  const reasons: string[] = [];
  if (input.industrialReliability < 45) {
    reasons.push("screen05:industrial-reliability-below-45");
  }
  if (input.softwareCompleteness < 50) {
    reasons.push("screen05:software-completeness-below-50");
  }
  if (input.tractionStrength < 40) {
    reasons.push("screen05:traction-strength-below-40");
  }
  if (input.compliancePosture < 60) {
    reasons.push("screen05:compliance-posture-below-60");
  }
  if (input.cashRunwayMonths < 6) {
    reasons.push("screen05:cash-runway-below-6m");
  }
  if (input.unresolvedCriticalIssues > 0) {
    reasons.push("screen05:unresolved-critical-issues");
  }
  if (finalScore < 70) {
    reasons.push("screen05:final-score-below-70");
  }

  return {
    weightedScore,
    penaltyScore,
    finalScore,
    reasons: sortReasons(reasons),
    decision: reasons.length === 0 ? "advance" : "hold"
  };
}

export function deriveScreen06Evaluation(
  input: ScreenDeterminismInput,
  screen05: Screen05Evaluation
): Screen06Evaluation {
  const executionScore = clamp(
    round(
      screen05.finalScore * 0.58 +
        input.softwareCompleteness * 0.24 +
        input.compliancePosture * 0.18
    ),
    0,
    100
  );

  const reasons: string[] = [];
  if (screen05.decision === "hold") {
    reasons.push("screen06:blocked-by-screen05");
  }
  if (executionScore < 75) {
    reasons.push("screen06:execution-score-below-75");
  }
  if (input.cashRunwayMonths < 9) {
    reasons.push("screen06:cash-runway-below-9m");
  }
  if (input.unresolvedCriticalIssues > 1) {
    reasons.push("screen06:more-than-one-critical-issue");
  }

  const sorted = sortReasons(reasons);
  if (sorted.length === 0) {
    return {
      executionScore,
      reasons: sorted,
      band: "ready"
    };
  }

  if (executionScore >= 60 && input.unresolvedCriticalIssues === 0) {
    return {
      executionScore,
      reasons: sorted,
      band: "watch"
    };
  }

  return {
    executionScore,
    reasons: sorted,
    band: "blocked"
  };
}

export function deriveScreenDeterminismEvaluation(
  input: ScreenDeterminismInput
): ScreenDeterminismEvaluation {
  const screen05 = deriveScreen05Evaluation(input);
  const screen06 = deriveScreen06Evaluation(input, screen05);
  return {
    screen05,
    screen06
  };
}

export function transitionPitchFlow(
  current: PitchFlowState,
  event: PitchFlowEvent,
  evaluation: ScreenDeterminismEvaluation
): PitchFlowTransitionResult {
  if (event === "reset") {
    return {
      previous: current,
      event,
      next: "draft",
      lockedReason: null
    };
  }

  if (current === "approved" || current === "rejected") {
    return {
      previous: current,
      event,
      next: current,
      lockedReason: "terminal-state-locked"
    };
  }

  if (event === "run-screen05") {
    return {
      previous: current,
      event,
      next: "screen05-assessed",
      lockedReason: null
    };
  }

  if (event === "run-screen06") {
    if (evaluation.screen05.decision !== "advance") {
      return {
        previous: current,
        event,
        next: "screen05-assessed",
        lockedReason: "screen05-not-advanced"
      };
    }

    return {
      previous: current,
      event,
      next: "screen06-assessed",
      lockedReason: null
    };
  }

  if (event === "approve") {
    if (evaluation.screen05.decision !== "advance" || evaluation.screen06.band !== "ready") {
      return {
        previous: current,
        event,
        next: "screen06-assessed",
        lockedReason: "approval-gates-not-satisfied"
      };
    }

    return {
      previous: current,
      event,
      next: "approved",
      lockedReason: null
    };
  }

  if (event === "reject") {
    return {
      previous: current,
      event,
      next: "rejected",
      lockedReason: null
    };
  }

  return {
    previous: current,
    event,
    next: current,
    lockedReason: "unknown-event"
  };
}

export function normalizeScreenInput(
  input: ScreenDeterminismInput
): ScreenDeterminismInput {
  return {
    industrialReliability: clamp(round(input.industrialReliability), 0, 100),
    softwareCompleteness: clamp(round(input.softwareCompleteness), 0, 100),
    tractionStrength: clamp(round(input.tractionStrength), 0, 100),
    compliancePosture: clamp(round(input.compliancePosture), 0, 100),
    cashRunwayMonths: clamp(round(input.cashRunwayMonths), 0, 36),
    unresolvedCriticalIssues: clamp(round(input.unresolvedCriticalIssues), 0, 20)
  };
}

export function evaluateNormalized(
  input: ScreenDeterminismInput
): ScreenDeterminismEvaluation {
  return deriveScreenDeterminismEvaluation(normalizeScreenInput(input));
}

