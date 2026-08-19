# PRISMA PC Customer Experience Closure — Wave 2

Status: `SOURCE_CLOSURE_READY_RUNTIME_EVIDENCE_PENDING`

Certification: `NOT_YET_PC_CUSTOMER_EXPERIENCE_CLOSURE_CERTIFIED`

This document is the durable checklist and continuity record for PC Customer Experience Closure Wave 2. It does not reopen PC Surface Truth Wave 1 and it does not authorize merge.

## 1. Frozen continuity base

PC Surface Truth Wave 1 is `DONE / doNotRebuild / VERIFY_ONLY_ON_DIRECT_DRIFT`.

- PR: `#287`
- certified head: `be81c188cb8619fb25a54d91cbdab044414e6149`
- merge commit: `53365ed66c836fbabc77baa714bb382afd1a2b52`
- certified route count: `28`
- runtime result: `28 PASS / 0 WARN / 0 FAIL`
- V03 visual gate: `10 PASS / 0 WARN / 0 FAIL`

Frozen Wave 1 routes:

`/dashboard`, `/sales-control`, `/cash-sessions`, `/metricas-dia`, `/purchasing`, `/ordenes-compra`, `/receiving`, `/recepcion-proveedor`, `/incidencias-recepcion`, `/replenishment`, `/senal-reabasto`, `/exportables`, `/prisma-insights`, `/audit`, `/settings/license`, `/outbox-operativo`, `/tablas-operativas`, `/detalle-registros`, `/estados-operativos`, `/glosario`, `/forecast-basico`, `/acciones-masivas`, `/contratos-reporte`, `/scorecards-negocio`, `/tablero-kpi`, `/vistas-ejecutivas`, `/filtros-avanzados`, `/filtros-fecha`.

Wave 2 does not convert findings inside those routes into new defects unless post-merge direct drift is demonstrated.

## 2. Authority

Fresh task-exact Authority Mesh used for this Wave 2 lane:

- profile: `pc-customer-experience-closure-wave2-v4`
- run: `32155155537`
- artifact ID: `9331444690`
- artifact name: `prisma-automesh-707041e920560418-32155155537-1`
- artifact digest: `sha256:736f14c18d5d6a241d28f068067be1020555bf746e3ce319b64e3b93fffdeb39`
- authorized head: `d14effee1a1223cc772247ea9d7ec8547dc15c78`

Scope lock:

- PC only.
- No Tablet, Mobile, Chart Lab or Shared UI writes.
- No Prisma schema, migrations, seeds or database writes.
- No shared sync architecture changes.
- No Factory Ledger, Code Atlas, RIFAT, UIMAP or Visual Governor mutations.
- No deploy, process, port or user dev-server manipulation.
- Shared/other-surface dependency => `BLOCKED_SHARED_DEPENDENCY`.
- No fake green and no merge authorization.

## 3. Delta inventory

### Customer-facing Wave 2 universe

These are the current customer-facing routes outside the 28 frozen Wave 1 routes that remain in the Wave 2 customer lane:

1. `/catalog`
2. `/proveedores`
3. `/clientes`
4. `/sync`
5. `/devices`
6. `/settings`
7. `/stock`
8. `/movements`
9. `/counts`
10. `/auditoria-inventario`
11. `/salud-barcodes`

### Internalized / support-only / duplicate projections

These routes remain addressable where compatibility or support requires it, but are removed from customer secondary navigation because they are duplicate, legacy, diagnostic or insufficiently productized projections:

- `/ajustes-inventario`
- `/alertas-ejecutivas`
- `/alertas-operativas`
- `/catalogo-activo`
- `/conteos-operativos`
- `/data-quality`
- `/integridad-barcodes`
- `/license-runtime`
- `/politica-precios`
- `/sync-operativo`
- `/tablet-communication`
- `/validacion-catalogo`

This is `wrong visibility / duplicate projection / support-only governance`, not feature deletion.

## 4. Customer-facing checklist

| Area | Status | Evidence / resolution |
|---|---|---|
| Wave 1 anti-rework | PASS | Exact frozen 28-route set retained; known Wave 1 page/component/service blobs are asserted by the Wave 2 source verifier. |
| Primary Wave 2 visibility | PASS_SOURCE | Catalog, Proveedores, Clientes, Sync, Equipos and Configuración remain primary customer destinations. |
| Legacy/duplicate secondary visibility | FIXED_SOURCE | Legacy `iXX`, duplicate, diagnostic and unproductized routes are fail-closed from customer secondary navigation. |
| Owner/data truth | PASS_SOURCE | Visible Wave 2 owners read existing services/repositories; no new fake data source was introduced. |
| Raw filesystem / ENOENT leakage | FIXED_SOURCE | Catalog/media workspaces no longer project raw exception details or filesystem guidance. |
| Raw Prisma / SQL / migration leakage | FIXED_SOURCE_FOR_WAVE2 | Wave 2 customer workspaces and opted-in APIs use customer-safe failures. Wave 1 routes remain frozen and are not rewritten here. |
| Internal ORM/model/endpoint/owner vocabulary | FIXED_OR_INTERNALIZED | Visible Wave 2 projections were humanized; technical projections that were not customer-ready were internalized. |
| Placeholder identity | FIXED_SOURCE | Sync/Devices project `Prisma Original Customer` to neutral customer copy instead of exposing placeholder identity. |
| Sync/device machine identifiers | FIXED_SOURCE | Customer tables are rebuilt from allowed columns and do not forward diagnostic row metadata or direct GET API links. |
| Customer API unexpected failures | FIXED_SOURCE | Customers, product media, product variants, Sync and Devices opt in to customer-safe 500 responses. |
| Devices license API guard | FIXED_SOURCE | `/api/backoffice/devices` now uses `guardPcFeatureForApi("pc.open")`. |
| Customers focused source evidence | PASS_SOURCE | CRUD wiring, read-after-write flow, customer-safe failures and dedicated loading/error states are source-verifiable. |
| Customers E2E runtime evidence | EVIDENCE_GAP_RUNTIME | Must prove create/search/open/update against isolated runtime evidence before certification. |
| Catalog actions | FIXED_SOURCE | Misleading adjustment/edit CTAs were replaced by real read/navigation actions or honest unavailable states. |
| Catalog image duplication | FIXED_SOURCE | Product ficha has one image preview owner instead of duplicated previews. |
| Stock direct adjustment | HONESTLY_UNAVAILABLE | No fake mutation CTA. Direct adjustment is shown unavailable; read paths remain available. |
| Counts loading/error | FIXED_SOURCE | Dedicated loading exists; error boundary no longer renders raw `error.message`. |
| Inventory audit loading/error | FIXED_SOURCE | Dedicated loading and customer-safe error boundaries added. |
| Barcode health loading/error | FIXED_SOURCE | Dedicated loading and customer-safe error boundaries added. |
| Movements loading/error | FIXED_SOURCE | Runtime/path engineering copy removed from loading/error states. |
| Proveedores copy | FIXED_SOURCE | Customer copy is isolated to `/proveedores`; frozen purchasing/receiving/replenishment routes keep Wave 1 output. |
| Settings copy | FIXED_SOURCE | `/settings` uses a customer projection while frozen Wave 1 module-overview routes retain their prior output. |
| Pricing policy visibility | INTERNALIZED_PENDING_PRODUCTIZATION | Capability is retained, but the current JSON/version/idempotency-heavy UI is not presented as customer-ready. |
| Data Quality / Tablet Communication visibility | INTERNALIZED_PENDING_ROLE_PRODUCTIZATION | Diagnostic capabilities are retained without pretending their current projection is a general customer surface. |
| Reports/exports | DONE_WAVE1_FROZEN | `/exportables` is Wave 1 certified; no re-audit without drift. |
| Receiving overlap | DONE_WAVE1_FROZEN | Receiving routes are Wave 1 certified; not reopened. |
| Replenishment overlap | DONE_WAVE1_FROZEN | Replenishment routes are Wave 1 certified; not reopened. |
| Hidden filter 404 behavior | DONE_WAVE1_FROZEN | Hidden filter routes are part of frozen Wave 1 evidence. |
| Role/license API gating | PASS_SOURCE_FOR_INSPECTED_APIS | Inspected Wave 2 customer APIs are guarded. |
| Role/license navigation visibility | EVIDENCE_GAP_RUNTIME_SHARED_NAV | Primary/secondary AppShell navigation has not been proven against concrete role/license states. No PASS is claimed. |
| Contradictory state/value semantics | EVIDENCE_GAP_RUNTIME | Requires populated runtime evidence; source absence of a contradiction is not proof. |
| Progressive disclosure | PASS_SOURCE_RUNTIME_VISUAL_PENDING | Catalog/inventory use master/detail or row details; Sync/Devices strip diagnostic expansion metadata. |
| Loading/empty/error states | PASS_SOURCE | The 11 Wave 2 customer routes are required by the source verifier to have page/loading/error boundaries. |
| Offline/unavailable/blocked semantics | PASS_SOURCE_PARTIAL_RUNTIME_PENDING | Unavailable and blocked paths are explicit in source; actual offline/runtime behavior still requires execution evidence. |
| Responsive populated-state readiness | EVIDENCE_GAP_RUNTIME_VISUAL | Requires populated screenshots at 1440x900 and 1366x768. |
| Customer journeys | EVIDENCE_GAP_RUNTIME | Source contracts are ready; end-to-end journeys remain mandatory before final certification. |

## 5. P0/P1 hypotheses from Authority Mesh

| Hypothesis | Classification |
|---|---|
| P0 raw filesystem / ENOENT | `FIXED_WAVE2` |
| P0 Prisma / SQL / migration leakage | `FIXED_WAVE2_AND_WAVE1_FROZEN` |
| P0 ORM / endpoint / owner / gate vocabulary | `FIXED_OR_INTERNALIZED_WAVE2` |
| P0 license internal IDs | `CONFIRMED_WAVE1_FROZEN` |
| P0 machine sync/runtime IDs | `FIXED_WAVE2` |
| P0 placeholder identity | `FIXED_WAVE2` |
| P0 contradictory state/value semantics | `EVIDENCE_GAP_RUNTIME` |
| P0 Clientes focused evidence | `SOURCE_READY_RUNTIME_EVIDENCE_GAP` |
| P1 Receiving purpose overlap | `DONE_WAVE1_FROZEN` |
| P1 Replenishment purpose overlap | `DONE_WAVE1_FROZEN` |
| P1 duplicate data-quality projections | `FIXED_OR_INTERNALIZED_WAVE2` |
| P1 hidden-filter 404 | `DONE_WAVE1_FROZEN` |
| P1 generic empty states | `FIXED_WAVE2_SOURCE` |
| P1 progressive disclosure | `PASS_SOURCE_RUNTIME_VISUAL_PENDING` |
| P1 populated responsive readiness | `EVIDENCE_GAP_RUNTIME_VISUAL` |
| P1 role/license navigation visibility | `EVIDENCE_GAP_RUNTIME_SHARED_NAV` |

## 6. Focused source verifier

Canonical verifier:

`tools/verify_pc_customer_experience_closure_wave2.mjs`

Package command:

`pnpm run verify:pc-customer-experience-wave2`

The verifier is boundary-aware. It checks exact customer-visible contracts instead of flagging arbitrary internal substrings. It verifies:

- the 11 Wave 2 customer routes have page/loading/error boundaries;
- those error boundaries do not render raw `error.message`;
- the three known Wave 1 frozen blobs remain unchanged;
- the six primary Wave 2 routes remain in navigation;
- internalized routes remain fail-closed from customer secondary navigation;
- customer services do not project raw exception or migration guidance;
- customer-safe API failure is opt-in so Wave 1 callers are not silently changed;
- Catalog, Customers, Inventory, Sync/Devices, Proveedores, Settings and Barcode Health customer-copy invariants;
- license/API guards for inspected Wave 2 endpoints;
- all Authority Mesh P0/P1 classifications and remaining evidence gaps.

A source-gate PASS is not equivalent to runtime certification.

## 7. Customer journeys required for final certification

Runtime evidence must cover journeys from live authority, without inventing features:

1. Catalog: enter → search/filter → open product → inspect stock/codes/movements → execute only real actions or observe honest unavailable state.
2. Suppliers: enter → inspect orders/receipts/replenishment context → follow real owner paths.
3. Customers: enter → search → open → create/update → observe success/error states against real customer owner.
4. Sync: enter → inspect freshness/activity → execute permitted sync action → observe success/error/blocked state.
5. Devices: enter → inspect equipment state → confirm license guard → execute only authorized action.
6. Settings: enter → inspect users/roles/terminals → verify visibility for concrete role/license combinations.
7. Inventory: stock → movements → counts → audit → barcode health, with no dead action and no internal leakage.

## 8. Runtime evidence still required

Before `PC_CUSTOMER_EXPERIENCE_CLOSURE_CERTIFIED` may be declared, obtain:

- focused verifier execution result;
- isolated PC runtime;
- screenshots for all Wave 2 customer routes, including populated states where available;
- 1440x900 and 1366x768 visual evidence;
- browser console errors;
- page errors;
- server logs;
- route/redirect assertions;
- real-data / fail-closed assertions;
- role/license visibility evidence for concrete entitlement states;
- customer journey results;
- final artifact manifest.

If runtime infrastructure cannot produce one of these artifacts, classify it `EVIDENCE_GAP` or `BLOCKED`, never PASS.

## 9. Merge rule

No merge is authorized by this document or by source-gate success.

Merge remains explicitly blocked until:

1. source gate is green;
2. CI/repository checks are green;
3. remaining runtime/visual/role evidence is either proven PASS or explicitly accepted as a separate blocked lane by the operator;
4. the operator gives explicit final merge authorization.

## 10. Current closure statement

Wave 2 has a bounded, evidence-driven customer surface inventory. Known customer-facing source leaks and misleading projections have been fixed or internalized without rebuilding Wave 1. The remaining blockers are evidence blockers, not automatically defects.

Current truthful state:

`PC_CUSTOMER_EXPERIENCE_CLOSURE_WAVE2_SOURCE_READY_RUNTIME_EVIDENCE_PENDING`

Do not promote to `PC_CUSTOMER_EXPERIENCE_CLOSURE_CERTIFIED` until the runtime and customer-journey gates above are satisfied.
