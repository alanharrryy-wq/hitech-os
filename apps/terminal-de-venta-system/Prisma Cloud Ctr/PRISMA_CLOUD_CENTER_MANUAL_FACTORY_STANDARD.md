# Prisma Cloud Center Manual

**Document status:** Updated operational master manual
**Audience:** Operators, support, engineering, release owners, and future agents
**Tone:** Factory-standard, step-by-step, no guessing, no fake green
**Canonical product name:** Prisma Cloud Center
**Canonical live base:** `https://app.hitechrts.com`
**Canonical Cloudflare/D1 authorization:** Cloudflare OAuth through Wrangler
**Canonical Wrangler command:**

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler
```

---

## 0. Executive Decision Summary

This manual describes how Prisma Cloud Center, Cloud License Gateway, License Admin Bridge, Customer Setup, Cloudflare Worker, D1, diagnostics, audit evidence, and license operations must be operated.

The current certified scope is:

```text
LICFLOW3 Cloudflare/D1/OAuth production readiness: CERTIFIED
Certification status: PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED
production_cloud_d1_certified_today: true
```

This certification means:

- Cloudflare OAuth authorization through Wrangler is valid.
- Wrangler works through the canonical project-local command.
- The live Cloud License Gateway responds at `https://app.hitechrts.com`.
- The Cloud Bridge health endpoint reports LICFLOW3 and D1-bound evidence.
- D1 remote read-only verification passes.
- License status counts exist in D1.
- Required license/customer audit events exist.
- The broken legacy trigger pattern `NEW.license_id` is absent.
- Fine secret scan passes with zero findings.
- `PRISMA_ADMIN_TOKEN` is not required for Cloudflare/D1/OAuth certification.

This certification does **not** mean every internal admin HTTP endpoint has been executed with `PRISMA_ADMIN_TOKEN`. That token is only relevant for internal admin HTTP calls or local License Admin Bridge confirmed operations that explicitly require it.

---

## 1. What Prisma Cloud Center Is

Prisma Cloud Center is the local operator console for PRISMA cloud licensing and customer setup.

It lives in:

```text
apps/terminal-de-venta-system/Prisma Cloud Ctr
```

The folder name remains `Prisma Cloud Ctr` for compatibility. The visible product name is:

```text
Prisma Cloud Center
```

It gives operators one place to inspect:

- Cloud health.
- Cloud License Gateway live status.
- Customer license state.
- Cloud License Gateway route metadata.
- License Admin Bridge state.
- Prisma Customer Setup readiness.
- Device slot claim status.
- Local license runtime state.
- Self-test output.
- License Operation Audit.
- License Diagnostics.
- Sanitized evidence.
- Operator-safe route maps.

Prisma Cloud Center is not a deploy tool. It is not a secret viewer. It is not a D1 dump tool. It is not a port killer. It is an operator console and evidence surface.

---

## 2. Canonical License Naming

Use these names in UI, manuals, dashboards, support documents, and operator procedures.

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
| Cloudflare OAuth through Wrangler | `Cloudflare Operator Authorization` |
| D1 remote read-only verification | `Cloud License Database Verification` |

Historical names may remain in:

- Filenames.
- Routes.
- Package scripts.
- Verifiers.
- Raw diagnostics.
- Constants.
- Changelog history.
- Legacy compatibility code.

Historical names must not be the primary operator-facing product language.

---

## 3. Certified Current State

### 3.1 Cloud License Gateway

| Item | Value |
|---|---|
| Visible status | `Cloud License Gateway: Live` |
| Legacy/internal status | `LICFLOW3_CLOUDFLARE_ROUTES_LIVE` |
| Cloud License Gateway Worker | `prisma-cloud-semilla` |
| Cloud License Database D1 | `prisma_cloud_semilla` |
| Live base | `https://app.hitechrts.com` |
| Canonical Wrangler command | `pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler` |
| Verified Wrangler version | `4.93.0` |
| Authorization method for D1/Cloudflare | Cloudflare OAuth through Wrangler |
| Cloud/D1 certification status | `PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED` |

### 3.2 Live Cloud Bridge Health

The canonical health check is:

```powershell
curl.exe -sS https://app.hitechrts.com/health
```

Expected result:

```json
{
  "ok": true,
  "service": "PRISMA LICFLOW3 Cloud Licensing Support Bridge",
  "version": "0.2.0-prisma-cloud-semilla-routing",
  "dbHealth": "D1_BOUND",
  "hostedCloudEvidence": "LICFLOW3_CLOUDFLARE_ROUTES_LIVE"
}
```

The exact version may change after authorized releases. The required evidence markers are:

```text
LICFLOW3
D1_BOUND
Cloud Licensing
prisma-cloud-semilla
Cloudflare
```

If the endpoint returns 200 but those markers are missing, do not call it certified. Mark it as `HEALTH_200_MARKERS_MISSING`.

### 3.3 Live License Endpoints

The live license endpoints are:

```text
POST https://app.hitechrts.com/api/licenses/activate
POST https://app.hitechrts.com/api/licenses/refresh
POST https://app.hitechrts.com/api/licenses/revoke
```

Without the correct admin authorization for those admin operations, unauthenticated calls are expected to return:

```text
HTTP 401 ADMIN_TOKEN_REQUIRED
```

That 401 is a correct unauthenticated smoke result. A 404 is not expected.

---

## 4. Authorization Model

This is the part people keep mixing up. Do not mix it up.

### 4.1 Cloudflare/D1 Authorization

For LICFLOW3 Cloudflare and D1 verification, authorization is:

```text
Cloudflare OAuth via Wrangler
```

The canonical command is:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler whoami
```

Expected gate:

```text
returncode: 0
```

If `whoami` fails, Cloudflare/D1 verification is blocked.

### 4.2 Prisma Admin Token

`PRISMA_ADMIN_TOKEN` is **not** required for the Cloudflare/D1/OAuth certification.

It is only required for internal admin HTTP endpoints or local License Admin Bridge confirmed actions that explicitly require server-side admin authorization.

Correct rule:

```text
Do not block D1/OAuth certification because PRISMA_ADMIN_TOKEN is missing.
Use PRISMA_ADMIN_TOKEN only for internal admin HTTP operations when explicitly required.
Never print, paste, export, log, or commit the token value.
```

### 4.3 Token Safety Rule

The UI may show only presence:

```json
{ "adminTokenPresent": true, "tokenMode": "presence-only" }
```

or:

```json
{ "adminTokenPresent": false, "tokenMode": "presence-only" }
```

The token value must never appear in:

- Browser JavaScript.
- HTML.
- Diagnostics.
- JSON evidence.
- Local SQLite.
- D1 query output.
- Logs.
- Git diffs.
- Markdown docs.
- ZIP evidence.
- Screenshots.
- Chat messages.

---

## 5. How To Open Prisma Cloud Center

From the Prisma Cloud Center folder or repo tooling, run:

```cmd
00_ABRIR_PRISMA_CLOUD_CTR.cmd
```

Open:

```text
http://127.0.0.1:3160/unified-shell.html
```

Port rule:

- Prisma Cloud Center normally must not kill or replace arbitrary processes.
- For this specific 3160 launcher flow, the operator may intentionally free/reset port `3160` if the current task explicitly requires a clean Cloud Command Center launch.
- Do not generalize this exception to other dev servers or repo workflows.

---

## 6. Factory Standard Operating Procedure

This section is the “dummies mode” path. Follow it exactly.

### 6.1 Operator Preflight

Before doing anything with licenses, confirm:

| Check | Expected |
|---|---|
| Repo path exists | `F:\repos\hitech-os` |
| Product app exists | `apps/terminal-de-venta-system` |
| Cloudflare worker dir exists | `apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker` |
| D1 DB name | `prisma_cloud_semilla` |
| Live base URL | `https://app.hitechrts.com` |
| Wrangler command | project-local `pnpm -C ... exec wrangler` |
| Authorization | Cloudflare OAuth via Wrangler |
| Output folder | `F:\descargasf` |
| Final evidence | one ZIP per run |
| No fake green | mandatory |

### 6.2 Exact Certification Sequence

Run checks in this exact order:

1. Git context read-only.
2. Wrangler OAuth verification.
3. Live Cloud Bridge health probe.
4. D1 schema read-only check.
5. License table read-only check.
6. Audit event read-only check.
7. Fine secret scan.
8. Classification.
9. Single final ZIP generation.

Never reorder steps just because something “looks okay”. Factory line means station by station.

### 6.3 Canonical PowerShell Setup

Use PowerShell, from any directory.

```powershell
Set-Location F:\repos\hitech-os
```

Do not assume the current directory. Scripts must work from any directory, but humans should still know where they are.

### 6.4 Canonical Wrangler Verification

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler --version
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler whoami
```

Expected:

```text
wrangler 4.93.0
whoami returncode: 0
```

Version may advance in the future. If it advances, record the new version in the certification evidence.

### 6.5 D1 Database List

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 list
```

Expected:

```text
prisma_cloud_semilla
```

If the database is missing, stop. Do not create a new D1 database unless an authorized Cloudflare release task explicitly says so.

### 6.6 D1 Migration Read-only Check

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 migrations list prisma_cloud_semilla --remote
```

Expected:

```text
No migrations to apply
```

or equivalent output showing remote migration state is current.

If migrations are pending, do not apply them from this SOP. Escalate to an explicitly authorized Cloudflare release procedure.

### 6.7 Schema Check

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE type IN ('table','index','trigger','view') ORDER BY type,name;"
```

Hard fail if output contains:

```text
NEW.license_id
```

Reason: that was the known legacy trigger breakage. It must not return.

Expected:

```text
bad_trigger_new_license_id: false
```

### 6.8 Licenses Table Check

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "PRAGMA table_info(licenses);"
```

Expected legacy-compatible columns:

```text
id
tenant_id
plan
status
max_devices
starts_at
expires_at
created_at
updated_at
```

Do not assume `license_id` exists. The Worker must remain schema-aware.

### 6.9 License Status Counts

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT status, COUNT(*) AS count FROM licenses GROUP BY status ORDER BY status;"
```

Known certified evidence included:

```text
active: 2
revoked: 2
```

Counts may change as real operations happen. The expected condition is not the exact number. The expected condition is:

- Query returns successfully.
- Statuses are readable.
- Status values make operational sense.
- No SQL error.
- No schema drift error.

### 6.10 Audit Events Table Check

Run:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "PRAGMA table_info(audit_events);"
```

Important: the event column is:

```text
event_type
```

not:

```text
type
```

The wrong query is:

```sql
SELECT type, COUNT(*) FROM audit_events GROUP BY type;
```

Do not use it. It fails because `audit_events.type` does not exist.

The correct query is:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT event_type, COUNT(*) AS count FROM audit_events GROUP BY event_type ORDER BY count DESC LIMIT 50;"
```

### 6.11 Required Audit Evidence

The certification must verify these event types:

```text
customer_setup.create
customer_setup.plan_based_provision
customer_device.claim
customer_license.refresh
license.revoke
license.renew
license.commercial-state
customer_device.replacement.request
customer_device.replacement.approve
```

Use:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT event_type, COUNT(*) AS count FROM audit_events WHERE event_type IN ('customer_setup.create','customer_setup.plan_based_provision','customer_device.claim','customer_license.refresh','license.revoke','license.renew','license.commercial-state','customer_device.replacement.request','customer_device.replacement.approve') GROUP BY event_type ORDER BY event_type;"
```

Known certified evidence included these counts:

```text
customer_device.claim: 16
customer_license.refresh: 12
license.revoke: 3
customer_setup.create: 3
license.commercial-state: 2
license.activate: 2
customer_setup.plan_based_provision: 2
license.renew: 1
customer_device.replacement.request: 1
customer_device.replacement.approve: 1
```

Counts may increase. Required event types must not disappear.

### 6.12 Cloud Bridge Health Check

Run:

```powershell
curl.exe -sS https://app.hitechrts.com/health
```

Pass requires:

- HTTP 200.
- `ok: true`.
- LICFLOW3 marker.
- D1-bound marker.
- Cloud Licensing marker.

### 6.13 Fine Secret Scan Rule

A correct secret scan must not flag every `prisma_*` identifier. That is a false-positive machine.

The scan should flag only realistic secret patterns:

- GitHub token literals.
- Cloudflare API token literals.
- Admin token assignment literals.
- Bearer token literals.
- Hardcoded secret-like values.

It must ignore:

- `process.env.PRISMA_ADMIN_TOKEN`.
- `os.environ.get("PRISMA_ADMIN_TOKEN")`.
- `[REDACTED]`.
- Placeholders.
- Examples.
- Token generation functions.
- Hash prefixes.
- Variable names.
- Generic `prisma_*` identifiers.

Expected certified result:

```text
findings_count: 0
```

---

## 7. License Admin Bridge

The License Admin Bridge is the local backend bridge that lets Prisma Cloud Center operate license admin actions without exposing `ADMIN_TOKEN` to browser JavaScript.

Local License Admin API routes:

```text
GET  /api/licflow4/bridge/status
POST /api/licflow4/bridge/activate
POST /api/licflow4/bridge/refresh
POST /api/licflow4/bridge/revoke
```

The status route returns sanitized metadata such as:

- `bridgeAvailable`
- `displayName`
- `tokenMode`
- `mutationMode`
- `operatorChecklist`
- Worker metadata
- Cloud License Database metadata
- License Route Map
- Confirmation requirements
- License Operation Audit summary

It must never return:

- Token value.
- Token path.
- Raw headers.
- D1 dumps.
- Cloudflare account details.
- Private environment values.
- Secret folders.

### 7.1 Simulation and Confirmed Operation Policy

| Operation | Token required | Confirmation required | Mutation |
|---|---:|---:|---:|
| Simulation (Dry Run) activate | No | No | No |
| Simulation (Dry Run) refresh | No | No | No |
| Simulation (Dry Run) revoke | No | No, but reason required | No |
| Confirmed activate | Yes | `confirmAdminLicenseAction: true` | Yes |
| Confirmed refresh | Yes | `confirmAdminLicenseAction: true` | Yes |
| Confirmed revoke | Yes | `confirmAdminLicenseAction: true`, `confirmRevoke: "REVOKE_LICENSE"`, `reason` | Yes |

Each result must include:

```text
operatorMessage
nextStep
resultCode
secretsExposed: false
```

---

## 8. Controlled License Operation Ceremony

Use this ceremony for any confirmed license mutation.

1. Identify the operator.
2. Identify the authorization source.
3. Identify tenant.
4. Identify license.
5. Identify device if applicable.
6. Identify reason.
7. Confirm business approval.
8. Run `Simulation (Dry Run)` first.
9. Review route map.
10. Review token mode.
11. Review operator message.
12. Review next step.
13. Review diagnostics.
14. Execute confirmed operation only after explicit approval.
15. For revoke, type exactly:

```text
REVOKE_LICENSE
```

16. Save sanitized evidence only.
17. Confirm no token values are exposed.
18. Confirm `secretsExposed: false`.
19. Confirm audit record exists.
20. Export diagnostics only if needed.

Forbidden during this ceremony:

- Cloudflare deploy.
- DNS changes.
- Tunnel changes.
- D1 migration apply.
- D1 dump/export/copy.
- Git commits.
- Git clean/reset.
- Prisma generate.
- Process or port killing.
- Customer device registration unless the procedure explicitly says customer setup.

---

## 9. Prisma Customer Setup

Prisma Customer Setup is customer onboarding, not an admin license mutation.

For a customer buying Tablet + PC + Mobile:

1. Admin creates customer/package in Prisma Cloud Center.
2. Prisma creates Setup Link.
3. Prisma creates Setup Code.
4. Prisma creates Setup QR.
5. Customer opens setup on Tablet.
6. Tablet claims the Tablet POS Slot.
7. Customer opens setup on PC.
8. PC claims the PC Admin Slot.
9. Customer opens setup on Mobile.
10. Mobile claims the Mobile Companion Slot.
11. Local license state is stored safely.
12. Refresh/status keeps devices in sync.
13. Support can see sanitized setup evidence.

Device slots:

```text
Tablet POS Slot
PC Admin Slot
Mobile Companion Slot
```

Source-only Cloud License Gateway endpoints:

```text
POST /api/admin/customer-setups/create
GET  /api/customer/setup/:setupCode
POST /api/customer/devices/claim
GET  /api/customer/license/status?setupCode=...&deviceId=...
POST /api/customer/license/refresh
GET  /api/customer/portal?setupCode=...
GET  /api/customer/magic-link?setupCode=...
POST /api/customer/devices/replacement/request
POST /api/admin/customer-devices/replacement/approve
```

Customer setup endpoints use Setup Code. They never require or expose `ADMIN_TOKEN`.

Canonical create result:

```text
PLAN_BASED_CUSTOMER_ONBOARDING_READY
```

Canonical setup audit events:

```text
customer_setup.create
customer_setup.plan_based_provision
```

---

## 10. Source-ready vs Live-ready vs Certified

Do not mix these statuses. This is the factory label system.

| Label | Meaning | Allowed claim |
|---|---|---|
| Source-ready | Code/contracts/UI/verifiers exist in repo | "Prepared in source" |
| Live-ready | Deployed/live dependencies are reachable | "Live dependencies respond" |
| OAuth/D1 certified | Wrangler OAuth, D1 read-only, audit evidence, bridge health, secret scan pass | "Cloudflare/D1 production readiness certified" |
| Admin HTTP certified | Internal admin endpoint E2E with required admin authorization passes | "Admin HTTP operations certified" |
| Customer production certified | Real customer onboarding flow passes through setup/link/code/QR/device claim/status | "Customer onboarding certified" |

Current certified claim:

```text
LICFLOW3 Cloudflare/D1/OAuth production readiness is certified.
```

Do not expand that into unrelated claims unless those gates are run.

---

## 11. Self-Test and Diagnostics

Self-test:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
```

Diagnostics:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Diagnostics must remain sanitized.

Diagnostics must not include:

- Token values.
- `.env` contents.
- Private keys.
- D1 exports.
- Production DB copies.
- Raw Authorization headers.
- Local secret folders.
- Cloudflare account secrets.
- Full sensitive payloads.

Diagnostics should include:

- Product version.
- Route map.
- Token presence only.
- Bridge availability.
- Cloud health.
- Last safe audit summary.
- Diagnostics timestamp.
- Sanitized errors.
- `secretsExposed: false`.

---

## 12. Evidence Package Standard

Every certification, diagnostic, closeout, or verification run must produce one final ZIP in:

```text
F:\descargasf
```

Do not leave scattered final report folders.

The ZIP must include:

```text
REPORT.json
REPORT.md
SUMMARY_FOR_CHAT.md
CONTINUATION.md
logs/transcript.txt
git/status_short_branch.txt
git/head_log.txt
http/*.json
d1/**/*.txt
security/fine_secret_scan_findings.json
```

If a run fails, the same single ZIP must contain:

```text
ERROR.txt
blockers
warnings
executed commands
sanitized outputs
continuation instructions
```

The ZIP must never contain:

- Token values.
- `.env` files.
- Private key files.
- D1 dumps.
- Raw production DB exports.
- Cloudflare secret values.
- Git credentials.
- Browser session secrets.

---

## 13. PASS/FAIL Standard

### 13.1 PASS: Cloudflare/D1/OAuth Certified

A run can return:

```text
PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED
```

only when all are true:

| Gate | Required |
|---|---:|
| `wrangler --version` via project-local command | Pass |
| `wrangler whoami` via project-local command | Pass |
| `https://app.hitechrts.com/health` | HTTP 200 |
| Health markers | Present |
| D1 `d1 list` | Pass |
| D1 migrations list | Pass |
| Schema read-only query | Pass |
| `NEW.license_id` absent | Pass |
| `licenses` table readable | Pass |
| License status counts readable | Pass |
| `audit_events.event_type` counts readable | Pass |
| Required audit events present | Pass |
| Fine secret scan | 0 findings |
| Blockers | 0 |

### 13.2 FAIL

Fail if any of these occur:

- Wrangler OAuth fails.
- D1 remote cannot be read.
- Health endpoint returns 404.
- Health endpoint lacks required markers.
- Schema contains `NEW.license_id`.
- `licenses` table cannot be read.
- `audit_events.event_type` cannot be read.
- Required audit evidence is missing.
- Fine secret scan finds real token literals.
- Evidence ZIP contains secrets.
- Tool claims green without evidence.

### 13.3 WARNING

Warn but do not fail Cloudflare/D1/OAuth certification for:

- Working tree not clean due to active user work.
- `PRISMA_ADMIN_TOKEN` missing.
- Optional `audit_log` table query missing or incompatible.
- Counts changed since last run.
- Wrangler version advanced, if core behavior passes.

---

## 14. Troubleshooting

### 14.1 Wrangler Not Found

Symptom:

```text
wrangler_available: false
```

Wrong assumption:

```text
Wrangler must be global.
```

Correct fix:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler --version
```

If this passes, Wrangler is fine.

### 14.2 OAuth Not Authorized

Symptom:

```text
wrangler whoami fails
```

Fix:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler login
```

Then rerun:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler whoami
```

Do not paste OAuth tokens into chat or docs.

### 14.3 D1 Query Says `no such column: type`

Wrong query:

```sql
SELECT type, COUNT(*) FROM audit_events GROUP BY type;
```

Correct query:

```sql
SELECT event_type, COUNT(*) FROM audit_events GROUP BY event_type;
```

This is not a licensing failure. It is a verifier bug.

### 14.4 `PRISMA_ADMIN_TOKEN` Missing

For Cloudflare/D1/OAuth certification:

```text
Not a blocker.
```

For internal admin HTTP operations:

```text
Blocker.
```

Do not use one status for the other.

### 14.5 401 ADMIN_TOKEN_REQUIRED

For unauthenticated admin endpoint smoke:

```text
Expected.
```

For authorized admin operation:

```text
Fail.
```

Context matters.

### 14.6 404 on License Endpoint

A 404 is not expected for live license routes.

Check:

```text
https://app.hitechrts.com/api/licenses/activate
https://app.hitechrts.com/api/licenses/refresh
https://app.hitechrts.com/api/licenses/revoke
```

If endpoint route returns 404, inspect Cloud License Route Map and Worker deployment.

### 14.7 Secret Scan Finds 200+ `prisma_*` Findings

That is almost certainly a bad scanner.

Use fine scan rules. Do not flag generic `prisma_*` identifiers.

---

## 15. Security and Token Handling

Prisma Cloud Center may detect whether a local admin token file exists. It reads the token value only inside the backend License Admin Bridge immediately before a confirmed outbound server-side admin call.

Hard rules:

1. Never paste token values into chat.
2. Never store token values in repo files.
3. Never export token values into diagnostics.
4. Never print Authorization headers.
5. Never log token file contents.
6. Never put tokens into evidence ZIPs.
7. Never write tokens into browser JavaScript.
8. Never write tokens into HTML.
9. Never write tokens into local SQLite.
10. Never use token values as test fixtures.

Allowed evidence:

```text
adminTokenPresent: true
tokenMode: presence-only
tokenHashPrefix: optional short fingerprint only if needed
value_logged: false
```

---

## 16. Limits and Prohibitions

Prisma Cloud Center must not:

- Deploy Cloudflare.
- Change DNS.
- Change Tunnel state.
- Run D1 dump/export/copy in diagnostics.
- Apply D1 migrations from read-only certification.
- Read or print token values.
- Store secrets in repo files.
- Store secrets in local SQLite.
- Kill or free unrelated ports.
- Create duplicate Control Centers.
- Create duplicate license adapters.
- Create duplicate customer setup subsystems.
- Recreate legacy license flows.
- Declare production green without evidence.
- Use `git add .` for operational closeout.
- Use `git reset --hard`.
- Use `git clean`.
- Force push.
- Mix unrelated local working changes into license certification.

---

## 17. Main File Map

| File | Purpose |
|---|---|
| `internal/py/prisma_unified_lab_v3.py` | Local HTTP server, self-test, diagnostics |
| `internal/py/licflow4_admin_bridge.py` | License Admin Bridge implementation |
| `internal/py/cloud_saas_api.py` | Cloud License Gateway metadata adapter |
| `internal/py/license_ops_api.py` | Local runtime/license read-only adapter |
| `internal/web/cloud_command_center.html` | Primary HTML shell |
| `internal/web/cloud_command_center.js` | Primary UI behavior |
| `internal/web/cloud_saas_console.js` | Cloud/licensing subconsole |
| `internal/web/license_ops_console.js` | Local license runtime subconsole |
| `internal/config/cloud_saas.json` | Cloud License Gateway base, endpoints, and live state metadata |
| `infra/cloudflare/licflow3-worker/wrangler.jsonc` | Cloudflare Worker/D1 config |
| `infra/cloudflare/licflow3-worker/worker.js` | LICFLOW3 Worker |
| `docs/ops/licscope/LICFLOW3_CLOUDFLARE_WRANGLER_D1_RUNBOOK.md` | D1/Wrangler runbook |

---

## 18. Operator Checklist

Before claiming Cloudflare/D1 certification:

```text
[ ] I used project-local Wrangler, not global-only Wrangler.
[ ] Wrangler version passed.
[ ] Wrangler whoami passed.
[ ] Live base was https://app.hitechrts.com.
[ ] Health returned HTTP 200.
[ ] Health included LICFLOW3/D1 markers.
[ ] D1 list found prisma_cloud_semilla.
[ ] D1 migration list passed.
[ ] Schema query passed.
[ ] NEW.license_id was absent.
[ ] licenses table info passed.
[ ] license status counts passed.
[ ] audit_events.event_type counts passed.
[ ] required audit events were present.
[ ] fine secret scan found 0 real secrets.
[ ] no token values were logged.
[ ] one final ZIP was generated in F:\descargasf.
[ ] blockers count was 0.
```

Before claiming Admin HTTP operation certification:

```text
[ ] PRISMA_ADMIN_TOKEN was present only in local secure environment.
[ ] Token value was never printed.
[ ] Simulation ran first.
[ ] Confirmed operation had explicit approval.
[ ] Revoke used REVOKE_LICENSE and reason.
[ ] Result had secretsExposed: false.
[ ] Audit entry was present.
[ ] Sanitized evidence was exported.
```

Before claiming Customer Setup production certification:

```text
[ ] Setup create passed.
[ ] Setup Link was created.
[ ] Setup Code was created.
[ ] Setup QR was created.
[ ] Setup create returned PLAN_BASED_CUSTOMER_ONBOARDING_READY.
[ ] Audit includes customer_setup.create.
[ ] Audit includes customer_setup.plan_based_provision.
[ ] Tablet POS Slot claim passed.
[ ] PC Admin Slot claim passed.
[ ] Mobile Companion Slot claim passed.
[ ] Status refresh passed.
[ ] Sanitized customer evidence passed.
[ ] No admin token was exposed.
```

---

## 19. Standard Decision Labels

Use these labels exactly:

```text
PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED
PASS_D1_READONLY_SECRETSCAN_FINE_ADMIN_TOKEN_MISSING
PASS_D1_READONLY_SECRETSCAN_FINE_ADMIN_TOKEN_PRESENT_NO_MUTATION_E2E
BLOCKED_ADMIN_TOKEN_MISSING
FAIL_BLOCKERS_FOUND
WARN_INCOMPLETE_OAUTH_CERTIFICATION
HEALTH_200_MARKERS_MISSING
D1_SCHEMA_LEGACY_TRIGGER_FOUND
SECRET_SCAN_REAL_FINDINGS
```

Do not invent “green-ish”, “probably ready”, “almost prod”, or other gelatinous statuses. This is not horchata.

---

## 20. Change Control

Any future change to LICFLOW3, Worker, D1 schema, Customer Setup, License Admin Bridge, or Prisma Cloud Center must follow:

1. Authority/readset preflight if source code changes are planned.
2. Scope declaration.
3. App impact matrix.
4. Contract/gate matrix.
5. No duplicate subsystem check.
6. No secrets check.
7. No deploy unless explicitly authorized.
8. No D1 mutation unless explicitly authorized.
9. Rollback plan.
10. One final ZIP in `F:\descargasf`.
11. No fake green.

---

## 21. Glossary for Dummies

| Term | Meaning |
|---|---|
| Cloud License Gateway | The live Worker/API layer for cloud licensing |
| D1 | Cloudflare SQLite-like database used by the licensing bridge |
| Wrangler | Cloudflare CLI used to access Worker/D1 |
| OAuth | Browser-based Cloudflare login used by Wrangler |
| `whoami` | Wrangler command proving OAuth session is valid |
| `PRISMA_ADMIN_TOKEN` | Internal admin HTTP authorization token, not needed for D1 OAuth verification |
| Simulation | Dry run, no mutation |
| Confirmed operation | Real mutation with explicit approval |
| Audit event | Sanitized evidence that a license/customer action occurred |
| Fine secret scan | Scanner that detects real secrets without false-flagging `prisma_*` identifiers |
| Fake green | Claiming PASS without enough evidence. Forbidden. |

---

## 22. Final Current Declaration

The current certified declaration is:

```text
LICFLOW3 Cloudflare/D1/OAuth production readiness is certified today.
```

The certification is valid for the Cloudflare/D1/OAuth scope only.

It includes:

```text
Cloudflare OAuth
Wrangler project-local command
Live Cloud Bridge health
D1 remote read-only schema
D1 license status counts
D1 required audit evidence
Legacy trigger absence
Fine secret scan
Sanitized evidence discipline
```

It does not automatically include:

```text
Internal admin HTTP token operations
New customer onboarding production run
Future deployments
Future D1 migrations
Unrelated local working tree changes
```

If someone wants to expand the claim, they must run the relevant gate and produce a new evidence ZIP.

---

## 23. Minimal Factory Command Reference

Use these as the exact command references.

```powershell
Set-Location F:\repos\hitech-os
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler --version
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler whoami
```

```powershell
curl.exe -sS https://app.hitechrts.com/health
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 list
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 migrations list prisma_cloud_semilla --remote
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE type IN ('table','index','trigger','view') ORDER BY type,name;"
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "PRAGMA table_info(licenses);"
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT status, COUNT(*) AS count FROM licenses GROUP BY status ORDER BY status;"
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT event_type, COUNT(*) AS count FROM audit_events GROUP BY event_type ORDER BY count DESC LIMIT 50;"
```

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT event_type, COUNT(*) AS count FROM audit_events WHERE event_type IN ('customer_setup.create','customer_setup.plan_based_provision','customer_device.claim','customer_license.refresh','license.revoke','license.renew','license.commercial-state','customer_device.replacement.request','customer_device.replacement.approve') GROUP BY event_type ORDER BY event_type;"
```

---

## 24. Human Rule

When in doubt:

```text
Read evidence.
Run read-only checks.
Do not mutate.
Do not deploy.
Do not print secrets.
Do not declare green early.
Put everything in one ZIP.
```

If the evidence says PASS, say PASS.
If the evidence says blocked, say blocked.
If the tool was wrong, fix the tool and rerun.

No teatro, no incienso, no “ahí medio quedó”. Factory standard.
