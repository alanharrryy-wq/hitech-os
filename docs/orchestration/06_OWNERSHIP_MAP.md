# Ownership Map

This document defines who owns what in the stabilized system and during the first `control_tower` phase.

## Ownership doctrine

Ownership means authority to define, mutate, and be held responsible for a target object, path, or capability.
Observation is not ownership.
Documentation is not ownership transfer.
Wrapping is not ownership transfer.

## Ownership table by domain

### `git_sentinel_modular`

**Owned**
- `F:\repos\hitech-os\tools\hos\git_sentinel_modular\**`
- package-internal CLI behavior
- package-internal docs/tests/plugins
- package-internal rollout logic

**Read-only to others**
- its observable status
- its artifact evidence
- its declared lifecycle state

**Forbidden to others by default**
- broad internal rewrites
- ownership appropriation by guardian or `control_tower`

### `engine_guardian`

**Owned**
- `F:\repos\hitech-os\engine_guardian\**`
- `F:\OneDrive\Descargas\engine_guardian\**`
- official scheduler tasks:
  - `HITECH-EngineGuardian-Boot`
  - `HITECH-EngineGuardian-Pulse`
- guardian activation/install/report outputs
- guardian runtime folders:
  - `state`
  - `locks`
  - `logs`
  - `reports`
  - `snapshots`
  - `backups`
  - `install`
- guardian relationship with `igniters`
- guardian wrapper responsibility over public engine health model

**Read-only to `control_tower`**
- lifecycle state
- runtime evidence
- reports
- install artifacts
- snapshot inputs

**Forbidden to `control_tower`**
- runtime mutation
- scheduler mutation
- service control
- Cloudflare remediation
- endpoint healing

### `repo_analizer`

**Owned**
- `F:\repos\hitech-os\tools\graphviz\repo_analizer\**`

**Relationship**
- sibling domain
- may be wrapped by guardian
- not absorbed by `control_tower`

### `control_tower`

**Owned**
- `F:\repos\hitech-os\control_tower\**`
- `F:\repos\hitech-os\docs\orchestration\**` for orchestration docs
- governance definitions
- ownership mapping definitions
- promotion gate definitions
- artifact and snapshot contracts
- assurance model definitions

**Not owned**
- guardian scheduler tasks
- guardian runtime mutation
- sentinel internals
- legacy protected systems
- Cloudflare operational ownership

## Ownership split by chat

### Chat A owns
Target files:
- `control_tower\__init__.py`
- `control_tower\boundaries.py`
- `control_tower\ownership.py`
- `control_tower\contracts.py`
- `control_tower\dependency_graph.py`
- `control_tower\promotion_gate.py`
- `control_tower\work_orders.py`

Document authority:
- `BOUNDARIES`
- `OWNERSHIP_MAP`
- `RULES_AND_RESTRICTIONS`
- `PROMOTION_RULES`

### Chat B owns
Target files:
- `control_tower\state_model.py`
- `control_tower\artifact_registry.py`
- `control_tower\snapshot.py`
- `control_tower\audit_log.py`
- `control_tower\cli.py`
- `control_tower\readers\__init__.py`
- `control_tower\readers\engine_guardian_reader.py`
- `control_tower\readers\gsm_reader.py`

Document authority:
- `ARTIFACT_REGISTRY`
- `STATUS_SNAPSHOT`
- `ASSURANCE_MODEL`

### Shared documentary authority
Both chats are bound by:
- `AUTHORITY_AND_USAGE`
- `CONTROL_TOWER_SCOPE`
- `SHARED_DICTIONARY`
- `REPO_PLACEMENT_STRUCTURE`
- `CHAT_SPLIT_AND_FILE_ALLOCATION`
- `PATH_AUTHORITY_MATRIX`
- `CHANGE_CONTROL_AND_DECISION_POLICY`

## Ownership transfer rule

Ownership does not move because:
- a chat can technically generate code
- a module reads another domain
- a future bundle wants convenience
- a runtime path contains useful evidence

Ownership changes require:
- explicit documentary revision
- impact review
- cross-chat compatibility review
- confirmation that operational closed phases stay closed
