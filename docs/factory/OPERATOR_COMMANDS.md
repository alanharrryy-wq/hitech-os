# Operator Commands

Use the operator orchestrator through the package entrypoint:

```powershell
python -m tools.codex.factory operator --help
```

## Bootstrap

Bootstraps a deterministic run using:
`preflight -> init-run -> worktrees create -> bundle-init -> worktrees verify -> prompt generation`

```powershell
python -m tools.codex.factory operator bootstrap --run-id RUN_PHASE1_EXTRACT_001 --base-ref HEAD
```

Dry-run bootstrap plan (no git/worktree mutations):

```powershell
python -m tools.codex.factory operator bootstrap --run-id RUN_PHASE1_EXTRACT_001 --base-ref HEAD --dry-run
```

## Watch

Watches worker completion files and then runs:
`bundle-validate -> integrate`

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
python -m tools.codex.factory operator phase1-extract --run-id RUN_PHASE1_EXTRACT_001 --base-ref HEAD
```

Deterministic dry-run plan:

```powershell
python -m tools.codex.factory operator phase1-extract --run-id RUN_PHASE1_EXTRACT_001 --base-ref HEAD --dry-run
```

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
