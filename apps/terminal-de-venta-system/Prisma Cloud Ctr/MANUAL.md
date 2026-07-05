# Prisma Cloud Center Manual

## 1. What Prisma Cloud Center Is

Prisma Cloud Center is the local operator console for PRISMA cloud licensing and customer setup. It lives in the existing repo folder:

```text
apps/terminal-de-venta-system/Prisma Cloud Ctr
```

The folder name remains `Prisma Cloud Ctr` for compatibility. The visible product name is `Prisma Cloud Center`.

It gives operators one place to inspect cloud health, customer license state, Cloud License Gateway route metadata, License Admin Bridge state, Prisma Customer Setup source readiness, local license runtime state, self-test output, License Operation Audit, License Diagnostics, and sanitized evidence.

## 2. Canonical License Naming

| Technical lineage | Operator-facing name |
|---|---|
| `Prisma Cloud Ctr` visible product text | `Prisma Cloud Center` |
| `LICFLOW3` | `Cloud License Gateway` |
| `LICFLOW3 Cloudflare routes` | `Cloud License Routes` |
| `LICFLOW3_CLOUDFLARE_ROUTES_LIVE` | `Cloud License Gateway: Live` |
| `LICFLOW4 Admin Bridge` | `License Admin Bridge` |
| `/api/licflow4/bridge/*` | `Local License Admin API` |
| `/api/licenses/*` | `Cloud License Gateway API` |
| `dry-run` / `dryRun` | `Simulation (Dry Run)` |
| real action / mutation | `Confirmed License Operation` |
| audit | `License Operation Audit` |
| diagnostics | `License Diagnostics` |
| route map | `License Route Map` |
| `adminTokenPresent` | `Admin Token Status: presence-only` |

Historical names may remain in filenames, routes, package scripts, verifiers, raw diagnostics, constants, and changelog history. They must not be the primary operator-facing product language.

## 3. Current Cloud License Gateway State

- Visible status: `Cloud License Gateway: Live`
- Legacy/internal status: `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`
- Cloud License Gateway Worker: `prisma-cloud-semilla`
- Cloud License Database D1: `prisma_cloud_semilla`
- Live base: `https://app.hitechrts.com`
- Wrangler command: `pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler`
- Wrangler version: `4.93.0`
- Deploy result: `pass_deployed_live`
- Deployed version: `4a6df40b-1e4d-4989-9fbe-7a848bd0fd24`
- Rollback target: `a94eeb69-250f-483a-8572-f1566c5aa8a6`

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

That 401 is the correct unauthenticated smoke result. A 404 is not expected.

## 4. How To Open It

Run:

```cmd
00_ABRIR_PRISMA_CLOUD_CTR.cmd
```

Open:

```text
http://127.0.0.1:3160/unified-shell.html
```

If port `3160` is already owned, Prisma Cloud Center does not kill or replace that process. Close the old local process yourself if you want a fresh local server.

## 5. License Admin Bridge

The License Admin Bridge is the local backend bridge that lets Prisma Cloud Center operate license admin actions without exposing `ADMIN_TOKEN` to browser JavaScript.

Local License Admin API routes:

```text
GET  /api/licflow4/bridge/status
POST /api/licflow4/bridge/activate
POST /api/licflow4/bridge/refresh
POST /api/licflow4/bridge/revoke
```

The status route returns sanitized metadata such as `bridgeAvailable`, `displayName`, `tokenMode`, `mutationMode`, `operatorChecklist`, Worker, Cloud License Database, License Route Map, confirmation requirements, and License Operation Audit summary. It never returns token value, token path, raw headers, D1 dumps, or Cloudflare account details.

Simulation and confirmed-operation policy:

- `Simulation (Dry Run)` validates required fields.
- Simulation does not require `ADMIN_TOKEN`.
- Simulation does not require `confirmAdminLicenseAction`.
- Revoke Simulation requires `reason`, but not `REVOKE_LICENSE`.
- Confirmed activate/refresh require `confirmAdminLicenseAction: true`.
- Confirmed revoke requires `confirmAdminLicenseAction: true`, `confirmRevoke: "REVOKE_LICENSE"`, and `reason`.

Each result includes `operatorMessage`, `nextStep`, `resultCode`, and `secretsExposed: false`.

## 6. Controlled Operation Ceremony

1. Identify operator and authorization source.
2. Fill tenant, device, license, and reason as required.
3. Run `Simulation (Dry Run)` first.
4. Review result, `operatorMessage`, `nextStep`, route map, token mode, and audit.
5. Execute `Confirmed License Operation` only with explicit authorization.
6. For revoke, type `REVOKE_LICENSE` only after authorization.
7. Save or copy sanitized evidence only.
8. Never paste, print, log, or export `ADMIN_TOKEN`.
9. If upstream rejects, review `License Diagnostics` and `License Route Map`.
10. Never use this flow for deploy, D1 mutation, Cloudflare changes, tenant data migration, or customer device registration.

## 7. Prisma Customer Setup

Prisma Customer Setup is customer onboarding, not an admin license mutation.

For a customer buying Tablet + PC + Mobile:

1. Admin creates customer/package in Prisma Cloud Center.
2. Prisma creates Setup Link, Setup Code, and Setup QR.
3. Customer opens setup on Tablet, PC, and Mobile.
4. Each app claims its own Device Slot.
5. Local license state is stored safely.
6. Refresh/status keeps devices in sync.
7. Support can see sanitized setup evidence.

Device slots:

- `Tablet POS Slot`
- `PC Admin Slot`
- `Mobile Companion Slot`

Source-only Cloud License Gateway endpoints:

```text
POST /api/admin/customer-setups/create
GET  /api/customer/setup/:setupCode
POST /api/customer/devices/claim
GET  /api/customer/license/status?setupCode=...&deviceId=...
```

Customer setup endpoints use Setup Code and never require or expose `ADMIN_TOKEN`. Live customer use requires authorized Cloud License Gateway deploy and D1 migration.

## 8. Security And Token Handling

Prisma Cloud Center may detect whether a local admin token file exists. It reads the token value only inside the backend License Admin Bridge immediately before a confirmed outbound server-side admin call.

The UI may show only:

```json
{ "adminTokenPresent": true, "tokenMode": "presence-only" }
```

or:

```json
{ "adminTokenPresent": false, "tokenMode": "presence-only" }
```

No token value is returned to frontend JavaScript. No token is written to diagnostics, JSON config, local SQLite, HTML, JavaScript, logs, docs, or evidence ZIPs.

## 9. Operating Modes

- Read-only: safe cloud and local status inspection.
- Simulation: validates fields and returns sanitized preview without admin token.
- Confirmed License Operations: available only through License Admin Bridge with local operator enforcement and explicit confirmations.
- Prisma Customer Setup: source-ready onboarding through Setup Link, Setup Code, Setup QR, and Device Claim.
- License Diagnostics: exports sanitized JSON/TXT to `F:\descargasf`.
- Self-test: validates local files, JSON, runtime contract, and safe health probes.

## 10. Self-Test And Diagnostics

Self-test:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
```

Diagnostics:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Diagnostics must remain sanitized and must not include token values, `.env`, private keys, D1 exports, production DB copies, or local secret folders.

## 11. Limits And Prohibitions

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
- Create duplicate customer setup subsystems.
- Recreate legacy license flows.

## 12. License Operation Audit Records

License Operation Audit stores sanitized in-memory records for bridge operations. Audit may include timestamp, action, mode, tenant, device/license fingerprints, operator note or reason, result code, upstream HTTP status, latency, request id, `operatorMessage`, `nextStep`, and `secretsExposed: false`.

Audit must not include `ADMIN_TOKEN`, Authorization headers, token file contents, raw secret files, full sensitive payloads, D1 dumps, or production DB copies.

Future polish can persist these sanitized records in an operator-owned audit store, but this implementation deliberately avoids committing generated runtime audit records.

## 13. Main File Map

- `internal/py/prisma_unified_lab_v3.py`: local HTTP server, self-test, diagnostics.
- `internal/py/licflow4_admin_bridge.py`: License Admin Bridge implementation.
- `internal/py/cloud_saas_api.py`: Cloud License Gateway metadata adapter.
- `internal/py/license_ops_api.py`: local runtime/license read-only adapter.
- `internal/web/cloud_command_center.html`: primary HTML shell.
- `internal/web/cloud_command_center.js`: primary UI behavior.
- `internal/web/cloud_saas_console.js`: cloud/licensing subconsole.
- `internal/web/license_ops_console.js`: local license runtime subconsole.
- `internal/config/cloud_saas.json`: Cloud License Gateway base, endpoints, and live state metadata.

## 14. How To Know It Is Correct

- Visible product name is Prisma Cloud Center.
- Cloud License Gateway, License Admin Bridge, Simulation (Dry Run), Confirmed License Operation, License Operation Audit, License Diagnostics, and License Route Map appear as operator language.
- Historical names remain only as compatibility, technical lineage, routes, filenames, package scripts, verifiers, raw diagnostics, or changelog history.
- Worker and D1 names match production.
- Activate, refresh, and revoke endpoints are preserved.
- `/api/licflow4/bridge/*` routes are preserved.
- Expected unauthenticated smoke is `401 ADMIN_TOKEN_REQUIRED`.
- Prisma Customer Setup has Setup Link, Setup Code, Setup QR, and tri-device slots.
- No token value appears in UI, logs, diagnostics, repo, or evidence ZIPs.
- No duplicate Control Center root exists.

## Source-ready vs live Customer Setup

Prisma Customer Setup can display Setup Link, Setup Code, Setup QR and Device Slots as source-ready artifacts. This means the repo source, contracts, UI and verifiers are prepared. It does **not** mean live customer onboarding is active.

Before real customers use the flow, the Cloud License Gateway source and D1 customer setup migration must be deployed/executed through an explicitly authorized Cloudflare release. Until that happens, Customer Setup must remain labeled as source-ready / deploy not executed.
