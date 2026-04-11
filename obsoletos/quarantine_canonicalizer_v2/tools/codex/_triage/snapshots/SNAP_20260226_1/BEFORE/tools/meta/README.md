# HITECH Meta-Gov Tooling

## Purpose

`tools/meta` provides deterministic federation orchestration for Level 2 meta-governance across multiple repositories.

## Scope

This tooling:

- Reads per-repo governance report state from `docs/govos/_reports/FINAL_REPORT.md`
- Optionally runs each repo's `Docs-Doctor.ps1 --check` when reports are missing
- Aggregates blockers and debt into federation-level outputs
- Writes deterministic artifacts to `docs/meta-gov/`

This tooling does not:

- Modify product/runtime code
- Force convergence actions by default
- Perform mass file moves

## Entry Point

Primary CLI:
`python -m tools.meta.meta_orchestrator`

Wrapper:
`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/meta/wrappers/Run-MetaGov.ps1`

## CLI Flags

- `--registry <path>`
- `--repo-root <path>`
- `--run-id <id>`
- `--write`
- `--open`
- `--strict`
- `--no-run-docs-doctor`

## Determinism Rules

- Repo list is sorted by repo name.
- Blockers are sorted by `(repo, category, message)`.
- Debt IDs are deterministic SHA256 over `repo_name + normalized_line`.
- JSON outputs use sorted keys.
- Markdown report sections use fixed ordering.

## Federation Law (Level 2)

1. If any ONLINE repo has constitutional blockers, federation status is `BLOCKED`.
2. Else if strict mode is on and any repo is OFFLINE, federation status is `DEGRADED`.
3. Else if any repo is DEGRADED or MISSING_TOOLING, federation status is `DEGRADED`.
4. Else federation status is `OK`.

OFFLINE repos do not block by default.

## Output Files

The orchestrator writes:

- `docs/meta-gov/FEDERATION_STATUS.json`
- `docs/meta-gov/GLOBAL_DEBT_LOG.json`
- `docs/meta-gov/META_REPORT.md`
- `docs/meta-gov/LATEST_RUN.txt`
- `docs/meta-gov/LATEST/*`
- `docs/meta-gov/_runs/<RUN_ID>/*`

## Registry

Default registry path:
`docs/meta-gov/REPO_REGISTRY.yaml`

Default repos:

- hitech-os
- inversion-next
- hitech-frontend

## Error Semantics

- `0`: run completed with federation status `OK` or `DEGRADED`
- `2`: run completed with federation status `BLOCKED`
- `1`: execution failure

## Progress Visibility

The orchestrator prints deterministic step progress:
`[step/total] percent% message`

The PowerShell wrapper prints `Write-Progress` stages.

## Minimal Example

```powershell
python -m tools.meta.meta_orchestrator --registry docs/meta-gov/REPO_REGISTRY.yaml --write
```

```powershell
python -m tools.meta.meta_orchestrator --registry docs/meta-gov/REPO_REGISTRY.yaml --write --open
```

## Testing

Run deterministic tests:

```powershell
python -m tools.meta.tests.test_meta_orchestrator
```

## Governance Notes

- Feature flags remain OFF by default.
- No forced repo changes are applied.
- Orchestrator reads reports and writes only meta-governance artifacts.

## Module Map

- `constants.py`: constants and defaults
- `pathing.py`: repo root detection and time helpers
- `hashing.py`: deterministic hashing and canonical JSON helpers
- `registry.py`: deterministic minimal registry parser
- `report_parser.py`: FINAL_REPORT parsing and blocker extraction
- `debt_parser.py`: debt extraction and stable debt IDs
- `federation.py`: repo evaluation and federation law evaluation
- `report_writer.py`: deterministic META_REPORT renderer
- `meta_orchestrator.py`: CLI entry point

## Safety

- No deletions.
- No product/runtime code changes.
- No cross-universe document merges.
- No randomization in outputs.
