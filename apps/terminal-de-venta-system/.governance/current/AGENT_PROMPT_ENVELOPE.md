# PRISMA AUTHORITY MESH ENVELOPE

Task: PRISMA data-to-surface certification: PC sales-control, Tablet POS, Mobile client-first home and tabs, Chart Lab runtime counters, Data Lifecycle dashboard; correct loaders APIs queries contracts and verifiers without browser runtime servers Prisma generate migrations or production changes

Status: `PASS`

## Apps / surfaces detected

- backgrounds
- chart-lab
- control-center
- database-sync
- mobile
- pc
- productization
- quality
- shared-kernel
- shared-ui
- tablet
- web

## Change types detected

- data_sync
- visual

## Mandatory readset lock

Use `.governance/current/AUTHORITY_READSET.lock.json` as the authority readset for this task. Do not create patches without it.

## Required gates

- real_db_destructive_tests_forbidden
- schema_parity_required
- sync_fixture_required
- visual_manifest_required
- visual_evidence_required
- layer_budget_required
- no_fake_green
- authority_readset_lock_required
- app_impact_matrix_required
- contract_gate_matrix_required
- rollback_required
- diagnostic_zip_on_failure
- no_fake_green
- visual_capability_matrix_required
- visual_stack_decision_required
- app_visual_exploitation_matrix_required
- visual_capability_rejection_reasons_required
- visual_exploitation_contract_required
- app_capability_requirements_required
- screen_visual_stack_plan_required
- premium_acceptance_bar_required
- used_rejected_capability_matrix_required
- layer_budget_decision_required
- visual_evidence_or_pending_verification_required

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
