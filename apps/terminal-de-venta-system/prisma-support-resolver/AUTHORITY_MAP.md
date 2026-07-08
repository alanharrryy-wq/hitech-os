# Authority Map

Fecha: 2026-07-08

Clasificacion ledger: `BUILD` para este root fisico nuevo; `EXTEND_EXISTING`
para Prisma Cloud Center; `USE_AND_CONNECT` para LICFLOW2/3/4/5 y Customer
Setup ya verificados. No se reconstruyen capacidades con `doNotRebuild=true`.

| Concepto | Decision | Canonical source | Files merged into it | Duplicate sources | Legacy sources | Useful sources | Deprecated sources | Missing parts created | Implementation owner | UI surfaces affected |
|---|---|---|---|---|---|---|---|---|---|---|
| Customer | USE_AND_CONNECT | `Prisma Cloud Ctr/internal/py/command_center_store.py` + `shared/licensing/customer-setup-contract.ts` | Mapas y schemas de este root | N/A | docs productization historicos | `docs/productization/PRISMA_CUSTOMER_SETUP_MULTI_DEVICE_CONTRACT.md` | N/A | `schemas/support-search.schema.json`, `schemas/support-case.schema.json` | Prisma Cloud Center support API | Cloud Ctr #support |
| Business | USE_AND_CONNECT | `shared/licensing/customer-setup-contract.ts` | `AUTHORITY_MAP.md` concepto Business | N/A | runtime examples | `F:\PRISMA_CTX\LICENSING\activations\...\runtime\*.json` sanitized only | N/A | surface status fields | Cloud Ctr support API | Cloud Ctr, PC, Tablet, Mobile |
| License | USE_AND_CONNECT | `shared/licensing/*`, `tools/verify-licflow2.mts`, `tools/verify-licflow3.mts`, `tools/verify-licflow4.mts` | Catalog code mapping | duplicate example fixtures | `tooling/licensing/*` historical fixtures | `license-governor.ts`, `licflow3-cloud-contract.ts` | `prisma-control-center/*` references only | `catalogs/support-error-codes.json` | shared licensing + support resolver API | All support surfaces |
| Device | USE_AND_CONNECT | `shared/runtime/device-identity.ts`, `tooling/productization/schemas/device-identity.schema.json` | `schemas/device-identity.schema.json` wrapper | N/A | device08 docs | Customer Setup slots | N/A | device status mapping | shared runtime | Tablet, PC, Mobile |
| Surface | CREATE_MISSING | `schemas/surface-status.schema.json` | Status standard doc | N/A | per-surface license messages | PC/Tablet license cards | N/A | `PRISMA_SUPPORT_SURFACE_STATUS_STANDARD.md` | support resolver | Tablet, PC, Mobile |
| Setup Code | USE_AND_CONNECT | `shared/licensing/customer-setup-contract.ts` | `PRISMA_CUSTOMER_SETUP_CANONICAL_CONTRACT.md` | docs examples | `PRISMA-SETUP-STARTER` sample only | Customer Setup verifier | N/A | support issue requirements | Customer Setup | Cloud Ctr, tri-surface setup |
| Setup Link | USE_AND_CONNECT | `shared/licensing/customer-setup-contract.ts` | contract docs | N/A | productization docs | Cloud Gateway source | N/A | support bundle fields | Customer Setup | Cloud Ctr |
| Device Claim | USE_AND_CONNECT | `shared/licensing/customer-setup-contract.ts` + Cloud License Gateway source | resolver action matrix | N/A | device08 policy | `verify:customer-setup:*` | N/A | resolver actions | Customer Setup | Cloud Ctr |
| Slot | USE_AND_CONNECT | `CUSTOMER_SETUP_SLOT_LABELS` | surface status doc | N/A | docs matrices | plan provisioning catalog | N/A | slot fields in schemas | Customer Setup | Tablet, PC, Mobile |
| Runtime Identity | USE_AND_CONNECT | `shared/runtime/*`, `tools/provision-prisma-runtime.mjs` | runtime config contract wrapper | runtime examples | productization runtime docs | external sanitized runtime JSON | N/A | diagnostics schema fields | Runtime | PC, Tablet, Mobile |
| Local License | USE_AND_CONNECT | `shared/licensing/local-license-store.ts`, `license-loader.ts` | support issue mappings | duplicate signed fixtures | tooling fixtures | `license-governor.ts` | N/A | local missing/invalid codes | shared licensing | PC, Tablet |
| Signed License | USE_AND_CONNECT | `shared/licensing/license-signature.ts`, `signed-license-types.ts` | security codes | duplicate fixture folders | tooling signing docs | signature verifiers | N/A | support action blocks | shared licensing | Cloud Ctr |
| Terminal | USE_AND_CONNECT | runtime context + POS server contracts | POS error codes | N/A | productization docs | Tablet POS licensing service | N/A | terminal issue codes | Tablet/PC runtime | Tablet |
| Cash Session | CREATE_MISSING | support resolver catalog | N/A | N/A | POS docs | Tablet POS signals | N/A | cash session issue codes | Tablet POS | Tablet |
| Feature Gate | USE_AND_CONNECT | `shared/licensing/feature-keys.ts`, `feature-resolver.ts` | `catalogs/feature-gates.json` | `tooling/productization/catalogs/license-local/feature-key-catalog.full.json` | productization feature docs | feature resolver | N/A | resolver mapping | shared licensing | PC, Tablet, Mobile |
| Support Issue | CREATE_MISSING | `schemas/support-issue.schema.json` | required case fixture | `support-ticket.schema.json` is ticket-only | support bundle docs | productization support docs | N/A | unified model | support resolver | All |
| Support Bundle | EXTEND_EXISTING | productization support bundle docs/schemas | `PRISMA_SUPPORT_BUNDLE_STANDARD.md` | multiple support bundle specs | `quality/docs/support-pack.md` | redaction policy | N/A | support bundle schema wrapper | support resolver | Cloud Ctr |
| Diagnostics | EXTEND_EXISTING | `Prisma Cloud Ctr/internal/py/license_ops_api.py`, `cloud_saas_api.py`, `licflow4_admin_bridge.py` | support API endpoint | N/A | old control center | diagnostics exporters | `prisma-control-center/*` as authority | support diagnose API | Cloud Ctr | Cloud Ctr #support |
| Resolver Action | CREATE_MISSING | `catalogs/resolver-actions.json` | action matrix contract | N/A | admin bridge action docs | LICFLOW4 bridge | N/A | simulate/apply contract | support resolver API | Cloud Ctr #support |
| Remote Operation | USE_AND_CONNECT | `licflow4_admin_bridge.py` | resolver action matrix | N/A | LICFLOW4 docs | dry-run/confirm flow | N/A | support action wrappers | License Admin Bridge | Cloud Ctr |
| Evidence Export | EXTEND_EXISTING | `export_diagnostics()` + support bundle policies | `evidence/evidence-export-contract.md` | support-pack profiles | old diagnostics exports | redaction policies | N/A | support export-case shape | Cloud Ctr support API | Cloud Ctr |

## Fuentes bloqueadas

- `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\private-key.pem`:
  `BLOCK_SECRET_RISK`. No se copia, no se imprime, no entra al root canonico.
