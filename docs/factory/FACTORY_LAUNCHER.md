# Factory Launcher

## Purpose

`OPEN_HOS_FACTORY.ps1` launches factory worker windows in deterministic order (`A_core`, `B_tooling`, `C_features`, `D_validation`, `Z_aggregator`) using fixed worker worktrees and workspace files.

This launcher does not dispatch prompts and does not send keystrokes.

## How To Run

Default launch:

```powershell
pwsh -File scripts/OPEN_HOS_FACTORY.ps1 -RunId "20260227_3"
```

With self-update first (`git pull --ff-only`):

```powershell
pwsh -File scripts/OPEN_HOS_FACTORY.ps1 -RunId "20260227_3" -Update
```

Environment equivalent:

```powershell
$env:HOS_LAUNCHER_UPDATE = "1"
pwsh -File scripts/OPEN_HOS_FACTORY.ps1 -RunId "20260227_3"
```

Optional parameters:

- `-BaseBranch <name>` (default: `main`)
- `-CodeCmd <path-or-command>` to override VS Code command resolution

Python entrypoint:

```powershell
python -m tools.hos.launcher.hos_factory_launcher --run-id 20260227_3 --base-branch main
```

Validation-only command:

```powershell
python -m tools.hos.launcher.hos_factory_launcher --run-id 20260227_3 --validate
```

## What It Creates

- Worker worktrees under:
  - `tools/codex/worktrees/A_core`
  - `tools/codex/worktrees/B_tooling`
  - `tools/codex/worktrees/C_features`
  - `tools/codex/worktrees/D_validation`
  - `tools/codex/worktrees/Z_aggregator`
- Per-worker VS Code workspace files:
  - `tools/hos/launcher/workspaces/A_core.code-workspace`
  - `tools/hos/launcher/workspaces/B_tooling.code-workspace`
  - `tools/hos/launcher/workspaces/C_features.code-workspace`
  - `tools/hos/launcher/workspaces/D_validation.code-workspace`
  - `tools/hos/launcher/workspaces/Z_aggregator.code-workspace`
- Launcher logs:
  - `tools/codex/runs/<RUN_ID>/_debug/LAUNCHER_*.log`
  - `tools/codex/runs/<RUN_ID>/_debug/LAUNCHER_SUMMARY.json`

At process end, the PowerShell wrapper opens `tools/codex/runs/<RUN_ID>/_debug`.

## Troubleshooting

`git` missing:

- Symptom: launcher exits with `git is not available in PATH.`
- Fix: install Git and ensure `git` is on PATH.

VS Code command missing:

- Symptom: launcher exits with `VS Code CLI is unavailable`.
- Fix options:
  - install shell command `code` in PATH, or
  - pass `-CodeCmd "C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\Code.exe"`.

Worktree conflict / invalid path:

- Symptom: launcher reports path exists but is not registered worktree.
- Cause: folder exists at `tools/codex/worktrees/<worker>` but is not attached to this repo worktree list.
- Fix: move/clean the conflicting folder, or repair with Git worktree commands, then rerun launcher.

Self-update failure:

- Symptom: `-Update` run exits non-zero after `git pull --ff-only`.
- Fix: resolve pull error (auth/network/conflict) and rerun.

## Safety Notes

- The launcher only prepares worktrees and opens VS Code windows.
- It does not modify dispatcher prompt ordering.
- During active dispatch runs, do not move target VS Code windows while automation is operating.
