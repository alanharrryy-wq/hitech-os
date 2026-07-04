# Prisma Cloud Center Manual

## 1. What Prisma Cloud Center Is

Prisma Cloud Center is the local operator console for PRISMA cloud licensing. It is the canonical product in:

```text
apps/terminal-de-venta-system/prisma-control-center-unified-shell-lab-v3
```

The folder name is historical. The visible product name is Prisma Cloud Center.

It gives operators one place to inspect cloud health, customer license state, LICFLOW3 route metadata, local license runtime state, self-test output, and sanitized diagnostics.

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
00_ABRIR_PRISMA_CLOUD_CENTER.cmd
```

Open:

```text
http://127.0.0.1:3160/unified-shell.html
```

If port `3160` is already owned, Prisma Cloud Center does not kill or replace that process. Close the old local process yourself if you want a fresh local server.

## 4. Folder Structure

```text
README.md
MANUAL.md
RUNBOOK.md
ARCHITECTURE.md
SECURITY.md
TROUBLESHOOTING.md
CHANGELOG.md
00_ABRIR_PRISMA_CLOUD_CENTER.cmd
01_SELF_TEST_PRISMA_CLOUD_CENTER.cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CENTER.cmd
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

### Activate

The live route is `POST /api/licenses/activate`.

Prisma Cloud Center represents the route and expected unauthenticated smoke behavior. It does not auto-run activation.

### Refresh

The live route is `POST /api/licenses/refresh`.

Refresh is treated as mutating if it can change server-side state. It is blocked by default until an explicit admin bridge is available.

### Revoke

The live route is `POST /api/licenses/revoke`.

Revoke is always admin/mutating and requires explicit confirmation in a future admin bridge. It is never run during validation.

## 6. Security And Token Handling

Prisma Cloud Center may detect whether a local admin token file exists, but it never reads, prints, sends, copies, or stores the token value.

The UI may show only:

```json
{ "adminTokenPresent": true }
```

or:

```json
{ "adminTokenPresent": false }
```

No token value is returned to frontend JavaScript. No token is written to diagnostics, JSON config, local SQLite, HTML, JavaScript, logs, docs, or evidence ZIPs.

## 7. Operating Modes

- Read-only: safe cloud and local status inspection.
- Smoke dummy: documents expected unauthenticated route behavior without sending secrets.
- Admin mutating: blocked until LICFLOW4 Admin Bridge exists.
- Diagnostics: exports sanitized JSON/TXT to `F:\descargasf`.
- Self-test: validates local files, JSON, runtime contract, and safe health probes.

## 8. Self-Test Command And Expected Output

Run:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CENTER.cmd
```

Expected summary:

```text
SELF TEST: PASS
Report: F:\descargasf\PRISMA_CLOUD_CENTER_SELF_TEST_<timestamp>.json
```

Self-test must not deploy, run D1 operations, kill processes, or execute admin mutations.

## 9. Diagnostics Export Command And Expected ZIP

Run:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CENTER.cmd
```

Expected files:

```text
F:\descargasf\PRISMA_CLOUD_CENTER_DIAGNOSTICS_<timestamp>.json
F:\descargasf\PRISMA_CLOUD_CENTER_DIAGNOSTICS_<timestamp>.txt
```

Diagnostics must remain sanitized and must not include token values, `.env`, private keys, D1 exports, production DB copies, or local secret folders.

## 10. Troubleshooting

- If the page does not open, run the self-test first.
- If `3160` is busy, Prisma Cloud Center will not kill the owner. Close it manually if you own it.
- If cloud health is partial, inspect the System view and compare `health`, `capabilities`, and tenant status.
- If license actions are blocked, that is expected until LICFLOW4 Admin Bridge is implemented.
- If an unauthenticated license POST returns `401 ADMIN_TOKEN_REQUIRED`, the route exists.
- If an unauthenticated license POST returns `404`, hosted routing has regressed and must be investigated.

## 11. Operational Runbook

1. Run self-test.
2. Open Prisma Cloud Center.
3. Confirm status `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
4. Confirm Worker `prisma-cloud-semilla`.
5. Confirm D1 `prisma_cloud_semilla`.
6. Confirm the three license endpoints are listed.
7. Confirm admin token is shown only as present or absent.
8. Export diagnostics if support evidence is needed.
9. Do not run mutating actions from this console until LICFLOW4 Admin Bridge exists.

## 12. Limits And Prohibitions

Prisma Cloud Center must not:

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

## 13. Future LICFLOW4 Admin Bridge

LICFLOW4 Admin Bridge should provide an explicit, audited path for admin mutations. It must include confirmation, sanitized logs, operation IDs, rollback notes, and no frontend token exposure.

Until then, activate, refresh, revoke, tenant updates, device registration, and receipt writes remain blocked or documented-only in Prisma Cloud Center.

## 14. Main File Map

- `internal/py/prisma_unified_lab_v3.py`: local HTTP server, self-test, diagnostics.
- `internal/py/cloud_saas_api.py`: Cloud SaaS and LICFLOW3 metadata adapter.
- `internal/py/license_ops_api.py`: local runtime/license read-only adapter.
- `internal/web/cloud_command_center.html`: primary HTML shell.
- `internal/web/cloud_command_center.js`: primary UI behavior.
- `internal/web/cloud_saas_console.js`: cloud/licensing subconsole.
- `internal/web/license_ops_console.js`: local license runtime subconsole.
- `internal/config/cloud_saas.json`: cloud base, endpoints, LICFLOW3 live state.

## 15. How To Know It Is Correct

- Visible product name is Prisma Cloud Center.
- `MANUAL.md`, `README.md`, `RUNBOOK.md`, `ARCHITECTURE.md`, `SECURITY.md`, `TROUBLESHOOTING.md`, and `CHANGELOG.md` exist.
- LICFLOW3 status is `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
- Worker and D1 names match production.
- Activate, refresh, and revoke endpoints are listed.
- Expected unauthenticated smoke is `401 ADMIN_TOKEN_REQUIRED`.
- No active stale pending status is shown.
- No token value appears in UI, logs, diagnostics, repo, or evidence ZIPs.
- No duplicate Control Center root exists.
- Legacy launchers are wrappers only.
