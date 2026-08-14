# Code Atlas Neutrality Contract

Status: `ENFORCED_BY_CI`

## Goal

Code Atlas neutral execution must be able to analyze an arbitrary supported repository without knowing the repository name, developer workstation, operating system, drive layout, product surfaces, local ports, internal project brands, or private evidence locations in advance.

## Neutral core

The continuously certified neutral execution surface includes:

- `src/code_atlas/core/**`
- `src/code_atlas/operational/**`
- `src/code_atlas/surface_target_atlas/**`
- `src/code_atlas/legal_readiness/**`
- `src/code_atlas/coverage/**`
- `src/code_atlas/db_glass/**`
- `src/code_atlas/manifest/**`
- `src/code_atlas/cli/**`

`tests/test_code_atlas_neutrality.py` and `.github/workflows/code-atlas-neutrality.yml` are blocking guards for this boundary.

## Required invariants

1. **Explicit root authority.** The caller-provided repository root is authoritative. Core never searches for a developer-specific repository path.
2. **No workstation defaults.** Core contains no fixed drive letters, user homes, download folders, private tool roots, or OS-specific executable defaults.
3. **No product assumptions.** Surface names and roots come from a profile or generic directory discovery. Tablet, desktop, mobile, admin, web, or any other product is data, not core knowledge.
4. **No brand leakage.** Project-specific brands, internal service names, support roots, and governance labels do not appear in neutral output or default logic.
5. **Optional integrations are opt-in.** A project-specific profile may define paths, URLs, surfaces, evidence roots, support catalogs, or runtime adapters. Neutral core never activates one implicitly.
6. **Path-safe evidence.** Repository paths are relative. External paths are represented by a digest-backed opaque reference rather than an absolute workstation path.
7. **Read-only evidence collection.** Neutral analysis does not write source files, write Git, mutate databases, install dependencies, generate ORM clients, control ports, or start/kill product processes.
8. **Fail closed.** Missing policy, scope, provenance, evidence, adapter configuration, or runtime proof cannot become a positive certification claim.
9. **Certification separation.** Source hardening, observed runtime evidence, and production certification remain separate states. Neutrality does not imply production readiness.
10. **Cross-platform proof.** The same neutrality suite must pass on Linux and Windows.

## Explicit profiles

`profiles/generic.example.json` is the neutral reference profile.

Project-specific examples may coexist under `profiles/` as explicit opt-in adapters. Their values are configuration examples and are outside neutral defaults. A profile does not gain authority unless the caller selects it with `CODE_ATLAS_PROFILE` or supplies equivalent caller configuration.

## What counts as a neutrality regression

CI fails when the certified core reintroduces any of the following:

- fixed local drive paths or private output folders;
- a known repository name as a default;
- a fixed product root or surface hierarchy;
- a fixed PowerShell executable or other OS-specific runtime adapter;
- an implicit project support/governance bridge;
- project-branded output schemas in neutral core;
- absolute repository or temporary paths in neutral evidence output;
- source mutation during the synthetic neutral-repository run.

## Evidence

The definitive mechanical evidence is the `Code Atlas Neutrality` GitHub Actions workflow. Both matrix jobs must pass. The workflow also runs the operational fail-closed regression suite and the legal backend neutral self-test so neutrality cannot be achieved by amputating existing safety behavior.
