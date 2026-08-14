# Code Atlas Phase 0 Capability Census

**Status:** `PASS_STATIC_REMOTE_CENSUS`  
**Product mutation:** `BLOCKED_FRESH_EXACT_TASK_AUTHORITY_MESH_REQUIRED`  
**Merge:** `BLOCKED_PENDING_FRESH_AUTHORITY_MESH_AND_PHASE0_REVIEW`  
**Baseline:** `main@bf4c61d16ab71a09d5f84de81be3d4e1b8c58134`  
**Date:** 2026-08-14

## Purpose

Create a deterministic, no-fake-green Phase 0 census before completing Code Atlas. This artifact classifies the live Operational Evidence Atlas 50 registry and defines the shared foundations that should be built before individual placeholders are replaced.

This is a **static remote preflight**, not a motor-generated Authority Mesh. The session can inspect and write GitHub, but it cannot dispatch a task-parameterized Authority Mesh run and the sandbox cannot clone the repository. No exact-task Mesh result is fabricated.

## Authority decision

- Factory Ledger gate and ledger were consulted.
- The Ledger has broad Code Atlas evidence, but it does not individually certify the 50 operational capabilities.
- The live registry contains **50 capabilities**: `35 implemented_v1`, `14 placeholder_v1`, `1 placeholder_blocked`.
- All 35 `implemented_v1` entries are classified **VERIFY_AND_HARDEN**, because their registry notes explicitly describe safe heuristic evidence that should be improved with real contracts.
- The 14 placeholders are **BUILD**.
- Multi-Tenant Leakage Guard remains **BLOCKED** until real tenant-scope authority and negative cross-tenant testing exist.

## Hard findings

### 1. No dedicated Operational Evidence Atlas 50 test suite

`tools/code-atlas/tests/` currently contains tests for Legal Readiness, Smart AllMesh and UI Bridge, but no dedicated suite for the 50-capability operational subsystem.

Before any capability leaves `implemented_v1` or placeholder state, add capability contract tests, negative tests, fail-closed tests, production-green boundary regressions and deterministic fixture/snapshot tests where applicable.

### 2. Scoped LICSCOPE green must not become global green

`features50.py` contains the `DBEVLINK_LICSCOPE_BRIDGE_AUTOPATCH` bridge, while `licscope_bridge.py` can project `productionGreenAllowed` and scoped manifest status for the LICSCOPE lane.

That bridge may remain valid, but its provenance and scoping must be explicit. A `PRODUCTION_CERTIFIED_LICSCOPE_LANE` result must never certify unrelated Atlas capabilities, tenants, databases, routes or surfaces.

### 3. Implemented V1 is not equivalent to DONE

Phase 0 deliberately does not rename or cosmetically promote the 35 V1 capabilities. Promotion requires, at minimum:

`HEURISTIC -> SOURCE_BACKED -> CONTRACT_BACKED -> CROSSCHECKED -> NEGATIVE_TESTED -> REPRODUCIBLE`

Add `RUNTIME_BACKED` only when the capability genuinely requires and possesses fresh runtime evidence.

### 4. Multi-Tenant Leakage Guard remains blocked

A green leakage verdict requires authoritative end-to-end scope:

`tenant -> business -> store/site -> device/session -> entity/event -> canonical projection`

and negative tests proving that cross-tenant access/association is rejected or detected. Naming conventions such as `tenantId` or `businessId` alone are insufficient.

## Shared implementation phases

| Phase | Foundation | Purpose |
|---|---|---|
| P1 | Evidence Core V2 | Stable evidence identity, provenance, confidence, source-level and freshness metadata. |
| P2 | Temporal + Diff | Snapshot contract, deterministic diff, timeline and staleness semantics. |
| P3 | Entity + Provenance Graph | Unified graph for orphan detection, lineage and runtime evidence links. |
| P4 | Operational Assurance | Surface roles, audit completeness, required evidence and golden-path comparison. |
| P5 | Risk + Scope | Explicit risk scoring policy and tenant-isolation contract. |
| P6 | Query Layer | Read-only indexed query contract over Atlas knowledge. |
| P7 | Investigator UI | Entity detail, history and journey views built on the query/graph layers. |
| P8 | V1 Hardening | Upgrade the 35 heuristic V1 capabilities using real contracts and negative tests. |
| P9 | Productization | Neutral core/profile adapters, compatibility, packaging and externalization after closure. |

## Capability census

| # | Capability ID | Capability | Registry | Phase 0 | Target |
|---:|---|---|---|---|---|
| 1 | `operational_evidence_atlas_row_level` | Operational Evidence Atlas row-level | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 2 | `client_followup_atlas` | Client Follow-up Atlas / CLIENT_OPERATIONS_MATRIX | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 3 | `device_claim_crosscheck` | Device Claim Crosscheck | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 4 | `sales_lineage_matrix` | Sales Lineage Matrix | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 5 | `flow_health_map` | Flow Health Map | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 6 | `breakage_radar` | Breakage Radar | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 7 | `snapshot_diff_engine` | Snapshot Diff Engine | `placeholder_v1` | **BUILD** | `P2_TEMPORAL_DIFF` |
| 8 | `contract_coverage_matrix` | Contract Coverage Matrix | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 9 | `customer_visible_scanner` | Customer Visible Scanner | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 10 | `surface_role_matrix` | Surface Role Matrix | `placeholder_v1` | **BUILD** | `P4_OPERATIONAL_ASSURANCE` |
| 11 | `operational_timeline` | Operational Timeline | `placeholder_v1` | **BUILD** | `P2_TEMPORAL_DIFF` |
| 12 | `why_this_is_red` | WHY_THIS_IS_RED | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 13 | `client_risk_score` | Client Risk Score | `placeholder_v1` | **BUILD** | `P5_RISK_SCOPE` |
| 14 | `next_best_action_engine` | Next Best Action Engine | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 15 | `orphan_detector` | Orphan Detector | `placeholder_v1` | **BUILD** | `P3_ENTITY_PROVENANCE_GRAPH` |
| 16 | `duplicate_detector` | Duplicate Detector | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 17 | `staleness_monitor` | Staleness Monitor | `placeholder_v1` | **BUILD** | `P2_TEMPORAL_DIFF` |
| 18 | `schema_drift_guard` | Schema Drift Guard | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 19 | `fixture_contamination_scanner` | Fixture Contamination Scanner | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 20 | `audit_completeness_matrix` | Audit Completeness Matrix | `placeholder_v1` | **BUILD** | `P4_OPERATIONAL_ASSURANCE` |
| 21 | `data_lineage_graph` | Data Lineage Graph | `placeholder_v1` | **BUILD** | `P3_ENTITY_PROVENANCE_GRAPH` |
| 22 | `impact_radius_calculator` | Impact Radius Calculator | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 23 | `safe_fix_recommendation_map` | Safe Fix Recommendation Map | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 24 | `verifier_coverage_map` | Verifier Coverage Map | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 25 | `runtime_evidence_links` | Runtime Evidence Links | `placeholder_v1` | **BUILD** | `P3_ENTITY_PROVENANCE_GRAPH` |
| 26 | `api_data_map` | API Data Map | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 27 | `secret_exposure_guard` | Secret Exposure Guard | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 28 | `production_gate_readiness` | Production Gate Readiness | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 29 | `human_operator_summary` | Human Operator Summary | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 30 | `machine_continuation_pack` | Machine Continuation Pack / CONTINUATION_SUPREME | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 31 | `atlas_query_console` | Atlas Query Console | `placeholder_v1` | **BUILD** | `P6_QUERY_LAYER` |
| 32 | `entity_detail_drawer` | Entity Detail Drawer | `placeholder_v1` | **BUILD** | `P7_INVESTIGATOR_UI` |
| 33 | `evidence_confidence_score` | Evidence Confidence Score | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 34 | `ownership_map` | Ownership Map | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 35 | `do_not_touch_map` | Do Not Touch Map | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 36 | `safe_scope_guard` | Safe Scope Guard | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 37 | `data_quality_ruleset` | Data Quality Ruleset | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 38 | `reconciliation_recipes` | Reconciliation Recipes | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 39 | `alert_rules_export` | Alert Rules Export | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 40 | `evidence_bundle_index` | Evidence Bundle Index | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 41 | `pii_privacy_classifier` | PII/Privacy Classifier | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 42 | `support_ticket_generator` | Support Ticket Generator | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 43 | `release_readiness_matrix` | Release Readiness Matrix | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 44 | `historical_trend_mini_atlas` | Historical Trend Mini Atlas | `placeholder_v1` | **BUILD** | `P7_INVESTIGATOR_UI` |
| 45 | `trust_source_level_per_datum` | Trust/source level per datum | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 46 | `atlas_manifest_plus` | ATLAS_MANIFEST_PLUS | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 47 | `can_patch_decision` | CAN_PATCH_DECISION | `implemented_v1` | **VERIFY_AND_HARDEN** | `P8_V1_HARDENING` |
| 48 | `client_setup_journey_map` | Client Setup Journey Map | `placeholder_v1` | **BUILD** | `P7_INVESTIGATOR_UI` |
| 49 | `multi_tenant_leakage_guard` | Multi-Tenant Leakage Guard | `placeholder_blocked` | **BLOCKED** | `P5_RISK_SCOPE` |
| 50 | `golden_path_comparator` | Golden Path Comparator | `placeholder_v1` | **BUILD** | `P4_OPERATIONAL_ASSURANCE` |

## Exit gates by family

### Temporal family
`Snapshot Diff Engine`, `Operational Timeline`, `Staleness Monitor` and `Historical Trend Mini Atlas` must share stable snapshot identity, timestamps and freshness policies instead of implementing four separate interpretations of time.

### Graph family
`Orphan Detector`, `Data Lineage Graph`, `Runtime Evidence Links` and `Audit Completeness Matrix` must use a shared entity/provenance graph. A relation inferred by naming is evidence of a candidate edge, not proof of a physical or runtime constraint.

### Assurance family
`Surface Role Matrix`, `Golden Path Comparator` and `Client Setup Journey Map` must consume governed surface/event/evidence contracts rather than Markdown-only claims.

### Query/UI family
`Atlas Query Console` must be read-only and schema-bound. `Entity Detail Drawer`, historical views and journey views should consume the same query/index contract, not scan the repository independently.

### Risk family
`Client Risk Score` requires an explicit versioned scoring contract with signal, severity, confidence, weight, decay, threshold and explanation. `Multi-Tenant Leakage Guard` remains blocked until the real tenant-scope contract is certifiable end to end.

## Non-mutation rules

1. Do not change `tools/code-atlas/code-atlas.py` or `visualgdeep.py` in Phase 0.
2. Do not mutate product apps, runtime, databases, Prisma, processes, ports or dev servers.
3. Do not convert scoped evidence into global production green.
4. Do not replace placeholders with decorative output. Every replacement requires real evidence, a contract and fail-closed tests.
5. Do not merge this branch until a **fresh exact-task Authority Mesh** is produced and reconciled with this census.

## Next gate

Run a fresh exact-task Authority Mesh for:

> Complete Code Atlas by maturing all 35 implemented_v1 capabilities and replacing the 14 placeholder_v1 plus 1 placeholder_blocked, preserving modular architecture, neutrality/profile boundaries and anti-fake-green contracts.

Then reconcile its `AUTHORITY_READSET.lock.json`, app/surface impact matrix, contract/gate matrix, missing/unmapped risk, mandatory Layer Map and authority report against `CODE_ATLAS_PHASE0_CAPABILITY_CENSUS.json`.

Only after that reconciliation may Code Atlas product/source implementation begin.
