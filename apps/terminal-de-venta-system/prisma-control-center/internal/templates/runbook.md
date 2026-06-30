# PRISMA Control Center Runbook

## Operator buttons

- `01_LEVANTAR_TODO_LOCAL.cmd`: checks 3110, 3120, 3130, 3140 and starts only missing expected services.
- `02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd`: local first, then Cloudflare, then final report.
- `03_LEVANTAR_SOLO_UN_MODULO.cmd`: starts one selected PRISMA module and validates Cloudflare for that module.
- `04_ABRIR_ATLAS_DEPENDENCIAS.cmd`: opens the dependency atlas.
- `00_KILL_ALL_LOCAL.cmd` / `09_KILL_EVERYTHING_PRISMA.cmd`: stop PRISMA local ports only.
- `12_ABRIR_PRISMA_CLOUD_COMMAND_CENTER_3160.cmd`: starts the private PRISMA Cloud Command Center on 3160 without touching Control Center 3150.

## Safety rule

Unknown processes are never killed. A blocked port becomes `BLOCKED_UNKNOWN_PROCESS` with PID, executable path, command line, and best-effort cwd/inference.

## Logs

Launcher evidence ZIPs are written under:

`F:\descargasf`
