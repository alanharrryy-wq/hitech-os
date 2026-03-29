# 39. One-Button v1.2 Codex Validation Guide

## Purpose
This guide explains how Codex or an operator should validate the one-button v1.2 runtime after waves 1 through 5 are applied.

## Validation order
1. Apply waves 1 through 5 in order.
2. Confirm schemas and configs exist under `schemas/execution_framework` and `configs/execution_framework`.
3. Run the Ola 5 unittest suite.
4. Run a non-interactive `new_project` launch.
5. Re-run the same command to observe idempotency or reuse behavior.
6. Inspect the canonical ZIP, sidecars, lock directory, and session ledger.

## Minimum operator checks
- `tools/one_button.ps1` ends with `exit $LASTEXITCODE`.
- `validate_session_zip_contract.py --print-acceptance-stub` exits successfully.
- `one_button_session.py` returns JSON for non-interactive runs.
- The exported ZIP contains the exact required v1.2 paths.
- `acceptance_report.json` remains compatible with `acceptance_result.schema.json`.

## Notes for Codex
- Do not rewrite the contract during integration.
- Treat the Ola 5 tests as contract protectors, not style suggestions.
- If a test fails, determine whether the failure indicates a real drift or an expected environment mismatch.
