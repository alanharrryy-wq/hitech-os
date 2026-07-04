# Prisma Cloud Center Troubleshooting

## Page Does Not Open

Run:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CENTER.cmd
```

If port `3160` is already busy, Prisma Cloud Center will not kill it. Close your own old process and open again.

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

## Admin Actions Are Disabled

That is expected. Prisma Cloud Center does not read token values and does not run admin mutations until LICFLOW4 Admin Bridge exists.

## Diagnostics Need Review

Use:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CENTER.cmd
```

Confirm the output contains no token values, `.env`, private keys, D1 exports, or DB copies.
