
# Starter Index

Read these in order for the fastest correct bootstrap:

1. `README.md`
2. `OPERATOR_ONE_PAGE_FLOW.md`
3. `00-governance-core/README.md`
4. `00-governance-core/docs/control/project_bootstrap_checklist.md`
5. `00-governance-core/docs/control/framework_readiness_gates.md`
6. `00-governance-core/docs/control/install_bootstrap_run_separation.md`
7. `00-governance-core/docs/control/idea_intake_and_homologation.md`
8. `00-governance-core/docs/control/run_id_standard.md`
9. `parallel_manifest.json`
10. `parallel_launch_order.md`
11. `master_chat_routing.md`
12. `docs/parallel_execution/README.md`
13. `docs/parallel_execution/16_pilot_run_001_playbook.md`

## Minimum bootstrap path
- Confirm the framework passes install readiness
- Create or confirm `project_id`
- Instantiate `ops/projects/<project_id>/`
- Homologate the idea into a project baseline
- Freeze package topology and runtime path policies
- Initialize `run_id`
- Initialize `rd-001`
- Generate work packets and prompts
- Launch the six package chats
- Validate bundles before integration

## Files you edit first on a new project
- `templates/execution_framework/project/idea_intake.template.md`
- `templates/execution_framework/project/homologation_record.template.md`
- `templates/execution_framework/project/canonical_source_register.template.md`
- `templates/execution_framework/project/contract_register.template.md`
- `templates/execution_framework/project/project_manifest.template.json`
- `configs/execution_framework/path_policies.json`

## Files you usually leave alone
- constitutional docs in `00-governance-core/`
- schemas, tools, and tests in the tactical subsystem
- package folder names in the default six-package topology unless governance records a topology override
