# LICFLOW2 Process Spec

Generated: 2026-07-02

LICFLOW2 implements three activation modes on top of the existing LICDESK4/ADLANT4 licensing core. It does not introduce a second issuer, a second customer registry, or a new device truth source.

## Authority

- Live repo source of truth: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Existing issuer: `shared/licensing/adlant4-local-issuer.ts`
- Existing customer identity: `shared/customer/prisma-original-customer.ts`
- Existing runtime resolver: `shared/runtime/runtime-context-resolver.ts`
- Existing provisioning tool: `tools/provision-prisma-runtime.mjs`
- New LICFLOW2 activation layer: `shared/licensing/licflow2-activation.ts`

## Distribution Model From Live Evidence

| Surface | Evidence | Model |
| --- | --- | --- |
| Tablet | `products/tablet/app/package.json` has Next `dev`, `build`, `start` scripts on port 3120 and local Prisma scripts. | Local Next/web app with local Tablet data plane. Tablet PWA/native packaging is unresolved from inspected evidence. |
| PC | `products/pc/app/package.json` has Next `dev`, `build`, `start` scripts on port 3130. | Local Next/web app for PC backoffice/governance. Desktop/Electron packaging is unresolved from inspected evidence. |
| Mobile | `products/mobile/app/package.json`, `public/manifest.webmanifest`, `public/prisma-mobile-sw.js`. | Next web/PWA evidence exists. Native/Play Store readiness has scripts, but hosted/store distribution is not claimed by LICFLOW2. |
| Shell Lab | `prisma-control-center-unified-shell-lab-v3/internal/py/license_ops_api.py`, `internal/web/license_ops_console.js`, `internal/web/cloud_command_center.js`. | Local Shell Lab/control surface with read-only License Ops and prepared customer/device/license desks. |

## New-Customer Flow

1. Operator prepares customer/license/device in Shell Lab using Prisma Original Customer truth and canonical plan catalog.
2. LICFLOW2 emits a signed activation artifact using the ADLANT4 Ed25519 issuer.
3. Private key remains outside repo under `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\private-key.pem`.
4. Public key remains registered through `shared/licensing/license-public-keys.ts` and outside-repo public metadata.
5. Activation package/receipt/evidence is written outside repo under `F:\PRISMA_CTX` or `F:\descargasf` verifier evidence.
6. `tools/provision-prisma-runtime.mjs --activation-package <package> --role <pc|tablet|mobile> --runtime-root <target> --apply` installs:
   - `Config/runtime.json`
   - `Config/device-identity.json`
   - `Config/license.json`
   - `Config/activation-receipt.json`
7. PC, Tablet, and Mobile resolve license state through existing governor/runtime context.
8. Support reads activation mode/receipt through License Ops, governor snapshots, and Mobile account contract metadata.

## Activation Modes

- `OFFLINE_PACKAGE`: field/operator receives a safe package ZIP with signed license, role runtime templates, role device identities, manifest, and receipt. No hosted service required.
- `ONLINE_ACTIVATION`: local service contract `POST /licenses/activate` issues the same signed license and receipt. This is a contract/loopback implementation, not a hosted cloud claim.
- `HYBRID`: starts from a local package, permits online refresh/activation contract later, and preserves local signed operation when remote service is unavailable.

## Runtime Files

The package contains safe source artifacts:

- `activation-package.json`
- `activation-receipt.json`
- `license.signed.json`
- `roles/pc/runtime.json`
- `roles/pc/device-identity.json`
- `roles/tablet/runtime.json`
- `roles/tablet/device-identity.json`
- `roles/mobile/runtime.json`
- `roles/mobile/device-identity.json`

Provisioning writes target runtime artifacts:

- `Config/runtime.json`
- `Config/device-identity.json`
- `Config/license.json`
- `Config/activation-receipt.json`
- `Config/provisioning-evidence.json`

## Product Boundaries

- Tablet remains locally operable for sales when its signed local license is active.
- PC remains governance/backoffice/sync authority, not a POS replacement.
- Mobile remains owner/supervisor data plane and account/status reader.
- Shell Lab is read-only for License Ops in this flow unless a human operator explicitly runs provisioning.

## Unresolved Or Not Claimed

- No hosted cloud activation infrastructure is claimed by LICFLOW2.
- No Tablet native/PWA install claim is made beyond live Next/local app evidence.
- No PC desktop/Electron install claim is made.
- No Mobile Play Store publication is claimed by LICFLOW2.
