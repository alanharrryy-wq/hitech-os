# Wave 5 Batch Manifest

## Included files
- tests/execution_framework/_test_support.py
- tests/execution_framework/test_one_button_existing_flow.py
- tests/execution_framework/test_one_button_new_project_flow.py
- tests/execution_framework/test_session_lock.py
- tests/execution_framework/test_session_idempotency.py
- tests/execution_framework/test_session_export_contract.py
- tests/fixtures/execution_framework/acceptance_result.schema.json
- tests/fixtures/execution_framework/expected_session_zip_contract.json
- tests/fixtures/execution_framework/sample_existing_project_state/project_manifest.json
- tests/fixtures/execution_framework/sample_existing_project_state/run_manifest.json
- tests/fixtures/execution_framework/sample_existing_project_state/round_manifest.json
- tests/fixtures/execution_framework/sample_existing_project_state/coordination_snapshot.latest.json
- tests/fixtures/execution_framework/sample_existing_project_state/coordination_snapshot.latest.md
- tests/fixtures/execution_framework/sample_existing_project_state/readiness_report.json
- tests/fixtures/execution_framework/sample_existing_project_state/acceptance_report.json
- docs/parallel_execution/39_one_button_v12_codex_validation_guide.md
- docs/parallel_execution/40_one_button_v12_integration_checklist.md
- docs/parallel_execution/41_one_button_v12_test_matrix.md

## Validation intent
This wave closes the loop on robustness by testing the runtime created in waves 2, 3, and 4 without adding any new runtime dependencies.
