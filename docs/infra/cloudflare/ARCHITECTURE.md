# Cloudflare Tunnel Architecture

## Objective

Provide a permanent, self-healing setup that prevents Cloudflare Error 1033 by enforcing:

- Correct DNS route
- Correct tunnel ingress config
- Persistent Windows service
- Scheduled watchdog recovery

## Components

1. `setup_tunnel_forever.ps1`
- Fixed absolute repo root (`F:\repos\hitech-os`)
- Thin wrapper over Python core
- Displays setup progress with `Write-Progress`
- Runs final validation checks and writes `FINAL_REPORT.txt`

2. `tunnel_forever.py`
- Full mode:
  - Ensure DNS route
  - Ensure config
  - Ensure service (auto-elevate if needed)
  - Ensure watchdog task (auto-elevate if needed)
  - Validate full state and persist JSON
- Guard mode:
  - Check active tunnel connections
  - Restart service on unhealthy state with cooldown guard

3. Submodules
- `fix_dns.py`
- `ensure_config.py`
- `ensure_service.py`
- `ensure_watchdog.py`
- `validate_tunnel.py`

4. Shared runtime
- `cloudflared_helpers.py` (logging, command execution, parsing, admin elevation)
- `ensure_origin.py` (ensures Keystone origin process on `localhost:3000`)

## Idempotency Model

- DNS add only when route is missing.
- Config rewrite only when values/ingress do not match required state.
- Service install only when service is missing.
- Startup mode/service running repaired only when drift is detected.
- Watchdog task updated in place (`/F`) under the same task name.

## Storage

- Infra report: `F:\repos\hitech-os\tools\infra\cloudflare\FINAL_REPORT.txt`
- Operational logs:
  - `F:\repos\hitech-os\logs\cloudflare`
