# Engineering Health Metrics

This document defines machine-readable engineering health outputs for monorepo hardening.

## Report files
Primary CI report directory:
- `F:\repos\hitech-os\tools\_local\reports\ci`

Core artifacts:
- `dependencies_policy_validation.json`
- `workspace_boundaries.json`
- `dependency_hygiene.json`
- `affected_projects.json`
- `codeowners_coverage.json`
- `dependency_cycles.json`
- `release_discipline.json`
- `sensitive_paths.json`
- `repo_hygiene.json`
- `engineering_health.json`

Graph health input:
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_top_risks.json`

## Health indicators
Tracked now:
- pipeline timing samples (`checkout`, `install`, `guardrails`, `artifact_upload`, `total`)
- dependency-policy structural/sync status
- workspace-boundary validation status
- affected project count and global-trigger fallback
- dependency cycle count and new-cycle count
- boundary-policy violation count in workspace manifest graph
- ownership concentration (`owner_count`, `single_owner_mode`)
- release violation count/status
- sensitive-path change count + secret finding count
- graph signal-to-noise (`focus_clean_active_folders`, `noise_active_folders`, top-risk score)
- repo hygiene (`large_file_count`, `lfs_candidate_count`)

Planned (insufficient evidence from repo-only context):
- p50/p95 over rolling windows
- cache hit/miss rate trend
- flaky job rate

## Target thresholds (initial)
- pipeline p50 target: `<= 900s`
- pipeline p95 target: `<= 1800s`
- new dependency cycles: `0`
- sensitive unowned changed files: `0`

## Review cadence
1. Per PR: inspect artifact deltas and warning trends.
2. Weekly: review p50/p95 trend and contract completeness ratio once historical telemetry is available.
3. Monthly: tighten checks from report-only to blocking where false positives stay low.
