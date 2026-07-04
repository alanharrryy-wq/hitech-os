# LICFLOW3 Reuse Map

Generated: 2026-07-02

## Objective Mapping

| LICFLOW3 requirement | Existing first source | Classification | Action |
| --- | --- | --- | --- |
| Reconcile existing infrastructure | `docs/reports/LICFLOW2_*`, governance files, 3160 files, Cloudflare config | REUSE | Keep this report set as the reconciliation baseline. |
| Do not duplicate LICFLOW2 | `shared/licensing/licflow2-activation.ts`, `tools/verify-licflow2.mts` | REUSE | Add LICFLOW3 contract beside LICFLOW2; do not create another issuer, governor, or local activation package builder. |
| Cloud contract: activate | `shared/licensing`, `cloud_saas.json` | CREATE | Add canonical LICFLOW3 endpoint contract and configure `licenseActivate` without auto-calling it. |
| Cloud contract: refresh | `shared/licensing/license-refresh-client.ts`, LICFLOW2 hybrid fallback | EXTEND | Model hosted refresh endpoint separately while preserving local hybrid fallback. |
| Cloud contract: revoke | No canonical hosted endpoint found | CREATE | Add endpoint contract only; no destructive cloud action or live revoke call. |
| Cloud contract: register device | `cloud_saas.json` already has `deviceRegister`; 3160 smoke action exists | EXTEND | Keep admin/local-only POST guard; expose as LICFLOW3 contract endpoint. |
| Cloud contract: integration receipt | `cloud_saas.json` already has `integrationReceipt`; 3160 smoke action exists | EXTEND | Keep admin/local-only POST guard; expose as LICFLOW3 contract endpoint. |
| Cloud contract: tenant status | `cloud_saas.json` has `tenantStatus`; 3160 reads it | REUSE | Use as read-only public status. |
| Cloud contract: support diagnostics | No explicit endpoint found | CREATE | Add read-only/admin endpoint contract and cockpit evidence slot. |
| Cloud contract: capabilities | `cloud_saas.json` has `capabilities`; 3160 reads it | REUSE | Use as read-only public capabilities. |
| Cloud contract: commercial summary | `cloud_saas.json` has `commercialSummary`; 3160 reads with admin token guard | REUSE | Keep local/admin-only behavior. |
| Cloud contract: contract fetch | `cloud_saas.json` has `clientContract`; 3160 reads it | REUSE | Use as client contract fetch. |
| 3160 cockpit bridge | `Prisma Cloud Ctr` and `cloud_command_center_3160.ps1` | EXTEND | Keep `127.0.0.1:3160` as only cockpit; add LICFLOW3 contract status/hosted evidence to existing panels. |
| app.hitechrts.com bridge | `cloud_saas_api.py`, `cloud_saas.json` | EXTEND | Point bridge at existing target; if live endpoint is absent, report live evidence required. |
| app.hitechrts.com backend | No Worker/Pages/D1 root found | CREATE | Add minimal governed Worker/D1 scaffold with no deploy and no DNS/Tunnel mutation. |
| Wrangler usage | `products/chart-lab/app` has package-local Wrangler | REUSE | For licensing worker, document/use `pnpm -C <worker-root> exec wrangler`; never require global Wrangler. |
| Offline/hybrid remains valid | LICFLOW2 verifiers | REUSE | LICFLOW3 verifiers delegate or assert LICFLOW2 offline/hybrid remain passing. |
| Evidence ZIP | User explicitly requested result/fail ZIP under `F:\descargasf` | CREATE | Build evidence package without DBs/secrets/private keys. |

## Non-Duplication Rules

- ADLANT4 remains the local signing authority.
- LICFLOW2 remains the local/offline/hybrid activation implementation.
- LICFLOW3 adds hosted contract definitions and cloud bridge evidence, not a second local license stack.
- 3160 remains the only cockpit for operator bridge work.
- Chart Lab remains Cloudflare Pages; it is not the licensing backend.
- Tunnel hostnames in `cloudflare.json` remain untouched.
- Tablet POS must not depend on app.hitechrts.com, Cloudflare, PC, Mobile, or Control Center.

## Files Expected To Change After This Inventory

| File or directory | Classification | Why |
| --- | --- | --- |
| `shared/licensing/licflow3-cloud-contract.ts` | CREATE | Canonical LICFLOW3 hosted licensing/support contract. |
| `shared/licensing/index.ts` | EXTEND | Export the new contract module. |
| `Prisma Cloud Ctr/internal/config/cloud_saas.json` | EXTEND | Add missing LICFLOW3 endpoints and contract metadata. |
| `Prisma Cloud Ctr/internal/py/cloud_saas_api.py` | EXTEND | Expose redacted LICFLOW3 contract status and support diagnostics evidence. |
| `Prisma Cloud Ctr/internal/web/cloud_command_center.js` | EXTEND | Show contract/support diagnostics/hosted evidence in existing cockpit. |
| `Prisma Cloud Ctr/internal/web/cloud_saas_console.js` | EXTEND | Show support diagnostics and LICFLOW3 contract status. |
| `infra/cloudflare/licflow3-worker` | CREATE | Minimal app.hitechrts.com Worker/D1 scaffold because no canonical backend root was found. |
| `tools/verify-licflow3.mts` | CREATE | LICFLOW3 verifier suite. |
| `package.json` | EXTEND | Add `verify:licflow3:*` scripts. |
| `docs/reports/LICFLOW3_VERIFICATION_REPORT.md` | CREATE | Final verification summary after implementation. |

## Files Not To Touch

| Area | Classification | Reason |
| --- | --- | --- |
| `tooling/licensing/server11*` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Legacy signing experiments are not authority for LICFLOW3. |
| `tooling/licensing/server06/mock_license_server.py` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Mock server is not hosted cloud authority. |
| Cloudflare DNS/Tunnel config files | CLOUDFLARE_LIVE_EVIDENCE_REQUIRED | No authorization to mutate DNS/Tunnel/deploy. |
| Existing PC/Tablet dirty visibility files | EXTEND | Pre-existing unrelated/pending navigation changes; do not mix with LICFLOW3. |
| Runtime DBs and ProgramData live files | DANGER_DO_NOT_AUTORUN | Sensitive runtime state; do not copy into evidence. |
