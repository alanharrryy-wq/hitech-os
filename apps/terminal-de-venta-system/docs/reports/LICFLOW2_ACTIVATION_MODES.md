# LICFLOW2 Activation Modes

Generated: 2026-07-02

## OFFLINE_PACKAGE

Purpose: activate a customer/device set without network dependency.

Implementation:

- Builds package via `createLicflow2ActivationPackage({ mode: "OFFLINE_PACKAGE" })`.
- Reuses ADLANT4 Ed25519 signing.
- Produces a ZIP in verifier evidence.
- Applies with `tools/provision-prisma-runtime.mjs --activation-package ... --role tablet --apply`.
- Verifier: `pnpm run verify:licflow2:offline`.

Support status:

- License governor reports `active`, `TABLET_PC_MANAGED`, `assigned`.
- Raw license activation mode is `OFFLINE_PACKAGE`.

## ONLINE_ACTIVATION

Purpose: model first activation through a service contract.

Implementation:

- Builds request/response evidence through `createLicflow2OnlineActivationEvidence`.
- Contract endpoint: `POST /licenses/activate`.
- `hostedCloud` is explicitly `false`; this is local loopback/operator-service evidence unless hosted infra is later implemented.
- Verifier: `pnpm run verify:licflow2:online`.

Support status:

- PC governor reports `active`, `TABLET_PC_MANAGED`, `assigned`.
- Raw license activation mode is `ONLINE_ACTIVATION`.

## HYBRID

Purpose: combine offline continuity with online refresh/activation later.

Implementation:

- Builds package via `createLicflow2HybridActivationEvidence`.
- Writes `hybrid-refresh-fallback.json` showing remote unavailable simulation and local signed license continuity.
- Applies with `tools/provision-prisma-runtime.mjs --activation-package ... --role tablet --apply`.
- Verifier: `pnpm run verify:licflow2:hybrid`.

Support status:

- Tablet governor reports `active`, `TABLET_PC_MANAGED`, `assigned`.
- Raw license activation mode is `HYBRID`.
- Remote refresh failure does not remove the signed local license.
