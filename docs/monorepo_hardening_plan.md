# Monorepo Hardening Plan - HITECH OS

## Strategy
No big-bang migration. Harden in small additive steps:
1. Observe first.
2. Add soft-fail guardrails.
3. Promote selected checks to blocking only after stable signal.

## Success metrics (engineering health indicators)
Track these per PR and over rolling windows:
- pipeline duration p50/p95
- cache hit rate
- number of affected projects per change
- dependency cycle count
- packages/folders without owners
- checkout/fetch time
- flaky job rate

Machine-readable report targets:
- `F:\repos\hitech-os\tools\_local\reports\ci\affected_projects.json`
- `F:\repos\hitech-os\tools\_local\reports\ci\codeowners_coverage.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`

## Phase 0 - Observe and baseline
### Goal
Create trustworthy baseline telemetry without changing enforcement semantics.

### Changes
1. Capture current structure and CI behavior in audit docs.
2. Produce Graphviz scoped summary over existing outputs (no pipeline replacement).
3. Produce CODEOWNERS coverage report.
4. Produce conservative affected-project report.

### Risk
Low. Read-only analysis and report generation.

### Validation
- Reports are generated and JSON-parseable.
- Existing CI behavior is not made stricter yet.

### Rollback
- Remove reporting scripts and workflow steps; no runtime impact.

## Phase 1 - Safe guardrails (implemented in this PR)
### Goal
Reduce entropy growth with non-breaking controls and better selectivity.

### Changes
1. Add conservative affected detection with transitive dependents:
   - `F:\repos\hitech-os\tools\scripts\compute_affected_projects.mjs`
2. Add CODEOWNERS coverage reporting:
   - `F:\repos\hitech-os\tools\scripts\report_codeowners_coverage.mjs`
3. Extend Graphviz workflow additively with scoped index/summary:
   - `F:\repos\hitech-os\tools\graphviz\build_scope_index.py`
   - outputs: `scope_summary.json`, `index.scoped.html` under existing graph folder.
4. Apply coarse CI path filtering where confidence is high:
   - `F:\repos\hitech-os\.github\workflows\ci.yml`
   - `F:\repos\hitech-os\.github\workflows\docs-governor.yml`
   - `F:\repos\hitech-os\.github\workflows\dev-console-architecture-guard.yml`
5. Keep enforcement soft: reports + artifacts, no new hard-fail quality gate introduced.

## Phase 1b - Second-pass hardening pack (implemented in this PR)
### Goal
Increase governability with enforceable low-risk automation while preserving report-first rollout safety.

### Changes
1. Added executable policy files:
   - `F:\repos\hitech-os\policies\dependencies.json`
   - `F:\repos\hitech-os\policies\release.json`
   - `F:\repos\hitech-os\policies\security.json`
2. Added guardrail scripts:
   - `check_no_new_cycles.mjs` (strict-safe workspace cycle gate)
   - `check_release_discipline.mjs` (report-first release governance)
   - `report_sensitive_paths.mjs` (sensitive-path + high-confidence secret scan)
   - `report_repo_hygiene.mjs` (tracked large/generated artifact visibility)
   - `collect_engineering_health.mjs` (machine-readable CI health summary)
3. Strengthened CI workflows:
   - `ci.yml` now runs deterministic guardrails + observability artifacts + timing metrics.
   - `dependency-check.yml`, `security-scan.yml`, `release.yml` moved from TODO stubs to real checks/reporting.
4. Extended Graphviz scoped outputs with:
   - workspace cycle/hub summaries
   - cross-boundary edge summaries
   - ownership overlays
5. Improved CODEOWNERS precision for sensitive paths while keeping placeholder-safe ownership assumptions.

### Risk
Low-medium.
- Added checks are mostly report-first.
- Strict mode is used only where signal is stable (`no-new-cycles`).

### Validation
1. `node --check` on all new scripts.
2. Local execution of each guardrail script with JSON outputs.
3. Python compile + run of updated Graphviz scope index builder.

### Rollback
1. Revert new workflow steps to report-only/no-op stubs.
2. Keep policies/docs for traceability even if enforcement steps are rolled back.

### Risk
Low-medium.
- Workflow trigger scope changes can skip unnecessary runs, but may hide edge cases if filters are too narrow.

### Validation
1. Confirm workflows still trigger on relevant code changes.
2. Confirm new JSON artifacts are uploaded in CI runs.
3. Confirm `index.scoped.html` and `scope_summary.json` are generated.

### Rollback
- Revert workflow trigger filters to previous broad triggers.
- Remove new reporting steps/scripts.
- Keep existing graph outputs untouched.

## Phase 2 - Enforce gradually
### Goal
Move from visibility to reliable governance gates.

### Changes
1. Affected execution in CI:
   - Drive lint/test/build matrix from affected report.
   - Always include transitive dependents.
2. Ownership hardening:
   - Replace single catch-all CODEOWNERS with path-granular ownership.
   - Require mandatory review for sensitive paths.
3. Release governance:
   - Decide lockstep vs independent versioning explicitly.
   - Add change-file/changelog enforcement for publishable surfaces.
   - Add API change gates for `packages/contracts` and service API contracts.
4. Security governance:
   - Add automated secret scanning gate (soft mode first).
   - Define segregation policy for high-sensitivity non-runtime content.
5. Observability hardening:
   - Publish p50/p95, cache hit, affected-count, flakiness and checkout-time trends.

### Risk
Medium.
- Team process change and potential short-term CI friction.

### Validation
- Two to four weeks of stable metrics without major false positives.
- Measurable reduction in unnecessary jobs and PR latency.

### Rollback
- Downgrade new checks to warning mode.
- Keep telemetry/report generation active for diagnosis.

## Lockstep vs independent versioning recommendation
Current state: all workspace packages are private and release flow is not package-centric.

Recommendation:
- Keep lockstep governance at repository level for now.
- Treat `packages/contracts` and service HTTP contracts as release-critical surfaces with mandatory change documentation.
- Re-evaluate independent versioning only if packages become externally published or independently deployed.

## Decision gates before tightening enforcement
1. CI observability available for at least 10-20 representative PRs.
2. CODEOWNERS granularity agreed by maintainers.
3. Affected detector false-positive/false-negative review completed.
4. Graphviz scoped summary adopted as architecture review entrypoint.

## Exit criteria
Phase 1 is successful when:
- CI generates affected + ownership artifacts on each relevant run.
- Graphviz scoped summary exists and is stable.
- Workflow over-triggering decreases for known noisy paths.

Phase 2 can start when:
- Metrics baseline is stable and trusted.
- Owners are assigned for sensitive paths.
- Release governance policy is explicit and documented.
