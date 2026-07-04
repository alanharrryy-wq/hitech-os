# Prisma Cloud Ctr Manual

## 1. What Prisma Cloud Ctr Is

Prisma Cloud Ctr is the local operator console for PRISMA cloud licensing. It is the canonical product in:

```text
apps/terminal-de-venta-system/Prisma Cloud Ctr
```

The folder name is historical. The visible product name is Prisma Cloud Ctr.

It gives operators one place to inspect cloud health, customer license state, LICFLOW3 route metadata, LICFLOW4 admin bridge state, local license runtime state, self-test output, and sanitized diagnostics.

## 2. Current LICFLOW3 Live State

- Status: `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`
- Worker: `prisma-cloud-semilla`
- D1: `prisma_cloud_semilla`
- Live base: `https://app.hitechrts.com`
- Wrangler command: `pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler`
- Wrangler version: `4.93.0`
- Deploy result: `pass_deployed_live`
- Deployed version: `4a6df40b-1e4d-4989-9fbe-7a848bd0fd24`
- Rollback target: `a94eeb69-250f-483a-8572-f1566c5aa8a6`
- Evidence ZIP: `F:\descargasf\licflow3-cloudflare-deploy-result-20260703-144721.zip`

The live license endpoints are:

```text
POST https://app.hitechrts.com/api/licenses/activate
POST https://app.hitechrts.com/api/licenses/refresh
POST https://app.hitechrts.com/api/licenses/revoke
```

Without an admin token, all three are expected to return:

```text
HTTP 401 ADMIN_TOKEN_REQUIRED
```

That 401 is the correct unauthenticated smoke result. A 404 is not expected after the LICFLOW3 deploy.

## 3. How To Open It

Run:

```cmd
00_ABRIR_PRISMA_CLOUD_CTR.cmd
```

Open:

```text
http://127.0.0.1:3160/unified-shell.html
```

If port `3160` is already owned, Prisma Cloud Ctr does not kill or replace that process. Close the old local process yourself if you want a fresh local server.

## 4. Folder Structure

```text
README.md
MANUAL.md
RUNBOOK.md
ARCHITECTURE.md
SECURITY.md
TROUBLESHOOTING.md
CHANGELOG.md
00_ABRIR_PRISMA_CLOUD_CTR.cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
internal/
  py/
  web/
  config/
  data/
  docs/
  runtime/
  prisma/
```

Legacy launchers with the old folder-era names are wrappers only. They are not separate products.

## 5. License Flow

### LICFLOW4 Admin Bridge

LICFLOW4 is the local/admin bridge that lets Prisma Cloud Ctr operate license admin actions without exposing `ADMIN_TOKEN` to browser JavaScript.

Local bridge routes:

```text
GET  /api/licflow4/bridge/status
POST /api/licflow4/bridge/activate
POST /api/licflow4/bridge/refresh
POST /api/licflow4/bridge/revoke
```

The status route returns only sanitized metadata such as `bridgeAvailable`, `adminTokenPresent`, Worker, D1, live route map, confirmation requirements, and audit summary. It never returns token value, token path, raw headers, D1 dumps, or Cloudflare account details.

All mutating routes require:

```json
{ "confirmAdminLicenseAction": true }
```

Revoke also requires:

```json
{ "confirmRevoke": "REVOKE_LICENSE" }
```

Dry-run mode is non-mutating and returns a sanitized preview. Real activation, refresh, and revoke calls are server-side only and read the admin token immediately before the outbound LICFLOW3 call.

### Activate

The live route is `POST /api/licenses/activate`.

Prisma Cloud Ctr reaches it only through `POST /api/licflow4/bridge/activate` with explicit confirmation.

### Refresh

The live route is `POST /api/licenses/refresh`.

Refresh is treated as mutating if it can change server-side state. Prisma Cloud Ctr reaches it only through `POST /api/licflow4/bridge/refresh` with explicit confirmation.

### Revoke

The live route is `POST /api/licenses/revoke`.

Revoke is always admin/mutating. Prisma Cloud Ctr reaches it only through `POST /api/licflow4/bridge/revoke` with both confirmations.

## 6. Security And Token Handling

Prisma Cloud Ctr may detect whether a local admin token file exists. It reads the token value only inside the backend LICFLOW4 bridge immediately before a confirmed outbound server-side admin call.

The UI may show only:

```json
{ "adminTokenPresent": true }
```

or:

```json
{ "adminTokenPresent": false }
```

No token value is returned to frontend JavaScript. No token is written to diagnostics, JSON config, local SQLite, HTML, JavaScript, logs, docs, or evidence ZIPs.

Expected bridge error codes:

- `ADMIN_TOKEN_NOT_CONFIGURED`
- `ADMIN_ACTION_CONFIRMATION_REQUIRED`
- `REVOKE_CONFIRMATION_REQUIRED`
- `INVALID_ADMIN_ACTION_PAYLOAD`
- `UPSTREAM_ADMIN_TOKEN_REQUIRED`
- `UPSTREAM_CALL_FAILED`

## 7. Operating Modes

- Read-only: safe cloud and local status inspection.
- Smoke dummy: documents expected unauthenticated route behavior without sending secrets.
- Admin mutating: available only through LICFLOW4 Admin Bridge with local operator enforcement and explicit confirmations.
- Diagnostics: exports sanitized JSON/TXT to `F:\descargasf`.
- Self-test: validates local files, JSON, runtime contract, and safe health probes.

## 8. Self-Test Command And Expected Output

Run:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
```

Expected summary:

```text
SELF TEST: PASS
Report: F:\descargasf\PRISMA_CLOUD_CTR_SELF_TEST_<timestamp>.json
```

Self-test must not deploy, run D1 operations, kill processes, or execute admin mutations.

## 9. Diagnostics Export Command And Expected ZIP

Run:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Expected files:

```text
F:\descargasf\PRISMA_CLOUD_CTR_DIAGNOSTICS_<timestamp>.json
F:\descargasf\PRISMA_CLOUD_CTR_DIAGNOSTICS_<timestamp>.txt
```

Diagnostics must remain sanitized and must not include token values, `.env`, private keys, D1 exports, production DB copies, or local secret folders.

## 10. Troubleshooting

- If the page does not open, run the self-test first.
- If `3160` is busy, Prisma Cloud Ctr will not kill the owner. Close it manually if you own it.
- If cloud health is partial, inspect the System view and compare `health`, `capabilities`, and tenant status.
- If license actions are blocked, check the LICFLOW4 bridge result code and confirmation fields.
- If an unauthenticated license POST returns `401 ADMIN_TOKEN_REQUIRED`, the route exists.
- If an unauthenticated license POST returns `404`, hosted routing has regressed and must be investigated.

## 11. Operational Runbook

1. Run self-test.
2. Open Prisma Cloud Ctr.
3. Confirm status `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
4. Confirm Worker `prisma-cloud-semilla`.
5. Confirm D1 `prisma_cloud_semilla`.
6. Confirm the three license endpoints are listed.
7. Confirm admin token is shown only as present or absent.
8. Export diagnostics if support evidence is needed.
9. Run admin actions only through LICFLOW4 bridge controls with dry-run first and explicit confirmation.

## 12. Limits And Prohibitions

Prisma Cloud Ctr must not:

- Deploy Cloudflare.
- Change DNS.
- Change Tunnel state.
- Run D1 dump/export/copy/execute.
- Read or print token values.
- Store secrets in repo files or local SQLite.
- Kill or free ports.
- Create duplicate Control Centers.
- Create duplicate license adapters.
- Recreate LICFLOW2.

## 13. LICFLOW4 Audit Records

LICFLOW4 stores sanitized in-memory audit records for bridge operations. Audit may include timestamp, action, dry-run flag, tenant, device/license fingerprints, operator note or reason, result code, upstream HTTP status, request id, and `secretsExposed: false`.

Audit must not include `ADMIN_TOKEN`, Authorization headers, token file contents, raw secret files, full sensitive payloads, D1 dumps, or production DB copies.

Future polish can persist these sanitized records in an operator-owned audit store, but this implementation deliberately avoids committing generated runtime audit records.

## 14. Main File Map

- `internal/py/prisma_unified_lab_v3.py`: local HTTP server, self-test, diagnostics.
- `internal/py/licflow4_admin_bridge.py`: local/admin bridge for activate, refresh, revoke, status, audit, and sanitized diagnostics.
- `internal/py/cloud_saas_api.py`: Cloud SaaS and LICFLOW3 metadata adapter.
- `internal/py/license_ops_api.py`: local runtime/license read-only adapter.
- `internal/web/cloud_command_center.html`: primary HTML shell.
- `internal/web/cloud_command_center.js`: primary UI behavior.
- `internal/web/cloud_saas_console.js`: cloud/licensing subconsole.
- `internal/web/license_ops_console.js`: local license runtime subconsole.
- `internal/config/cloud_saas.json`: cloud base, endpoints, LICFLOW3 live state.

## 15. How To Know It Is Correct

- Visible product name is Prisma Cloud Ctr.
- `MANUAL.md`, `README.md`, `RUNBOOK.md`, `ARCHITECTURE.md`, `SECURITY.md`, `TROUBLESHOOTING.md`, and `CHANGELOG.md` exist.
- LICFLOW3 status is `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
- Worker and D1 names match production.
- Activate, refresh, and revoke endpoints are listed.
- LICFLOW4 bridge routes are available under `/api/licflow4/bridge/*`.
- Expected unauthenticated smoke is `401 ADMIN_TOKEN_REQUIRED`.
- No active stale pending status is shown.
- No token value appears in UI, logs, diagnostics, repo, or evidence ZIPs.
- No duplicate Control Center root exists.
- Legacy launchers are wrappers only.
