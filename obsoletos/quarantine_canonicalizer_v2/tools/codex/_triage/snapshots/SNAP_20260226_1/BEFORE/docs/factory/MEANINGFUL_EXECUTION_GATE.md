# Meaningful Execution Gate v1

## Goal

Prevent false-positive `PASS` outcomes where integration artifacts exist but no meaningful repository mutation happened.

`PASS` now means:

- real repository mutation exists and is consistent with declarations, or
- explicit `noop: true` is declared with `noop_reason` and `noop_ack`.

## Inputs

- `tools/codex/runs/<RUN_ID>/Z_integrator/FILES_CHANGED.json`
- `tools/codex/runs/<RUN_ID>/Z_integrator/DIFF.patch`
- `tools/codex/runs/<RUN_ID>/RUN_MANIFEST.json` (for `base_ref`, optional fallback to `HEAD`)
- git mutation signals from:
  - `git diff --name-status <base>..HEAD`
  - `git status --porcelain=v1 --untracked-files=all`

## Outputs

- `tools/codex/runs/<RUN_ID>/VERIFY_MEANINGFUL_GATE.json`
- `tools/codex/runs/<RUN_ID>/VERIFY_MEANINGFUL_GATE.md`

JSON report fields:

- `verdict`: `PASS|FAIL|BLOCKED|WARN`
- `fail_modes`: explicit list of failures
- `stats`: `changed_files_count`, `diff_bytes`, `declared_paths_count`, `git_paths_count`
- `samples`: up to 10 representative paths

## Checks (v1)

1. Non-empty semantics:

- Fail `EMPTY_DECLARATIONS` when `changes` is empty and explicit NOOP is not declared.
- Fail `EMPTY_PATCH` when `DIFF.patch` is empty and explicit NOOP is not declared.

2. Declared paths exist:

- For `added/modified/...`, declared file must exist after integration.
- For `deleted`, declared file must not exist.
- Mismatches fail with `PHANTOM_PATHS`.

3. Git mutation proof:

- Mutation set is derived from git diff range + worktree status.
- Empty mutation set without explicit NOOP fails with `NO_GIT_MUTATION`.
- Declared paths not present in mutation set fail with `DECLARATION_MISMATCH`.

4. Patch applicability:

- `git apply --check` (forward or reverse) validates patch applicability.
- Failure yields `PATCH_NOT_APPLICABLE`.

5. Consistency triangle:

- `FILES_CHANGED` paths, patch paths, and git mutation paths must agree on declared scope.
- Mismatches fail with `DECLARATION_MISMATCH`.

## NOOP Policy

- Allowed only when explicit:
  - `noop: true`
  - `noop_reason` non-empty
  - `noop_ack` non-empty
- Empty mutation without explicit NOOP is `FAIL`.
- Explicit NOOP can pass meaningful gate, but run summary must label it as NOOP and it must not count as phase progress.

## Integration Points

- Gate runs after integrator outputs are written.
- Integrator adds required check `meaningful_execution_gate`.
- Final integrator status is re-evaluated with gate verdict and fail modes.
- `watch` output reports meaningful gate verdict/fail modes/noop clearly.
