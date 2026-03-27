# Master Index

This is the master catalog for the final outer bundle.

## Reading modes

- Read `README.md` for the short overview.
- Read `COMPARATIVE_DIAGNOSTIC.md` for the rigorous source comparison.
- Read `FINAL_FRAMEWORK_DESIGN.md` for the unified structural design.
- Read `GOVERNANCE_CORE_EXPANSION.md` for the constitutional map.
- Read `TACTICAL_EXECUTION_SUBSYSTEM.md` for the tactical machinery map.
- Use the catalog below to locate any exact file.

## Legend

- **Class**: constitutional, tactical, starter-kit, optional-reference, reference
- **Scope**: global, per-project, per-run, per-package, template, example
- **Deps**: upstream files or concepts this file depends on


## Constitutional

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `00-governance-core/README.md` | `global` | `constitution` | Mission and authority statement for the constitutional governance package. | parallel_manifest.json |
| `00-governance-core/chat_prompt_codex_only.md` | `global` | `constitution` | Bounded governance-chat prompt that keeps constitutional work separate from package-local work. | 00-governance-core/README.md |
| `00-governance-core/docs/contracts/cross_package_contracts.md` | `global` | `constitution` | Cross_package_contracts | 00-governance-core/README.md |
| `00-governance-core/docs/contracts/dependency_contract_rules.md` | `global` | `constitution` | Dependency_contract_rules | 00-governance-core/README.md |
| `00-governance-core/docs/contracts/interface_freeze_protocol.md` | `global` | `constitution` | Interface_freeze_protocol | 00-governance-core/README.md |
| `00-governance-core/docs/contracts/package_contract_template.md` | `global` | `constitution` | Package_contract_template | 00-governance-core/README.md |
| `00-governance-core/docs/control/canonical_source_rules.md` | `global` | `constitution` | Canonical_source_rules | 00-governance-core/README.md |
| `00-governance-core/docs/control/codex_insert_only_policy.md` | `global` | `constitution` | Codex_insert_only_policy | 00-governance-core/README.md |
| `00-governance-core/docs/control/codex_operating_model.md` | `global` | `constitution` | Codex_operating_model | 00-governance-core/README.md |
| `00-governance-core/docs/control/codex_review_checklist.md` | `global` | `constitution` | Codex_review_checklist | 00-governance-core/README.md |
| `00-governance-core/docs/control/codex_task_contract_template.md` | `global` | `constitution` | Codex_task_contract_template | 00-governance-core/README.md |
| `00-governance-core/docs/control/conflict_resolution_and_escalation.md` | `global` | `constitution` | Conflict_resolution_and_escalation | 00-governance-core/README.md |
| `00-governance-core/docs/control/decision_logging_rules.md` | `global` | `constitution` | Decision_logging_rules | 00-governance-core/README.md |
| `00-governance-core/docs/control/definition_of_done_global.md` | `global` | `constitution` | Definition_of_done_global | 00-governance-core/README.md |
| `00-governance-core/docs/control/documentation_layering.md` | `global` | `constitution` | Documentation_layering | 00-governance-core/README.md |
| `00-governance-core/docs/control/idea_intake_and_homologation.md` | `global` | `constitution` | Idea_intake_and_homologation | 00-governance-core/README.md |
| `00-governance-core/docs/control/project_bootstrap_checklist.md` | `global` | `constitution` | Project_bootstrap_checklist | 00-governance-core/README.md |
| `00-governance-core/docs/control/prompt_usage_model.md` | `global` | `constitution` | Prompt_usage_model | 00-governance-core/README.md |
| `00-governance-core/docs/control/review_model.md` | `global` | `constitution` | Review_model | 00-governance-core/README.md |
| `00-governance-core/docs/control/run_id_standard.md` | `global` | `constitution` | Run_id_standard | 00-governance-core/README.md |
| `00-governance-core/docs/control/run_lifecycle.md` | `global` | `constitution` | Run_lifecycle | 00-governance-core/README.md |
| `00-governance-core/docs/dictionaries/global_dictionary.md` | `global` | `constitution` | Global_dictionary | 00-governance-core/README.md |
| `00-governance-core/docs/dictionaries/naming_conventions.md` | `global` | `constitution` | Naming_conventions | 00-governance-core/README.md |
| `00-governance-core/docs/parallelism/change_budget_matrix.yaml` | `global` | `constitution` | Change_budget_matrix.yaml | 00-governance-core/README.md |
| `00-governance-core/docs/parallelism/dependency-graph.md` | `global` | `constitution` | Dependency graph | 00-governance-core/README.md |
| `00-governance-core/docs/parallelism/merge-and-handoff-protocol.md` | `global` | `constitution` | Merge and handoff protocol | 00-governance-core/README.md |
| `00-governance-core/docs/parallelism/package_topology_rationale.md` | `global` | `constitution` | Package_topology_rationale | 00-governance-core/README.md |
| `00-governance-core/docs/parallelism/path-ownership-matrix.yaml` | `global` | `constitution` | Path ownership matrix.yaml | 00-governance-core/README.md |
| `00-governance-core/docs/standards/acceptance-gates-shared.md` | `global` | `constitution` | Acceptance gates shared | 00-governance-core/README.md |
| `00-governance-core/docs/standards/paths-and-boundaries.md` | `global` | `constitution` | Paths and boundaries | 00-governance-core/README.md |
| `00-governance-core/docs/standards/traceability-model.md` | `global` | `constitution` | Traceability model | 00-governance-core/README.md |
| `master_chat_routing.md` | `global` | `constitution` | Default chat routing for the 1 governance + 6 parallel package chat model. | parallel_manifest.json, parallel_launch_order.md |
| `parallel_launch_order.md` | `global` | `constitution` | Recommended sequence for opening chats, freezing rules, and running rounds under the default 1+6 model. | parallel_manifest.json, 00-governance-core/docs/control/run_lifecycle.md |
| `parallel_manifest.json` | `global` | `constitution` | Default six-package topology and dependency manifest used by the framework and the tactical tooling. | 00-governance-core/README.md |
| `01-identity-access-and-trust/README.md` | `per-package` | `package` | README for package 01-identity-access-and-trust. | 00-governance-core, 00-governance-core/README.md |
| `01-identity-access-and-trust/acceptance-gates.md` | `per-package` | `package` | Acceptance gates and freeze gate for 01-identity-access-and-trust. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `01-identity-access-and-trust/chat_prompt_codex_only.md` | `per-package` | `package` | Package-specific bounded prompt for 01-identity-access-and-trust. | 00-governance-core/chat_prompt_codex_only.md |
| `01-identity-access-and-trust/deliverables-manifest.md` | `per-package` | `package` | Deliverables inventory and quality bar for 01-identity-access-and-trust. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `01-identity-access-and-trust/dependency-contracts.md` | `per-package` | `package` | Dependency declaration and consumption rules for 01-identity-access-and-trust. | 00-governance-core, 00-governance-core/docs/contracts/dependency_contract_rules.md |
| `01-identity-access-and-trust/docs/seed-index.md` | `per-package` | `package` | Suggested first documents and first freeze target for 01-identity-access-and-trust. | 01-identity-access-and-trust/deliverables-manifest.md |
| `01-identity-access-and-trust/handoff-format.md` | `per-package` | `package` | Handoff metadata requirements for 01-identity-access-and-trust. | 00-governance-core/docs/parallelism/merge-and-handoff-protocol.md |
| `01-identity-access-and-trust/non-goals.md` | `per-package` | `package` | Explicit non-goals for 01-identity-access-and-trust. | 00-governance-core/docs/standards/paths-and-boundaries.md |
| `01-identity-access-and-trust/scope-and-boundaries.md` | `per-package` | `package` | Scope, out-of-scope limits, and write/read rules for 01-identity-access-and-trust. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml, 00-governance-core |
| `02-domain-data-and-persistence/README.md` | `per-package` | `package` | README for package 02-domain-data-and-persistence. | 00-governance-core, 00-governance-core/README.md |
| `02-domain-data-and-persistence/acceptance-gates.md` | `per-package` | `package` | Acceptance gates and freeze gate for 02-domain-data-and-persistence. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `02-domain-data-and-persistence/chat_prompt_codex_only.md` | `per-package` | `package` | Package-specific bounded prompt for 02-domain-data-and-persistence. | 00-governance-core/chat_prompt_codex_only.md |
| `02-domain-data-and-persistence/deliverables-manifest.md` | `per-package` | `package` | Deliverables inventory and quality bar for 02-domain-data-and-persistence. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `02-domain-data-and-persistence/dependency-contracts.md` | `per-package` | `package` | Dependency declaration and consumption rules for 02-domain-data-and-persistence. | 00-governance-core, 00-governance-core/docs/contracts/dependency_contract_rules.md |
| `02-domain-data-and-persistence/docs/seed-index.md` | `per-package` | `package` | Suggested first documents and first freeze target for 02-domain-data-and-persistence. | 02-domain-data-and-persistence/deliverables-manifest.md |
| `02-domain-data-and-persistence/handoff-format.md` | `per-package` | `package` | Handoff metadata requirements for 02-domain-data-and-persistence. | 00-governance-core/docs/parallelism/merge-and-handoff-protocol.md |
| `02-domain-data-and-persistence/non-goals.md` | `per-package` | `package` | Explicit non-goals for 02-domain-data-and-persistence. | 00-governance-core/docs/standards/paths-and-boundaries.md |
| `02-domain-data-and-persistence/scope-and-boundaries.md` | `per-package` | `package` | Scope, out-of-scope limits, and write/read rules for 02-domain-data-and-persistence. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml, 00-governance-core |
| `03-service-contracts-and-orchestration/README.md` | `per-package` | `package` | README for package 03-service-contracts-and-orchestration. | 00-governance-core, 01-identity-access-and-trust, 02-domain-data-and-persistence, 00-governance-core/README.md |
| `03-service-contracts-and-orchestration/acceptance-gates.md` | `per-package` | `package` | Acceptance gates and freeze gate for 03-service-contracts-and-orchestration. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `03-service-contracts-and-orchestration/chat_prompt_codex_only.md` | `per-package` | `package` | Package-specific bounded prompt for 03-service-contracts-and-orchestration. | 00-governance-core/chat_prompt_codex_only.md |
| `03-service-contracts-and-orchestration/deliverables-manifest.md` | `per-package` | `package` | Deliverables inventory and quality bar for 03-service-contracts-and-orchestration. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `03-service-contracts-and-orchestration/dependency-contracts.md` | `per-package` | `package` | Dependency declaration and consumption rules for 03-service-contracts-and-orchestration. | 00-governance-core, 01-identity-access-and-trust, 02-domain-data-and-persistence, 00-governance-core/docs/contracts/dependency_contract_rules.md |
| `03-service-contracts-and-orchestration/docs/seed-index.md` | `per-package` | `package` | Suggested first documents and first freeze target for 03-service-contracts-and-orchestration. | 03-service-contracts-and-orchestration/deliverables-manifest.md |
| `03-service-contracts-and-orchestration/handoff-format.md` | `per-package` | `package` | Handoff metadata requirements for 03-service-contracts-and-orchestration. | 00-governance-core/docs/parallelism/merge-and-handoff-protocol.md |
| `03-service-contracts-and-orchestration/non-goals.md` | `per-package` | `package` | Explicit non-goals for 03-service-contracts-and-orchestration. | 00-governance-core/docs/standards/paths-and-boundaries.md |
| `03-service-contracts-and-orchestration/scope-and-boundaries.md` | `per-package` | `package` | Scope, out-of-scope limits, and write/read rules for 03-service-contracts-and-orchestration. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml, 00-governance-core, 01-identity-access-and-trust, 02-domain-data-and-persistence |
| `04-experience-clients-and-interactions/README.md` | `per-package` | `package` | README for package 04-experience-clients-and-interactions. | 00-governance-core, 01-identity-access-and-trust, 03-service-contracts-and-orchestration, 00-governance-core/README.md |
| `04-experience-clients-and-interactions/acceptance-gates.md` | `per-package` | `package` | Acceptance gates and freeze gate for 04-experience-clients-and-interactions. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `04-experience-clients-and-interactions/chat_prompt_codex_only.md` | `per-package` | `package` | Package-specific bounded prompt for 04-experience-clients-and-interactions. | 00-governance-core/chat_prompt_codex_only.md |
| `04-experience-clients-and-interactions/deliverables-manifest.md` | `per-package` | `package` | Deliverables inventory and quality bar for 04-experience-clients-and-interactions. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `04-experience-clients-and-interactions/dependency-contracts.md` | `per-package` | `package` | Dependency declaration and consumption rules for 04-experience-clients-and-interactions. | 00-governance-core, 01-identity-access-and-trust, 03-service-contracts-and-orchestration, 00-governance-core/docs/contracts/dependency_contract_rules.md |
| `04-experience-clients-and-interactions/docs/seed-index.md` | `per-package` | `package` | Suggested first documents and first freeze target for 04-experience-clients-and-interactions. | 04-experience-clients-and-interactions/deliverables-manifest.md |
| `04-experience-clients-and-interactions/handoff-format.md` | `per-package` | `package` | Handoff metadata requirements for 04-experience-clients-and-interactions. | 00-governance-core/docs/parallelism/merge-and-handoff-protocol.md |
| `04-experience-clients-and-interactions/non-goals.md` | `per-package` | `package` | Explicit non-goals for 04-experience-clients-and-interactions. | 00-governance-core/docs/standards/paths-and-boundaries.md |
| `04-experience-clients-and-interactions/scope-and-boundaries.md` | `per-package` | `package` | Scope, out-of-scope limits, and write/read rules for 04-experience-clients-and-interactions. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml, 00-governance-core, 01-identity-access-and-trust, 03-service-contracts-and-orchestration |
| `05-platform-infrastructure-and-delivery/README.md` | `per-package` | `package` | README for package 05-platform-infrastructure-and-delivery. | 00-governance-core, 03-service-contracts-and-orchestration, 00-governance-core/README.md |
| `05-platform-infrastructure-and-delivery/acceptance-gates.md` | `per-package` | `package` | Acceptance gates and freeze gate for 05-platform-infrastructure-and-delivery. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `05-platform-infrastructure-and-delivery/chat_prompt_codex_only.md` | `per-package` | `package` | Package-specific bounded prompt for 05-platform-infrastructure-and-delivery. | 00-governance-core/chat_prompt_codex_only.md |
| `05-platform-infrastructure-and-delivery/deliverables-manifest.md` | `per-package` | `package` | Deliverables inventory and quality bar for 05-platform-infrastructure-and-delivery. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `05-platform-infrastructure-and-delivery/dependency-contracts.md` | `per-package` | `package` | Dependency declaration and consumption rules for 05-platform-infrastructure-and-delivery. | 00-governance-core, 03-service-contracts-and-orchestration, 00-governance-core/docs/contracts/dependency_contract_rules.md |
| `05-platform-infrastructure-and-delivery/docs/seed-index.md` | `per-package` | `package` | Suggested first documents and first freeze target for 05-platform-infrastructure-and-delivery. | 05-platform-infrastructure-and-delivery/deliverables-manifest.md |
| `05-platform-infrastructure-and-delivery/handoff-format.md` | `per-package` | `package` | Handoff metadata requirements for 05-platform-infrastructure-and-delivery. | 00-governance-core/docs/parallelism/merge-and-handoff-protocol.md |
| `05-platform-infrastructure-and-delivery/non-goals.md` | `per-package` | `package` | Explicit non-goals for 05-platform-infrastructure-and-delivery. | 00-governance-core/docs/standards/paths-and-boundaries.md |
| `05-platform-infrastructure-and-delivery/scope-and-boundaries.md` | `per-package` | `package` | Scope, out-of-scope limits, and write/read rules for 05-platform-infrastructure-and-delivery. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml, 00-governance-core, 03-service-contracts-and-orchestration |
| `06-quality-release-and-operations/README.md` | `per-package` | `package` | README for package 06-quality-release-and-operations. | 00-governance-core, 01-identity-access-and-trust, 02-domain-data-and-persistence, 03-service-contracts-and-orchestration, 04-experience-clients-and-interactions, 05-platform-infrastructure-and-delivery, 00-governance-core/README.md |
| `06-quality-release-and-operations/acceptance-gates.md` | `per-package` | `package` | Acceptance gates and freeze gate for 06-quality-release-and-operations. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `06-quality-release-and-operations/chat_prompt_codex_only.md` | `per-package` | `package` | Package-specific bounded prompt for 06-quality-release-and-operations. | 00-governance-core/chat_prompt_codex_only.md |
| `06-quality-release-and-operations/deliverables-manifest.md` | `per-package` | `package` | Deliverables inventory and quality bar for 06-quality-release-and-operations. | 00-governance-core/docs/standards/acceptance-gates-shared.md |
| `06-quality-release-and-operations/dependency-contracts.md` | `per-package` | `package` | Dependency declaration and consumption rules for 06-quality-release-and-operations. | 00-governance-core, 01-identity-access-and-trust, 02-domain-data-and-persistence, 03-service-contracts-and-orchestration, 04-experience-clients-and-interactions, 05-platform-infrastructure-and-delivery, 00-governance-core/docs/contracts/dependency_contract_rules.md |
| `06-quality-release-and-operations/docs/seed-index.md` | `per-package` | `package` | Suggested first documents and first freeze target for 06-quality-release-and-operations. | 06-quality-release-and-operations/deliverables-manifest.md |
| `06-quality-release-and-operations/handoff-format.md` | `per-package` | `package` | Handoff metadata requirements for 06-quality-release-and-operations. | 00-governance-core/docs/parallelism/merge-and-handoff-protocol.md |
| `06-quality-release-and-operations/non-goals.md` | `per-package` | `package` | Explicit non-goals for 06-quality-release-and-operations. | 00-governance-core/docs/standards/paths-and-boundaries.md |
| `06-quality-release-and-operations/scope-and-boundaries.md` | `per-package` | `package` | Scope, out-of-scope limits, and write/read rules for 06-quality-release-and-operations. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml, 00-governance-core, 01-identity-access-and-trust, 02-domain-data-and-persistence, 03-service-contracts-and-orchestration, 04-experience-clients-and-interactions, 05-platform-infrastructure-and-delivery |

## Tactical

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `docs/parallel_execution/00_architecture_overview.md` | `global` | `tactical` | 00 architecture overview | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/01_operating_model.md` | `global` | `tactical` | 01 operating model | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/02_round_protocol.md` | `global` | `tactical` | 02 round protocol | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/03_work_packet_model.md` | `global` | `tactical` | 03 work packet model | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/04_ownership_map_model.md` | `global` | `tactical` | 04 ownership map model | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/05_acceptance_rubric.md` | `global` | `tactical` | 05 acceptance rubric | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/06_bundle_contract.md` | `global` | `tactical` | 06 bundle contract | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/07_failure_retry_playbook.md` | `global` | `tactical` | 07 failure retry playbook | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/08_naming_conventions.md` | `global` | `tactical` | 08 naming conventions | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/09_operator_handoff.md` | `global` | `tactical` | 09 operator handoff | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/10_chat_operator_playbook.md` | `global` | `tactical` | 10 chat operator playbook | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/11_run_round_01.md` | `global` | `tactical` | 11 run round 01 | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/12_run_round_n.md` | `global` | `tactical` | 12 run round n | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/13_integration_readiness.md` | `global` | `tactical` | 13 integration readiness | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/14_prompt_choreography.md` | `global` | `tactical` | 14 prompt choreography | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/15_repo_shape_profiles.md` | `global` | `tactical` | 15 repo shape profiles | 00-governance-core/README.md, parallel_manifest.json |
| `docs/parallel_execution/README.md` | `global` | `tactical` | README | 00-governance-core/README.md, parallel_manifest.json |

## Starter-Kit

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `README.md` | `global` | `starter` | Primary human-facing overview of the framework, its layers, and how to start a new governed execution effort. | STARTER_INDEX.md, parallel_manifest.json, 00-governance-core/README.md |
| `STARTER_INDEX.md` | `global` | `starter` | Quick-start index for bootstrapping a new project from the starter kit. | README.md, 00-governance-core/docs/control/project_bootstrap_checklist.md |
| `STARTER_MANIFEST.json` | `global` | `starter` | Machine-readable manifest for the nested starter zip. | parallel_manifest.json |
| `configs/execution_framework/repo_target_layout.json` | `global` | `tactical` | Minimal directory layout the framework expects to exist. | README.md |
| `configs/execution_framework/system_config.json` | `global` | `tactical` | Active tactical subsystem configuration used by the tools. | parallel_manifest.json |
| `prompts/execution_framework/end_of_round_integration_prompt.md` | `global` | `tactical` | Prompt template for the tactical subsystem. | docs/parallel_execution/14_prompt_choreography.md |
| `prompts/execution_framework/mission_control_prompt.md` | `global` | `tactical` | Prompt template for the tactical subsystem. | docs/parallel_execution/14_prompt_choreography.md |
| `prompts/execution_framework/package_worker_prompt.md` | `global` | `tactical` | Prompt template for the tactical subsystem. | docs/parallel_execution/14_prompt_choreography.md |
| `prompts/execution_framework/retry_prompt.md` | `global` | `tactical` | Prompt template for the tactical subsystem. | docs/parallel_execution/14_prompt_choreography.md |
| `schemas/execution_framework/acceptance_result.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `schemas/execution_framework/bundle_manifest.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `schemas/execution_framework/package_report.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `schemas/execution_framework/project_manifest.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `schemas/execution_framework/round_manifest.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `schemas/execution_framework/run_manifest.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `schemas/execution_framework/work_packet.schema.json` | `global` | `tactical` | Lightweight schema definition for tactical manifests and reports. | docs/parallel_execution/06_bundle_contract.md |
| `tests/execution_framework/__init__.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tests/execution_framework/test_acceptance_logic.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tests/execution_framework/test_dependency_order.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tests/execution_framework/test_deterministic_zip.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tests/execution_framework/test_manifest_validation.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tests/execution_framework/test_ownership_enforcement.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tests/execution_framework/test_zip_validation.py` | `global` | `tactical` | Automated test for the tactical subsystem. | tools/execution_framework/lib/common.py |
| `tools/execution_framework/__init__.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/apply_validated_bundle.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/assemble_round_summary.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/build_integration_ready_summary.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/compute_overlap_report.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/dry_run_bundle.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/emit_acceptance_report.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/enforce_ownership.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/generate_prompt_packets.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/generate_work_packets.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/init_round.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/init_run.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/__init__.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/bundles.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/common.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/config.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/reports.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/rounds.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/lib/validators.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/package_round_artifacts.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/prepare_next_round_prompts.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/qa/README.md` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/smoke_framework_checks.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `tools/execution_framework/validate_worker_bundle.py` | `global` | `tactical` | Executable tooling or library support for the tactical subsystem. | configs/execution_framework/system_config.json, parallel_manifest.json |
| `configs/execution_framework/path_policies.json` | `per-project` | `tactical` | Default active path policies. Replace these with real runtime paths during homologation. | 00-governance-core/docs/parallelism/path-ownership-matrix.yaml |
| `ops/runs/README.md` | `per-run` | `tactical` | Operational location and conventions for real runs. | 00-governance-core/docs/control/run_id_standard.md |
| `templates/execution_framework/package/README.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/acceptance-gates.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/chat_prompt_codex_only.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/deliverables-manifest.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/dependency-contracts.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/handoff-format.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/non-goals.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/package/scope-and-boundaries.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/project/canonical_source_register.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/project/decision_log.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/project/homologation_record.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/project/idea_intake.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/project/project_manifest.template.json` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/run/bundle_manifest.template.json` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/run/integration_ready_summary.template.md` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/run/package_report.template.json` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/run/round_manifest.template.json` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/run/run_manifest.template.json` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |
| `templates/execution_framework/run/work_packet.template.json` | `template` | `templates` | Reusable template for project, package, or run artifacts. | 00-governance-core/docs/control/documentation_layering.md |

## Optional-Reference

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `examples/execution_framework/README.md` | `example` | `examples` | Optional reference examples for operators adopting the framework. | 00-governance-core/docs/control/canonical_source_rules.md |
| `examples/execution_framework/example_project_saas_portal/README.md` | `example` | `examples` | Example project showing one possible application of the universal framework. | examples/execution_framework/README.md |
| `examples/execution_framework/example_project_saas_portal/path_policies.sample.json` | `example` | `examples` | Sample runtime path policy mapping for a SaaS portal reference project. | configs/execution_framework/path_policies.json |
| `examples/execution_framework/example_project_saas_portal/project_manifest.sample.json` | `example` | `examples` | Sample project manifest for a SaaS portal reference project. | templates/execution_framework/project/project_manifest.template.json |
| `examples/execution_framework/example_project_saas_portal/sample_acceptance_report.json` | `example` | `examples` | Sample acceptance report for the reference project. | schemas/execution_framework/acceptance_result.schema.json |
| `examples/execution_framework/example_project_saas_portal/sample_bundle.zip` | `example` | `examples` | Sample worker bundle zip for the reference project. | examples/execution_framework/example_project_saas_portal/sample_bundle_unzipped/bundle_manifest.json |
| `examples/execution_framework/example_project_saas_portal/sample_bundle_unzipped/bundle_manifest.json` | `example` | `examples` | Bundle manifest inside the unzipped sample bundle. | schemas/execution_framework/bundle_manifest.schema.json |
| `examples/execution_framework/example_project_saas_portal/sample_bundle_unzipped/notes/summary.md` | `example` | `examples` | Human summary inside the unzipped sample bundle. | examples/execution_framework/example_project_saas_portal/sample_bundle_unzipped/bundle_manifest.json |
| `examples/execution_framework/example_project_saas_portal/sample_bundle_unzipped/package_report.json` | `example` | `examples` | Package report inside the unzipped sample bundle. | schemas/execution_framework/package_report.schema.json |
| `examples/execution_framework/example_project_saas_portal/sample_bundle_unzipped/payload/services/api/contracts/customer_status.schema.json` | `example` | `examples` | Payload file inside the unzipped sample bundle. | examples/execution_framework/example_project_saas_portal/sample_bundle.zip |
| `examples/execution_framework/example_project_saas_portal/sample_integration_ready_summary.md` | `example` | `examples` | Sample integration readiness summary for the reference project. | examples/execution_framework/example_project_saas_portal/sample_acceptance_report.json |
| `examples/execution_framework/example_project_saas_portal/sample_work_packet.json` | `example` | `examples` | Sample work packet for the service package in the reference project. | templates/execution_framework/run/work_packet.template.json |

## Reference

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `COMPARATIVE_DIAGNOSTIC.md` | `global` | `analysis` | Rigorous comparison of Zip A and Zip B, including preserved strengths, extracted tactics, and design decisions. | parallel_manifest.json, 00-governance-core/docs/parallelism/package_topology_rationale.md |
| `FINAL_FRAMEWORK_DESIGN.md` | `global` | `analysis` | Detailed structural design of the final unified framework, including tree, layering, topology, and classification rules. | COMPARATIVE_DIAGNOSTIC.md, parallel_manifest.json, 00-governance-core/README.md |
| `GOVERNANCE_CORE_EXPANSION.md` | `global` | `analysis` | Guide to the expanded governance core and where each constitutional capability lives in the bundle. | 00-governance-core/README.md |
| `OVERRIDE_LEDGER.md` | `global` | `analysis` | Explicit record of the major generalizations and overrides applied during unification. | COMPARATIVE_DIAGNOSTIC.md |
| `TACTICAL_EXECUTION_SUBSYSTEM.md` | `global` | `analysis` | Guide to the tactical parallel execution subsystem, its documents, schemas, prompts, and tools. | docs/parallel_execution/README.md, tools/execution_framework/smoke_framework_checks.py |
| `framework_manifest.json` | `global` | `analysis` | Machine-readable manifest for the final outer framework bundle. | STARTER_MANIFEST.json, parallel_manifest.json |


## Additive Hardening Patch v1.0.1

### Constitutional additions

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `00-governance-core/docs/control/framework_readiness_gates.md` | `global` | `constitution` | Stage-based readiness gates from install through integration. | `00-governance-core/README.md` |
| `00-governance-core/docs/control/install_bootstrap_run_separation.md` | `global` | `constitution` | Explicit separation between framework install, project bootstrap, run execution, and round execution. | `00-governance-core/README.md` |
| `00-governance-core/docs/control/inter_chat_communication_policy.md` | `global` | `constitution` | Artifact-only communication policy for governance and worker chats. | `00-governance-core/README.md` |
| `00-governance-core/docs/control/waiver_and_exception_policy.md` | `global` | `constitution` | Controlled exception process for waivers, overrides, and emergency paths. | `00-governance-core/README.md` |
| `00-governance-core/docs/control/canonical_tree_hygiene.md` | `global` | `constitution` | Exclusion and hygiene rules for canonical tree docs and starter assets. | `00-governance-core/README.md` |
| `00-governance-core/docs/contracts/contract_versioning_policy.md` | `global` | `constitution` | Semantic versioning and freeze-state handling for shared contracts. | `00-governance-core/docs/contracts/interface_freeze_protocol.md` |
| `ops/projects/README.md` | `global` | `starter` | Canonical location for homologated per-project baselines. | `00-governance-core/docs/control/documentation_layering.md` |

### Tactical and starter additions

| Path | Scope | Layer | Purpose | Deps |
|---|---|---|---|---|
| `OPERATOR_ONE_PAGE_FLOW.md` | `global` | `starter` | Fast operator path from install to first integrated round. | `STARTER_INDEX.md`, `parallel_launch_order.md` |
| `docs/parallel_execution/16_pilot_run_001_playbook.md` | `global` | `tactical` | Controlled pilot guidance for real run-001 usage. | `docs/parallel_execution/README.md` |
| `configs/execution_framework/canonical_tree_excludes.json` | `global` | `tactical` | Machine-readable exclusion list for canonical tree hygiene. | `00-governance-core/docs/control/canonical_tree_hygiene.md` |
| `schemas/execution_framework/readiness_report.schema.json` | `global` | `tactical` | Schema for readiness reports. | `00-governance-core/docs/control/framework_readiness_gates.md` |
| `schemas/execution_framework/waiver_record.schema.json` | `global` | `tactical` | Schema for waiver records. | `00-governance-core/docs/control/waiver_and_exception_policy.md` |
| `tools/execution_framework/init_project.py` | `global` | `tactical` | Initializes a homologated project baseline skeleton under `ops/projects/`. | `templates/execution_framework/project/*` |
| `tools/execution_framework/check_framework_readiness.py` | `global` | `tactical` | Checks install, bootstrap, run, round, acceptance, and integration readiness. | `configs/execution_framework/*`, `tools/execution_framework/lib/readiness.py` |
| `templates/execution_framework/project/contract_register.template.md` | `template` | `templates` | Template for project-level contract tracking. | `00-governance-core/docs/contracts/contract_versioning_policy.md` |
| `templates/execution_framework/run/waiver_record.template.md` | `template` | `templates` | Template for run-scoped waiver records. | `00-governance-core/docs/control/waiver_and_exception_policy.md` |
