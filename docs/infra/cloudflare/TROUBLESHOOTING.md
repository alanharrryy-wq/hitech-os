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
5. `origin_reachable` is `true` for `http://127.0.0.1:3100`.

If any fails, rerun full setup and inspect:

- `FINAL_REPORT.txt`
- latest `validate_*.json`
- latest `setup_*.log`
- latest `actions_*.jsonl`

## Symptom: 502 Bad Gateway (Host Error)

Cause:
- Common case A: Keystone origin is down on `127.0.0.1:3100`.
- Common case B: service-mode runtime drift (Windows service process differs from known-good foreground invocation), so edge requests fail while local checks can look healthy.

Fix:
1. Run full setup again (it auto-deploys origin):
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\setup_tunnel_forever.ps1`
2. Inspect origin runtime log:
   - `F:\repos\hitech-os\logs\cloudflare\keystone_origin_runtime.log`
3. If local origin is healthy and tunnel has active connections but public endpoint still returns 502, force-reinstall service:
   - `python F:\repos\hitech-os\tools\infra\cloudflare\ensure_service.py --apply --force-reinstall`
4. Re-validate public edge explicitly:
   - `python F:\repos\hitech-os\tools\infra\cloudflare\validate_tunnel.py --json-out F:\repos\hitech-os\logs\cloudflare\validate_manual.json`

Expected validation signal after fix:
- `local_origin_healthy: true`
- `tunnel_connected: true`
- `public_hostname_healthy: true` with `public_status_code` in `2xx/3xx`

## Symptom: No alerts received when public endpoint fails

Checklist:

1. Public-health task exists and is enabled:
   - `schtasks /Query /TN HITECH-Cloudflared-PublicHealth /V /FO LIST`
2. Probe script can run manually:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\infra\cloudflare\public_health_probe.ps1`
3. Probe output files update:
   - `F:\repos\hitech-os\logs\cloudflare\public_health_probe_last.json`
   - `F:\repos\hitech-os\logs\cloudflare\public_health_alert_state.json`
4. Event log writes are allowed (`Application`):
   - `Get-WinEvent -LogName Application -MaxEvents 50 | ? { $_.ProviderName -match 'HITECH-Cloudflare|EventCreate' }`
5. If webhook is expected, verify env var:
   - `$env:HITECH_CLOUDFLARE_ALERT_WEBHOOK`
