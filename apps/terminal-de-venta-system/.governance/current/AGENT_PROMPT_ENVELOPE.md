# PRISMA AUTHORITY MESH ENVELOPE

Task: Corregir LICFLOW3 Cloudflare licensing routes para que POST /api/licenses/activate, /refresh y /revoke funcionen contra app.hitechrts.com sin downgrades, sin duplicar LICFLOW2, sin tocar secretos, sin copiar DB, sin deploy automático no autorizado y preservando Worker real prisma-cloud-semilla y D1 real prisma_cloud_semilla.

Status: `PASS`

## Apps / surfaces detected

- productization
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
