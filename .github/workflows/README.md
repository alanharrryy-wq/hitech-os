# .github/workflows

This directory contains the repository automation that is still active and justified.

## CI policy

GitHub-hosted runners are a scarce resource. A workflow must either protect an active product/governance boundary, run only when its owned paths change, or be explicitly operator-triggered. Placeholder and duplicate workflows are not kept alive merely for historical continuity.

`ci.yml` is the consolidated broad guardrail lane. It owns dependency-policy, workspace-boundary, dependency-hygiene, cycle, release-discipline, sensitive-path, CODEOWNERS/repository-hygiene reporting, scope-index generation, and the live-runtime zero-priority (`!important`) gate.

Heavy specialist workflows must be path-scoped. Historical/replay workflows may remain manual when they preserve reproducible evidence without consuming routine pull-request minutes.

## Branch-protection exception

`forgeos-quality-gate.yml` intentionally remains global because `main` currently requires the `forgeos-quality-gate` status context. The workflow performs a cheap scope check and skips ForgeOS execution for unrelated changes. Do not path-scope or remove it until branch protection is changed first.

## Retired automation

The following workflows were removed because they were placeholders or duplicated checks already executed by `ci.yml`:

- `cla-check.yml`
- `ci-local.yml`
- `dependency-check.yml`
- `security-scan.yml`
- `labels.yml`
- `stale.yml`
- `zero-important.yml` (logic consolidated into `ci.yml`)

See `docs/WORKFLOW_CATALOG.md` for the current operating model.
