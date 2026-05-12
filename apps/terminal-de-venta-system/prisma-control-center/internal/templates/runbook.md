# PRISMA Control Center Runbook

## Operator buttons

- `01_LEVANTAR_TODO_LOCAL.cmd`: checks 3110, 3120, 3130, 3140 and starts only missing expected services.
- `02_LEVANTAR_TODO_CLOUDFLARE.cmd`: validates cloudflared, Windows service, config, public endpoints, and restarts cloudflared only when the Cloudflare action decides it is safe.
- `03_CHECAR_SALUD_LOCAL_Y_CLOUDFLARE.cmd`: diagnostic only. It does not stop, restart, or edit anything.
- `04_LEVANTAR_LOCAL_LUEGO_CLOUDFLARE.cmd`: local first, then Cloudflare, then final report.
- `05_ABRIR_PANEL_CONTROL_3150.cmd`: serves the local panel on `http://127.0.0.1:3150`.

## Safety rule

Unknown processes are never killed. A blocked port becomes `BLOCKED_UNKNOWN_PROCESS` with PID, executable path, command line, and best-effort cwd/inference.

## Logs

All Control Center logs and reports are written under:

`F:\repos\hitech-os\tools\_local\logs\prisma-control-center`
