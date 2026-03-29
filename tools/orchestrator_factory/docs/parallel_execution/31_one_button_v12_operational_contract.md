# One-Button v1.2 Operational Contract

## Document Status
- Status: Frozen
- Version: v1.2
- Applies to: `F:\repos\hitech-os\tools\orchestrator_factory`
- Scope: Headless one-button session launcher, no GUI plugin in this version
- Intent: Define the operator-facing contract and the minimum internal orchestration required to produce a canonical session bundle

## 1. Why this exists
The execution framework already contains multiple building blocks for validating contracts, checking readiness, generating packets, generating prompt packets, creating coordination state, and exporting artifacts. What is missing is a single operator-facing entrypoint that:
1. exposes a deterministic user experience,
2. separates `existing_project` and `new_project` from the first screen,
3. enforces explicit session policy,
4. prevents concurrent writes to the same project state,
5. records enough metadata to reuse identical sessions safely, and
6. emits a canonical zip that can be handed back into ChatGPT for prompt generation and downstream orchestration.

This document freezes the operator contract for One-Button v1.2 so implementation can proceed without renegotiating behavior later.

## 2. Non-negotiable design principles
1. **Single human entrypoint.** The human operator runs one wrapper only.
2. **No business logic in the wrapper.** PowerShell launches Python, propagates arguments, exits with Python's exit code.
3. **Two hard lanes.** `existing_project` and `new_project` never share ambiguous startup logic.
4. **Policy before mutation.** The launcher must know exactly whether it is resuming, opening a new round, or upgrading before touching state.
5. **Lock before mutation.** Concurrency protection is mandatory for the project scope.
6. **Idempotency before creation.** The launcher checks whether the requested session already exists before generating a new one.
7. **Canonical zip before handoff.** The canonical zip is the contract boundary between runtime state and conversational orchestration.
8. **No new dependencies.** Implementation must remain stdlib-only and additive to the existing architecture.
9. **Compatible integration.** Existing project structures and framework scripts must continue to work.

## 3. Public entrypoint
### Human wrapper
`F:\repos\hitech-os\tools\orchestrator_factory\tools\one_button.ps1`

Responsibilities:
- resolve repo-relative paths safely on Windows,
- invoke Python against `tools\execution_framework\one_button_session.py`,
- pass all user arguments through,
- write clear operator-facing console output,
- terminate with `exit $LASTEXITCODE`.

Non-responsibilities:
- no session policy decisions,
- no state mutation,
- no lock logic,
- no schema validation,
- no zip construction.

### Python entrypoint
`F:\repos\hitech-os\tools\orchestrator_factory\tools\execution_framework\one_button_session.py`

Responsibilities:
- argument parsing,
- interactive or non-interactive flow selection,
- lock lifecycle,
- idempotency resolution,
- project/run/round state resolution,
- readiness checks,
- export of canonical session zip,
- deterministic exit codes.

## 4. Supported modes
### Session lanes
- `existing_project`
- `new_project`

### Session policies
- `resume_latest_round`
- `open_new_round`
- `upgrade`

### Execution modes
- `--dry-run`
- `--non-interactive`
- `--retry`
- `--force-lock-steal` (only valid when lock is stale or stale-safe)

## 5. Operator UX
## 5.1 Startup screen
The launcher must present the lane choice first:

```text
Modo de sesión:
[1] existing_project
[2] new_project
[3] exit
```

No background auto-detection may skip this choice in interactive mode.

## 5.2 Existing project flow
1. Discover project inventory.
2. Display a deterministic list with:
   - `project_id`
   - `project_name`
   - last `run_id`
   - last `round_id`
   - summarized readiness state
3. Prompt for `project_id`.
4. Prompt for policy:
   - `resume_latest_round`
   - `open_new_round`
   - `upgrade`
5. Prompt for session intent:
   - optional for `resume_latest_round`
   - required for `open_new_round`
   - required for `upgrade`
6. Render a normalized summary.
7. Confirm before mutation.

## 5.3 New project flow
1. Prompt for:
   - `project_id`
   - `project_name`
   - `initiative_type`
   - `brief`
2. Normalize intake.
3. Ensure path policies are materialized and aligned.
4. Render a normalized summary.
5. Confirm before mutation.

## 5.4 Non-interactive mode
In `--non-interactive` mode, all required values must be provided by flags or config. Missing required values produce `invalid_arguments` exit behavior. Non-interactive mode must not fall back to hidden prompts.

## 6. Internal execution pipeline
The following sequence is mandatory for real execution. Dry-run may simulate writes but must still evaluate the same decision graph.

1. Parse arguments and load config.
2. Resolve lane and policy.
3. Normalize intent.
4. Resolve project target.
5. Acquire project lock.
6. Compute idempotency key using current or sentinel context hashes.
7. Consult session ledger for reuse candidates.
8. Run `validate_framework_contracts`.
9. Run `smoke_framework_checks`.
10. Run readiness stage 1 (install/bootstrap level).
11. Resolve or create project/run/round according to lane and policy.
12. For `new_project`, align `path_policies.json` or mark readiness as blocked.
13. Run readiness stage 2 (round-level readiness).
14. Generate work packets if supported by runtime state.
15. Generate prompt packets if supported by runtime state.
16. Initialize coordination plane if absent.
17. Build coordination snapshot.
18. Emit acceptance report; if no bundles exist, emit a schema-valid stub.
19. Construct `session_manifest.json`.
20. Construct `session_file_index.json`.
21. Validate session bundle contract.
22. Export canonical zip to canonical repo path.
23. Write sidecars (`.manifest.json`, `.sha256`) if enabled by implementation.
24. Copy zip to configurable handoff directory if enabled.
25. Append final record to ledger.
26. Release lock in `finally`.

## 7. Policy semantics
### resume_latest_round
- Never creates a new run.
- Never creates a new round.
- Reuses the latest round state and artifacts as far as allowed by idempotency.
- If an equivalent completed session exists, return `reused`.

### open_new_round
- Reuses the target run.
- Creates the next sequential round.
- Requires a non-empty normalized intent.
- Reuses previous context only by inheritance rules, not by mutating prior rounds.

### upgrade
- Creates a new sequential run.
- Starts a fresh round sequence at `round_001`.
- Requires a non-empty normalized intent.
- May reference prior run context, but must not masquerade as the same run lineage.

## 8. Canonical output paths
### Canonical zip path
`F:\repos\hitech-os\tools\orchestrator_factory\ops\projects\<project_id>\bundles\sessions\<session_id>.zip`

### Lock path
`F:\repos\hitech-os\tools\orchestrator_factory\ops\projects\<project_id>\state\locks\one_button.lock.json`

### Session ledger path
`F:\repos\hitech-os\tools\orchestrator_factory\ops\projects\<project_id>\state\sessions\session_ledger.jsonl`

### Handoff copy path
Configured via `configs\execution_framework\one_button_config.json`. Default may point to `F:\OneDrive\Descargas`, but the implementation must not hardcode the handoff destination in logic.

## 9. Mandatory runtime guarantees
1. Every successful or reused session has a `session_manifest.json`.
2. Every exported zip contains a `session_file_index.json`.
3. Every exported zip contains `acceptance_report.json`.
4. `dispatch_plan.json` is not required in v1.2.
5. Lock release occurs in `finally` even when export fails.
6. Reuse decisions are auditable via the session ledger.
7. Warnings and blockers are surfaced in `session_manifest.issues[]`.

## 10. Exit codes
- `0` ready or reused
- `10` blocked by lock
- `20` framework contracts failed
- `21` smoke checks failed
- `22` readiness stage install failed
- `23` readiness stage round failed
- `30` invalid arguments
- `31` invalid policy transition
- `40` session zip contract failed
- `50` unexpected runtime error

The PowerShell wrapper must not translate these codes.

## 11. Out of scope for v1.2
- GUI or plugin shell
- automatic cross-machine lock arbitration service
- prompt synthesis for the six human chat threads
- alternate artifact backends
- non-Windows operator shells as first-class entrypoints

## 12. Acceptance criteria for implementation
The implementation satisfies this contract when:
1. an operator can run one command only,
2. lane selection is deterministic,
3. each policy behaves as defined,
4. the lock prevents concurrent mutation on the same project,
5. an equivalent session is reused instead of duplicated,
6. the session zip validates against the contract schema, and
7. the resulting zip is ready to be handed into ChatGPT for downstream prompt generation.

## 13. Change control
Changes to this contract after implementation starts must be treated as versioned contract changes, not ad hoc edits. Any future change that alters lane semantics, policy semantics, required zip contents, or lock/idempotency rules should bump the contract version to avoid silent drift.
