# Prisma Cloud Center Troubleshooting

## Page Does Not Open

Run:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
```

If port `3160` is already busy, Prisma Cloud Center will not kill it. Close your own old process and open again.

## Cloud License Gateway Shows Wrong State

Expected visible state:

```text
Cloud License Gateway: Live
```

Legacy/internal status:

```text
LICFLOW3_CLOUDFLARE_ROUTES_LIVE
```

Expected Worker/D1:

```text
prisma-cloud-semilla
prisma_cloud_semilla
```

If a pending/local-only status appears in active UI, treat it as stale metadata.

## License Route Smoke

Without admin token, expected:

```text
401 ADMIN_TOKEN_REQUIRED
```

Unexpected:

```text
404
5xx
```

## License Admin Bridge Status

Open License Operations or call:

```text
GET http://127.0.0.1:3160/api/licflow4/bridge/status
```

Expected status includes `bridgeAvailable`, `adminTokenPresent`, `tokenMode: presence-only`, `mutationMode`, `operatorChecklist`, Worker, Cloud License Database, License Route Map, and `secretsExposed: false`.

## Admin Actions Are Blocked

Expected blocks:

- `ADMIN_TOKEN_NOT_CONFIGURED`: admin token is not configured locally. Configure it outside the repo and rerun Simulation.
- `ADMIN_ACTION_CONFIRMATION_REQUIRED`: confirmation is required before executing a confirmed license operation.
- `REVOKE_CONFIRMATION_REQUIRED`: type `REVOKE_LICENSE` only after approval.
- `INVALID_ADMIN_ACTION_PAYLOAD`: fill tenant, device, license, and reason where required.
- `UPSTREAM_ADMIN_TOKEN_REQUIRED`: Cloud License Gateway rejected admin authorization. Check local token configuration without printing or pasting the token.
- `UPSTREAM_CALL_FAILED`: review upstream status, License Diagnostics, and License Route Map before retrying.

Do not paste admin token values into the browser. Do not put tokens in query params, localStorage, sessionStorage, docs, screenshots, or evidence ZIPs.

## Customer Setup Is Source Ready

If Prisma Customer Setup says source ready, deploy/D1 migration has not been executed. This is correct for source-only work. Live customer use requires explicit authorization for Cloud License Gateway deploy and D1 migration.

## Diagnostics Need Review

Use:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Confirm the output contains no token values, `.env`, private keys, D1 exports, or DB copies.

## Prisma Customer Setup Source-Ready Boundary

If Prisma Customer Setup shows Setup Link, Setup Code, Setup QR, or Device Claim while the Cloud License Gateway has not been deployed with the customer setup migration, treat the flow as **source-ready, not live**.

Live customer use requires explicit authorization for Cloud License Gateway deployment and D1 migration. Do not retry by pasting admin tokens in the browser, running Wrangler manually from the UI, or treating local source readiness as production readiness.
