# 52_COMMIT_REVERT_DISCARD_FLOW

## Flow summary

The intended flow is:

1. surface action happens
2. mutation intent is built
3. shallow validation runs
4. policy classification runs
5. preview request is sent
6. preview session is updated
7. compare / diagnostics stay readable
8. user chooses commit, discard, or local revert
9. bridge receives the final governed transition

## Commit
Commit means the previewed work is now accepted relative to the authoring workflow.

## Discard
Discard means the active preview session is abandoned and draft/baseline clarity is restored.

## Revert
Revert means a narrower rollback plan is applied to a known scope.
This should stay narrower than full discard when possible.

## Required invariants
- commit never happens implicitly
- discard never corrupts baseline
- revert has explicit scope
- failures preserve diagnostics
- rejected commit cannot partially write unrelated state
