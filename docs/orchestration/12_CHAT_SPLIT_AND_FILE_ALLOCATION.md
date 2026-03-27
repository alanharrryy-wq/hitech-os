# Chat Split and File Allocation

This document freezes the non-overlapping split between the two future implementation chats.

## Split objective

Enable parallel work without:
- file collisions
- ownership ambiguity
- semantic drift
- accidental authority widening

## Chat A mission

Chat A builds the normative/write-side governance core.

### Chat A target files
- `F:\repos\hitech-os\control_tower\__init__.py`
- `F:\repos\hitech-os\control_tower\boundaries.py`
- `F:\repos\hitech-os\control_tower\ownership.py`
- `F:\repos\hitech-os\control_tower\contracts.py`
- `F:\repos\hitech-os\control_tower\dependency_graph.py`
- `F:\repos\hitech-os\control_tower\promotion_gate.py`
- `F:\repos\hitech-os\control_tower\work_orders.py`

### Chat A documentary authority
- boundaries
- ownership
- rules/restrictions
- promotion rules

## Chat B mission

Chat B builds the read-side state, registry, snapshot, and audit layer.

### Chat B target files
- `F:\repos\hitech-os\control_tower\state_model.py`
- `F:\repos\hitech-os\control_tower\artifact_registry.py`
- `F:\repos\hitech-os\control_tower\snapshot.py`
- `F:\repos\hitech-os\control_tower\audit_log.py`
- `F:\repos\hitech-os\control_tower\cli.py`
- `F:\repos\hitech-os\control_tower\readers\__init__.py`
- `F:\repos\hitech-os\control_tower\readers\engine_guardian_reader.py`
- `F:\repos\hitech-os\control_tower\readers\gsm_reader.py`

### Chat B documentary authority
- artifact registry
- status snapshot
- assurance model

## Shared documentary binders

Both chats are bound by:
- authority and usage
- scope
- shared dictionary
- placement structure
- this split document
- path authority matrix
- change control policy

## Hard non-overlap rule

No target file may be:
- created by both chats
- revised by both chats
- semantically redefined by the non-owner chat

## Dependency rule

Chat B must not hard-depend physically on Chat A files being present.
Chat A and Chat B should align by shared vocabulary and documentary contract, not by premature cross-imports.

## Collision examples

Violations include:
- Chat A shipping `state_model.py`
- Chat B redefining promotion gates
- Chat B inserting boundary doctrine into reader modules as if it were code authority
- Chat A creating audit registry code

## Merge readiness condition

Parallel bundles are merge-ready only when:
- file sets are disjoint
- dictionary usage matches
- no protected domain authority was widened
- docs remain aligned with the canonical orchestration baseline
