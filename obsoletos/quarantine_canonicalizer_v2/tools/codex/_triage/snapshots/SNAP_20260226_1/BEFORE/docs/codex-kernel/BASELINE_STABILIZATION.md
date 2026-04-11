# BASELINE STABILIZATION (Mission 0)

STATUS: LAW-ALIGNED NOTE

## TL;DR

A clean baseline means these required commands exit with `rc=0`:

```bash
pnpm -w -r typecheck
pnpm -w -r build
pnpm -w -r test
python tools/codex/run.py --run-id <RUN_ID>
```

`tools/codex/run.py` is authoritative for PASS/BLOCKED because it enforces required checks from `tools/codex/validation.json`.

## Clean Baseline Criteria

The baseline is clean only when all required checks are green:

1. `typecheck` required and `rc=0`
2. `build` required and `rc=0`
3. `test_unit` required and `rc=0`
4. `guardrails` required and `rc=0`
5. Integrator status final is `PASS` in `STATUS.json`

Optional checks (example: dependency install bootstrap) do not decide final PASS/BLOCKED.

## Logs And Artifacts

All run evidence is stored under:

`tools/codex/runs/<RUN_ID>/Z_integrator/`

Required files:

- `FINAL_REPORT.txt`
- `STATUS.json`
- `DIFF.patch`
- `FILES_CHANGED.json`
- `RUN_LOG.txt`
- `ERROR.txt`
- `LOGS/*.log.txt`

## BLOCKED Triage Order

When any required check fails, stop and triage in order:

1. Missing imports/module resolution (first real error, not cascades)
2. Package exports/entrypoint mismatches
3. Build config mismatch (Node ESM/TS mode)
4. Deterministic unit failures (assertions/fixtures)
5. Environment prerequisites that cannot be installed deterministically

If still blocked, report exact failing step, log path, and one next action.

## Phase 1 Extraction Readiness Checklist

- [ ] `pnpm -w -r typecheck` green
- [ ] `pnpm -w -r build` green
- [ ] `pnpm -w -r test` green
- [ ] `python tools/codex/run.py --run-id <RUN_ID>` final `PASS`
- [ ] Guardrail for `.js` imports in TS `src/**` active
- [ ] No generated artifacts under `src/**`
- [ ] Feature flags default OFF unless explicitly required

## Anti-Goals Reminder

- Do not write build/test artifacts under `src/**`.
- Do not enable feature flags by default.
- Do not bypass required validation checks using `allow_fail`.
