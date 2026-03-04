# Cloudflare Tunnel Troubleshooting

## Symptom: `cloudflared` not found

Cause:
- Binary not installed or not in `PATH`.

Fix:
- Install cloudflared.
- Confirm command:
  - `cloudflared --version`

## Symptom: Tunnel not found (`engine`)

Cause:
- Tunnel does not exist in current account/token context.

Fix:
- Authenticate and create tunnel, then rerun setup:
  - `cloudflared tunnel list`
  - `cloudflared tunnel create engine`

## Symptom: DNS route missing or not sticking

Cause:
- Route not created or insufficient API permissions.

Fix:
- Check route list:
  - `cloudflared tunnel route dns list --tunnel engine`
- Add route manually (same operation setup performs):
  - `cloudflared tunnel route dns add engine engine.hitechrts.com`

## Symptom: Service install fails or missing after install

Cause:
- Non-admin context, interrupted install, or permissions.

Fix:
- Run setup again and approve UAC prompt.
- Verify:
  - `Get-Service cloudflared`

## Symptom: Watchdog task not present

Cause:
- Task creation requires elevated rights for SYSTEM context.

Fix:
- Run full setup and approve UAC prompt.
- Verify:
  - `schtasks /Query /TN HITECH-Cloudflared-TunnelGuard /V /FO LIST`

## Symptom: Error 1033 still appears

Checklist:
1. `hostname_bound` is `true` in validation JSON.
2. `ingress_ok` is `true`.
3. Service is installed and running.
4. `connections_count > 0`.
5. `origin_reachable` is `true` for `http://localhost:3000`.

If any fails, rerun full setup and inspect:

- `FINAL_REPORT.txt`
- latest `validate_*.json`
- latest `setup_*.log`
- latest `actions_*.jsonl`

## Symptom: 502 Bad Gateway (Host Error)

Cause:
- Keystone origin is down on `localhost:3000`.

Fix:
1. Run full setup again (it auto-deploys origin):
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1`
2. Inspect origin runtime log:
   - `F:\repos\hitech-os\logs\cloudflare\keystone_origin_runtime.log`

