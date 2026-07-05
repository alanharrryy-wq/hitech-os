# Prisma Cloud Center Changelog

## 2026-07-04

- Canonized visible license terminology for Prisma Cloud Center.
- Promoted `Cloud License Gateway`, `License Admin Bridge`, `Simulation (Dry Run)`, `Confirmed License Operation`, `License Operation Audit`, `License Diagnostics`, and `License Route Map` as operator-facing names.
- Added bridge status fields for `tokenMode`, `mutationMode`, last simulation/confirmed-operation timestamps, last result, upstream reachability, operator checklist, conservative `safeToMutate`, and `secretsExposed: false`.
- Implemented Simulation policy so dry-run validates fields without admin token or confirmed-operation confirmation; confirmed revoke still requires `REVOKE_LICENSE`.
- Added Prisma Customer Setup source readiness with Setup Link, Setup Code, Setup QR, Device Slots, Tablet POS Slot, PC Admin Slot, and Mobile Companion Slot.
- Preserved legacy/internal identifiers `LICFLOW3`, `LICFLOW4`, `/api/licflow4/bridge/*`, `/api/licenses/*`, `prisma-cloud-semilla`, and `prisma_cloud_semilla` for compatibility and verifiers.
- No Cloudflare deploy, DNS/Tunnel change, D1 operation, secret exposure, or real license operation.

## 2026-07-03

- Historical/legacy note: promoted the folder-era product name `Prisma Cloud Ctr` and added LICFLOW4 route compatibility.
- Added server-side-only admin token handling for confirmed bridge actions.
- Added bridge UI status, dry-run controls, explicit confirmations, revoke phrase, and sanitized result display.
- Added sanitized in-memory audit records and diagnostics bridge summary.
- Added safe LICFLOW4 verifiers for bridge routes, frontend token absence, confirmations, sanitized diagnostics, and no auto-run mutations.
- No Cloudflare deploy, DNS/Tunnel change, D1 export/copy, or real license mutation was part of that milestone.
- Documented live Worker `prisma-cloud-semilla` and D1 `prisma_cloud_semilla`.
- Documented expected unauthenticated license route smoke: `401 ADMIN_TOKEN_REQUIRED`.
- Preserved the existing canonical folder instead of creating a duplicate root.

## 2026-07-04 - Final operator readiness closure

- `safeToMutate` is now an explicitly calculated conservative readiness field, not a magic permission and not decorative copy.
- The calculation requires admin-token presence, configured Cloud License Gateway routes, a prior Simulation, and confirmed upstream reachability.
- When reachability is `unknown`, Prisma Cloud Center must keep `safeToMutate: false` and explain the missing gate through `safeToMutateReason` and `safeToMutateChecks`.
- Prisma Customer Setup remains source-ready until Cloud License Gateway deploy and D1 migration are explicitly authorized. Setup Link, Setup Code, Setup QR and Device Claim must not be sold as live customer onboarding until then.
- No Cloudflare deploy, no D1 operation, no secret exposure, no process/port change, and no commit were performed by this closure package.
