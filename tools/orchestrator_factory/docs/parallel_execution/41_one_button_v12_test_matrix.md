# 41. One-Button v1.2 Test Matrix

| Area | Test file | Focus |
|---|---|---|
| Existing project flow | `test_one_button_existing_flow.py` | Dry-run behavior, round resolution, resume behavior |
| New project flow | `test_one_button_new_project_flow.py` | Dry-run output and full export path |
| Lock manager | `test_session_lock.py` | Same-host and cross-host stale rules |
| Idempotency and ledger | `test_session_idempotency.py` | Sentinel hashes and reusable ledger entries |
| Export contract | `test_session_export_contract.py` | ZIP required files, acceptance stub, validator pass |

## Fixture coverage
- Existing project manifests
- Coordination snapshot stubs
- Readiness report
- Acceptance report stub
- Expected required ZIP paths
- Acceptance schema fallback

## Success criteria
All tests pass under the standard library test runner on Windows using the current repo implementation plus waves 1 through 5.
