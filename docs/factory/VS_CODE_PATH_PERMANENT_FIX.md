# VS Code PATH Permanent Fix (User Scope)

## Purpose

Ensure VS Code CLI is permanently available as `code` / `code.cmd` for:

- fresh PowerShell sessions
- Python (`shutil.which`)

without changing Machine PATH and without manual UI steps.

## What the guard checks

`tools/codex/tooling/ensure_vscode_path.ps1` performs:

1. Verifies git is available.
2. Verifies repo root from `git rev-parse --show-toplevel` is `F:\repos\hitech-os`.
3. Verifies Python is available.
4. Resolves VS Code CLI path, preferring:
   `C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd`
5. Reads User and Machine `Path` via EnvironmentVariable APIs.
6. Normalizes path entries (trim, unquote, trailing slash removal, case-insensitive compare).
7. Ensures VS Code `bin` is present in **User Path** (adds only if missing, no duplicates).
8. Refreshes current process `PATH` for immediate checks.
9. Validates:
   - `Get-Command code.cmd`
   - `code --version`
   - `python -c "import shutil; ..."` for `code` and `code.cmd`
   - helper script `tools/codex/tooling/ensure_vscode_path.py`
10. Emits deterministic report table and exits:

- `0` = PASS
- `2` = FAIL
- `3` = BLOCKED

## Single command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/codex/tooling/ensure_vscode_path.ps1
```

## Deterministic output example (PASS)

```text
REPO_ROOT: F:\repos\hitech-os
RESULT: PASS
check | result | details
--- | --- | ---
git_available | PASS | git found at C:\Program Files\Git\cmd\git.EXE
repo_root_match | PASS | expected=F:\repos\hitech-os actual=F:\repos\hitech-os
python_available | PASS | python found at C:\Users\alanh\AppData\Local\Programs\Python\Python312\python.EXE
code_cmd_detect | PASS | code.cmd resolved at C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd
path_read | PASS | user_entries=... machine_entries=...
user_path_contains_vscode_bin_before | PASS | present=True target=C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin
user_path_update | PASS | no change needed
user_path_contains_vscode_bin_after | PASS | present=True target=C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin
process_path_refresh | PASS | process PATH refreshed with target entry
powershell_get_command_code_cmd | PASS | C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd
powershell_code_version | PASS | 1.100.3
python_which_validation | PASS | code=...code.cmd | code.cmd=...code.cmd
python_helper_validation | PASS | helper exit=0
```

## Deterministic output example (FAIL)

```text
RESULT: FAIL
check | result | details
--- | --- | ---
code_cmd_detect | FAIL | expected path missing and Get-Command code.cmd returned no result. missing=C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd
```

## Deterministic output example (BLOCKED)

```text
RESULT: BLOCKED
check | result | details
--- | --- | ---
repo_root_match | BLOCKED | expected=F:\repos\hitech-os actual=D:\other\repo
```
