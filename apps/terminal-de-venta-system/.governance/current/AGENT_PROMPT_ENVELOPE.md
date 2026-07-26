# PRISMA AUTHORITY MESH ENVELOPE

Task: FIX deuda residual Tablet 3120 posterior al PASS del ChunkLoadError. Corregir exclusivamente: (1) referencias mediaRef locales bajo /product-media/ que apuntan a archivos inexistentes, sin mutar DB ni sync y usando el packshot gobernado ya existente como fallback; (2) GET /api/pos/export/sales-today?format=csv reutilizando el read model canonico probado de sales-today; (3) migrar Tablet de middleware.ts a proxy.ts sin cambiar comportamiento; (4) actualizar solo los verifiers Tablet que resuelven esa convencion. Scope Tablet, Quality y Governance. Excluir PC, Mobile, Web, Chart Lab, Shared UI, Control Center, DB, schema, migraciones, datos, sync, Git y deploy. Runtime permitido unicamente Tablet 3120 despues de demostrar ownership. No ejecutar Prisma generate. Clasificacion Factory Ledger FIX.

Status: `PASS`

## Apps / surfaces detected

- chart-lab
- control-center
- database-sync
- mobile
- pc
- quality
- shared-ui
- tablet
- web

## Change types detected

- data_sync
- ops_hot_injection
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
- kill processes
- free ports
- start dev server
- regenerate prisma hot
- pc:typecheck hot

## Missing authority check

No missing authority patterns detected.

## Required output evidence

- Include `.governance/current` in result or diagnostic ZIP.
- Do not claim PASS without contract/gate evidence.
- For visual work, include visual evidence beyond functional smoke tests.
- For hot work, do not kill processes or regenerate Prisma.
