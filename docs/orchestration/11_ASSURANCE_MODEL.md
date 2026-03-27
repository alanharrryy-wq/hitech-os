# Assurance Model

This document defines how assurance should be reasoned about in the first `control_tower` phase.

## Assurance meaning

Assurance is the disciplined claim that the system is consistent with its declared boundaries, states, evidence, and promotion requirements.

Assurance is not optimism.
Assurance is not operational control.
Assurance is not healing.

## Assurance questions

The initial assurance model should answer:

- Are closed fronts still preserved as closed?
- Are boundaries still intact?
- Is ownership still where it is supposed to be?
- Is the shared dictionary being preserved?
- Are documented artifacts and evidence discoverable?
- Is the snapshot coherent?
- Is any drift visible?
- Is any promotion candidate blocked by documentary or state mismatch?

## Assurance dimensions

### Boundary assurance
Checks that domains are not widening authority improperly.

### Ownership assurance
Checks that owned/read-only/forbidden distinctions remain intact.

### Artifact assurance
Checks that evidence and reports exist and are categorized coherently.

### Lifecycle assurance
Checks that claimed lifecycle states are compatible with evidence.

### Parallel-work assurance
Checks that Chat A and Chat B outputs do not overlap.

### Documentary assurance
Checks that canonical docs remain the baseline instead of being replaced with shadow docs.

## Verdict model

Use the canonical verdicts:

- `pass`
- `fail`
- `blocked`
- `not_applicable`

## Recommended judgment posture

When evidence is incomplete, prefer:
- `blocked`

When evidence contradicts a claimed safe state, prefer:
- `fail`

Do not inflate weak evidence into `pass`.

## Assurance inputs

Expected assurance inputs may include:

- orchestration docs
- manifests
- validation reports
- activation reports
- snapshots
- audit records
- protected evidence paths from guardian
- observable package state from sentinel

## Assurance outputs

Assurance outputs should be able to express:

- verdict
- rationale
- evidence references
- drift flags
- blocked prerequisites
- recommendation category

## Recommendation categories

Recommendations should remain non-invasive.
Examples:
- document correction needed
- promotion should be blocked
- evidence missing
- path ownership ambiguous
- lifecycle claim unsupported

Recommendations should not issue imperative runtime repair steps unless a future governance revision authorizes that.

## Non-invasive constraint

The assurance layer may observe, compare, and judge.
It may not:
- repair
- activate
- restart
- re-register
- change ownership
- mutate protected runtime state

## Trust model

Highest trust:
- direct runtime evidence from closed activation outputs
- explicit documentary authority
- verified manifests and reports

Lower trust:
- casual notes
- inferred status without evidence
- convenience assumptions in a future chat
