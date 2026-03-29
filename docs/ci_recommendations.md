# CI Recommendations - HITECH OS

## Current CI behavior
### Workflows present
- `F:\repos\hitech-os\.github\workflows\ci.yml`
- `F:\repos\hitech-os\.github\workflows\factory.yml`
- `F:\repos\hitech-os\.github\workflows\docs-governor.yml`
- `F:\repos\hitech-os\.github\workflows\dev-console-architecture-guard.yml`
- `F:\repos\hitech-os\.github\workflows\promotion.yml`
- plus release/security/dependency placeholders.

### Observed behavior
1. Placeholder workflows were replaced in second pass with reportable guardrails:
   - `dependency-check.yml`
   - `security-scan.yml`
   - `release.yml` (release governance lane)
2. `factory.yml` is the most mature workflow (path-filtered, matrix, pip cache).
3. Core CI now computes affected scope, ownership, dependency cycles, release discipline, sensitive-path scans, repo hygiene, and engineering-health summary.
4. CI metrics artifacts now exist, but p50/p95/cache-hit/flakiness trend computation still needs historical run aggregation.

## Coarse path filtering recommendations
Coarse filters should skip known noise paths that should not trigger full CI:
- `tools/graphviz/graphs/**`
- `tools/_local/**`
- `_reports/**`
- `.repo_map/**`
- `docs/knowledge/codex_chats/**`
- `artifacts/**`

Status:
- Added to `F:\repos\hitech-os\.github\workflows\ci.yml` in Phase 1.
- Added targeted paths to docs/dev-console workflows in Phase 1.

## Fine-grained affected detection recommendations
### Introduce conservative affected selection
Use:
- `F:\repos\hitech-os\tools\scripts\compute_affected_projects.mjs`

Behavior:
- maps changed files to workspace projects
- includes transitive dependents
- falls back to global trigger for unmatched non-doc changes

Recommendation:
1. Keep report-only mode first (current state).
2. After stability window, execute project-level lint/test/build using affected project list.
3. Keep always-run global checks for governance/security paths.

## Caching opportunities
### Node and pnpm
Current state:
- core CI now uses `pnpm/action-setup@v4` + `actions/setup-node@v4` with `cache: pnpm`.
- frozen lockfile install is part of the CI baseline.

Recommendation:
1. Use `pnpm/action-setup@v4` + `actions/setup-node@v4` with cache enabled.
2. Enable Turbo local/remote cache progressively:
   - `F:\repos\hitech-os\tools\hos\turbo\turbo_wrap.py`
   - `F:\repos\hitech-os\docs\system\REMOTE_CACHE_SETUP.md`

### Python
Current state:
- `factory.yml` uses `actions/setup-python@v5` with pip cache.

Recommendation:
- Keep pip cache and mirror this pattern for other Python-heavy workflows where needed.

## Jobs that should remain global triggers
Even after affected execution, keep these global:
1. policy/governance checks for `docs/CONTRACT.md`, `docs/CONSTITUTION.md`, `.github/workflows/**`
2. security baseline checks
3. lockfile/package manager integrity checks
4. release metadata consistency checks on main/release branches

## PR pipeline vs main/release pipeline split
### PR pipeline (fast, selective)
- affected lint/test/typecheck/build for workspace projects
- boundary validation
- CODEOWNERS coverage report
- graph scope summary refresh (optional artifact)

### Main pipeline (broader, confidence)
- full quality gate (or full affected + nightly full)
- security scans
- release safety checks
- baseline observability report publish

### Release pipeline (strictest)
- provenance, changelog/change-file completeness
- public API contract diff checks for publishable surfaces
- immutable artifact checks

## Observability instrumentation (required)
Produce machine-readable artifacts per run:
1. `affected_projects.json` (affected count + fallback reason)
2. `codeowners_coverage.json` (coverage + single-owner flag)
3. `dependency_cycles.json` (no-new-cycles guardrail)
4. `release_discipline.json`
5. `sensitive_paths.json`
6. `repo_hygiene.json`
7. `engineering_health.json`
8. `scope_summary.json` snapshot from Graphviz scoped index

Add computed CI metrics (next step):
- p50/p95 duration from workflow run history
- cache hit ratio
- flaky retry count
- checkout/fetch duration

## Release/versioning governance recommendations for CI
Current state:
- all workspace packages private
- no package-level changeset enforcement
- release workflow is placeholder

Recommendation:
1. Maintain lockstep repo-level release policy now.
2. Add CI gates for `packages/contracts` and service API contract changes.
3. Require changelog/change-note files for contract/API touching PRs.

## Security and sensitive-path CI governance
Add dedicated review and checks for:
- `.github/workflows/**`
- `services/**`
- `packages/contracts/**`
- `apps/keystone/app/api/**`
- infra paths (`terraform`, `helm`, `k8s`)

Secret-sprawl guard recommendation:
- add automated secret scan gate in non-blocking mode first.

## Evidence references
- `F:\repos\hitech-os\.github\workflows\ci.yml`
- `F:\repos\hitech-os\.github\workflows\factory.yml`
- `F:\repos\hitech-os\.github\workflows\docs-governor.yml`
- `F:\repos\hitech-os\.github\workflows\dev-console-architecture-guard.yml`
- `F:\repos\hitech-os\tools\scripts\compute_affected_projects.mjs`
- `F:\repos\hitech-os\tools\scripts\report_codeowners_coverage.mjs`
- `F:\repos\hitech-os\tools\hos\turbo\turbo_wrap.py`
- `F:\repos\hitech-os\docs\system\REMOTE_CACHE_SETUP.md`
