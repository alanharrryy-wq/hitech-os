# One-Button v1.2 Session Zip Contract

## Document Status
- Status: Frozen
- Version: v1.2
- Scope: Canonical session bundle structure

## 1. Purpose
The session zip is the canonical export boundary between the local execution framework and later conversational orchestration. The zip must be deterministic, auditable, and structurally valid. This document defines the **minimum required contents** for v1.2 and explicitly distinguishes required, conditionally required, and optional artifacts.

## 2. Canonical output location
Canonical zip path:
`F:\repos\hitech-os\tools\orchestrator_factory\ops\projects\<project_id>\bundles\sessions\<session_id>.zip`

The implementation may also emit sidecars and a handoff copy, but the canonical contract is the zip itself.

## 3. Required artifacts
The following files are **always required** in every valid v1.2 session zip:

```text
session/session_manifest.json
session/session_summary.md
session/operator_instructions.md
session/intake_normalized.md
session/session_file_index.json
project/project_manifest.json
run/run_manifest.json
round/round_manifest.json
round/coordination/snapshots/coordination_snapshot.latest.json
round/coordination/snapshots/coordination_snapshot.latest.md
round/reports/readiness_report.json
round/reports/acceptance_report.json
```

If any required artifact is missing, the zip is invalid.

## 4. Conditionally required artifacts
The following artifacts become required **only when the runtime reports successful generation** of their corresponding outputs:

```text
round/packets/<package_id>/work_packet.json
round/prompts/<package_id>.prompt.md
round/prompts/mission-control.prompt.md
```

### Interpretation
- If packet generation runs successfully and produces N packages, then all N package work packet files are required.
- If prompt packet generation runs successfully, the corresponding prompt seeds are required.
- If packet or prompt generation is skipped legitimately due to runtime state, their absence should not invalidate the zip, but the reason should be visible in `session_manifest.issues[]`.

## 5. Explicitly not required in v1.2
The following artifact is intentionally **not required** in v1.2:
- `dispatch_plan.json`

Rationale:
- the current runtime contract does not require a dedicated dispatch plan artifact,
- forcing it would create false failures or placeholder artifacts without operational value,
- the coordination snapshot pair already provides minimum coordination state for v1.2.

## 6. Required content semantics
### session/session_summary.md
Human-readable summary of:
- lane,
- policy,
- project/run/round,
- whether the session is new or reused,
- main outputs and next operator action.

### session/operator_instructions.md
Must explain, at minimum:
- where the canonical zip lives,
- whether a handoff copy was created,
- what the operator should do next,
- which warnings or blockers matter.

### session/intake_normalized.md
Must persist the normalized human intent and normalized startup inputs. For `new_project`, this file is mandatory evidence that intake was normalized before state creation.

### session/session_file_index.json
Must include one entry per file exported into the zip, each entry containing:
- `path`
- `sha256`
- `size_bytes`

The file index is a bundle-level integrity ledger, not a replacement for the manifest.

### round/reports/acceptance_report.json
Must always exist. When no bundles were present at export time, this file must be a schema-valid stub aligned to `acceptance_result.schema.json`.

## 7. Recommended optional artifacts
These artifacts may be added without breaking the contract:
- metrics snapshots,
- observability summaries,
- waiver reports,
- export diagnostics,
- compatibility notes,
- additional coordination state.

Optional artifacts must not be relied upon by v1.2 consumers.

## 8. session_file_index.json norms
### Required shape
```json
[
  {
    "path": "session/session_manifest.json",
    "sha256": "sha256...",
    "size_bytes": 1234
  }
]
```

### Rules
- `path` is the relative path inside the zip
- `sha256` is computed over file bytes
- `size_bytes` is the uncompressed file size
- all files in the zip must appear exactly once in the index

## 9. Validation behavior
A `validate_session_zip_contract.py` guardrail must validate:
1. presence of required artifacts,
2. validity of required JSON files where schemas are available,
3. completeness and internal consistency of `session_file_index.json`,
4. that conditionally required artifacts are present when generation success is declared.

Warnings that do not invalidate the contract should be surfaced in `session_manifest.issues[]`.

## 10. Packaging rules
- Paths must use forward-slash semantics inside the zip.
- The implementation may generate files in temporary workspace locations before packing, but the zip must match the canonical relative paths defined here.
- The zip should be reproducible enough for stable debugging, though byte-for-byte deterministic archives are not mandatory for v1.2.

## 11. Contract evolution
Any addition of new required artifacts after v1.2 constitutes a contract change. Optional additions do not.
