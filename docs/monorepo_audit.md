# Monorepo Audit - HITECH OS

## Executive summary
The repository is a real monorepo with one shared lockfile (`F:\repos\hitech-os\pnpm-lock.yaml`) and 10 workspace packages under `apps/*`, `services/*`, `packages/*`, and `tools/*`. The main entropy drivers are not core package coupling; they are governance and operational drift: ownership concentration, noisy architecture graph scope, and tracked generated artifacts. CI has moved from placeholder state to reportable guardrails, but long-horizon metrics and stricter release/security enforcement are still pending.

The fastest low-risk hardening path is:
1. Observe and instrument first.
2. Reduce CI over-triggering and add conservative affected detection.
3. Improve Graphviz signal-to-noise using the existing pipeline (no Mermaid, no replacement).
4. Keep new checks non-blocking first.

## Second-pass hardening delta (implemented)
1. Placeholder workflows converted into executable guardrail/report lanes:
   - `F:\repos\hitech-os\.github\workflows\dependency-check.yml`
   - `F:\repos\hitech-os\.github\workflows\security-scan.yml`
   - `F:\repos\hitech-os\.github\workflows\release.yml`
2. Core CI now emits machine-readable observability and governance artifacts.
3. No-new-workspace-cycles guardrail added (`check_no_new_cycles.mjs`) with strict-safe mode.
4. Release discipline, sensitive-path governance, and repo hygiene scripts added in report-first mode.
5. Graphviz scoped summary now includes ownership overlays and workspace dependency health metadata.
6. CODEOWNERS precision improved for sensitive paths (concentration risk still present: single owner).

## Is this truly a monorepo?
Yes.

Evidence:
- Single workspace root and lockfile:
  - `F:\repos\hitech-os\pnpm-workspace.yaml`
  - `F:\repos\hitech-os\pnpm-lock.yaml`
- Multiple logical projects share one CI namespace and one root package manager:
  - `F:\repos\hitech-os\apps\keystone\package.json`
  - `F:\repos\hitech-os\apps\web\package.json`
  - `F:\repos\hitech-os\services\core-api\package.json`
  - `F:\repos\hitech-os\services\ai-agent\package.json`
  - `F:\repos\hitech-os\packages\contracts\package.json`
  - `F:\repos\hitech-os\packages\ui-kit\package.json`
- Shared boundary guard exists and passes:
  - `F:\repos\hitech-os\tools\scripts\validate_workspace_boundaries.mjs`
  - Result: `[workspace:validate] OK`

Qualification:
- It is also a semi-monorepo from an operations standpoint because the repo contains large governance/docs/artifact surfaces beyond runtime code (`.agents`, `.codex`, `_reports`, `.repo_map`, `docs/knowledge/codex_chats`).

## Top 5 pain points (impact x urgency)

### 1) CI quality gates are under-enforced and over-broad
Impact: Very high. Urgency: Immediate.

Evidence:
- Core workflows now execute deterministic guardrails and machine-readable reporting:
  - `F:\repos\hitech-os\.github\workflows\ci.yml`
  - `F:\repos\hitech-os\.github\workflows\dependency-check.yml`
  - `F:\repos\hitech-os\.github\workflows\security-scan.yml`
  - `F:\repos\hitech-os\.github\workflows\release.yml`
- Some workflows still trigger globally on both `push` and `pull_request` with no path selectivity:
  - `F:\repos\hitech-os\.github\workflows\docs-governor.yml` (before Phase 1 changes)
  - `F:\repos\hitech-os\.github\workflows\dev-console-architecture-guard.yml` (before Phase 1 changes)
- Historical pipeline p50/p95 and cache-hit trend reporting is still missing.

### 2) Graphviz architecture view is correct but too noisy for decision-making
Impact: High. Urgency: Immediate.

Evidence:
- Existing Graphviz pipeline is present and must be preserved:
  - Generator: `F:\repos\hitech-os\tools\graphviz\generate_repo_graphs.py`
  - Outputs: `F:\repos\hitech-os\tools\graphviz\graphs\**` with `graph.svg`, `graph.dot`, `summary.json`, `README.txt`, master `index.html`
- Active manifest includes many operational/non-runtime folders:
  - `active_folder_count = 939`
  - `noise_active_count = 670`
  - from `F:\repos\hitech-os\tools\graphviz\.graphviz_manifest.json`
- Scope skew:
  - `tools = 693 folders`, `apps = 78`, `packages = 48`, `services = 11`

### 3) Ownership technically covers files but governance is single-owner
Impact: High. Urgency: High.

Evidence:
- `F:\repos\hitech-os\.github\CODEOWNERS` contains one catch-all owner: `* @alanharrryy`
- Coverage is 100%, but owner count is 1 (bus-factor concern):
  - verified by `F:\repos\hitech-os\tools\scripts\report_codeowners_coverage.mjs`

### 4) Git hygiene has tracked generated/binary payloads that increase clone and review cost
Impact: High. Urgency: High.

Evidence:
- Large tracked blobs include non-runtime artifacts:
  - `F:\repos\hitech-os\hitech_logo.png` (19.33 MB)
  - `F:\repos\hitech-os\.repo_map\repo_map.sqlite` (6.61 MB)
  - `F:\repos\hitech-os\docs\knowledge\codex_chats\...\REPO_HITS.json` (5.90 MB)
  - `F:\repos\hitech-os\_reports\hydration_guard\hydration_guard_findings.json` (5.35 MB)
- Tracked volume concentration:
  - `docs` ~28.19 MB tracked
  - `.repo_map` ~10.53 MB tracked
  - `_reports` ~7.79 MB tracked
- Full history is available (`git rev-parse --is-shallow-repository = false`), so old large blobs remain historical weight.

### 5) Release and versioning governance is minimally defined and effectively coupled
Impact: Medium-high. Urgency: Medium.

Evidence:
- All workspace packages are private (`private: true` in all package manifests).
- Release config exists but only for root package context:
  - `F:\repos\hitech-os\release-please-config.json`
  - `F:\repos\hitech-os\.releaserc.json`
- No changeset/changelog enforcement per package found (`NO .changeset directory`).
- Release governance workflow exists, but remains report-first and not yet a complete publishing gate.

## Dependency graph findings
- Workspace package dependency graph is small and acyclic:
  - edges:
    - `apps/keystone -> packages/contracts`
    - `apps/keystone -> packages/ui-kit`
    - `apps/web -> packages/contracts`
    - `apps/web -> packages/ui-kit`
  - cycles found: none (package level)
- Boundary validator currently reports no explicit violations:
  - `F:\repos\hitech-os\tools\scripts\validate_workspace_boundaries.mjs`
  - Result: `[workspace:validate] OK`

## CI and build pain findings
- Turbo config exists (`F:\repos\hitech-os\turbo.json`) but root CI is not yet using real turbo affected execution.
- Path filtering exists in targeted workflows (`factory.yml`, `promotion.yml`) but not consistently across core checks.
- Caching is limited:
  - `factory.yml` caches pip.
  - Node dependency/turbo cache strategy is not wired in core CI workflow.

## Security and sensitive-path governance findings
- No obvious credential leak signatures were found in tracked content via pattern checks.
- Secrets policy exists but is high-level and minimal:
  - `F:\repos\hitech-os\docs\security\SECRETS.md` is placeholder-level.
  - `F:\repos\hitech-os\SECURITY.md` defines principles but not enforcement gates.
- Sensitive paths are now codified in CODEOWNERS, but still concentrated in one owner:
  - `.github/workflows`, `services`, `packages/contracts`, `apps/keystone/app/api`, `tools/codex`, `tools/graphviz`, `terraform`, `helm`, `k8s`, `policies`.

Privacy boundary note:
- There are high-context exports under `F:\repos\hitech-os\docs\knowledge\codex_chats\...`.
- If strong privacy isolation is required by design, this domain should be reviewed for externalization outside core runtime monorepo scope.

## Developer experience and local tooling hygiene findings
- Golden-path command consistency is partial:
  - Strong root scripts exist (`quality`, `workspace:validate`, `deps:check`, `health`).
  - `Makefile` and `Taskfile.yml` are placeholders (`TODO`), causing command-surface drift.
- Toolchain pinning is partial:
  - Node/pnpm are pinned in root `package.json`.
  - No active root `.nvmrc`/`.node-version`/`.python-version` found.
- Dependency hygiene script references missing `factory/package.json` and warns:
  - `F:\repos\hitech-os\tools\scripts\check_dependency_hygiene.mjs`
  - warning: skipped missing manifest `factory/package.json`.

## Observability baseline status
Current status: insufficient baseline metrics.

Available now:
- New machine-readable scope reports were added in Phase 1 (see plan/doc files).

Still missing:
- pipeline duration p50/p95
- cache hit rate
- flakiness rate
- checkout/fetch timing trend
- affected-project count trend over time

## Short-term risks (0-30 days)
- Regressions can still merge when report-mode warnings are not enforced as blocking checks.
- Ownership bottleneck in critical paths increases operational risk.
- Graph review burden remains high if scoped view is not used.

## Medium-term risks (1-3 quarters)
- Repository clone/review performance and cognitive load continue to degrade if generated/binary artifacts keep accumulating in Git history.
- Release safety remains manual and brittle without per-scope change governance.
- Security controls remain policy-level but not consistently enforced at CI gate level.

## What is currently missing
1. Progressive enforcement plan to move stable report-only checks into blocking gates.
2. First-class CI observability trend dashboards (p50/p95, cache hit, flake rate) and retention policy.
3. Granular CODEOWNERS policy for sensitive paths and secondary reviewers.
4. Explicit release governance for API/public-contract changes and changelog/change-file discipline.
5. Graphviz scoped architecture view as default human entrypoint for runtime code.
6. Strong secret-sprawl controls beyond policy text (automated scanners, deny rules, segregation policy).

## Insufficient evidence notes
1. Branch protection/ruleset enforcement is not visible from local checkout alone. GitHub repository settings are required to confirm effective review gates.
2. CI p50/p95 durations and cache hit rates are not derivable from repository files only. Historical workflow run telemetry is required.

## Evidence references
- `F:\repos\hitech-os\.github\workflows\ci.yml`
- `F:\repos\hitech-os\.github\workflows\docs-governor.yml`
- `F:\repos\hitech-os\.github\workflows\dev-console-architecture-guard.yml`
- `F:\repos\hitech-os\.github\workflows\factory.yml`
- `F:\repos\hitech-os\tools\graphviz\generate_repo_graphs.py`
- `F:\repos\hitech-os\tools\graphviz\.graphviz_manifest.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\index.html`
- `F:\repos\hitech-os\tools\scripts\validate_workspace_boundaries.mjs`
- `F:\repos\hitech-os\tools\scripts\check_dependency_hygiene.mjs`
- `F:\repos\hitech-os\.github\CODEOWNERS`
- `F:\repos\hitech-os\SECURITY.md`
- `F:\repos\hitech-os\docs\security\SECRETS.md`
