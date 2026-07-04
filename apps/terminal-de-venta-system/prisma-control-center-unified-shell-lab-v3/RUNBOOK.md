# Prisma Cloud Center Runbook

## Normal Operation

1. Run `01_SELF_TEST_PRISMA_CLOUD_CENTER.cmd`.
2. Run `00_ABRIR_PRISMA_CLOUD_CENTER.cmd`.
3. Open `http://127.0.0.1:3160/unified-shell.html`.
4. Confirm LICFLOW3 status is `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
5. Use read-only views for health, customer status, local license state, and diagnostics.

## License Route Check

The expected live routes are:

- `POST /api/licenses/activate`
- `POST /api/licenses/refresh`
- `POST /api/licenses/revoke`

Without admin auth, each route should answer `401 ADMIN_TOKEN_REQUIRED`. This proves the route exists and is protected.

## Admin Mutations

Do not run activation, refresh, revoke, device registration, receipt writes, tenant updates, or license creation from this console until LICFLOW4 Admin Bridge exists.

## Diagnostics

Run:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CENTER.cmd
```

Attach only sanitized diagnostics. Do not attach local secret folders, `.env`, D1 exports, production DB copies, or token files.

## Recovery

- If local server is stale, close your own 3160 process and reopen.
- If self-test fails, fix missing files or invalid JSON first.
- If cloud read-only checks fail, inspect `System` and export diagnostics.
- If a license POST returns `404`, treat it as a hosted route regression.
- If a license POST returns `401 ADMIN_TOKEN_REQUIRED`, that is the expected unauthenticated smoke result.
