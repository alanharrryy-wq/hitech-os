# LICFLOW2 Continuation

Generated: 2026-07-02

## Current State

LICFLOW2 adds explicit offline, online, and hybrid activation modes on top of existing LICDESK4/ADLANT4 signed licensing.

Implemented:

- Shared activation module: `shared/licensing/licflow2-activation.ts`
- Activation package apply support: `tools/provision-prisma-runtime.mjs`
- Verifier suite: `tools/verify-licflow2.mts`
- Package scripts: `verify:licflow2:*`
- Shell Lab License Ops activation summary
- Mobile data-plane activation metadata
- Process/support/security/rollback docs

## Rules For Next Agent

- Do not treat generated activation packages as repo source.
- Do not package private keys or DBs.
- Do not claim hosted online activation without real hosted endpoint evidence.
- Do not use demo IDs or `DEVELOPMENT` as productive customer truth.
- Preserve Tablet local-sale autonomy and PC backoffice/governance role.

## Expected Validation

Run from `apps/terminal-de-venta-system`:

- `pnpm run verify:licflow2:inventory`
- `pnpm run verify:licflow2:offline`
- `pnpm run verify:licflow2:online`
- `pnpm run verify:licflow2:hybrid`
- `pnpm run verify:licflow2:support`
- `pnpm run verify:licflow2:no-duplicates`
- `pnpm run verify:licflow2:no-secrets`
- `pnpm run verify:licflow2:no-db-commit`
- `pnpm run verify:licflow2:no-demo-leaks`
- `pnpm run verify:licdesk:signing`
- `pnpm run verify:licdesk:governor`
- `pnpm run verify:adlant4:sync-e2e`
