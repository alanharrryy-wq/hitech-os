# AutoGit Repo-Local Curator

This folder is intentionally rooted with only `AutoGit.cmd`.

Subfolders:

- `bin/`: launchers and rollback wrappers.
- `engine/`: Python package, validators, recipes, policies, and PR gate logic.
- `config/`: repo-local extension point for future config.
- `state/`: reserved for local state placeholders.
- `logs/`, `reports/`: reserved for future repo-local manual exports. Runtime output should go to `F:\descargasf`.
- `trash_manifests/`, `rollback/`: reserved for future integration.

Run from the repo root or anywhere:

```cmd
autogit\AutoGit.cmd
```

Useful modes:

```cmd
set AUTOGIT_MODE=audit && autogit\AutoGit.cmd
set AUTOGIT_MODE=commit-only && autogit\AutoGit.cmd
set AUTOGIT_MODE=pr-only && autogit\AutoGit.cmd
```
