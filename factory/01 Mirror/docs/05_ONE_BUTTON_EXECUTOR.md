# One-Button Executor

## Purpose

`tools/hos/launcher/hos_factory_one_button.ps1` runs a deterministic, non-interactive prompt-pack pipeline using the shared prompt-pack inbox:

`F:\repos\hitech-os\factory\shared\01 Prompt_Packs`

It preserves canonical factory contracts by executing dispatcher/runtime against canonical paths under:

- `tools/codex/runs/<RUN_ID>/...`
- `tools/codex/prompts/<RUN_ID>/...`

and exposing shared run folders through worker junctions.

## Shared Folders

Base:

- `F:\repos\hitech-os\factory\shared\01 Prompt_Packs`

Subfolders (auto-created if missing):

- `01 En_bruto`
- `02 Runs`
- `03 Archive`

Inbox rule:

- consumed file must be exactly: `01 En_bruto\PROMPTS_PACK_NEXT.txt`
- `PROMPTS_PACK_NEXT.tmp -> PROMPTS_PACK_NEXT.txt` is supported as atomic ready signaling.

## Run Layout

For each run:

- `02 Runs\<RUN_ID>\pack\raw_pack.txt`
- `02 Runs\<RUN_ID>\pack\materialized\` (precheck mirror)
- `02 Runs\<RUN_ID>\workers\A_core`
- `02 Runs\<RUN_ID>\workers\B_tooling`
- `02 Runs\<RUN_ID>\workers\C_features`
- `02 Runs\<RUN_ID>\workers\D_validation`
- `02 Runs\<RUN_ID>\workers\Z_aggregator`
- `02 Runs\<RUN_ID>\_debug\`

Worker paths above are NTFS junctions to canonical worker run folders:

- `tools/codex/runs/<RUN_ID>/<WORKER>`

## Commands

Standard run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/launcher/hos_factory_one_button.ps1
```

Dry preflight only:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/launcher/hos_factory_one_button.ps1 --dry-only
```

Resume an existing run id:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/launcher/hos_factory_one_button.ps1 --resume 20260228_215959_A1B2
```

Snapshot GC:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/launcher/hos_factory_one_button.ps1 --gc --keep-days 14 --keep-count 20
```

## Exit Codes

- `0`: success
- `2`: pipeline failure
- `3`: preflight failure

## Logs and Summary

Canonical logs:

- `tools/codex/runs/<RUN_ID>/_debug/`
- `tools/codex/prompts/<RUN_ID>/logs/`

Shared mirror:

- `02 Runs\<RUN_ID>\_debug\`

Executor artifacts:

- `tools/codex/runs/<RUN_ID>/STATUS.json`
- `tools/codex/runs/<RUN_ID>/TXN_EXECUTOR_REPORT.md`
- `tools/codex/_debug/branch_guard_report.json`
- `tools/codex/_debug/worktree_guard_report.json`
