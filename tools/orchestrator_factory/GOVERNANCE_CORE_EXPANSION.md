# Expanded Governance Core

This document maps the expanded governance core to the required capabilities of the final framework.

## Constitutional purpose

The governance core exists to keep multi-chat execution coherent. It prevents:
- duplicate work
- path collisions
- contract drift
- prompt drift
- non-canonical documentation growth
- tactical artifacts outranking policy

## Governance capabilities and primary files

| Capability | Primary file(s) |
|---|---|
| operating model | `00-governance-core/docs/control/codex_operating_model.md` |
| run lifecycle | `00-governance-core/docs/control/run_lifecycle.md` |
| run ID standard | `00-governance-core/docs/control/run_id_standard.md` |
| idea intake and homologation | `00-governance-core/docs/control/idea_intake_and_homologation.md` |
| glossary | `00-governance-core/docs/dictionaries/global_dictionary.md` |
| naming conventions | `00-governance-core/docs/dictionaries/naming_conventions.md` |
| boundaries and ownership | `00-governance-core/docs/parallelism/path-ownership-matrix.yaml`, `00-governance-core/docs/standards/paths-and-boundaries.md` |
| change budgets | `00-governance-core/docs/parallelism/change_budget_matrix.yaml` |
| acceptance gates | `00-governance-core/docs/standards/acceptance-gates-shared.md`, package `acceptance-gates.md` files |
| package contracts | `00-governance-core/docs/contracts/cross_package_contracts.md`, `package_contract_template.md`, package `dependency-contracts.md` files |
| merge and handoff rules | `00-governance-core/docs/parallelism/merge-and-handoff-protocol.md`, package `handoff-format.md` files |
| freeze protocol | `00-governance-core/docs/contracts/interface_freeze_protocol.md` |
| conflict resolution | `00-governance-core/docs/control/conflict_resolution_and_escalation.md` |
| escalation model | `00-governance-core/docs/control/conflict_resolution_and_escalation.md` |
| canonical source rules | `00-governance-core/docs/control/canonical_source_rules.md` |
| decision logging | `00-governance-core/docs/control/decision_logging_rules.md` |
| traceability model | `00-governance-core/docs/standards/traceability-model.md` |
| documentation layering | `00-governance-core/docs/control/documentation_layering.md` |
| review model | `00-governance-core/docs/control/review_model.md`, `codex_review_checklist.md` |
| prompt usage model | `00-governance-core/docs/control/prompt_usage_model.md`, package `chat_prompt_codex_only.md` files |

## Authority chain

1. Homologated project truth
2. Frozen governance core
3. Frozen package contracts and path ownership
4. Active run manifest
5. Active round manifest and work packets
6. Tactical prompts and worker bundles
7. Examples and references

Anything lower in the chain must yield to anything above it.

## Constitutional additions beyond both source zips

The following were added because neither input was sufficient alone:
- project ID plus run ID identity model
- idea intake and homologation flow
- canonical source register concept
- document layering rules
- decision-log obligations
- explicit escalation paths
- traceability from idea through artifact
- starter-kit packaging rules


## Additive hardening patch

The governance core now also carries these hardening additions:

| Capability | Primary file(s) |
|---|---|
| framework readiness gates | `00-governance-core/docs/control/framework_readiness_gates.md` |
| install/bootstrap/run separation | `00-governance-core/docs/control/install_bootstrap_run_separation.md` |
| inter-chat communication policy | `00-governance-core/docs/control/inter_chat_communication_policy.md` |
| waiver and exception policy | `00-governance-core/docs/control/waiver_and_exception_policy.md` |
| contract versioning policy | `00-governance-core/docs/contracts/contract_versioning_policy.md` |
| canonical tree hygiene | `00-governance-core/docs/control/canonical_tree_hygiene.md`, `configs/execution_framework/canonical_tree_excludes.json` |
| project baseline storage location | `ops/projects/README.md`, `00-governance-core/docs/control/documentation_layering.md` |
