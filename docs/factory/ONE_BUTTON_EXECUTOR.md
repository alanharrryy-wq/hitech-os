# One-Button Executor

## Purpose

`OPEN_HOS_FACTORY_ONE_BUTTON.ps1` runs a deterministic, non-interactive prompt-pack pipeline using the shared prompt-pack inbox:

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
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/OPEN_HOS_FACTORY_ONE_BUTTON.ps1
```

Dry preflight (no launcher/run_iter dispatch):

```powershell
$env:DRY_RUN = "1"
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/OPEN_HOS_FACTORY_ONE_BUTTON.ps1
```

Equivalent switch:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/OPEN_HOS_FACTORY_ONE_BUTTON.ps1 -DryRun
```

Optional outer retry (off by default):

```powershell
$env:OUTER_RETRY = "1"
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/OPEN_HOS_FACTORY_ONE_BUTTON.ps1
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

Executor summary:

- `02 Runs\<RUN_ID>\_debug\EXECUTOR_SUMMARY.json`
