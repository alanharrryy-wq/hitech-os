# LICFLOW2 Support Model

Generated: 2026-07-02

## Operator Questions

1. Which customer is installed?
2. Which device role is installed: PC, Tablet, or Mobile?
3. Which activation mode is present?
4. Does the signed license verify?
5. Does the runtime point to the expected device identity and license files?
6. Is Tablet still locally allowed to sell?
7. Is PC sync/governance available?
8. Is Mobile only reading/supervising?

## Evidence Sources

- Shell Lab License Ops: `prisma-control-center-unified-shell-lab-v3/internal/py/license_ops_api.py`
- Shell Lab UI: `prisma-control-center-unified-shell-lab-v3/internal/web/license_ops_console.js`
- PC governor: `products/pc/app/src/server/licensing/pc-license-service.ts`
- Tablet governor: `products/tablet/app/src/server/licensing/tablet-license-service.ts`
- Mobile account contract: `products/mobile/app/src/lib/prisma-app/prisma-app-api-contracts.ts`
- Runtime context: `shared/runtime/runtime-context-resolver.ts`

## Support Flow

1. Ask the operator to export/read License Ops latest payload.
2. Confirm runtime files exist:
   - runtime config
   - device identity
   - license file
   - activation receipt
3. Confirm license summary:
   - plan `TABLET_PC_MANAGED`
   - status `active`
   - `signedEnvelope: true`
   - key algorithm `Ed25519`
   - activation mode and receipt id present
4. If Tablet is the reported problem, verify the Tablet governor still allows `pos.sale.complete`.
5. If PC is the reported problem, verify the PC governor allows `pc.open` and `sync.managed`.
6. If Mobile is the reported problem, verify account metadata includes `activationMode` and `activationModeLabel`.
7. If online refresh fails in hybrid mode, keep the local signed license installed and retry/collect evidence. Do not downgrade to demo or development license.

## Safe Support Actions

- Read JSON status and receipts.
- Re-run LICFLOW2 verifiers.
- Reapply a safe activation package to a chosen runtime root.
- Export result/fail ZIP evidence.

## Unsafe Support Actions

- Do not expose private keys.
- Do not copy DB files into support bundles.
- Do not replace productive customer identity with `DEVELOPMENT` or demo IDs.
- Do not start servers, kill processes, free ports, or run hot Prisma generate as part of LICFLOW2 verification.
