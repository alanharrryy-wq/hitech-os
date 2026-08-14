# 💎 Code Atlas

> Repository-neutral architecture atlas, dependency explorer, database reality checker, surface target mapper, and forensic evidence generator.

Code Atlas is a read-oriented analysis workspace for Python, JavaScript/TypeScript, Prisma, SQLite, and mixed full-stack repositories. Its neutral core accepts an explicit repository root and output root, records uncertainty instead of inventing green status, and keeps project-specific knowledge outside default execution paths.

## Neutrality contract

The default Code Atlas execution model is environment-neutral:

- no fixed drive letters, user-home paths, repository names, ports, domains, products, or operating-system executables;
- repository and output roots come from CLI arguments, caller configuration, or `CODE_ATLAS_*` environment variables;
- surfaces come from a caller profile or generic repository discovery;
- external evidence locations are explicit and path-redacted in exported evidence;
- optional project integrations are opt-in profiles or adapters and are never activated implicitly;
- missing policy, scope, provenance, runtime evidence, or adapters fail closed or remain explicitly unconfigured;
- neutral core is continuously certified on Linux and Windows by `.github/workflows/code-atlas-neutrality.yml`.

The reference neutral profile is `profiles/generic.example.json`. A project-specific example may coexist under `profiles/` to demonstrate explicit adapter configuration, but it does not change neutral defaults.

## Operational Evidence CLI

Set `PYTHONPATH` to `tools/code-atlas/src` or install the package in your preferred environment, then run:

```text
python -m code_atlas.operational --repo <PROJECT_ROOT> --out <OUTPUT_ROOT>
```

Optional prior evidence can be supplied explicitly:

```text
python -m code_atlas.operational --repo <PROJECT_ROOT> --out <OUTPUT_ROOT> --result-root <EVIDENCE_ROOT>
```

The operational runner emits a manifest, sanitized database/schema observations, scope/provenance evidence, capability hardening ledgers, fail-closed blockers, and investigator outputs. `productionCertified` remains false unless a separate evidence-backed gate proves otherwise.

## Surface Target Atlas

Surface mapping is also repository-neutral:

```text
python -m code_atlas.surface_target_atlas.runner --selected-path <PROJECT_ROOT> --target-app all --output-root <OUTPUT_ROOT>
```

When no app profile is provided, Code Atlas discovers conventional `apps/`, `services/`, `packages/`, or `products/` directories. A profile can define arbitrary surface IDs and roots. The atlas is read-only and never authorizes a patch by itself.

## Project profiles

Code Atlas reads `CODE_ATLAS_PROFILE` when supplied. Important profile fields include:

```json
{
  "profileId": "example",
  "projectName": "Example Project",
  "projectRoot": "${CODE_ATLAS_PROJECT_ROOT}",
  "outputRoot": "${CODE_ATLAS_OUTPUT_ROOT}",
  "apps": [
    {"id": "web", "label": "Web", "root": "apps/web", "kind": "web"}
  ],
  "metadata": {
    "scanRoots": ["."],
    "evidenceRoots": [],
    "supportResolverEnabled": false,
    "supportResolverRoots": []
  }
}
```

Project-specific paths, URLs, names, evidence roots, support catalogs, or runtime adapters belong in a profile or caller environment, never in neutral core defaults.

## Main modules

```text
tools/code-atlas/
├─ src/code_atlas/core/                 # project profile and shared neutral primitives
├─ src/code_atlas/operational/          # fail-closed operational evidence engine
├─ src/code_atlas/surface_target_atlas/ # generic surface/target discovery
├─ src/code_atlas/legal_readiness/      # adapter-driven diligence evidence coordinator
├─ src/code_atlas/coverage/             # coverage and important-file gates
├─ src/code_atlas/db_glass/             # database/schema reality inspection
├─ src/code_atlas/manifest/             # evidence packaging metadata
├─ profiles/generic.example.json        # neutral profile template
└─ tests/test_code_atlas_neutrality.py  # cross-platform neutrality certification
```

## Safety model

Code Atlas neutral core follows these invariants:

- database inspection is read-only;
- source repositories are not modified by evidence collection;
- no Git write is required by neutral analysis;
- no process kill, port release, server startup, dependency installation, or Prisma generation is part of neutral analysis;
- raw secret-like values are redacted or hashed where evidence is sampled;
- missing evidence is not converted into a positive claim;
- structure, runtime evidence, and production certification are separate layers of truth.

## Validation

The neutrality workflow compiles the neutral stack and runs the neutrality tests plus operational fail-closed regressions on both Linux and Windows. The certification intentionally fails if neutral source reintroduces machine-specific paths, project repository names, implicit product surfaces, fixed PowerShell execution, or other banned coupling.

Code Atlas is a trust machine for unfamiliar repositories: map the system, expose the unknowns, and only then decide what can safely be claimed or changed.
