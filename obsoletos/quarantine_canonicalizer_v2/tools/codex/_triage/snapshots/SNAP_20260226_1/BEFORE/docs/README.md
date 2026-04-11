# Docs README

Navigation and governance entrypoint for repository documentation.

## Governance Roots

- `docs/CONTRACT.md`: enforcement law and operational gates.
- `docs/CONSTITUTION.md`: Stage-0 intent and interpretation rules.
- `docs/snapshots/HITECH_OS__SNAPSHOT_MINI.json`: deterministic snapshot mini state.
- `docs/factory/CONTRACT.md`: Multi-Codex Factory runtime contract.

## Primary Navigation

- `docs/DOCS_INDEX.md`: deterministic generated file index.
- `docs/DOCS_INDEX_POLICY.md`: indexing policy and generation constraints.
- `docs/MASTER_MAP.md`: system ownership and runtime map.
- `docs/NOTEBOOK.md`: decisions, assumptions, and debt notes.
- `docs/CHANGELOG_POLICY.md`: change-log discipline across contracts and runtime docs.

## Runtime and Integration

- `docs/integration/JOBS_CONTRACT.md`: API payload and behavior contract.
- `docs/integration/SMOKE_RUN.md`: smoke validation flow and commands.
- `docs/integration/NODE_PYTHON_BRIDGE.md`: Node/Python bridge behavior.
- `docs/factory/INDEX.md`: factory docs hub.

## Authoring Rules

1. Keep docs deterministic: stable ordering, explicit dates, and reproducible commands.
2. Update `docs/DOCS_INDEX.md` via `pnpm run docs` whenever doc files change.
3. Governance changes must sync both `CONSTITUTION.md` (intent) and `CONTRACT.md` (enforcement).
4. Document temporary exceptions in `docs/NOTEBOOK.md` with expiration and rollback.
