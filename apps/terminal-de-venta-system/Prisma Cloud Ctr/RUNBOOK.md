# Prisma Cloud Ctr Runbook

## Normal Operation

1. Run `01_SELF_TEST_PRISMA_CLOUD_CTR.cmd`.
2. Run `00_ABRIR_PRISMA_CLOUD_CTR.cmd`.
3. Open `http://127.0.0.1:3160/unified-shell.html`.
4. Confirm LICFLOW3 status is `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
5. Confirm LICFLOW4 Admin Bridge status shows `bridgeAvailable` and `adminTokenPresent` as booleans only.
6. Use read-only views for health, customer status, local license state, and diagnostics.

## License Route Check

The expected live routes are:

- `POST /api/licenses/activate`
- `POST /api/licenses/refresh`
- `POST /api/licenses/revoke`

Without admin auth, each route should answer `401 ADMIN_TOKEN_REQUIRED`. This proves the route exists and is protected.

## LICFLOW4 Admin Mutations

Use the LICFLOW4 panel in the license section.

Safe order:

1. Fill tenant, device, and license fields.
2. Run dry-run first.
3. Review the sanitized payload preview and result code.
4. Check `confirmAdminLicenseAction`.
5. For revoke, type `REVOKE_LICENSE`.
6. Run the real action only when authorized.

Direct local routes:

- `GET /api/licflow4/bridge/status`
- `POST /api/licflow4/bridge/activate`
- `POST /api/licflow4/bridge/refresh`
- `POST /api/licflow4/bridge/revoke`

Expected blocks:

- Missing token: `ADMIN_TOKEN_NOT_CONFIGURED`
- Missing confirmation: `ADMIN_ACTION_CONFIRMATION_REQUIRED`
- Missing revoke phrase: `REVOKE_CONFIRMATION_REQUIRED`
- Upstream auth failure: `UPSTREAM_ADMIN_TOKEN_REQUIRED`

Device registration, receipt writes, tenant updates, or license creation are not part of LICFLOW4 in this milestone.

## Diagnostics

Run:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Attach only sanitized diagnostics. Do not attach local secret folders, `.env`, D1 exports, production DB copies, or token files.

## Recovery

- If local server is stale, close your own 3160 process and reopen.
- If self-test fails, fix missing files or invalid JSON first.
- If cloud read-only checks fail, inspect `System` and export diagnostics.
- If a license POST returns `404`, treat it as a hosted route regression.
- If a license POST returns `401 ADMIN_TOKEN_REQUIRED`, that is the expected unauthenticated smoke result.
