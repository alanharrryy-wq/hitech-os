# Cloudflare Tunnel Operations

## Standard Setup Run

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1
```

This performs full remediation and validation:

1. Verifies tunnel exists
2. Ensures DNS route for `engine.hitechrts.com`
3. Ensures deterministic `config.yml`
4. Ensures `cloudflared` service is installed/running/automatic
5. Ensures watchdog scheduled task exists and is enabled
6. Produces validation JSON and final report

## Guard-Only Run

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1 -GuardOnly
```

Used by the scheduled task every 5 minutes.

Behavior:

- Reads tunnel active connections
- If unhealthy, restarts service (cooldown-protected)
- Writes setup/action logs

## Manual Validation

```powershell
python F:\repos\hitech-os\tools\infra\cloudflare\validate_tunnel.py --json-out F:\repos\hitech-os\logs\cloudflare\validate_manual.json
```

Exit codes:

- `0`: critical checks pass
- `2`: one or more critical checks failed

## Operational Artifacts

- Report: `F:\repos\hitech-os\tools\infra\cloudflare\FINAL_REPORT.txt`
- Logs:
  - `setup_<timestamp>.log`
  - `actions_<timestamp>.jsonl`
  - `validate_<timestamp>.json`

## Origin (Keystone) Auto Deploy

The setup now auto-ensures origin availability on `http://localhost:3000`:

- Builds Keystone if needed (`apps/keystone/.next/BUILD_ID` missing)
- Starts detached origin process with:
  - `pnpm --filter @hitech/keystone exec next start -p 3000`
- Runtime output is appended to:
  - `F:\repos\hitech-os\logs\cloudflare\keystone_origin_runtime.log`

