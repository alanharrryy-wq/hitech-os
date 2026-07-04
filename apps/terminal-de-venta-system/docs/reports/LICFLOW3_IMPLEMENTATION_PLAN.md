# LICFLOW3 Implementation Plan

Generated: 2026-07-02

This plan follows the existing-first inventory and preserves LICFLOW2, Tablet standalone operation, and 3160 as the only cockpit.

## Patch Plan

1. Add canonical LICFLOW3 hosted contract.
   - File: `shared/licensing/licflow3-cloud-contract.ts`
   - Export from `shared/licensing/index.ts`
   - Include activate, refresh, revoke, register device, integration receipt, tenant status, support diagnostics, capabilities, commercial summary, and contract fetch.
   - Mark live status as `CLOUDFLARE_LIVE_EVIDENCE_REQUIRED` until live verification is authorized and passes.

2. Extend existing 3160 cloud bridge.
   - File: `Prisma Cloud Ctr/internal/config/cloud_saas.json`
   - File: `Prisma Cloud Ctr/internal/py/cloud_saas_api.py`
   - File: `Prisma Cloud Ctr/internal/web/cloud_command_center.js`
   - File: `Prisma Cloud Ctr/internal/web/cloud_saas_console.js`
   - Do not create another cockpit.
   - Do not auto-call mutating license endpoints in summary refresh.

3. Add minimal app.hitechrts.com Worker/D1 scaffold.
   - Directory: `infra/cloudflare/licflow3-worker`
   - Include `wrangler.jsonc`, `package.json`, `src/worker.js`, D1 migration SQL, and README.
   - No deploy, no DNS, no Tunnel edits, no live Cloudflare mutation.
   - Document expected binding/secret names only, never values.

4. Add LICFLOW3 verifiers.
   - File: `tools/verify-licflow3.mts`
   - Package scripts:
     - `verify:licflow3:inventory`
     - `verify:licflow3:no-duplicates`
     - `verify:licflow3:cloud-contract`
     - `verify:licflow3:3160-bridge`
     - `verify:licflow3:app-hitechrts-contract`
     - `verify:licflow3:no-secrets`
     - `verify:licflow3:no-db-commit`
     - `verify:licflow3:no-danger-autorun`
     - `verify:licflow3:offline-still-valid`
     - `verify:licflow3:hybrid-still-valid`

5. Keep required legacy LICFLOW2/LICDESK/ADLANT4 validations passing.
   - `verify:licflow2:inventory`
   - `verify:licflow2:offline`
   - `verify:licflow2:online`
   - `verify:licflow2:hybrid`
   - `verify:licdesk:signing`
   - `verify:licdesk:governor`
   - `verify:adlant4:sync-e2e`

6. Generate final evidence package under `F:\descargasf`.
   - Name: `licflow3 <DDMM HHmm> result.zip` on partial/pass result.
   - Use fail ZIP only if implementation or validation fails.
   - Exclude DBs, secrets, private keys, raw `.env`, token files, and sensitive runtime data.

## Validation Strategy

- Static compile:
  - `node --check infra/cloudflare/licflow3-worker/src/worker.js`
  - `python -m py_compile Prisma Cloud Ctr/internal/py/cloud_saas_api.py`
- LICFLOW3 verifiers:
  - Run all new `verify:licflow3:*` scripts.
- Existing compatibility:
  - Run required LICFLOW2/LICDESK/ADLANT4 commands.
- Do not run:
  - dev servers
  - process kill scripts
  - Prisma generate hot
  - Cloudflare deploy
  - DNS/Tunnel mutation

## Expected Final Classification

Expected: `PARTIAL_CLOUDFLARE_LIVE_EVIDENCE_REQUIRED`

Reason: repo can provide the canonical contract, 3160 bridge, and Worker/D1 scaffold, but a full hosted-cloud PASS requires authorized live Cloudflare verification for `https://app.hitechrts.com`.
