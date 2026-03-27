# Cloudflare Tunnel Operations

## Standard Setup Run

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1
```

Optional override:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1 -OriginUrl http://127.0.0.1:3100
```

This performs full remediation and validation:

1. Verifies tunnel exists
2. Ensures DNS route for `engine.hitechrts.com`
3. Ensures deterministic `config.yml`
4. Ensures `cloudflared` service is installed/running/automatic with canonical `ImagePath`
5. Ensures watchdog scheduled task exists and is enabled (`HITECH-Cloudflared-TunnelGuard`)
6. Ensures public-health scheduled task exists and is enabled (`HITECH-Cloudflared-PublicHealth`)
7. Validates public edge endpoint (`https://engine.hitechrts.com`) returns `2xx/3xx`
8. Produces validation JSON and final report

## Guard-Only Run

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1 -GuardOnly
```

Used by the scheduled task every 5 minutes.

Behavior:

- Ensures Keystone origin is reachable on `127.0.0.1:3100`
- If origin is down, attempts forced relaunch of origin before declaring failure
- Reads tunnel active connections
- If tunnel connections are unhealthy, restarts service (cooldown-protected)
- Writes setup/action logs

## Manual Validation

```powershell
python F:\repos\hitech-os\tools\infra\cloudflare\validate_tunnel.py --json-out F:\repos\hitech-os\logs\cloudflare\validate_manual.json
```

Exit codes:

- `0`: critical checks pass
- `2`: one or more critical checks failed

Critical checks are now explicit and separate:

- local origin healthy (`origin_reachable` / `local_origin_healthy`)
- tunnel connected (`connections_count > 0` / `tunnel_connected`)
- public hostname healthy (`public_hostname_healthy`, HTTP `2xx/3xx`)

If local origin and tunnel are healthy but public still fails (for example HTTP `502`), run deterministic service remediation:

```powershell
python F:\repos\hitech-os\tools\infra\cloudflare\ensure_service.py --apply --force-reinstall
python F:\repos\hitech-os\tools\infra\cloudflare\validate_tunnel.py --json-out F:\repos\hitech-os\logs\cloudflare\validate_manual.json
```

## Public Failure Alerting

Public-health probe task runs every 5 minutes:

- Task: `HITECH-Cloudflared-PublicHealth`
- Script: `F:\repos\hitech-os\tools\infra\cloudflare\public_health_probe.ps1`
- Probe output:
  - `F:\repos\hitech-os\logs\cloudflare\public_health_probe_last.json`
  - `F:\repos\hitech-os\logs\cloudflare\public_health_alert_state.json`

Alert channels:

- Windows Event Log (`Application`) via `eventcreate`
- Optional webhook if `HITECH_CLOUDFLARE_ALERT_WEBHOOK` is set

Manual probe run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\public_health_probe.ps1
```

## Operational Artifacts

- Report: `F:\repos\hitech-os\tools\infra\cloudflare\FINAL_REPORT.txt`
- Logs:
  - `setup_<timestamp>.log`
  - `actions_<timestamp>.jsonl`
  - `validate_<timestamp>.json`

## Origin (Keystone) Auto Deploy

The setup now auto-ensures origin availability on `http://127.0.0.1:3100`:

- Builds Keystone if needed (`apps/keystone/.next/BUILD_ID` missing)
- Starts detached origin process with:
  - `pnpm --filter @hitech/keystone exec next start -p 3100`
- Runtime output is appended to:
  - `F:\repos\hitech-os\logs\cloudflare\keystone_origin_runtime.log`
