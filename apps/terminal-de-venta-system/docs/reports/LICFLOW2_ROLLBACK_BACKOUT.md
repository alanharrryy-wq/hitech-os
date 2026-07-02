# LICFLOW2 Rollback And Backout

Generated: 2026-07-02

## Repo Backout

Revert only LICFLOW2-owned source changes:

- `shared/licensing/licflow2-activation.ts`
- LICFLOW2 additions in `shared/licensing/index.ts`
- activation metadata additions in `shared/licensing/license-types.ts`
- runtime payload export refactor in `shared/licensing/adlant4-local-issuer.ts`
- activation package support in `tools/provision-prisma-runtime.mjs`
- `tools/verify-licflow2.mts`
- `package.json` `verify:licflow2:*` scripts
- Shell Lab License Ops activation summary additions
- Mobile activation metadata additions
- LICFLOW2 docs under `docs/reports/`

Do not revert preexisting dirty files listed in `LICFLOW2_PREEXISTING_DIRTY_FILES.md`.

## Runtime Backout

For a runtime root provisioned from a LICFLOW2 package, remove:

- `Config/runtime.json`
- `Config/device-identity.json`
- `Config/license.json`
- `Config/activation-receipt.json`
- `Config/provisioning-evidence.json`

Keep the private issuer key outside repo unless key compromise is confirmed.

## Activation Package Backout

Packages generated under `F:\descargasf` or `F:\PRISMA_CTX\LICENSING\licflow2` can be archived or deleted by an operator after evidence retention is complete.

Never delete customer DBs as part of LICFLOW2 backout.

## Support Backout

If online activation/refresh fails in HYBRID mode:

- Keep the signed local license installed.
- Keep Tablet local sales available if governor still allows the POS feature.
- Retry online contract later.
- Export support evidence before changing runtime files.
