# Prisma Cloud Ctr Changelog

## 2026-07-03

- Renamed the canonical folder and visible product references to Prisma Cloud Ctr.
- Added LICFLOW4 Admin Bridge routes for status, activate, refresh, and revoke.
- Added server-side-only admin token handling for confirmed bridge actions.
- Added bridge UI status, dry-run controls, explicit confirmations, revoke phrase, and sanitized result display.
- Added sanitized in-memory audit records and diagnostics bridge summary.
- Added safe LICFLOW4 verifiers for bridge routes, frontend token absence, confirmations, sanitized diagnostics, and no auto-run mutations.
- No Cloudflare deploy, DNS/Tunnel change, D1 export/copy, or real license mutation is part of this milestone.
- Promoted the visible product name to Prisma Cloud Ctr.
- Added canonical open, self-test, and diagnostics launchers.
- Kept old launchers as compatibility wrappers only.
- Added complete operator docs: manual, runbook, architecture, security, troubleshooting.
- Updated LICFLOW3 metadata to `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
- Documented live Worker `prisma-cloud-semilla` and D1 `prisma_cloud_semilla`.
- Documented expected unauthenticated license route smoke: `401 ADMIN_TOKEN_REQUIRED`.
- Preserved the existing canonical folder instead of creating a duplicate root.
