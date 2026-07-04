# LICFLOW2 Existing Inventory

Generated: 2026-07-02

This inventory is source-grounded in the live repository under `F:\repos\hitech-os\apps\terminal-de-venta-system`. The ZIP packages are context only; live repo files win.

## Context Read

- Read LICFLOW2 prompt attachment from `C:\Users\alanh\.codex\attachments\ded5b50f-53dc-4a71-9b76-8cd071a47d40\pasted-text.txt`.
- Read mesh context package `F:\descargasf\licflow mesh 0207 0100.zip` entries:
  - `CODEX_PROMPT_LICFLOW_PROCESS_SPEC.md`
  - `LICFLOW_MESH_QUESTIONS.md`
  - `CONTINUATION.md`
  - `MANIFEST.json`
- Read live governance/manual files:
  - `.governance/current/AUTHORITY_READSET.lock.json`
  - `.governance/current/APP_IMPACT_MATRIX.md`
  - `.governance/current/CONTRACT_AND_GATE_MATRIX.json`
  - `.governance/current/MISSING_OR_UNMAPPED_RISK.md`
  - `.governance/current/AUTHORITY_MESH_REPORT.md`
  - `docs/visual-layer-map/LAYER_MAP.md`
  - `docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`

## Existing Licensing Core To Reuse

| Area | Live file | Existing responsibility | LICFLOW2 disposition |
| --- | --- | --- | --- |
| Ed25519 issuer/bootstrap | `shared/licensing/adlant4-local-issuer.ts` | Creates/loads outside-repo private key, writes public key metadata, signs Prisma Original Customer license, writes runtime/device files and activation receipt outside repo. | Extend, do not duplicate. Add activation modes and package/receipt helpers here or in a nearby shared module. |
| Signed license verification | `shared/licensing/license-signature.ts` | Validates Ed25519 signed envelopes against registered public keys. | Reuse unchanged unless mode metadata needs schema support. |
| Public key registry | `shared/licensing/license-public-keys.ts` | Registers trusted public key(s) for signature verification. | Reuse. No private key material in repo. |
| License schema/types | `shared/licensing/license-types.ts`, `shared/licensing/license-schema.ts`, `shared/licensing/signed-license-types.ts` | Defines license document, device authorization, state, plan, envelope validation. | Extend minimally for activation mode/status metadata if required. |
| Local load/governor | `shared/licensing/license-loader.ts`, `shared/licensing/license-governor.ts` | Loads local license from runtime context, verifies signature, resolves assignment and feature decisions. | Reuse and surface activation/support status through existing snapshot shape if possible. |
| Refresh client | `shared/licensing/license-refresh-client.ts`, `shared/licensing/license-refresh-state.ts`, `shared/licensing/license-refresh-config.ts` | Existing online refresh contract posts to `/licenses/refresh`, verifies returned signed envelope, preserves local operation on failure. | Reuse for ONLINE_ACTIVATION/HYBRID semantics; avoid new competing refresh system. |
| Feature gates | `shared/licensing/feature-resolver.ts`, `shared/licensing/feature-keys.ts`, `shared/licensing/license-gate.ts` | Enforces entitlement decisions. | Reuse. |

## Existing Runtime/Customer Core To Reuse

| Area | Live file | Existing responsibility | LICFLOW2 disposition |
| --- | --- | --- | --- |
| Runtime path truth | `shared/runtime/runtime-paths.ts` | Canonical ProgramData layout, legacy fallback, dev layout. | Reuse for activation package targets. |
| Runtime context | `shared/runtime/runtime-context-resolver.ts` | Resolves runtime.json, device identity, license file, role, customer/store/device identity. | Reuse for PC/Tablet/Mobile support status. |
| Device identity | `shared/runtime/device-identity.ts` | Normalizes identity files. | Reuse. |
| Prisma Original Customer | `shared/customer/prisma-original-customer.ts` | Holds canonical customer, business, store, license, and device IDs. | Reuse as productive customer truth for LICFLOW2 verifiers. Do not replace with demo ids. |
| Provisioning tool | `tools/provision-prisma-runtime.mjs` | Writes runtime.json, device-identity.json, provisioning evidence, and copies license to runtime root in dry-run/apply modes. | Extend carefully to accept/apply activation package evidence without changing default behavior. |

## Existing Surface Consumers

| Surface | Live evidence | Current model | LICFLOW2 disposition |
| --- | --- | --- | --- |
| PC | `products/pc/app/package.json` has Next scripts on port 3130; `products/pc/app/src/server/licensing/pc-license-service.ts`; `products/pc/app/app/api/license/*`; `products/pc/app/app/settings/license/page.tsx`. | Local Next/web app for PC backoffice/governance. No Electron/native evidence found in inspected files. | Reuse license governor and refresh endpoints; support view should consume shared status rather than new PC-only logic. |
| Tablet | `products/tablet/app/package.json` has Next scripts on port 3120 and local Prisma scripts; `products/tablet/app/src/server/licensing/tablet-license-service.ts`; `products/tablet/app/app/api/license/*`; `products/tablet/app/app/settings/license/page.tsx`. | Local Next/web app with local Tablet data plane. No PWA/native evidence found for Tablet in inspected files. | Reuse governor/refresh/status APIs and keep Tablet local-sale autonomy. |
| Mobile | `products/mobile/app/package.json` has Next scripts on port 3140, PWA/playstore verifiers; `products/mobile/app/public/manifest.webmanifest`; `products/mobile/app/public/prisma-mobile-sw.js`; mobile data plane config under `src/lib/prisma-app/mobile-data-plane`. | Next web/PWA evidence exists. Android/Play Store readiness scripts exist, but native package completion is not assumed without verifier evidence. | Reuse mobile data-plane config/status labels and add LICFLOW2 support evidence without inventing native activation. |
| Shell Lab | `Prisma Cloud Ctr/internal/py/license_ops_api.py`; `internal/py/command_center_store.py`; `internal/web/license_ops_console.js`; `internal/web/cloud_command_center.js`. | Local Shell Lab / command-center surfaces expose license ops read-only, prepared customers/devices/licenses, and cloud/SaaS probes. | Reuse for support/activation summaries; do not claim hosted cloud unless endpoint evidence exists. |

## Existing Distribution/Install Evidence

- Tablet: `products/tablet/app/package.json` proves a Next app with `dev`, `build`, and `start` scripts, port 3120. No inspected Tablet manifest/service-worker/native packaging evidence proves Tablet PWA/native.
- PC: `products/pc/app/package.json` proves a Next app with `dev`, `build`, and `start` scripts, port 3130. No inspected Electron/native packaging evidence proves desktop app.
- Mobile: `products/mobile/app/package.json`, `public/manifest.webmanifest`, and `public/prisma-mobile-sw.js` prove PWA-oriented Next app evidence. Scripts also mention Android/Play Store readiness, but LICFLOW2 must rely on verifiers rather than assuming store distribution.

## Current Activation Artifacts And Runtime Writes

Existing ADLANT4 bootstrap writes outside repo by default:

- Private key: `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\private-key.pem` (outside repo, never package)
- Public key metadata: `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\public-key.json`
- Signed license: `F:\PRISMA_CTX\LICENSING\activations\prisma-original-customer\license.signed.json`
- Activation receipt: `F:\PRISMA_CTX\LICENSING\activations\prisma-original-customer\activation-receipt.json`
- Runtime configs:
  - `runtime\runtime.pc.json`
  - `runtime\runtime.tablet.json`
  - `runtime\runtime.mobile.json`
- Device identities:
  - `runtime\device-identity.pc.json`
  - `runtime\device-identity.tablet.json`
  - `runtime\device-identity.mobile.json`

Existing provisioning tool writes, for a selected runtime root:

- `Config\runtime.json`
- `Config\device-identity.json`
- `Config\license.json` when `--license-file` is supplied
- `Config\provisioning-evidence.json`
- Data/support/update/rollback/log/export/backup directories under the runtime root/business tree

## Existing Verifiers To Reuse

Root package scripts already expose:

- `verify:licdesk:signing`
- `verify:licdesk:governor`
- `verify:licdesk:support`
- `verify:adlant4:license-governor`
- `verify:adlant4:sync-e2e`
- `verify:adlant4:no-db-commit`
- `verify:adlant4:no-demo-leaks`
- `verify:license-ops-console`
- `verify:runtime-config`
- `verify:tablet-provisioning`

LICFLOW2 should add wrapper/subcommand scripts instead of replacing these.

## Gaps LICFLOW2 Must Patch

1. No explicit shared activation mode model exists for `OFFLINE_PACKAGE`, `ONLINE_ACTIVATION`, and `HYBRID`.
2. No activation package manifest/zip builder exists for support-safe offline provisioning.
3. Online activation exists only as refresh-client semantics; there is no local issuer-backed service-contract simulator/verifier for first activation.
4. Hybrid fallback is implied by refresh failure handling but not captured as an explicit activation flow with receipts.
5. Shell Lab License Ops exposes license/runtime summary, but not an explicit activation mode/process summary.
6. Required LICFLOW2 verifier script names do not exist yet.
7. Required LICFLOW2 process/support/security/reports do not exist yet.

## Planned Patch Set

Only after this inventory:

- Add a shared LICFLOW2 activation module under `shared/licensing` that reuses ADLANT4 signing, runtime paths, refresh state, and Prisma Original Customer identity.
- Extend exports in `shared/licensing/index.ts`.
- Extend `tools/provision-prisma-runtime.mjs` only if needed to accept generated activation package inputs while preserving existing CLI behavior.
- Add `tools/verify-licflow2.mts` with subcommands for inventory, offline, online, hybrid, support, no-duplicates, no-secrets, no-db-commit, and no-demo-leaks.
- Add package scripts for all required `verify:licflow2:*` commands.
- Add LICFLOW2 docs/reports for process spec, modes, support model, security model, verifier summary, rollback/backout, and continuation.
- Extend Shell Lab license ops summary to expose activation mode/status only if the live Python adapter can do it without server/runtime side effects.

## Duplicate Risk Controls

- Do not create another issuer; reuse `ADLANT4_LOCAL_KEY_ID`, `bootstrapPrismaOriginalCustomerLicense`, and `signLicenseDocument`.
- Do not create a new customer registry; use `PRISMA_ORIGINAL_CUSTOMER`.
- Do not create PC/Tablet-specific activation logic; consume shared LICFLOW2 status from the existing license governor/runtime context.
- Do not treat Mobile as native unless existing verifiers prove it.
- Do not package private keys, DB files, `.env`, `.pem`, `.sqlite`, `.db`, or runtime customer data into result ZIP.
