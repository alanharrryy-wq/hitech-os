# Capatch System

Capatch is a conservative multi-file patch engine for exact, structural, and semantic edits.

This upgraded layout keeps the repository clean: source code, tests, docs, plugins, and cartridges stay here; operational evidence, backups, logs, diagnostics, and run bundles are exported outside the target repository, by default to `F:\descargasf`.

## Core ideas

- **Core limpio:** patch engine, CLI, operations, verifiers, policy and plugin runtime stay reusable.
- **Cartuchos N64:** project/surface behavior is loaded as composable cartridges instead of hardcoding Tablet, PC, Mobile or PRISMA into the core.
- **External evidence:** every real modification should produce a `result.zip` or `fail.zip` outside the repo.
- **Rollback first:** changed files are backed up before mutation and rollback information is bundled.
- **No fake green:** functional verification is not treated as proof of visual quality.

## Important folders

```text
capatch_cli/          CLI facade
capatch_engine/       patch pipeline
capatch_ops/          operations
capatch_verify/       verifiers
capatch_cartridges/   surface/task cartridges
capatch_output/       external run-bundle helpers
capatch_intent/       surface and risk helpers
docs/                 operating documentation
tests/                regression tests
```

## Output policy

Runtime artifacts must not be committed here. Capatch writes run evidence to `F:\descargasf` on Windows unless overridden with environment variables such as `CAPATCH_AUDIT_EXPORT_DIR` or `CAPATCH_RUNTIME_ROOT`.
