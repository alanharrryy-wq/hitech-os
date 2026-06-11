# PRISMA AUTHORITY MESH ENVELOPE

Task: MODIFICAR PANTALLA DE VENDER DE TABLET POS Y HACERLA SUPER ULTRA PREMIUM: pantalla de venta, productos, carrito, checkout, cobrar, touch-first, visual premium claro, Liquid, Pill, Cloudglass, Visual OS, Shared UI, backgrounds, catalogo visual, component catalog, component variants, recipe map, layer budget, Tablet Atlas, Governor, quality contracts, no fake green, rollback, evidencia visual, sin tocar PC ni Mobile salvo lectura/impacto, sin modificar pantalla de inicio salvo que el Atlas/contrato lo exija, sin matar procesos, sin liberar puertos, sin levantar dev server, sin regenerar Prisma hot

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
- liquid_glass
- ops_hot_injection
- visual

## Mandatory readset lock

Use `.governance/current/AUTHORITY_READSET.lock.json` as the authority readset for this task. Do not create patches without it.

## Required gates

- real_db_destructive_tests_forbidden
- schema_parity_required
- sync_fixture_required
- liquid_runtime_scan_required
- surface_adapter_required
- layer_budget_required
- visual_manifest_required
- visual_evidence_required
- no_fake_green
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
