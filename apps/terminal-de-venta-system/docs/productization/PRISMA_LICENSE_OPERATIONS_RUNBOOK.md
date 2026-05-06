# PRISMA License Operations Runbook

## Purpose

This runbook documents the operator-facing flow for PRISMA licensing after phases 02AB and 02CD:

- local signed license runtime
- soft feature enforcement
- signed license verification
- optional remote refresh
- live smoke tests for Tablet and PC
- one-command evidence reports

## Main commands

From any PowerShell console:

```powershell
& "F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta_license_ops.cmd" --full-check --ensure-running
```

The command performs:

1. required file checks
2. signed fixture verification
3. Tablet typecheck/build
4. PC typecheck/build
5. live server detection
6. optional launch of missing dev servers
7. Tablet and PC license API smoke tests
8. report creation under `F:\descargasf`

## Quick live smoke only

```powershell
& "F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta_license_ops.cmd" --smoke-live
```

## Change demo license

```powershell
& "F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta_license_ops.cmd" --set-demo-license TABLET_PRO --smoke-live
```

Valid demo values:

- `TABLET_SOLO`
- `TABLET_PRO`
- `TABLET_PC_REQUIRED`
- `EXPIRED`
- `SUSPENDED`
- `REVOKED`
- `TAMPERED`

The previous license is backed up before replacement.

## Report only

```powershell
& "F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta_license_ops.cmd" --report
```

## Expected local URLs

Tablet:

- `http://127.0.0.1:3120/settings/license`
- `http://127.0.0.1:3120/api/license/status`
- `http://127.0.0.1:3120/api/license/features`
- `http://127.0.0.1:3120/api/license/refresh/status`

PC:

- `http://127.0.0.1:3130/settings/license`
- `http://127.0.0.1:3130/api/license/status`
- `http://127.0.0.1:3130/api/license/features`
- `http://127.0.0.1:3130/api/license/refresh/status`

## Verdicts

- `READY`: all requested checks passed.
- `READY WITH CAVEATS`: non-blocking warnings exist, usually live server state or optional refresh configuration.
- `BLOCKED`: a required check failed.

## Safety notes

- The ops command does not reset sales, stock, or operational databases.
- Demo license switching only replaces `local-runtime/license/license.signed.dev.json` and creates a backup first.
- Dev server startup is opt-in through `--ensure-running`.
- Remote refresh remains optional and governed by environment variables.
