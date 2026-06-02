# AutoGit fix report

## Review summary

This package was reviewed statically and with local smoke tests. The original ZIP compiled in Python, but several runtime safety issues were found and corrected.

## Fixed issues

1. Secret redaction could corrupt valid code such as `secret = scan_text(text)` into invalid syntax.
   - Fixed by making assignment redaction syntax-preserving and by skipping function calls/placeholders/code identifiers.
   - Unquoted secret literals now become quoted strings, for example `token = "<REDACTED>"`.

2. `audit` mode could continue into mutating stages.
   - Fixed so audit mode scans and validates only, then writes a result ZIP without sanitize, trash moves, commits, pushes, PRs, or merges.

3. `pr-only` mode could still scan/commit dirty files before PR gate.
   - Fixed so PR-only runs only the PR gate against existing local commits.

4. Python validation created `__pycache__` inside the target repository.
   - Fixed by using non-executing syntax compilation instead of bytecode-producing `py_compile`.
   - Launchers also set `PYTHONDONTWRITEBYTECODE=1`.

5. Path joining forced Windows backslashes and broke portable smoke tests.
   - Added `repo_path()` helper for safe Git-style relative paths across operating systems.

6. Empty trash manifests could create a weird `<LOCAL_PATH>` folder when tested outside Windows.
   - Trash folder creation is now lazy and skipped when there are no trash rows.

## Validations performed

- Python syntax check for all AutoGit engine files.
- Import smoke test for all AutoGit modules.
- Secret redaction regression test:
  - preserves `secret = scan_text(text)`;
  - redacts `token = "<REDACTED>""<REDACTED>"`;
  - redacts quoted passwords while preserving valid syntax.
- Fake Git repository audit-mode test:
  - produced a result ZIP;
  - did not modify files;
  - did not create `__pycache__`.
- Fake Git repository commit-only test:
  - sanitized risky literals;
  - created one local commit;
  - did not run PR gate;
  - did not create `__pycache__`.

## Notes

PowerShell parsing was not executed in the Linux sandbox because PowerShell was not installed there. The PowerShell scripts were inspected and kept simple.
