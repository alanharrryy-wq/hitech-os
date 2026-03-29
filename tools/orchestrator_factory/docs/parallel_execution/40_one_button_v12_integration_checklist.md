# 40. One-Button v1.2 Integration Checklist

## Before integration
- [ ] Waves 1 to 5 were applied in order.
- [ ] No new third-party dependencies were added.
- [ ] Existing runtime entrypoints still resolve.
- [ ] `acceptance_result.schema.json` exists at the framework path.

## During integration
- [ ] Unittest suite under `tests/execution_framework` passes.
- [ ] `new_project` dry-run produces `status = ready`.
- [ ] `new_project` full run produces `status = ready_for_dispatch`.
- [ ] `existing_project` open-new-round dry-run computes the next round correctly.
- [ ] Canonical ZIP validation report is clean.
- [ ] `session_ledger.jsonl` is appended only on completed exports.
- [ ] Live lock files are released after export.

## After integration
- [ ] Handoff copy behavior matches `one_button_config.json`.
- [ ] Sidecars are present when enabled.
- [ ] No temporary validation report files are left behind.
- [ ] Operator can hand the ZIP back into ChatGPT for prompt generation.
