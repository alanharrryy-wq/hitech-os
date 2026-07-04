# Prisma Cloud Ctr

Prisma Cloud Ctr is the local, repo-native control surface for PRISMA license operations. It lives in this folder and runs locally on `127.0.0.1:3160`.

It does not deploy Cloudflare, modify DNS or Tunnel state, export D1, kill processes, read secret values, or replace the protected Control Center.

## Open

Run:

```cmd
00_ABRIR_PRISMA_CLOUD_CTR.cmd
```

Then open:

```text
http://127.0.0.1:3160/unified-shell.html
```

## Verify

Run:

```cmd
01_SELF_TEST_PRISMA_CLOUD_CTR.cmd
```

## Diagnostics

Run:

```cmd
02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd
```

Diagnostics are written to `F:\descargasf` and are sanitized.

## LICFLOW3 Live State

- Status: `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`
- Worker: `prisma-cloud-semilla`
- D1: `prisma_cloud_semilla`
- Base URL: `https://app.hitechrts.com`
- Live POST endpoints:
  - `/api/licenses/activate`
  - `/api/licenses/refresh`
  - `/api/licenses/revoke`
- Expected unauthenticated smoke: `401 ADMIN_TOKEN_REQUIRED`

## LICFLOW4 Admin Bridge

Local protected routes:

- `GET /api/licflow4/bridge/status`
- `POST /api/licflow4/bridge/activate`
- `POST /api/licflow4/bridge/refresh`
- `POST /api/licflow4/bridge/revoke`

The bridge keeps `ADMIN_TOKEN` server-side. Browser UI sees only booleans, sanitized status/result codes, and sanitized audit summaries. Mutating calls require `confirmAdminLicenseAction: true`; revoke also requires `confirmRevoke: "REVOKE_LICENSE"`.

For full operating instructions, read `MANUAL.md`.
