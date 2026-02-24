# DIFF_OUTPUT_POLICY

## Purpose

Unified diffs are required evidence artifacts, but they are disk artifacts, not chat/console payloads.
Color-only UI diffs are non-authoritative.

## Disk-Only Diff Policy

For any run that changes files:

1. Generate deterministic plaintext unified diffs using `git diff --no-color --patch`.
2. Write diffs to `.patch` files under the run bundle:
   `tools/codex/<worker>/RUN_<RUN_ID>/DIFF*.patch`
3. Do not print raw unified diff content to stdout/stderr.
4. Do not include raw unified diff blocks in final responses.

## Final Report Policy

`FINAL_REPORT.txt` is the only user-facing run artifact and must contain:

- changed file summary
- patch artifact paths
- log artifact paths
- validation summary and debt/blockers

`FINAL_REPORT.txt` must not embed raw unified diff content.

## Do / Don't

- Do: use `git diff --no-color --patch`.
- Do: keep patch artifacts UTF-8 without ANSI sequences.
- Do: reference artifact paths in final responses/reports.
- Don't: print unified diff bodies in chat or console.
- Don't: rely only on IDE/UI color diffs.
