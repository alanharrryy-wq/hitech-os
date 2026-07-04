# Prisma Cloud Ctr Troubleshooting

## Page Does Not Open

Run:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
```

If port `3160` is already busy, Prisma Cloud Ctr will not kill it. Close your own old process and open again.

## LICFLOW3 Shows Wrong State

Expected state:

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

## LICFLOW4 Bridge Status

Open the license section or call:

```text
GET http://127.0.0.1:3160/api/licflow4/bridge/status
```

Expected status includes `bridgeAvailable`, `adminTokenPresent`, Worker, D1, route map, and `secretsExposed: false`.

## Admin Actions Are Blocked

Expected blocks:

- `ADMIN_TOKEN_NOT_CONFIGURED`: configure the local admin token outside the repo.
- `ADMIN_ACTION_CONFIRMATION_REQUIRED`: check the explicit confirmation box.
- `REVOKE_CONFIRMATION_REQUIRED`: type `REVOKE_LICENSE` for revoke.
- `INVALID_ADMIN_ACTION_PAYLOAD`: fill tenant, device, and license fields.
- `UPSTREAM_ADMIN_TOKEN_REQUIRED`: hosted LICFLOW3 rejected admin auth.

Do not paste admin token values into the browser. Do not put tokens in query params, localStorage, sessionStorage, docs, screenshots, or evidence ZIPs.

## Diagnostics Need Review

Use:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Confirm the output contains no token values, `.env`, private keys, D1 exports, or DB copies.
