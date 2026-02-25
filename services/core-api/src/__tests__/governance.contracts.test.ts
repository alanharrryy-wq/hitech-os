import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  GOVERNANCE_STAGE_ID_S1,
  GOVERNANCE_STAGE_S1_REQUIREMENT_IDS,
  GOVERNANCE_SUPPORTED_STAGE_IDS,
  createGovernanceStageSnapshot,
  isSafeRunId,
  sortDeterministicRunIds,
  sortIssuesDeterministically
} from "../contracts/governance.ts";
import {
  GOVERNANCE_RUN_ID_FIXTURE,
  GOVERNANCE_RUN_ID_FIXTURE_REVERSED
} from "./fixtures/governanceRunIds.fixture.ts";

describe("governance contracts", () => {
  it("returns deterministic S1 stage snapshot with expected requirement IDs", () => {
    const snapshot = createGovernanceStageSnapshot("S1");
    assert.ok(snapshot);
    assert.equal(snapshot?.stageId, GOVERNANCE_STAGE_ID_S1);
    assert.equal(snapshot?.deterministic, true);
    assert.equal(snapshot?.offlineFirst, true);
    assert.equal(snapshot?.featureFlagsDefaultOff, true);
    assert.deepEqual(snapshot?.requirementIds, [...GOVERNANCE_STAGE_S1_REQUIREMENT_IDS]);
    assert.deepEqual(GOVERNANCE_SUPPORTED_STAGE_IDS, [GOVERNANCE_STAGE_ID_S1]);
    assert.equal(snapshot?.requirements.length, GOVERNANCE_STAGE_S1_REQUIREMENT_IDS.length);
  });

  it("returns null for unsupported governance stage", () => {
    assert.equal(createGovernanceStageSnapshot("S2"), null);
    assert.equal(createGovernanceStageSnapshot(""), null);
  });

  it("sorts large run-id fixture deterministically regardless of input ordering", () => {
    const sortedFromForward = sortDeterministicRunIds(GOVERNANCE_RUN_ID_FIXTURE);
    const sortedFromReversed = sortDeterministicRunIds(GOVERNANCE_RUN_ID_FIXTURE_REVERSED);
    assert.deepEqual(sortedFromForward, sortedFromReversed);
    assert.equal(sortedFromForward.length, GOVERNANCE_RUN_ID_FIXTURE.length);
    assert.equal(
      sortedFromForward[0],
      [...sortedFromForward].sort((left, right) => left.localeCompare(right))[0]
    );
    assert.equal(
      sortedFromForward[sortedFromForward.length - 1],
      [...sortedFromForward].sort((left, right) => left.localeCompare(right))[
        sortedFromForward.length - 1
      ]
    );
  });

  it("applies stable deterministic issue ordering", () => {
    const sorted = sortIssuesDeterministically([
      {
        code: "B",
        message: "z",
        severity: "warn",
        target: "x"
      },
      {
        code: "A",
        message: "z",
        severity: "warn",
        target: "x"
      },
      {
        code: "A",
        message: "a",
        severity: "info",
        target: "y"
      }
    ]);

    assert.deepEqual(
      sorted.map((issue) => `${issue.code}:${issue.target}:${issue.message}`),
      ["A:x:z", "A:y:a", "B:x:z"]
    );
  });

  it("enforces safe run-id pattern constraints", () => {
    assert.equal(isSafeRunId("factory_20260224_120000_abcdef12_001"), true);
    assert.equal(isSafeRunId("RUN_PHASE1_EXTRACT_004"), true);
    assert.equal(isSafeRunId(""), false);
    assert.equal(isSafeRunId("../escape"), false);
    assert.equal(isSafeRunId("a/b"), false);
    assert.equal(isSafeRunId("x".repeat(200)), false);
    assert.equal(isSafeRunId("contains space"), false);
  });
});
