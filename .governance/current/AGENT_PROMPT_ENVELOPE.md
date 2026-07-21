# PRISMA AUTHORITY MESH ENVELOPE

Task: PC96FLOW functional data completion in PC and Tablet with shared kernel, local database schema and additive migrations, durable sync, audit, idempotency, ACK/checkpoint/conflict and quality verification. Resolve canonical owner chains for command center, sales, cash, catalog, pricing, inventory, purchasing, customers, security, organization devices, sync and licensing readiness. Complete the corresponding Tablet POS, checkout, catalog, inventory, sales, returns, shift, offline sync, settings and setup routes. Preserve unrelated current Tablet stylesheet changes.

Status: `PASS`

## Apps / surfaces detected

- database-sync
- pc
- productization
- quality
- shared-kernel
- tablet

## Change types detected

- data_sync

## Mandatory readset lock

Use `.governance/current/AUTHORITY_READSET.lock.json` as the authority readset for this task. Do not create patches without it.

## Required gates

- real_db_destructive_tests_forbidden
- schema_parity_required
- sync_fixture_required
- authority_readset_lock_required
- app_impact_matrix_required
- contract_gate_matrix_required
- rollback_required
- diagnostic_zip_on_failure
- no_fake_green

## Forbidden default actions

- kill dev processes
- free occupied ports
- start app/dev server
- regenerate Prisma hot
- delete files permanently
- force push
- global CSS blast without manifest

## Missing authority check

No missing authority patterns detected.

## Required output evidence

- Include `.governance/current` in result or diagnostic ZIP.
- Do not claim PASS without contract/gate evidence.
- For visual work, include visual evidence beyond functional smoke tests.
- For hot work, do not kill processes or regenerate Prisma.
