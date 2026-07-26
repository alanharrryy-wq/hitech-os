# PRISMA Authority Mesh Report

- Status: `PASS`
- Task: `FIX deuda residual Tablet 3120 posterior al PASS del ChunkLoadError. Corregir exclusivamente: (1) referencias mediaRef locales bajo /product-media/ que apuntan a archivos inexistentes, sin mutar DB ni sync y usando el packshot gobernado ya existente como fallback; (2) GET /api/pos/export/sales-today?format=csv reutilizando el read model canonico probado de sales-today; (3) migrar Tablet de middleware.ts a proxy.ts sin cambiar comportamiento; (4) actualizar solo los verifiers Tablet que resuelven esa convencion. Scope Tablet, Quality y Governance. Excluir PC, Mobile, Web, Chart Lab, Shared UI, Control Center, DB, schema, migraciones, datos, sync, Git y deploy. Runtime permitido unicamente Tablet 3120 despues de demostrar ownership. No ejecutar Prisma generate. Clasificacion Factory Ledger FIX.`
- Repo: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Authority files found: `822`
- Missing patterns: `0`
- Critical missing: `0`
- Apps: `chart-lab, control-center, database-sync, mobile, pc, quality, shared-ui, tablet, web`
- Change types: `data_sync, ops_hot_injection, visual`

## Generated files

- AUTHORITY_READSET.lock.json
- APP_IMPACT_MATRIX.md
- CONTRACT_AND_GATE_MATRIX.json
- MISSING_OR_UNMAPPED_RISK.md
- AGENT_PROMPT_ENVELOPE.md
- VISUAL_CAPABILITY_MATRIX.json
- VISUAL_CAPABILITY_MATRIX.md
- VISUAL_STACK_DECISION.md
- APP_VISUAL_EXPLOITATION_MATRIX.md
- VISUAL_EXPLOITATION_CONTRACT.md
- VISUAL_EXPLOITATION_CONTRACT.json
- APP_CAPABILITY_REQUIREMENTS.json
- APP_CAPABILITY_REQUIREMENTS.md
- SCREEN_VISUAL_STACK_PLAN.md
- PREMIUM_ACCEPTANCE_BAR.md
- USED_REJECTED_REQUIREMENT.md
