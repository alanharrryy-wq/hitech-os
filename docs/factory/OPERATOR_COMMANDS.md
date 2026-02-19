# Operator Commands

Use the operator orchestrator through the package entrypoint:

```powershell
python -m tools.codex.factory operator --help
```

## Bootstrap

Bootstraps a deterministic run using:
`preflight -> init-run -> worktrees create -> bundle-init -> worktrees verify -> prompt generation`

When shared bridge is enabled (`HITECH_SHARED_MODE=consume|both`), bootstrap also runs an optional pre-run shared consume hook into `tools/codex/runs/<RUN_ID>/incoming_shared/`.

```powershell
python -m tools.codex.factory operator bootstrap --base-ref HEAD
```

Dry-run bootstrap plan (no git/worktree mutations):

```powershell
python -m tools.codex.factory operator bootstrap --base-ref HEAD --dry-run
```

Optional explicit run id (strict collision mode blocks immediately if occupied):

```powershell
python -m tools.codex.factory operator bootstrap --run-id RUN_PHASE1_EXTRACT_001 --strict-run-id --base-ref HEAD
```

If `--run-id` is omitted or set to `auto`, the operator deterministically selects the next free ID:
`RUN_PHASE1_EXTRACT_001`, `_002`, `_003`, ...

## Watch

Watches worker completion files and then runs:
`bundle-validate -> integrate`

When shared bridge is enabled (`HITECH_SHARED_MODE=publish|both`), watch also runs an optional post-run shared publish hook.

```powershell
python -m tools.codex.factory operator watch --run-id RUN_PHASE1_EXTRACT_001 --base-ref HEAD
```

Custom poll cadence:

```powershell
python -m tools.codex.factory operator watch --run-id RUN_PHASE1_EXTRACT_001 --sleep-sec 5 --timeout-min 120
```

## Phase 1 Extract (One Command)

Runs the full operator sequence for phase1 extraction:
`bootstrap -> worker watch -> bundle-validate -> integrate`

```powershell
python -m tools.codex.factory operator phase1-extract --base-ref HEAD
```

Deterministic dry-run plan:

```powershell
python -m tools.codex.factory operator phase1-extract --base-ref HEAD --dry-run
```

Defaults in `phase1-extract`:
- Opens worker worktrees in new VS Code windows with `PROMPT_WORKER.txt`.
- Opens `RUNBOARD.md`.
- Watches worker `STATUS.json` completion.
- Runs `bundle-validate` and `integrate`.
- Opens `FINAL_REPORT.txt` and reveals the run folder in Explorer.

Every operator payload now includes:
- `stage_last_completed`
- `stage_failed`
- `resume_hint`

On `BLOCKED`/`FAIL`, operator prints:
- `[operator] status=... stage_failed=... reason="..."`

## Worker Prompt Flow

Generated prompt artifacts:

- `tools/codex/prompts/<RUN_ID>/PROMPT_A_worker.txt`
- `tools/codex/prompts/<RUN_ID>/PROMPT_B_worker.txt`
- `tools/codex/prompts/<RUN_ID>/PROMPT_C_worker.txt`
- `tools/codex/prompts/<RUN_ID>/PROMPT_D_worker.txt`
- `tools/codex/prompts/<RUN_ID>/RUNBOARD.md`
- `tools/codex/worktrees/<RUN_ID>/<WORKER>/PROMPT_WORKER.txt`

Required manual action in each worker VS Code window:

- `Ctrl+Alt+P -> New Codex Agent -> paste PROMPT_WORKER.txt`
