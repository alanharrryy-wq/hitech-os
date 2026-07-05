# Prisma Cloud Center Runbook

## Normal Operation

1. Run `01_SELF_TEST_PRISMA_CLOUD_CTR.cmd`.
2. Run `00_ABRIR_PRISMA_CLOUD_CTR.cmd`.
3. Open `http://127.0.0.1:3160/unified-shell.html`.
4. Confirm Cloud License Gateway status is `Cloud License Gateway: Live`.
5. Confirm the License Admin Bridge status shows `bridgeAvailable`, `tokenMode: presence-only`, `operatorChecklist`, and `secretsExposed: false`.
6. Use read-only views for health, customer status, local license state, Prisma Customer Setup, and diagnostics.

Legacy/internal name: LICFLOW3. Route compatibility name: LICFLOW4.

## Cloud License Routes

The expected live routes are:

- `POST /api/licenses/activate`
- `POST /api/licenses/refresh`
- `POST /api/licenses/revoke`

Without admin auth, each route should answer `401 ADMIN_TOKEN_REQUIRED`. This proves the route exists and is protected.

## License Admin Bridge Operations

Use the License Admin Bridge panel in License Operations.

Safe order:

1. Identify operator and authorization source.
2. Fill tenant, device, license, and reason when required.
3. Run `Simulation (Dry Run)` first.
4. Review result, `operatorMessage`, `nextStep`, token mode, License Route Map, and License Operation Audit.
5. Check `confirmAdminLicenseAction` only if authorized.
6. For revoke, type `REVOKE_LICENSE` only after approval.
7. Execute the `Confirmed License Operation`.
8. Save sanitized evidence only.

Local License Admin API routes:

- `GET /api/licflow4/bridge/status`
- `POST /api/licflow4/bridge/activate`
- `POST /api/licflow4/bridge/refresh`
- `POST /api/licflow4/bridge/revoke`

Expected blocks:

- `ADMIN_TOKEN_NOT_CONFIGURED`: configure the admin token outside the repo, then rerun Simulation.
- `ADMIN_ACTION_CONFIRMATION_REQUIRED`: review Simulation and confirm only if authorized.
- `REVOKE_CONFIRMATION_REQUIRED`: type `REVOKE_LICENSE` only after approval.
- `INVALID_ADMIN_ACTION_PAYLOAD`: complete tenant, device, license, and reason where required.
- `UPSTREAM_ADMIN_TOKEN_REQUIRED`: check local token configuration server-side; do not paste tokens into the browser.
- `UPSTREAM_CALL_FAILED`: review upstream status, License Diagnostics, and License Route Map.

Device registration, receipt writes, tenant updates, and license creation are outside the current License Admin Bridge scope.

## Prisma Customer Setup

For a customer buying Tablet + PC + Mobile:

1. Open Prisma Cloud Center.
2. Create or represent a Prisma Customer Setup package.
3. Generate Setup Link, Setup Code, and Setup QR.
4. Customer opens setup on Tablet, PC, and Mobile.
5. Each app claims its own Device Slot: Tablet POS Slot, PC Admin Slot, Mobile Companion Slot.
6. Support reviews sanitized setup evidence.

This is customer onboarding, not a Confirmed License Operation.

## Diagnostics

Run:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Attach only sanitized diagnostics. Do not attach local secret folders, `.env`, D1 exports, production DB copies, or token files.

## Recovery

- If local server is stale, close your own 3160 process and reopen.
- If self-test fails, fix missing files or invalid JSON first.
- If cloud read-only checks fail, inspect System and export diagnostics.
- If a license POST returns `404`, treat it as a hosted route regression.
- If a license POST returns `401 ADMIN_TOKEN_REQUIRED`, that is the expected unauthenticated smoke result.
