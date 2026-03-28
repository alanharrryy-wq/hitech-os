# One-Button v1.2 Exit Codes and Operator Flows

## Document Status
- Status: Frozen
- Version: v1.2
- Scope: operator-visible outcomes and machine-consumable process exits

## 1. Purpose
This document freezes:
- how the operator experiences major session flows,
- which exit codes the launcher returns,
- what each exit code means operationally,
- how the PowerShell wrapper must behave.

## 2. Wrapper behavior
The wrapper `tools\one_button.ps1` must end with:

```powershell
exit $LASTEXITCODE
```

This is mandatory. The wrapper must not reinterpret Python outcomes or swallow exit statuses.

## 3. Exit code table
| Exit code | Meaning | Operational interpretation |
|---|---|---|
| 0 | ready or reused | Session is usable, or a valid existing session was reused |
| 10 | blocked by lock | Another valid session holds the project lock |
| 20 | contracts failed | Framework contract validation failed |
| 21 | smoke failed | Smoke checks failed |
| 22 | readiness install failed | Install/bootstrap readiness was not achieved |
| 23 | readiness round failed | Round-level readiness was not achieved |
| 30 | invalid arguments | Required inputs were missing or malformed |
| 31 | invalid policy transition | Requested policy does not make sense for current state |
| 40 | zip contract failed | Exported artifacts did not satisfy the session zip contract |
| 50 | unexpected runtime error | Unhandled failure or unrecoverable internal error |

## 4. Startup operator flow
### Interactive
1. Launch wrapper.
2. Choose lane.
3. Fill required prompts.
4. Review normalized summary.
5. Confirm execution.
6. Watch deterministic progress and final status.

### Non-interactive
1. Launch wrapper with all required flags.
2. The launcher validates argument completeness.
3. Missing required values return exit `30`.
4. No hidden prompts may appear.

## 5. Final operator output
Every run should end with a concise final summary containing:
- final status,
- canonical zip path if available,
- handoff copy path if available,
- one-line next step.

Examples:
- `ready_for_dispatch`: "Hand this zip back to ChatGPT for six final prompts."
- `reused`: "Existing session zip reused; no new export was created."
- `blocked`: "Active lock prevents mutation; inspect lock details."

## 6. Flow outcomes by lane and policy
### existing_project + resume_latest_round
Expected:
- state reuse,
- no new run,
- no new round,
- frequent `reused` outcomes when intent/context match existing session history.

### existing_project + open_new_round
Expected:
- same run,
- incremented round,
- normalized intent required,
- potentially fresh packet and prompt seed generation.

### existing_project + upgrade
Expected:
- new run created,
- new round lineage started,
- normalized intent required.

### new_project
Expected:
- new project normalized,
- path policies aligned,
- run and round initialized,
- acceptance report stub allowed when no bundles exist yet.

## 7. Operator messaging standards
### Good messages
- "Lock is active for project hitech-os by pid 1234 on host DESKTOP-ABC."
- "Session reused from existing idempotency match: sess_20260327_001."
- "Round readiness not achieved because path policies are missing or invalid."

### Bad messages
- "Something went wrong."
- "Failed unexpectedly." with no context
- ambiguous use of internal stack traces as user-facing output

## 8. Mapping failures to next action
### Lock conflict
Exit `10`
- next operator action: inspect lock or wait for owner to finish

### Contracts fail
Exit `20`
- next operator action: inspect framework contract validation results

### Smoke fail
Exit `21`
- next operator action: inspect smoke report and fix framework health

### Readiness fail
Exit `22` or `23`
- next operator action: fix readiness blocker before retry

### Zip contract fail
Exit `40`
- next operator action: inspect missing/invalid bundle artifact and rerun after fix

## 9. Logging philosophy
Operator output should remain concise. Rich technical detail may still go to logs, reports, and issue fields. This prevents console noise while preserving diagnostics for Codex and humans.

## 10. Acceptance criteria
This contract is implemented correctly when:
- each failure class maps to a stable exit code,
- the wrapper propagates the code unchanged,
- interactive and non-interactive behavior are deterministic,
- final operator output always points to the next action.
