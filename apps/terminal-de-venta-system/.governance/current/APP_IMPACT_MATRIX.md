# PRISMA App Impact Matrix

- Task: `FIX deuda residual Tablet 3120 posterior al PASS del ChunkLoadError. Corregir exclusivamente: (1) referencias mediaRef locales bajo /product-media/ que apuntan a archivos inexistentes, sin mutar DB ni sync y usando el packshot gobernado ya existente como fallback; (2) GET /api/pos/export/sales-today?format=csv reutilizando el read model canonico probado de sales-today; (3) migrar Tablet de middleware.ts a proxy.ts sin cambiar comportamiento; (4) actualizar solo los verifiers Tablet que resuelven esa convencion. Scope Tablet, Quality y Governance. Excluir PC, Mobile, Web, Chart Lab, Shared UI, Control Center, DB, schema, migraciones, datos, sync, Git y deploy. Runtime permitido unicamente Tablet 3120 despues de demostrar ownership. No ejecutar Prisma generate. Clasificacion Factory Ledger FIX.`
- Status: `PASS`
- Generated: `2026-07-26T01:50:04-06:00`

| App / surface | Applies | Authority files found | Mutation allowed | Exclusion / notes |
|---|---:|---:|---:|---|
| tablet | yes | 33 | yes | Selected by task. |
| pc | yes | 35 | yes | Selected by task. |
| mobile | yes | 87 | yes | Selected by task. |
| chart-lab | yes | 13 | yes | Selected by task. |
| web | yes | 7 | yes | Selected by task. |
| control-center | yes | 95 | yes | Selected by task. |
| shared-ui | yes | 102 | yes | Selected by task. |
| backgrounds | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| quality | yes | 231 | no | Selected by task. |
| database-sync | yes | 49 | yes | Selected by task. |
| productization | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| shared-kernel | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
