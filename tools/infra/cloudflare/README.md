# Cloudflare Tunnel Forever (Industrial Mode)

Infra module to keep the `engine` Cloudflare tunnel permanently healthy on Windows 11.

## Scope

- Tunnel: `engine`
- Hostname: `engine.hitechrts.com`
- Origin: `http://localhost:3000`
- Repo root: `F:\repos\hitech-os`
- Runtime: PowerShell 7 + Python stdlib only

## Entrypoint

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1
```

Guard-only (used by Scheduled Task):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1 -GuardOnly
```

## What it enforces

1. DNS route exists for `engine.hitechrts.com -> engine`
2. `C:\Users\alanh\.cloudflared\config.yml` is correct and deterministic
3. `cloudflared` Windows service is installed, Automatic, and running
4. Scheduled task `HITECH-Cloudflared-TunnelGuard` runs every 5 minutes
5. Validation JSON and action logs are written every run

## Logs

Directory:

`F:\repos\hitech-os\logs\cloudflare`

Generated files:

- `setup_<yyyyMMdd-HHmmss>.log`
- `actions_<yyyyMMdd-HHmmss>.jsonl`
- `validate_<yyyyMMdd-HHmmss>.json`

## Python modules

- `cloudflared_helpers.py`: command exec, parsing, logging, elevation helpers
- `fix_dns.py`: ensure DNS route binding
- `ensure_config.py`: ensure deterministic config and ingress
- `ensure_origin.py`: ensure Keystone origin availability on `localhost:3000`
- `ensure_service.py`: ensure and restart Windows service
- `ensure_watchdog.py`: ensure scheduled watchdog task
- `validate_tunnel.py`: produce validation JSON and exit non-zero on critical failures
- `tunnel_forever.py`: full orchestration + guard mode

