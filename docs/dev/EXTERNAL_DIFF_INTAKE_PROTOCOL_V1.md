# External Diff Intake Protocol V1

## Purpose
Define a deterministic workflow for integrating external `.diff` files with low friction and no architecture drift.

## Non-Negotiable Defaults
- `MODE=reference` is the default for any external attachment.
- `BASE_COMMIT` is mandatory.
- Any auto-inferred field in `TASK_MANIFEST.txt` must be marked as `INFERRED`.
- Any explicit user instruction overrides inferred values.
- `tools/_local/inbox/**` is staging only and never source of truth.
- Source of truth files/docs always win over external diff proposals unless user explicitly sets authoritative mode.

## Task ID Format
- Use short deterministic IDs:
- `<project>-YYYYMMDD-HHMM-<slug>-rN`
- Example: `code-atlas-20260401-1805-starfield-motion-r1`

## Canonical Staging Layout
- `tools/_local/inbox/<project>/<task_id>/TASK_MANIFEST.txt`
- `tools/_local/inbox/<project>/<task_id>/incoming/`
- `tools/_local/inbox/<project>/<task_id>/working/`
- `tools/_local/inbox/<project>/<task_id>/outputs/`

## Intake Flow
1. Validate attachment exists and read headers/hunks.
2. Normalize patch paths to repo-relative paths when needed.
3. Run dry check: `git apply --check` (allow whitespace normalization when required).
4. Evaluate value before apply:
5. Reject if it adds no real improvement, duplicates existing behavior, or conflicts with source-of-truth contracts.
6. Apply only if it improves behavior and remains in scope.
7. If patch causes minor breakage, perform local targeted fix and continue.
8. If patch causes major architecture/behavior breakage, abort integration and report why.
9. Validate syntax/tests relevant to touched scope.
10. Export integrated plain-text diff for handoff/review.

## Minor vs Major Break Rule
- Minor break:
- small runtime error, import mismatch, tiny UI wiring issue, or obvious low-risk merge conflict.
- Action: fix and continue.
- Major break:
- contract violation, large cross-module regression, scope blowout, or destabilizing refactor.
- Action: cancel integration and report.

## Output Contract Per Integration
- Applied or rejected verdict.
- Exact files changed.
- Validation commands + results.
- Exported integrated diff path.
- Any compatibility risk detected.

## Integrated Diff Export (Operator Default)
- Save a plain-text diff to:
- `F:\OneDrive\Descargas\`
- Name pattern:
- `<project>_<short_topic>_integrated_YYYYMMDD.diff`

## Minimal Manifest Schema
- `TASK_ID`
- `PROJECT`
- `MODE`
- `BASE_COMMIT`
- `SOURCE_OF_TRUTH`
- `USER_EXPLICIT_OVERRIDES`
- `OBJECTIVE`
- `IN_SCOPE_FILES`
- `OUT_OF_SCOPE`
- `ACCEPTANCE_CRITERIA`
- `VALIDATION_COMMANDS`
- `ATTACHMENTS`
- `NOTES`

## Notes
- This protocol governs diff intake only.
- It does not replace architecture ownership docs or lane handoffs.
