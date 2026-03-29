# Final Unified Framework Design

This document is the authoritative structural design for the final unified framework.

## Design stance

- **Zip A remains the governing backbone.**
- **Zip B contributes tactical execution mechanisms only.**
- **The default operating model is 1 governance chat + 6 package chats.**
- **The governance chat doubles as mission control by default.**
- **The core is universal and provider-neutral.**
- **Examples and profiles are isolated from the reusable core.**

## Top-level folder tree

```text
universal_execution_framework_v1/
├── 00-governance-core/
│   ├── docs/
│   │   ├── contracts/
│   │   │   ├── cross_package_contracts.md
│   │   │   ├── dependency_contract_rules.md
│   │   │   ├── interface_freeze_protocol.md
│   │   │   └── package_contract_template.md
│   │   ├── control/
│   │   │   ├── canonical_source_rules.md
│   │   │   ├── codex_insert_only_policy.md
│   │   │   ├── codex_operating_model.md
│   │   │   ├── codex_review_checklist.md
│   │   │   ├── codex_task_contract_template.md
│   │   │   ├── conflict_resolution_and_escalation.md
│   │   │   ├── decision_logging_rules.md
│   │   │   ├── definition_of_done_global.md
│   │   │   ├── documentation_layering.md
│   │   │   ├── idea_intake_and_homologation.md
│   │   │   ├── project_bootstrap_checklist.md
│   │   │   ├── prompt_usage_model.md
│   │   │   ├── review_model.md
│   │   │   ├── run_id_standard.md
│   │   │   └── run_lifecycle.md
│   │   ├── dictionaries/
│   │   │   ├── global_dictionary.md
│   │   │   └── naming_conventions.md
│   │   ├── parallelism/
│   │   │   ├── change_budget_matrix.yaml
│   │   │   ├── dependency-graph.md
│   │   │   ├── merge-and-handoff-protocol.md
│   │   │   ├── package_topology_rationale.md
│   │   │   └── path-ownership-matrix.yaml
│   │   └── standards/
│   │       ├── acceptance-gates-shared.md
│   │       ├── paths-and-boundaries.md
│   │       └── traceability-model.md
│   ├── chat_prompt_codex_only.md
│   └── README.md
├── 01-identity-access-and-trust/
│   ├── docs/
│   │   └── seed-index.md
│   ├── acceptance-gates.md
│   ├── chat_prompt_codex_only.md
│   ├── deliverables-manifest.md
│   ├── dependency-contracts.md
│   ├── handoff-format.md
│   ├── non-goals.md
│   ├── README.md
│   └── scope-and-boundaries.md
├── 02-domain-data-and-persistence/
│   ├── docs/
│   │   └── seed-index.md
│   ├── acceptance-gates.md
│   ├── chat_prompt_codex_only.md
│   ├── deliverables-manifest.md
│   ├── dependency-contracts.md
│   ├── handoff-format.md
│   ├── non-goals.md
│   ├── README.md
│   └── scope-and-boundaries.md
├── 03-service-contracts-and-orchestration/
│   ├── docs/
│   │   └── seed-index.md
│   ├── acceptance-gates.md
│   ├── chat_prompt_codex_only.md
│   ├── deliverables-manifest.md
│   ├── dependency-contracts.md
│   ├── handoff-format.md
│   ├── non-goals.md
│   ├── README.md
│   └── scope-and-boundaries.md
├── 04-experience-clients-and-interactions/
│   ├── docs/
│   │   └── seed-index.md
│   ├── acceptance-gates.md
│   ├── chat_prompt_codex_only.md
│   ├── deliverables-manifest.md
│   ├── dependency-contracts.md
│   ├── handoff-format.md
│   ├── non-goals.md
│   ├── README.md
│   └── scope-and-boundaries.md
├── 05-platform-infrastructure-and-delivery/
│   ├── docs/
│   │   └── seed-index.md
│   ├── acceptance-gates.md
│   ├── chat_prompt_codex_only.md
│   ├── deliverables-manifest.md
│   ├── dependency-contracts.md
│   ├── handoff-format.md
│   ├── non-goals.md
│   ├── README.md
│   └── scope-and-boundaries.md
├── 06-quality-release-and-operations/
│   ├── docs/
│   │   └── seed-index.md
│   ├── acceptance-gates.md
│   ├── chat_prompt_codex_only.md
│   ├── deliverables-manifest.md
│   ├── dependency-contracts.md
│   ├── handoff-format.md
│   ├── non-goals.md
│   ├── README.md
│   └── scope-and-boundaries.md
├── configs/
│   └── execution_framework/
│       ├── path_policies.json
│       ├── repo_target_layout.json
│       └── system_config.json
├── docs/
│   └── parallel_execution/
│       ├── 00_architecture_overview.md
│       ├── 01_operating_model.md
│       ├── 02_round_protocol.md
│       ├── 03_work_packet_model.md
│       ├── 04_ownership_map_model.md
│       ├── 05_acceptance_rubric.md
│       ├── 06_bundle_contract.md
│       ├── 07_failure_retry_playbook.md
│       ├── 08_naming_conventions.md
│       ├── 09_operator_handoff.md
│       ├── 10_chat_operator_playbook.md
│       ├── 11_run_round_01.md
│       ├── 12_run_round_n.md
│       ├── 13_integration_readiness.md
│       ├── 14_prompt_choreography.md
│       ├── 15_repo_shape_profiles.md
│       └── README.md
├── examples/
│   └── execution_framework/
│       ├── example_project_saas_portal/
│       │   ├── sample_bundle_unzipped/
│       │   │   ├── notes/
│       │   │   ├── payload/
│       │   │   ├── bundle_manifest.json
│       │   │   └── package_report.json
│       │   ├── path_policies.sample.json
│       │   ├── project_manifest.sample.json
│       │   ├── README.md
│       │   ├── sample_acceptance_report.json
│       │   ├── sample_bundle.zip
│       │   ├── sample_integration_ready_summary.md
│       │   └── sample_work_packet.json
│       └── README.md
├── ops/
│   ├── projects/
│   │   └── README.md
│   └── runs/
│       └── README.md
├── prompts/
│   └── execution_framework/
│       ├── end_of_round_integration_prompt.md
│       ├── mission_control_prompt.md
│       ├── package_worker_prompt.md
│       └── retry_prompt.md
├── schemas/
│   └── execution_framework/
│       ├── acceptance_result.schema.json
│       ├── bundle_manifest.schema.json
│       ├── package_report.schema.json
│       ├── project_manifest.schema.json
│       ├── round_manifest.schema.json
│       ├── run_manifest.schema.json
│       └── work_packet.schema.json
├── templates/
│   └── execution_framework/
│       ├── package/
│       │   ├── acceptance-gates.template.md
│       │   ├── chat_prompt_codex_only.template.md
│       │   ├── deliverables-manifest.template.md
│       │   ├── dependency-contracts.template.md
│       │   ├── handoff-format.template.md
│       │   ├── non-goals.template.md
│       │   ├── README.template.md
│       │   └── scope-and-boundaries.template.md
│       ├── project/
│       │   ├── canonical_source_register.template.md
│       │   ├── decision_log.template.md
│       │   ├── homologation_record.template.md
│       │   ├── idea_intake.template.md
│       │   └── project_manifest.template.json
│       └── run/
│           ├── bundle_manifest.template.json
│           ├── integration_ready_summary.template.md
│           ├── package_report.template.json
│           ├── round_manifest.template.json
│           ├── run_manifest.template.json
│           └── work_packet.template.json
├── tests/
│   └── execution_framework/
│       ├── __init__.py
│       ├── test_acceptance_logic.py
│       ├── test_dependency_order.py
│       ├── test_deterministic_zip.py
│       ├── test_manifest_validation.py
│       ├── test_ownership_enforcement.py
│       └── test_zip_validation.py
├── tools/
│   └── execution_framework/
│       ├── lib/
│       │   ├── __init__.py
│       │   ├── bundles.py
│       │   ├── common.py
│       │   ├── config.py
│       │   ├── reports.py
│       │   ├── rounds.py
│       │   └── validators.py
│       ├── qa/
│       │   └── README.md
│       ├── __init__.py
│       ├── apply_validated_bundle.py
│       ├── assemble_round_summary.py
│       ├── build_integration_ready_summary.py
│       ├── compute_overlap_report.py
│       ├── dry_run_bundle.py
│       ├── emit_acceptance_report.py
│       ├── enforce_ownership.py
│       ├── generate_prompt_packets.py
│       ├── generate_work_packets.py
│       ├── init_round.py
│       ├── init_run.py
│       ├── package_round_artifacts.py
│       ├── prepare_next_round_prompts.py
│       ├── smoke_framework_checks.py
│       └── validate_worker_bundle.py
├── COMPARATIVE_DIAGNOSTIC.md
├── master_chat_routing.md
├── OVERRIDE_LEDGER.md
├── parallel_launch_order.md
├── parallel_manifest.json
├── README.md
├── STARTER_INDEX.md
└── STARTER_MANIFEST.json
```

## Layer model

### Constitutional layer
Files that define authority, boundaries, naming, lifecycle, freeze behavior, canonical source rules, and review gates.

Primary locations:
- `00-governance-core/`
- `parallel_manifest.json`
- `parallel_launch_order.md`
- `master_chat_routing.md`

### Tactical layer
Files that define how parallel execution happens once the constitutional layer is frozen.

Primary locations:
- `docs/parallel_execution/`
- `configs/execution_framework/`
- `prompts/execution_framework/`
- `schemas/execution_framework/`
- `tools/execution_framework/`
- `tests/execution_framework/`

### Starter-kit material
Reusable bootstrap material suitable for future projects.

Primary locations:
- root `README.md`
- `STARTER_INDEX.md`
- `STARTER_MANIFEST.json`
- governance core
- package skeletons
- templates
- tactical subsystem
- nested starter zip

### Optional reference material
Reference-only content that must not override active project governance.

Primary locations:
- `examples/execution_framework/`
- `COMPARATIVE_DIAGNOSTIC.md`
- `OVERRIDE_LEDGER.md`

## Package topology and purpose

| Package | Type | Purpose | Depends on |
|---|---|---|---|
| `00-governance-core` | Constitutional | Governs the system, defines lifecycle, contracts, traceability, and review rules. | none |
| `01-identity-access-and-trust` | Per-package | Identity, authorization, trust boundaries, secrets, policy, audit-facing controls. | `00-governance-core` |
| `02-domain-data-and-persistence` | Per-package | Domain entities, storage strategy, migrations, persistence semantics, durability. | `00-governance-core`, `01-identity-access-and-trust` |
| `03-service-contracts-and-orchestration` | Per-package | Service boundaries, contracts, orchestration, workflows, integration wiring. | `00-governance-core`, `01-*`, `02-*` |
| `04-experience-clients-and-interactions` | Per-package | Web, app, dashboard, portal, UX, client state, interaction surfaces. | `00-governance-core`, `03-*` |
| `05-platform-infrastructure-and-delivery` | Per-package | Runtime platform, infra, environment config, CI/CD, deploy and delivery controls. | `00-governance-core`, `03-*`, `04-*` |
| `06-quality-release-and-operations` | Per-package | QA, observability, release readiness, rollback, runbooks, operational verification. | `00-governance-core`, all delivery-impacting packages |

## File-class rules

- **Global** files govern or support the whole framework or whole project.
- **Per-project** files define one project's homologated reality.
- **Per-run** files define one governed execution run.
- **Per-package** files define one package's scope, gates, and handoff contract.
- **Template** files are reusable scaffolds.
- **Example** files are illustrative only and never canonical.

## Constitutional files

These are constitutional by intent and outrank tactical files:
- `parallel_manifest.json`
- `parallel_launch_order.md`
- `master_chat_routing.md`
- everything under `00-governance-core/`
- each package root governance seed:
  - `README.md`
  - `scope-and-boundaries.md`
  - `deliverables-manifest.md`
  - `dependency-contracts.md`
  - `non-goals.md`
  - `acceptance-gates.md`
  - `handoff-format.md`
  - `chat_prompt_codex_only.md`

## Tactical files

These remain subordinate to the constitutional layer:
- `docs/parallel_execution/`
- `configs/execution_framework/`
- `prompts/execution_framework/`
- `schemas/execution_framework/`
- `tools/execution_framework/`
- `tests/execution_framework/`

## Starter-kit files

The nested starter zip contains the reusable foundation only:
- root starter docs
- governance core
- six universal packages
- tactical subsystem
- templates
- schemas
- prompts
- tools
- tests
- run bootstrap directory

## Optional reference material

These must never become canonical without explicit homologation:
- `examples/execution_framework/`
- donor diagnostics
- sample bundles and sample reports

## Dependency rules

### Constitutional dependencies
1. Governance core freezes naming, scope, ownership, and review rules.
2. Package boundaries are frozen before execution starts.
3. Run and round artifacts are valid only if they point back to frozen governance and project sources.

### Tactical dependencies
1. Work packets depend on homologated project inputs plus frozen governance.
2. Bundles depend on work packets and runtime path policies.
3. Acceptance reports depend on bundle validation, overlap detection, and dependency order.
4. Integration readiness depends on accepted bundles and unresolved conflict count.

## Why this structure is more universal than both inputs

- provider-neutral package naming
- project/run/package/artifact traceability
- explicit canonical-source hierarchy
- separate core vs examples vs templates
- mission control merged into governance by default for the 1+6 model
- rounds treated as tactical subdivisions rather than top-level authority

## Additive hardening patch v1.0.1

This additive patch does not replace the framework. It strengthens it in place by adding:

- `ops/projects/<project_id>/` as the missing home for the project baseline layer
- `OPERATOR_ONE_PAGE_FLOW.md` for fast operator execution
- readiness gates plus `check_framework_readiness.py`
- explicit inter-chat communication and waiver policies
- contract versioning rules plus a contract register template
- canonical tree hygiene rules plus machine-readable exclusions
- a pilot `run-001` playbook
