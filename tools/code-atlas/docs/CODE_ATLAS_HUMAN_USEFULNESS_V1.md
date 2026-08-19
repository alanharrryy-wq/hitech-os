# Code Atlas Human Usefulness Study V1

**Status:** `STUDY_KIT_PROTOCOL`  
**Classification:** `VERIFY / bounded external-human evidence`  
**Product maturity effect:** none until a real external human response is scored  
**Source mutation authority:** none  

## 1. Purpose

This protocol measures a narrow question that existing automated and agent evidence does not answer:

> For the same unfamiliar repository task, does an external technical reviewer make a more useful, better-supported change-readiness decision when Code Atlas evidence is available than when only repository-native evidence is available?

The protocol exists because the current Factory Ledger truth is explicit: human usefulness is `NOT_MEASURED`. Existing single-external-agent evidence is valuable but cannot substitute for a human reviewer.

This study kit does not rebuild Code Atlas. It reuses the already-pinned public-repository task corpus and evidence primitives from `.github/scripts/caext_usefulness_pilot_v1.py` without modifying that historical evaluator.

## 2. What V1 produces

`caext_human_usefulness_v1.py prepare` creates two physically separate outputs:

- `reviewer_bundle/`
  - 12 opaque packets: two variants for each of six pinned tasks;
  - a deterministic presentation order;
  - a response template;
  - reviewer instructions;
  - no condition label;
  - no future diff or ground truth.
- `sealed_scoring_bundle/`
  - packet-to-condition map;
  - historical ground truth;
  - digest bindings;
  - scoring manifest.

The reviewer receives only `reviewer_bundle/` until all packet responses are complete.

## 3. Task corpus

V1 reuses the six pinned tasks already present in the historical usefulness pilot:

1. FastAPI
2. chi
3. Django
4. aiohttp
5. Ruff
6. Pydantic

For every task, both study variants use the same repository, same parent snapshot, same task statement, same pre-authorized target, and same repository-native evidence.

The only intended treatment difference is the presence or absence of the existing Code Atlas assistance package.

## 4. Pairing and presentation

Each task has:

- one `BASELINE` variant;
- one `ASSISTED` variant.

Condition names are stored only in the sealed scoring bundle. Reviewer packets use opaque deterministic packet IDs.

Presentation uses two deterministic blocks. One variant of every task appears in the first block and its counterpart appears in the second block. Pair order is counterbalanced from an explicit seed. The protocol avoids adjacent pairs where possible.

This reduces, but does not eliminate, learning and carryover. Therefore every scored V1 result must retain:

- `orderEffectEliminated=false`;
- `singleReviewerGeneralizationAllowed=false`;
- `causalClaimAllowed=false`.

## 5. Reviewer identity and privacy

V1 requires a pseudonymous reviewer ID matching a small identifier alphabet. Email addresses are not accepted as reviewer IDs.

A scored external-human study requires the response file to declare:

- `reviewerType=EXTERNAL_HUMAN`;
- `independenceAttested=true`.

This is self-attestation, not independent identity verification. Score output must keep:

- `externalReviewerIdentityIndependentlyVerified=false`;
- `independenceEvidence=REVIEWER_SELF_ATTESTATION_ONLY`.

No credential, account login, or personal contact information is required by the protocol.

## 6. Reviewer response contract

For every opaque packet, the reviewer records:

- decision: `READY`, `BLOCKED`, or `UNKNOWN`;
- `editableScope`;
- `inspectValidateScope`;
- `testPathsToValidate`;
- material `unknowns`;
- `evidenceReferences` chosen from packet evidence IDs;
- optional `elapsedSeconds` with source `OBSERVED` or `SELF_REPORTED`.

If time is not measured, use `elapsedSource=NOT_MEASURED` and omit `elapsedSeconds`.

After all 12 packet responses are complete, the reviewer performs the pair debrief. For each task pair the reviewer may select an opaque preferred packet or `TIE`, record whether the difference was material, and choose bounded reason codes such as scope clarity, dependency context, test selection, evidence quality, unknown handling, decision confidence, or faster review.

## 7. Authorization semantics

The study preserves the existing safety contract:

- the evaluator-provided target is the only pre-authorized editable path;
- impact radius is inspection evidence, not edit authorization;
- dependency evidence may widen inspection, never edit authority;
- history is evidence, not authorization;
- unknown remains unknown when evidence is insufficient.

Authorization widening is scored as a negative outcome. A reviewer response that silently expands edit scope is not made green by usefulness ratings.

## 8. Ground-truth boundary

Reviewer packets must not contain:

- historical target commit;
- actual changed paths;
- actual companion paths;
- actual changed test paths;
- ground-truth digest;
- future diff.

The sealed bundle is not reviewer material. Looking at it, or at the future historical diff, before responses are complete invalidates the intended blind boundary.

The protocol cannot technically prevent a reviewer from searching public history. It therefore records this as a procedural study constraint rather than pretending technical isolation that does not exist.

## 9. Integrity and fail-closed behavior

Every reviewer packet has a deterministic digest. Every response repeats that packet digest. The sealed scoring manifest binds:

- reviewer manifest digest;
- study-map digest;
- all packet digests;
- all ground-truth digests.

Scoring fails closed when:

- a packet is missing or altered;
- a response is missing or duplicated;
- a response references the wrong packet digest;
- the case-pair set is incomplete;
- ground truth is altered;
- the reviewer ID is not pseudonymous;
- external-human / independence self-attestation is absent;
- elapsed-time fields contradict their measurement source;
- pair preferences reference packets outside the pair.

Raw submitted responses are copied byte-for-byte into the score output and bound by SHA-256 before derived scoring is emitted.

## 10. Objective scoring

Per packet, V1 measures:

- target included in editable scope;
- edit-scope widening;
- historical companion inspection recall/precision;
- historical changed-test selection recall/precision;
- evidence-reference validity;
- unknown count;
- assisted unknown omission;
- assisted fake green;
- elapsed time when measured.

Condition summaries aggregate the same six tasks under both conditions, rather than comparing different task sets.

The post-pair debrief additionally records which opaque packet the reviewer found more useful and whether the difference was material.

## 11. Human-usefulness state machine

Before a real human response exists:

`HUMAN_USEFULNESS_STUDY_KIT_READY_NOT_MEASURED`

After a complete, digest-valid response from one self-attested external human is scored:

`SINGLE_EXTERNAL_HUMAN_PAIRED_STUDY_MEASURED_NO_GENERALIZATION`

That state means exactly what it says. It does not mean broad usefulness is proven.

## 12. Claims V1 does not authorize

Neither a green workflow nor one scored reviewer authorizes claims of:

- causal uplift;
- general human usefulness;
- independent evaluator replication;
- automatic `PAID_PILOT_READY`;
- production readiness;
- enterprise readiness;
- legal or privacy compliance;
- security certification;
- hosted multi-tenant readiness;
- zero regressions;
- universal repository compatibility.

Those remain separate gates.

## 13. CI role

`.github/workflows/caext-human-usefulness-v1.yml` does only three things:

1. compile and self-test the protocol on Ubuntu and Windows;
2. enforce an exact three-file additive scope and protect Code Atlas core / PR #273 / historical usefulness evidence;
3. prepare the six paired tasks on Ubuntu, then upload reviewer and sealed scoring bundles as separate artifacts.

CI never fabricates a human response and never promotes `humanUsefulness` above `NOT_MEASURED`.

## 14. Operator flow for a real study

1. Generate the study kit from a pinned Code Atlas/repository state.
2. Give the reviewer only the reviewer artifact.
3. Keep the sealed scoring artifact inaccessible to the reviewer until all packet responses and pair comparisons are complete.
4. Collect the completed response JSON.
5. Run `score` with the original prepared root and completed response file.
6. Preserve the raw response file and the scored evidence together.
7. Record the result as bounded single-human evidence only.

A future multi-reviewer study should be a new protocol/version, not a silent reinterpretation of V1.

## 15. Anti-rework and protected lanes

This protocol must not modify or replace:

- Code Atlas core;
- PR #273 `ui_bridge/**` or `app_map/uimap/**`;
- the frozen independent-evaluator / PR #296 lane;
- PR #308 source work;
- P0 private-repository lifecycle/sanitization;
- PC, Tablet, Mobile, Chart Lab, Shared UI product/runtime surfaces;
- DB/Prisma;
- licensing;
- deploys, processes, or ports.

The historical external-agent usefulness pilot remains evidence and is reused read-only.
