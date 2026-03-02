import { describe, expect, it } from "vitest";
import { SCREEN_TRANSITION_CASES } from "./_utils/screen-transition-cases.generated";
import {
  deriveScreenDeterminismEvaluation,
  evaluateNormalized,
  normalizeScreenInput,
  transitionPitchFlow,
  type ScreenDeterminismEvaluation,
  type ScreenDeterminismInput
} from "./_utils/screen-transition-determinism";

function assertStableTransitions(
  evaluation: ScreenDeterminismEvaluation,
  expected: (typeof SCREEN_TRANSITION_CASES)[number]["expectedTransitions"]
): void {
  const runScreen05 = transitionPitchFlow("draft", "run-screen05", evaluation);
  expect(runScreen05.next).toBe(expected.draftRunScreen05);
  expect(runScreen05.lockedReason).toBeNull();

  const runScreen06 = transitionPitchFlow("draft", "run-screen06", evaluation);
  expect(runScreen06.next).toBe(expected.draftRunScreen06);
  expect(runScreen06.lockedReason).toBe(expected.runScreen06Lock);

  const approve = transitionPitchFlow("screen06-assessed", "approve", evaluation);
  expect(approve.next).toBe(expected.approvalState);
  expect(approve.lockedReason).toBe(expected.approvalLock);

  const reject = transitionPitchFlow("screen06-assessed", "reject", evaluation);
  expect(reject.next).toBe(expected.rejectionState);
  expect(reject.lockedReason).toBeNull();

  const reset = transitionPitchFlow("screen06-assessed", "reset", evaluation);
  expect(reset.next).toBe(expected.resetState);
  expect(reset.lockedReason).toBeNull();
}

describe("screen 05/06 determinism matrix", () => {
  it("keeps large deterministic case matrix shape stable", () => {
    expect(SCREEN_TRANSITION_CASES.length).toBeGreaterThanOrEqual(625);

    const ids = new Set<string>();
    for (const testCase of SCREEN_TRANSITION_CASES) {
      expect(ids.has(testCase.id)).toBe(false);
      ids.add(testCase.id);

      expect(testCase.id.startsWith("case_")).toBe(true);
      expect(["hold", "advance"]).toContain(testCase.expected.screen05.decision);
      expect(["ready", "watch", "blocked"]).toContain(testCase.expected.screen06.band);
    }
  });

  it("returns deterministic evaluation for every generated case", () => {
    for (const testCase of SCREEN_TRANSITION_CASES) {
      const normalizedInput = normalizeScreenInput(testCase.input);
      const first = deriveScreenDeterminismEvaluation(normalizedInput);
      const second = deriveScreenDeterminismEvaluation(normalizedInput);
      const third = evaluateNormalized(testCase.input);

      expect(first).toEqual(second);
      expect(first).toEqual(third);
      expect(first).toEqual(testCase.expected);

      assertStableTransitions(first, testCase.expectedTransitions);
    }
  });

  it("stays deterministic regardless of Date.now values", () => {
    const originalNow = Date.now;
    let tick = 0;
    Date.now = () => {
      tick += 137;
      return tick;
    };

    try {
      for (let index = 0; index < SCREEN_TRANSITION_CASES.length; index += 5) {
        const testCase = SCREEN_TRANSITION_CASES[index];
        if (!testCase) {
          continue;
        }

        const a = evaluateNormalized(testCase.input);
        const b = evaluateNormalized(testCase.input);
        const c = evaluateNormalized(testCase.input);

        expect(a).toEqual(b);
        expect(b).toEqual(c);
      }
    } finally {
      Date.now = originalNow;
    }
  });

  it("supports an explicit approval path when gates are fully satisfied", () => {
    const readyInput: ScreenDeterminismInput = {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    };

    const evaluation = evaluateNormalized(readyInput);
    expect(evaluation.screen05.decision).toBe("advance");
    expect(evaluation.screen05.reasons).toEqual([]);
    expect(evaluation.screen06.band).toBe("ready");
    expect(evaluation.screen06.reasons).toEqual([]);

    const runScreen06 = transitionPitchFlow("draft", "run-screen06", evaluation);
    expect(runScreen06.next).toBe("screen06-assessed");
    expect(runScreen06.lockedReason).toBeNull();

    const approve = transitionPitchFlow("screen06-assessed", "approve", evaluation);
    expect(approve.next).toBe("approved");
    expect(approve.lockedReason).toBeNull();

    const rejectAfterApprove = transitionPitchFlow("approved", "reject", evaluation);
    expect(rejectAfterApprove.next).toBe("approved");
    expect(rejectAfterApprove.lockedReason).toBe("terminal-state-locked");
  });

  it("normalizes and clamps out-of-range input values", () => {
    const normalized = normalizeScreenInput({
      industrialReliability: -20,
      softwareCompleteness: 140.8,
      tractionStrength: -1,
      compliancePosture: 102.2,
      cashRunwayMonths: 72.7,
      unresolvedCriticalIssues: -9.3
    });

    expect(normalized).toEqual({
      industrialReliability: 0,
      softwareCompleteness: 100,
      tractionStrength: 0,
      compliancePosture: 100,
      cashRunwayMonths: 36,
      unresolvedCriticalIssues: 0
    });
  });
});
