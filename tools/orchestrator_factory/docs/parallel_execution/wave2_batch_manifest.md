# Wave 2 Batch Manifest

## Scope
Wave 2 contains schemas, config, and guardrails for the one-button motor v1.2.

## Included files
- tools/orchestrator_factory/schemas/execution_framework/session_manifest.schema.json
- tools/orchestrator_factory/schemas/execution_framework/session_zip_contract.schema.json
- tools/orchestrator_factory/configs/execution_framework/one_button_config.json
- tools/orchestrator_factory/tools/execution_framework/validate_session_zip_contract.py

## Intentional decisions
- No new dependencies.
- acceptance_report.json remains aligned with acceptance_result.schema.json required fields.
- Stub acceptance report is valid when overall_status is "pending" and package_results is [].
- handoff_copy_dir is configurable and not hardcoded in the runtime logic.
- Required versus optional ZIP members are explicit in session_zip_contract.schema.json.

## Validation commands
Use the commands from the assistant response for batch installation and verification.
