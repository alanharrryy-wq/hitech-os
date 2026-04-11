# Cloudflare Tunnel Forever (Industrial Mode)

Infra module to keep the `engine` Cloudflare tunnel permanently healthy on Windows 11.

## Scope

- Tunnel: `engine`
- Primary hostname: `engine.hitechrts.com` -> `http://127.0.0.1:3100`
- Forms hostname: `forms.hitechrts.com` -> `http://127.0.0.1:3200`
- Operator UI is intentionally not published by this tunnel automation
- Repo root: ``
- Runtime: PowerShell 7 + Python stdlib only

## Entrypoint

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/infra/cloudflare/setup_tunnel_forever.ps1
```

Guard-only (used by Scheduled Task):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/infra/cloudflare/setup_tunnel_forever.ps1 -GuardOnly
```

Optional origin override (default is `http://127.0.0.1:3100`):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/infra/cloudflare/setup_tunnel_forever.ps1 -OriginUrl http://127.0.0.1:3100
```

Optional forms overrides:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/infra/cloudflare/setup_tunnel_forever.ps1 -FormsHostname forms.hitechrts.com -FormsOriginUrl http://127.0.0.1:3200
```

## What it enforces

1. DNS routes exist for:
   - `engine.hitechrts.com -> engine`
   - `forms.hitechrts.com -> engine`
2. `C:\Users\alanh\.cloudflared\config.yml` is correct and deterministic
   - both ingress routes are present
   - catch-all `http_status:404` stays at the end
3. `cloudflared` Windows service is installed, Automatic, running, and aligned to canonical `ImagePath`
4. Public endpoints return `2xx/3xx`:
   - `https://engine.hitechrts.com`
   - `https://forms.hitechrts.com`
   - guard/public-health flows auto-ensure local origins on `3100` and `3200`
5. Scheduled task `HITECH-Cloudflared-TunnelGuard` runs every 5 minutes (connection self-heal)
6. Scheduled task `HITECH-Cloudflared-PublicHealth` runs every 5 minutes (public edge probe + alerts)
7. Validation JSON and action logs are written every run

If service-mode drift is detected (local origin healthy + tunnel connected + public still failing), orchestration applies deterministic service remediation via force-reinstall.

Public-health alerting:

- writes probe summary: `logs/cloudflare/public_health_probe_last.json`
- writes alert state: `logs/cloudflare/public_health_alert_state.json`
- emits Windows Event Log alerts (`Application`) on sustained failure/recovery
- optional webhook via env var: `HITECH_CLOUDFLARE_ALERT_WEBHOOK`

## Logs

Directory:

`logs/cloudflare`

Generated files:

- `setup_<yyyyMMdd-HHmmss>.log`
- `actions_<yyyyMMdd-HHmmss>.jsonl`
- `validate_<yyyyMMdd-HHmmss>.json`

## Python modules

- `cloudflared_helpers.py`: command exec, parsing, logging, elevation helpers
- `fix_dns.py`: ensure DNS route binding
- `ensure_config.py`: ensure deterministic config and ingress
- `ensure_origin.py`: ensure Keystone (`3100`) and Forms (`3200`) origins are available
- `ensure_service.py`: ensure and restart Windows service
- `ensure_watchdog.py`: ensure scheduled watchdog task
- `ensure_public_watchdog.py`: ensure scheduled public-health probe task
- `validate_tunnel.py`: produce validation JSON and exit non-zero on critical failures
- `tunnel_forever.py`: full orchestration + guard mode
- `public_health_probe.ps1`: periodic public endpoint probe + alert emitter
