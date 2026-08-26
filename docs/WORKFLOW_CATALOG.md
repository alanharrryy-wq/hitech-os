# Workflow Catalog

This document describes the current GitHub Actions operating model for `hitech-os`.

## Operating rule

CI must buy evidence, not burn runner minutes for ceremony. Broad checks are consolidated, specialist checks are path-scoped, and expensive historical/replay tooling is manual unless an active source boundary actually changes.

## Core CI

### `ci.yml`
Runs on normal pull requests and pushes to `main`, excluding generated/local/report-only paths. This is the consolidated repository guardrail lane and covers:

- dependency policy validation
- workspace boundaries
- dependency hygiene
- affected-project computation
- CODEOWNERS coverage
- dependency-cycle protection
- release-discipline reporting
- sensitive-path reporting
- repository hygiene
- Graphviz scope index
- engineering-health reports
- live-runtime zero-priority / no-`!important` enforcement

The former `dependency-check.yml`, `security-scan.yml`, and `zero-important.yml` lanes were retired because their useful checks are now covered here without extra hosted runners.

## Required compatibility check

### `forgeos-quality-gate.yml`
Remains global because `main` branch protection currently requires status context `forgeos-quality-gate`. For non-ForgeOS changes it performs only checkout + scope detection and reports PASS without running the heavy ForgeOS gate.

Do not path-scope or remove this workflow before changing branch protection, otherwise unrelated PRs can become permanently blocked waiting for a required status that never starts.

### Other ForgeOS workflows
- `forgeos-root-authority.yml` is already ForgeOS-path scoped.
- `forgeos-release-candidate.yml` is ForgeOS-path scoped plus manual dispatch.

ForgeOS itself is not globally retired: live code still consumes parts of `forgeos/shared`, so subsystem deletion requires a separate consumer migration.

## Specialist path-scoped checks

Examples include:

- `docs-governor.yml`
- `dev-console-architecture-guard.yml`
- `contract-python-parity.yml`
- `repo-navigation-guard.yml`
- `factory.yml`
- `orchestrator-factory.yml`
- `prisma-factory-anti-rework-gate.yml`
- `code-atlas-operational-hardening.yml`
- `automesh-parallel-cert.yml`
- `change-intelligence-capability-gate.yml`
- `change-intelligence-cloud-authority.yml`
- `license-pricing-canon.yml`
- `commercial-billing-authority.yml`

These remain because they guard active code/governance boundaries and are not global placeholders.

### `repo-analyzer-self-test.yml`
The Repo Analyzer Qt/failure-injection suite is expensive, so it now runs automatically only when `tools/graphviz/repo_analizer/**` or its own workflow changes. Manual dispatch remains available.

## Manual / evidence workflows

### `release.yml`
Release Governance remains available through `workflow_dispatch`, including explicit base/head SHA and strict mode. Automatic PR/push execution was removed because `ci.yml` already runs release-discipline reporting.

### `pc-surface-truth-wave1-visual.yml`
The completed PC Wave 1 / Wave 2 certification harness is preserved as a manual regression lane through `workflow_dispatch`. Its Wave 1 visual/runtime assertions and both Wave 2 certification modes remain intact, but routine PC source changes no longer wake this three-job suite automatically. The Factory Ledger already records the bounded Wave 2 capabilities as completed with `doNotRebuild=true`; this workflow exists for intentional historical regression/evidence replay, not recurring ceremony.

Historical Code Atlas external-replay/usefulness/rental workflows may remain manual or narrowly self-scoped because they preserve reproducible evidence and do not consume routine PR minutes.

## Documentation / promotion

- `docs-governor.yml` validates documentation changes.
- `promotion.yml` validates generated-doc promotion manifests in its narrow scope.

## Retired in CI Diet 2026-08-25

| Workflow | Reason |
| --- | --- |
| `cla-check.yml` | Placeholder only; every run printed `TODO: CLA assistant`. |
| `stale.yml` | Weekly placeholder that only printed `TODO`. |
| `labels.yml` | Issue-open placeholder that only printed `TODO`. |
| `ci-local.yml` | Push job only printed Node/npm versions; no validation. |
| `dependency-check.yml` | Duplicated dependency/workspace/cycle/repo-hygiene checks already in `ci.yml`. |
| `security-scan.yml` | Duplicated sensitive-path and CODEOWNERS reports already in `ci.yml`; it was not a vulnerability/secret scanner. |
| `zero-important.yml` | Separate global runner removed; the same live-runtime gate is enforced inside `ci.yml`. |

## Cost-control expectation

A normal unrelated PR should no longer wake placeholder jobs, the four-job Repo Analyzer Qt suite, or the completed PC Wave 1 / Wave 2 three-job certification suite. Routine hosted CI should be dominated by the consolidated `CI` job plus the branch-protection-required ForgeOS compatibility job, with specialist workflows activating only for their owned paths.

This catalog describes workflow intent. The YAML files remain the executable source of truth.
