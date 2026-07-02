# LICFLOW3 Existing Inventory

Generated: 2026-07-02

Scope: `F:\repos\hitech-os\apps\terminal-de-venta-system`

This report was created before LICFLOW3 code changes. It reconciles the current repo first and treats live repo files as authority over ZIPs, downloads, or legacy tooling.

## Git Preflight

Required commands captured before code edits:

- `git status --short --branch`: branch `main...origin/main`; existing dirty files listed below.
- `git diff --name-only`: existing dirty PC/Tablet license visibility files listed below.
- `git diff --cached --name-only`: no staged files.

Pre-existing dirty changes, classified:

| File | Classification | LICFLOW3 use |
| --- | --- | --- |
| `products/pc/app/src/composition/navigation.ts` | EXTEND | Existing pending license visibility navigation. Do not mix into LICFLOW3 unless verifier needs awareness. |
| `products/pc/app/src/uiux/pc-product-navigation.manifest.json` | EXTEND | Existing pending license visibility navigation. Do not rewrite. |
| `products/pc/app/src/uiux/pc-product-navigation.ts` | EXTEND | Existing pending license visibility navigation. Do not rewrite. |
| `products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx` | EXTEND | Existing pending Tablet license visibility. Do not rewrite. |
| `docs/product/surface-cleanup/PRISMA_LICENSE_SURFACE_VISIBILITY_0207.md` | DOC_ONLY | Documents existing license surface visibility patch. |
| `tools/quality/verify_license_surface_navigation_visibility_0207.mjs` | DOC_ONLY | Existing verifier for visibility patch; not a LICFLOW3 verifier. |

## Authority Sources Reviewed

| Source | Classification | Finding |
| --- | --- | --- |
| `docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md` | REUSE | Requires evidence, no fake green, no hot Prisma generate, no blind process kills, and Tablet standalone protection. |
| `.governance/current/AUTHORITY_READSET.lock.json` | REUSE | Current authority lock includes Cloudflare optional, Tablet sovereignty, control audit-only, no fake green, support redaction, PC/Tablet/Mobile/sync authorities. |
| `.governance/current/APP_IMPACT_MATRIX.md` | REUSE | Existing governance is broad visual/data-sync context; LICFLOW3 must stay narrower than this unless explicitly needed. |
| `.governance/current/CONTRACT_AND_GATE_MATRIX.json` | REUSE | Useful gates: no fake green, diagnostic ZIP on failure, no destructive real DB tests, rollback evidence. |
| `.governance/current/MISSING_OR_UNMAPPED_RISK.md` | REUSE | Current mesh reports no missing authority patterns. |
| `.governance/current/AUTHORITY_MESH_REPORT.md` | REUSE | PASS authority mesh, but task is not LICFLOW3-specific. |
| `quality/contracts/cloudflare-optional-base.contract.json` | REUSE | Cloudflare must not block base profiles except explicit cloudflare profile. |
| `quality/contracts/tablet-sovereignty.contract.json` | REUSE | Tablet must operate without PC, Mobile, Control Center, Cloudflare, internet, tunnels, or public endpoints. |
| `quality/contracts/support-pack-redaction.contract.json` | REUSE | Evidence/support packs must exclude DBs, PII, `.env`, tokens, and secrets. |
| `quality/contracts/control-audit-only.contract.json` | REUSE | Control Center observes/audits and must not become a Tablet dependency. |

## LICFLOW2 Sources To Reuse

| Source | Classification | Finding |
| --- | --- | --- |
| `docs/reports/LICFLOW2_EXISTING_INVENTORY.md` | REUSE | LICFLOW2 already mapped ADLANT4, runtime, PC/Tablet/Mobile license consumers, and Shell Lab License Ops. |
| `docs/reports/LICFLOW2_PROCESS_SPEC.md` | REUSE | LICFLOW2 is local/offline/online-loopback/hybrid; it explicitly does not claim hosted cloud. |
| `docs/reports/LICFLOW2_ACTIVATION_MODES.md` | REUSE | Offline, online local contract, and hybrid fallback are already modeled. |
| `docs/reports/LICFLOW2_SECURITY_MODEL.md` | REUSE | Private keys stay outside repo; activation artifacts exclude secrets and DBs. |
| `docs/reports/LICFLOW2_SUPPORT_MODEL.md` | REUSE | Support reads runtime, license, receipt, activation mode, and governor status. |
| `docs/reports/LICFLOW2_VERIFICATION_REPORT.md` | REUSE | LICFLOW2 verifiers previously passed and must remain valid. |
| `shared/licensing/licflow2-activation.ts` | EXTEND | Canonical local activation layer. LICFLOW3 must not duplicate the issuer or local package logic. |
| `tools/verify-licflow2.mts` | EXTEND | Verifier pattern to reuse for LICFLOW3. |
| `tools/provision-prisma-runtime.mjs` | REUSE | Runtime provisioning remains local/offline capable. No Cloudflare dependency may be introduced. |

## 3160 And Cloud SaaS Sources

| Source | Classification | Finding |
| --- | --- | --- |
| `prisma-control-center-unified-shell-lab-v3` | REUSE | Existing private cockpit lab for `127.0.0.1:3160`; do not create a parallel cockpit. |
| `prisma-control-center-unified-shell-lab-v3/internal/config/cloud_saas.json` | EXTEND | Already targets `https://app.hitechrts.com` and lists health, capabilities, tenant status, admin selftest, commercial summary, tenant snapshot, notes, device register, integration receipt, and client contract. Missing explicit activate/refresh/revoke/support diagnostics endpoints. |
| `prisma-control-center-unified-shell-lab-v3/internal/py/cloud_saas_api.py` | EXTEND | Existing redacted server-side bridge to app.hitechrts.com. It already blocks admin writes unless localhost and token are available. |
| `prisma-control-center-unified-shell-lab-v3/internal/py/license_ops_api.py` | REUSE | Existing read-only license/runtime summary for 3160. |
| `prisma-control-center-unified-shell-lab-v3/internal/py/prisma_unified_lab_v3.py` | REUSE | Routes `/api/cloud-saas`, `/api/license-ops`, `/api/contract`, diagnostics, and the unified shell. |
| `prisma-control-center-unified-shell-lab-v3/internal/runtime/prisma-module-contract.json` | EXTEND | Declares `PRISMA Cloud Command Center`, host `127.0.0.1`, port `3160`, cloud module direct URL `https://app.hitechrts.com`. |
| `prisma-control-center-unified-shell-lab-v3/internal/web/cloud_command_center.js` | EXTEND | Main 3160 cockpit already shows cloud, client, license, devices, receipts, support, contract, diagnostics, endpoint matrix. Needs explicit LICFLOW3 contract/hosted evidence visibility. |
| `prisma-control-center-unified-shell-lab-v3/internal/web/cloud_saas_console.js` | EXTEND | Secondary cloud console already shows health, capabilities, tenant status, contract, commercial, receipts, devices. Needs support diagnostics and LICFLOW3 contract status. |
| `prisma-control-center/internal/wrappers/cloud_command_center_3160.ps1` | REUSE | Existing private 3160 launcher. Do not duplicate. |

## Cloudflare Existing Evidence

| Source | Classification | Finding |
| --- | --- | --- |
| `prisma-control-center/internal/config/cloudflare.json` | REUSE | Cloudflare Tunnel config lists Tablet, PC, Mobile, EIT, Control Center hostnames. It does not list `app.hitechrts.com`. |
| `products/chart-lab/app/wrangler.jsonc` | REUSE | Chart Lab is Cloudflare Pages static export and has Wrangler locally as a package dependency. It is not the licensing backend. |
| `products/chart-lab/app/scripts/deploy-cloudflare-pages.mjs` | DOC_ONLY | Confirms Chart Lab Pages deploy path. Do not use for licensing backend. |
| `products/mobile/infra/cloudflare` | REUSE | Mobile Cloudflare domain bridge exists; not the app.hitechrts.com licensing backend. |
| `products/mobile/app/deploy` | REUSE | Mobile deploy metadata exists; not a hosted licensing backend. |
| `pnpm-lock.yaml` | REUSE | Wrangler `4.93.0` is present via existing package dependency. Do not assume global Wrangler. |

## External Metadata Checked

Only safe metadata was inspected under `F:\descargasf`; no secrets, DBs, raw `.env`, token files, or private keys were opened or copied.

Relevant metadata found:

- `licflow2-result-20260702-014703.zip`
- `licflow mesh 0207 0100.zip`
- `licflow 0107 0000.zip`
- `latest_CLOUD_COMMAND_CENTER_3160.zip`
- `CLOUD_COMMAND_CENTER_3160_20260630_054950.zip`
- multiple `PRISMA_cloud-command-center-3160_*.log`
- multiple `PRISMA_LICENSE_OPS_CONSOLE_*.json/.md`
- Cloudflare/module evidence ZIPs from prior runs

Classification: DOC_ONLY / RUNTIME_ARTIFACT. These are supporting evidence only, not source authority.

## Summary

LICFLOW3 should reuse LICFLOW2 local activation, shared licensing, existing 3160 cockpit, existing cloud_saas bridge, and existing Cloudflare/Tunnel documentation. No canonical app.hitechrts.com Worker/Pages/D1 backend root was found in the active workspace, so the backend side is CREATE only as a minimal governed scaffold unless later live evidence proves an existing backend.
