# Orchestration Documentation Index

This folder is the canonical documentary layer for the `control_tower` phase.

## Reading order

1. `01_AUTHORITY_AND_USAGE.md`
2. `02_CONTROL_TOWER_SCOPE.md`
3. `03_SHARED_DICTIONARY.md`
4. `04_REPO_PLACEMENT_STRUCTURE.md`
5. `05_BOUNDARIES.md`
6. `06_OWNERSHIP_MAP.md`
7. `07_RULES_AND_RESTRICTIONS.md`
8. `08_PROMOTION_RULES.md`
9. `09_ARTIFACT_REGISTRY.md`
10. `10_STATUS_SNAPSHOT.md`
11. `11_ASSURANCE_MODEL.md`
12. `12_CHAT_SPLIT_AND_FILE_ALLOCATION.md`
13. `13_PATH_AUTHORITY_MATRIX.md`
14. `14_CHANGE_CONTROL_AND_DECISION_POLICY.md`

## Why this order exists

The order goes from:
- authority
- scope
- vocabulary
- physical placement
- boundaries
- ownership
- restrictions
- gates
- registry
- status
- assurance
- chat split
- path authority
- change control

That sequence is deliberate.
It prevents implementation from outrunning governance.

## Main principle

`control_tower` is a governance layer above the stabilized system.
It is not another operational guardian and it is not a license to rewire already-closed domains.
