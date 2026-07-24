# PRISMA Used / Rejected Capability Requirement

Every visual/premium result package must include a completed table with these columns:

| Column | Description |
|---|---|
| capability | Capability/library/component id. |
| available | Was it detected in repo/package/lock/catalog evidence? |
| required_level | must_use, should_use, consider_required, bounded_optional, high_risk_optional, forbidden_for_scope, not_available. |
| used | yes/no. |
| where_used | Changed file(s), component(s), layer(s), or n/a. |
| why_used_or_rejected | Concrete task-specific rationale, not generic filler. |
| governance_evidence | Recipe/map/component/contract/atlas/layer-budget evidence consulted. |
| performance_layer_risk | Risk and mitigation. |
| visual_evidence | Screenshot/video/manual pending marker. |

## Gate

No premium/visual PASS is valid unless this used/rejected table is completed with concrete file-level and governance-level rationale.
