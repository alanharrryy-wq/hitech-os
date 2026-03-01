# REPO_HYGIENE

Optional hygiene scanners for repository cleanliness.
No scanner is enforced by default.

## Modules

- `tools/hos/hygiene/forbidden_paths.json`
- `tools/hos/hygiene/scan_root_artifacts.py`
- `tools/hos/hygiene/scan_worktree_contamination.py`
- `tools/hos/hygiene/scan_large_files.py`
- `tools/hos/hygiene/cli_hygiene.py`

## Scanner Coverage

- Root junk/artifact detection.
- Worktree contamination detection in `tools/codex/worktrees`.
- Optional large-file listing.

## Commands

```powershell
python tools/hos/hygiene/cli_hygiene.py
python tools/hos/hygiene/cli_hygiene.py --include-large-files --large-file-min-mb 8
python tools/hos/hygiene/cli_hygiene.py --strict
```

Reports are written to:

- `tools/_local/reports/hygiene/`

## Enforcement Status

- OFF by default.
- `--strict` is opt-in and local/manual.
- No default CI gate was added by this tooling rollout.

