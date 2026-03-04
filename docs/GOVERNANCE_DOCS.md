# Documentation Governance Policy

## Purpose

This policy controls documentation growth, keeps architecture decisions auditable, and enforces deterministic documentation placement across Hitech repositories.

## Documentation Policy

Documentation is allowed only in:

- `docs/`
- `docs/adr/`
- `docs/runbooks/`
- `docs/playbooks/`
- `docs/security/`
- `docs/architecture/`
- `docs/releases/`
- `docs/_generated/<RUN_ID>/`

Allowed root documentation files:

- `README.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `LICENSE`
- `NOTICE`
- `CLA.md`

Disallowed documentation directories:

- `docs2/`
- `documentation/`
- `wiki/`
- `notes/`
- `design_docs/`
- `random_docs/`

Any violation in disallowed locations fails governance checks.

## ADR Process

All architecture decisions use ADR files in `docs/adr/` with this format:

- `docs/adr/0001-title.md`
- `docs/adr/0002-title.md`

Required ADR support files:

- `docs/adr/README.md`
- `docs/adr/0000-template.md`

ADR lifecycle:

1. Draft ADR from template.
2. Review by architecture owners.
3. Approve and merge.
4. Mark superseded ADRs explicitly in newer records.

## Documentation Directory Map

- `docs/adr/`: Architecture Decision Records.
- `docs/runbooks/`: Operational procedures and incident execution.
- `docs/playbooks/`: Repeatable delivery/security response procedures.
- `docs/security/`: Security standards and operational controls.
- `docs/architecture/`: System design documentation.
- `docs/releases/`: Release notes and release-level change context.
- `docs/_generated/<RUN_ID>/`: Agent-generated docs sandbox for one isolated run.

## Multi-Agent Documentation Rules

1. Agents may create generated docs only in `docs/_generated/<RUN_ID>/`.
2. Each run folder must include `index.md`.
3. One run must not write into another run folder.
4. Agents must not create ad-hoc documentation directories.
5. New docs with duplicate names are blocked; high similarity names are warned.

## Examples

Allowed:

- `docs/runbooks/database-recovery.md`
- `docs/architecture/event-flow.md`
- `docs/_generated/20260304T101500Z/index.md`

Disallowed:

- `notes/meeting-summary.md`
- `random_docs/idea.md`
- `tools/README-extra.md`
