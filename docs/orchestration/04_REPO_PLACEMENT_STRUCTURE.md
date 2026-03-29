# Repo Placement Structure

This document fixes where the initial documentary layer should live.

## Canonical repo root

`F:\repos\hitech-os`

## Canonical documentary location

`F:\repos\hitech-os\docs\orchestration`

## Initial file structure

```text
F:\repos\hitech-os\docs\orchestration\
├─ 00_INDEX.md
├─ 01_AUTHORITY_AND_USAGE.md
├─ 02_CONTROL_TOWER_SCOPE.md
├─ 03_SHARED_DICTIONARY.md
├─ 04_REPO_PLACEMENT_STRUCTURE.md
├─ 05_BOUNDARIES.md
├─ 06_OWNERSHIP_MAP.md
├─ 07_RULES_AND_RESTRICTIONS.md
├─ 08_PROMOTION_RULES.md
├─ 09_ARTIFACT_REGISTRY.md
├─ 10_STATUS_SNAPSHOT.md
├─ 11_ASSURANCE_MODEL.md
├─ 12_CHAT_SPLIT_AND_FILE_ALLOCATION.md
├─ 13_PATH_AUTHORITY_MATRIX.md
└─ 14_CHANGE_CONTROL_AND_DECISION_POLICY.md
```

## Recommended future code structure

This code structure is documentary guidance, not yet code delivery:

```text
F:\repos\hitech-os\control_tower\
├─ __init__.py
├─ boundaries.py
├─ ownership.py
├─ contracts.py
├─ dependency_graph.py
├─ promotion_gate.py
├─ work_orders.py
├─ state_model.py
├─ artifact_registry.py
├─ snapshot.py
├─ audit_log.py
├─ cli.py
└─ readers\
   ├─ __init__.py
   ├─ engine_guardian_reader.py
   └─ gsm_reader.py
```

## Placement principle

Documentation comes first.
Code must later conform to these documents, not the other way around.

## Stability rule

Once these docs are placed under `docs\orchestration`, future implementations must reference them rather than creating duplicate boundary docs elsewhere.

## No-shadow-docs rule

Avoid parallel files such as:
- `docs\controltower\boundaries.md`
- `control_tower\README_boundaries.md`
- `notes\ownership_draft.md`

Those become ambiguity factories.
The canonical documentary home is `docs\orchestration`.

## Support files

If external support files are kept, they should live outside this canonical folder or be clearly labeled as generated support, not canonical source.
