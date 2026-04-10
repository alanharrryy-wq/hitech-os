# .gitignore and Local Files Policy

Status: ACTIVE
Authority: Binding for agents and operators

## Core Rule

Ignored files are ignored by Git only. They are not deleted from disk.

## Default Operating Policy

1. Do not move or delete local operator files as a cleanup method.
2. First option is always to add or refine .gitignore rules.
3. If a tracked file should become local-only, use git rm --cached <path> and keep the file on disk.
4. Temporary relocation is allowed only with explicit operator request, and all relocated files must be restored before task closeout.
5. Bulk destructive cleanup over ignored or untracked files is forbidden.

## Forbidden Commands for Local/Untracked Cleanup

- git clean -fdx
- git clean -fd
- rm -rf
- del /s /q
- Remove-Item -Recurse -Force
- git reset --hard

## Safe Commands

- git status
- git ls-files --others --ignored --exclude-standard
- git check-ignore -v <path>
- git rm --cached <path>

## Evidence Requirement

When changing ignore rules, include:
- files changed
- exact ignore rules added or modified
- validation command and result (git check-ignore -v <path>)
