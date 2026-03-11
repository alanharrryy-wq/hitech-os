# 35_ARCHITECTURAL_GRAVITY - Graph Criticality and Impact-Aware Dispatch Law

STATUS: LAW

## Purpose

This law formalizes deterministic graph-analysis and planning outputs for factory integration.

Scope:

- gravity classification
- protected-node protocol
- impact cone analysis
- dependency diff
- dispatch recommendations

## Canonical Artifact Set (JSON Canonical)

Z must produce:

- `GRAVITY_REPORT.json`
- `PROTECTED_NODES.json`
- `IMPACT_CONE_REPORT.json`
- `DEPENDENCY_DIFF.json`
- `DISPATCH_RECOMMENDATIONS.json`

Operator mirrors:

- `GRAVITY_SUMMARY.md`
- `DISPATCH_RECOMMENDATIONS.md`

Validation and automation MUST trust canonical JSON first.

## Canonical Enums

Reason-code vocabulary (shared across graph-analysis schemas):

- `ARCH_CENTRALITY_HIGH`
- `TRANSITIVE_DEPENDENCY_HIGH`
- `DIRECT_DEPENDENT_COUNT_HIGH`
- `CROSS_SCOPE_IMPACT`
- `CROSS_WORKER_IMPACT`
- `EXTERNAL_DEPENDENCY_PRESENT`
- `PROTECTED_POLICY_RULE`
- `CONTRACT_SURFACE_CRITICAL`
- `VALIDATION_BURDEN_HIGH`
- `CYCLE_MEMBERSHIP`
- `OWNERSHIP_AMBIGUOUS`
- `SNAPSHOT_NOT_COMPARABLE`
- `BASELINE_DRIFT`
- `HOTSPOT_RECURRING`
- `CHANGE_TOUCHES_PROTECTED_NODE`
- `DISPATCH_REQUIRES_A_CORE`
- `DISPATCH_REQUIRES_D_VALIDATION`
- `DISPATCH_DEFERRED_PENDING_UNBLOCK`
- `DISPATCH_BLOCKED_BY_POLICY`

Risk-level order (architectural/integration risk, not subjective importance):

- `NONE`
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Protection-level canonical values:

- `WATCHED`
- `GUARDED`
- `PROTECTED`
- `LOCKED`

Compatibility aliases (accepted for readers):

- `WATCH` -> `WATCHED`
- `ELEVATED` -> `GUARDED`
- `STRICT` -> `LOCKED`

## Structural Normalization Rules

Graph-analysis schemas use normalized structures for:

- node identity: `node_id`, `display_name`, `node_type`, `canonical_path`, `scope_id`, `owner_worker`
- scope identity: `scope_id`, `scope_type`, `scope_path`, `owner_worker`, `parent_scope_id`, `internal_only`
- dependency basis: `upstream_nodes`, `downstream_nodes`, `dependency_count`, `transitive_dependency_count`, `graph_scope_reference`
- impact radius category: `LOCAL`, `MULTI_SCOPE`, `CROSS_WORKER`, `REPO_WIDE`
- blocker taxonomy: `PROTECTED_NODE_CROSSING`, `MISSING_CONTRACT`, `OWNERSHIP_CONFLICT`, `VALIDATION_GAP`, `BASELINE_MISMATCH`, `INCOMPARABLE_SNAPSHOT`
- anomaly taxonomy: `CYCLE`, `ORPHAN`, `UNOWNED`, `UNSTABLE_HUB`, `EXTERNAL_DRIFT`, `CLASSIFICATION_REGRESSION`, `OWNERSHIP_MISMATCH`, `CONTRACT_GAP`

## Artifact Identity and Provenance

Each canonical artifact must carry:

- `artifact_type`
- `artifact_id`
- `run_id`
- `generated_at_utc`
- `schema_version`
- `schema_family`
- compatibility fields
- generator provenance
- repository provenance
- snapshot lineage

Required compatibility metadata:

- `compatibility_mode`
- `minimum_reader_version`
- `breaking_change`

Required generator provenance:

- `actor`
- `tool_name`
- `tool_version`
- `execution_mode`
- `invocation_context`
- `source_inputs`

Required repository/snapshot provenance:

- `repo_root`, `base_ref`, `head_ref`, `commit_sha`, `comparison_basis`
- `snapshot_id`, `previous_snapshot_id`, `baseline_snapshot_id`, `lineage_mode`, `graph_build_id`

## Semantic Versioning Rules

Graph-analysis schemas use semantic versions in `schema_version`.

1. PATCH:
- docs clarification and non-semantic fixes only
- must not break previously valid payloads

2. MINOR:
- additive optional fields/sections
- additive enum values only when reader tolerance is documented

3. MAJOR:
- required-field additions
- field removal/rename without alias support
- enum contraction
- semantic reinterpretation

Readers must validate against declared `schema_version` and `minimum_reader_version`.

Producer/reader model:

- producers are closed-world strict (`additionalProperties: false` by default)
- readers are compatibility-aware only where explicit aliasing is declared

## Protected Node Protocol

Protected-node mutation requires:

1. explicit declaration
2. impact-cone report
3. dependency diff
4. D-validation review
5. Z approval

Missing protocol evidence => `BLOCKED`.

## Z Responsibilities

Z must:

- classify gravity
- publish protected nodes
- publish impact cone
- publish dependency diff
- publish dispatch recommendations
- publish evidence-aligned Markdown mirrors

Z must not:

- invent features
- bypass protected-node protocol
- silently re-slice current-run ownership

## Worker-ID Compatibility

Canonical worker IDs:

- `A_core`, `B_tooling`, `C_features`, `D_validation`, `Z_aggregator`

Legacy runtime aliases accepted for compatibility:

- `A_worker`, `B_worker`, `C_worker`, `D_worker`, `Z_integrator`
