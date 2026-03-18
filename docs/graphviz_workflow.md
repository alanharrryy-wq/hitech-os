# Graphviz Workflow - HITECH OS

## Scope
This document describes the existing Graphviz dependency workflow and the additive Phase 1 improvements.

No Mermaid was introduced.

## Existing generator (preserved)
Generator script:
- `F:\repos\hitech-os\tools\graphviz\generate_repo_graphs.py`

Core behavior:
1. scans repository files by supported extensions
2. buckets files by folder
3. extracts import edges
4. renders per-folder graph artifacts
5. keeps historical graph folders on disk
6. writes/updates `index.html`

## Output locations
Primary output root:
- `F:\repos\hitech-os\tools\graphviz\graphs`

Per-folder artifact structure:
- `graph.svg`
- `graph.dot`
- `summary.json`
- `README.txt`

Master files:
- `F:\repos\hitech-os\tools\graphviz\graphs\index.html`
- `F:\repos\hitech-os\tools\graphviz\.graphviz_manifest.json`
- `F:\repos\hitech-os\tools\graphviz\.graphviz_state.json`

## Metadata produced
From each `summary.json`:
- folder id
- folder path
- file count
- edge count total/rendered
- rendered timestamp
- style version

From manifest/state:
- folder id mapping
- active/inactive folder status
- last seen index/timestamp

## Phase 1 additive improvements
New script:
- `F:\repos\hitech-os\tools\graphviz\build_scope_index.py`

New outputs:
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_top_risks.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\index.scoped.html`

Improvement intent:
1. preserve existing index and historical outputs
2. add focused runtime view for apps/services/packages/tools
3. expose machine-readable noise and blast-radius metrics

## Phase 2 additive improvements
`build_scope_index.py` now enriches scoped outputs with:
1. workspace dependency health (project count, edge count, cycle count)
2. fan-in/fan-out hub summaries
3. cross-boundary workspace edges
4. boundary-violation prominence from dependency policy model
4. CODEOWNERS ownership overlay for focus folders
5. explicit ownership concentration signal (`single_owner_mode`)
6. risk scoring and top-hotspot prioritization for faster triage

Stable output locations remain unchanged:
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_top_risks.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\index.scoped.html`

## Current scoped summary highlights
From `scope_summary.json` baseline:
- active folders: 939
- focus active folders: 829
- focus clean active folders: 262
- noise active folders: 670
- workspace cycles: reported in `workspace_dependency_health.cycle_count`
- ownership concentration: reported in `ownership_overlay.single_owner_mode`

Interpretation:
- graph generation is working but architecture signal is diluted by operational/noise folders.

## Safe validation workflow
1. Ensure generator output exists:
   - run existing generation workflow as currently operated by maintainers.
2. Build scoped index:
   - `python F:\repos\hitech-os\tools\graphviz\build_scope_index.py`
3. Validate files exist:
   - `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`
   - `F:\repos\hitech-os\tools\graphviz\graphs\scope_top_risks.json`
   - `F:\repos\hitech-os\tools\graphviz\graphs\index.scoped.html`
4. Confirm no destructive cleanup occurred:
   - historical folders remain on disk.

## CI hook recommendation
Non-blocking hook candidate:
1. run `build_scope_index.py` when graph outputs or graph tooling change
2. publish `scope_summary.json` as CI artifact
3. do not fail build on metric thresholds in initial rollout

## Rollback
If needed, rollback is trivial:
1. remove `build_scope_index.py`
2. stop consuming `index.scoped.html` and `scope_summary.json`
3. continue using existing `index.html` only

## Evidence references
- `F:\repos\hitech-os\tools\graphviz\generate_repo_graphs.py`
- `F:\repos\hitech-os\tools\graphviz\graphs\index.html`
- `F:\repos\hitech-os\tools\graphviz\build_scope_index.py`
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\index.scoped.html`
