# Code Atlas Neutrality Policy

Code Atlas reusable execution must remain **machine-neutral, repository-neutral and product-neutral**.

## Canonical runtime inputs

- `CODE_ATLAS_PROFILE`
- `CODE_ATLAS_PROJECT_ROOT`
- `CODE_ATLAS_OUTPUT_ROOT`
- `CODE_ATLAS_RESULT_ROOT`

Direct CLI/function arguments may override those values. When no location is supplied, reusable code falls back only to the current repository/process context and a relative `code-atlas-out` directory.

## Allowed in reusable code

- Relative paths resolved from an explicit project root.
- Generic repository/app/profile abstractions.
- Optional adapters selected explicitly by profile metadata.
- Technology detectors such as Python, SQLite, Prisma ORM, JavaScript or framework-specific parsers when they do not imply one customer's layout.

## Forbidden in reusable code

- Developer home paths or fixed drive roots.
- Fixed repository or application names.
- Fixed product domains, ports, labels or surface taxonomies.
- Automatic selection of a customer/product adapter.
- Writing to the analyzed repository, Git, databases, processes, ports or deployments from an analysis path.
- Any production/certification green inferred merely from detector existence.

## Product-specific compatibility

Product-specific values may exist only in explicit profiles/adapters and must be opt-in. Their presence does not contaminate the generic execution boundary when the neutrality contract marks them as adapters and generic entrypoints do not select them implicitly.

## Enforcement

`CODE_ATLAS_NEUTRALITY_CONTRACT.json` defines the neutral and adapter boundaries. `code_atlas.core.neutrality_gate` scans that boundary and fails closed with `BLOCKED_CODE_ATLAS_NEUTRALITY_VIOLATION` on machine/repository/product assumptions in reusable code.

GitHub CI runs the gate on Linux plus neutral temporary-repository execution tests. `productionCertified=false` remains invariant unless a separate evidence-backed certification gate proves otherwise.

## Migration rule

Never sanitize source code by blind string replacement. Classify a dependency first, migrate reusable behavior to runtime context/profile inputs, isolate genuine product compatibility behind an explicit adapter, then verify the boundary.
