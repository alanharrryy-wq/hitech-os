# ForgeOS Industrialization Playbook

## Purpose

Operationalize the reconstructed ForgeOS baseline so every change is reproducible, gated, and release-ready.

## Scope

This playbook applies to changes touching:

- `forgeos/**`
- `docs/forgeos-foundation/**`

## Operating Model

1. PR integration lane:
- Use the repository PR template.
- Include `STATUS`, `FILES_CHANGED`, and `DIFF summary` in the PR description.
- Treat acceptance gates as mandatory entry criteria.

2. Quality gate lane:
- Workflow: `.github/workflows/forgeos-quality-gate.yml`.
- Trigger: PRs and pushes that touch ForgeOS or foundation docs.
- Required outcome: PASS on boundary validation, package dry-run, and runtime tests.

3. Release candidate lane:
- Workflow: `.github/workflows/forgeos-release-candidate.yml`.
- Trigger: `workflow_dispatch` and `main` pushes affecting ForgeOS.
- Required outcome: package dry-run pass + RC manifest generation + packaged evidence artifacts.

## Gate Discipline

The following gates are blocking:

- ARCH-01
- BOUND-01
- CON-01
- LIFE-02
- PACK-01
- PACK-02
- PROD-02
- DOWN-01

Any failed blocking gate stops merge/release until fixed with evidence.

## Evidence Artifacts

Expected evidence outputs:

- `tools/_local/evidence/forgeos_import_boundaries_report.json`
- `tools/_local/evidence/forgeos_package_dry_run_report.json`
- `tools/_local/evidence/forgeos_release_candidate_manifest.json`

Artifacts are uploaded by workflow runs and must be referenced in PR/release records.

## Weekly Operating Cadence

1. Boundary drift check:
- Review import boundary report and dependency drift from the latest week.

2. Contract coverage check:
- Validate that new cross-layer interactions are registered in contract indexes.

3. Packaging check:
- Run RC lane and confirm manifests, BOMs, rollback plans, and release notes remain coherent.

4. Decision log hygiene:
- Record new defaults and architectural decisions in governance docs before shipping.
