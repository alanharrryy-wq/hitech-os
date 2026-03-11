# Add Contracts

STATUS: LAW

Use this process for every new canonical graph-analysis schema.

1. Add schema file in `tools/codex/schemas/`.
2. Register schema key/path in `tools/codex/contracts/factory/contracts_registry.json`.
3. Add schema key to `tools/codex/factory/schemas.py` (`SCHEMA_INDEX`).
4. If artifact is required, update required file lists in registry and runtime config.
5. Wire runtime validation in `tools/codex/factory/contracts.py`.
6. Update law docs in `docs/codex-kernel/docs/` and `docs/factory/`.
7. Record changes in `docs/factory/CHANGES.md`.

## SemVer Governance

Schema `schema_version` follows semver:

- PATCH: non-breaking
- MINOR: additive optional
- MAJOR: required/semantic break

If a change is MAJOR:

1. set `breaking_change: true` in produced artifacts during rollout
2. document migration in `CHANGES.md`
3. preserve aliases if feasible; otherwise document incompatibility explicitly

## Canonical JSON / Markdown Rule

- JSON remains canonical and validated.
- Markdown mirrors summarize JSON and must not contradict it.
