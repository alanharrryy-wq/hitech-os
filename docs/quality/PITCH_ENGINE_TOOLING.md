# PITCH_ENGINE_TOOLING

## Purpose

This document defines the owned tooling layer for deterministic Pitch Engine rendering, triage, retention, and Definition of Done automation.

The implementation is Windows-first and repository-local. It does not modify Pitch Engine core components or route logic.

## Owned Paths

- `apps/keystone/lib/pitch-engine-tooling/**`
- `apps/keystone/scripts/pitch-engine/**`
- `apps/keystone/tests/pitch-engine-tooling/**`
- `tools/hos/quality/dod/**`
- `tools/hos/launcher/pitch_engine_*.ps1`

## Runtime Artifacts

All tooling outputs target:

`F:/repos/hitech-os/artifacts/keystone-pitch-engine`

### Run Layout

`programs/<programId>/<runId>/`

Contains:

- `resolved-program.json`
- `timeline.json`
- `report.json`
- `report.md`
- `manifest.json`
- `sequences/<sequenceId>/frames/<tMs>.png`
- `sequences/<sequenceId>/report.json`
- `sequences/<sequenceId>/report.md`
- `sequences/<sequenceId>/DIFF_NOTES.md`
- `scenes/<sceneId>/before.png`
- `scenes/<sceneId>/after.png`
- `scenes/<sceneId>/diff.png`
- `scenes/<sceneId>/report.json`
- `scenes/<sceneId>/report.md`
- `scenes/<sceneId>/DIFF_NOTES.md`
- `player/index.html`
- `player/player.js`
- `player/styles.css`
- `logs/console.log`

## Determinism Rules

The renderer enforces deterministic behavior via these controls:

1. Fixed viewport presets.
2. Reduced motion context in Playwright.
3. CSS animation and transition disabling at init script level.
4. Deterministic scene-ready wait strategy using `data-scene-ready="1"`.
5. Stable capture ordering by `sequenceId` then `tMs`.
6. Stable JSON serialization with sorted keys.
7. Stable marker inclusion in every capture plan.

## Capture Plans

Capture plans resolve in this precedence order:

1. External capture plan candidate file from core-owned locations.
2. Sequence-local defaults from tooling program model.
3. Mandatory marker captures.

Default timestamps include `0ms, 400ms, ... 8000ms` and mandatory markers:

- `marker-start`
- `marker-narrative-shift`
- `marker-pivot`
- `marker-cta`
- `marker-end`

## Performance Profile Behavior

Profiles:

- `full`
- `smoke`
- `lite`

Deterministic degradation to `lite` occurs when resource policy requires it:

- less than 8GB memory, or
- fewer than 4 CPU cores.

Degradation is encoded in every sequence report.

## Playwright Harness

The harness is implemented as a dedicated Playwright spec invoked through:

`pnpm dlx --package=playwright@1.51.1 playwright test apps/keystone/scripts/pitch-engine/playwright-capture.spec.mjs`

### Harness Contract

Input:

- `PITCH_ENGINE_CAPTURE_JOB_PATH`
- `PITCH_ENGINE_CAPTURE_RESULT_PATH`

Output:

- deterministic capture result JSON with capture records and warnings.

Fallback mode:

- deterministic placeholder PNG generation when Playwright is unavailable.

## Triage Contract

Sequence triage statuses:

- `pending`
- `accepted`
- `rejected`

Scene triage statuses:

- `pending`
- `accepted`
- `rejected`

Required guardrails:

1. Run path must exist before mutation.
2. Sequence path must exist before mutation.
3. Notes are clipped to configured max length.
4. Actor labels are clipped to configured max length.
5. Decision history is append-only.

## Retention and Pinning

Default retention policy:

- Keep last 20 runs per program.
- Preserve pinned runs (`PIN.marker`).
- Delete unpinned runs older than keep-last window.

Commands:

- `keystone:pitch:pin`
- `keystone:pitch:prune`

## CLI Command Catalog

### Render Commands

- `keystone:pitch:render`
- `keystone:pitch:render:smoke`
- `keystone:pitch:render:update`
- `keystone:pitch:render:sequence`

### Triage Commands

- `keystone:pitch:accept`
- `keystone:pitch:reject`
- `keystone:pitch:rerun`
- `keystone:pitch:notes`

### Support Commands

- `keystone:pitch:report`
- `keystone:pitch:doctor`
- `keystone:pitch:onebutton`
- `keystone:pitch:dod`
- `keystone:pitch:engine`

## One-Button Workflow

`keystone:pitch:onebutton` executes:

1. doctor
2. smoke render
3. limited DoD

This workflow is non-interactive and exits nonzero on failure.

## Doctor Contract

Doctor performs non-interactive preflight checks:

- Node version
- platform
- pnpm availability
- Playwright CLI availability
- Chromium browser availability
- artifact root availability
- artifact root writability
- port 3100 status (informational)
- memory/cpu telemetry (informational)

## DoD Integration

`tools/hos/quality/dod/run_dod.mjs`:

- loads checklist JSON
- executes checks in deterministic order
- optionally runs safe autofix handlers
- writes `artifacts/keystone-pitch-engine/last_dod.json`
- returns nonzero on FAIL

### Safe Autofix Handlers

- regenerate indexes
- normalize artifact index JSON
- normalize artifact names
- regenerate route discovery outputs

## Offline Player

Generated player requirements:

- no external CDN
- no network dependency for static bundle operation
- references local `timeline.json` and frame PNGs

## Operational Checklist

1. Run `keystone:pitch:doctor`.
2. Run `keystone:pitch:render -- --programId=<id> --smoke`.
3. Inspect `artifacts/keystone-pitch-engine/index.html`.
4. Use `keystone:pitch:accept/reject/notes`.
5. Run `keystone:pitch:prune`.
6. Run `keystone:pitch:dod`.

## Failure Modes and Responses

### Playwright unavailable

Symptoms:

- doctor fails `playwright-cli` or `playwright-browser`.

Response:

- install browser package and rerun doctor.
- renderer can still emit placeholder captures for continuity.

### Scene-ready signal missing

Symptoms:

- warnings per capture indicate selector not found.

Response:

- requires core runtime signal adoption outside tooling ownership.

### Missing route discovery outputs

Symptoms:

- DoD route-discovery check fails.

Response:

- run Keystone build to regenerate outputs.

### Retention metadata missing
n
Symptoms:

- run-retention-invariant warns or fails.

Response:

- run prune command to write metadata summary.

## Data Contracts

### `report.json` top-level keys

- `programId`
- `runId`
- `mode`
- `profile`
- `sequenceCount`
- `sceneCount`
- `warnings`
- `hash`
- `sequenceSummaries`
- `sceneSummaries`

### Sequence report keys

- `route`
- `captureCount`
- `profile`
- `status`
- `warnings`
- `frames`
- `schemaEnvelope`

### Scene report keys

- `beforeImage`
- `afterImage`
- `diffImage`
- `baselineExists`
- `status`
- `warnings`

## Security and Safety Notes

- All IDs are sanitized to a Windows-safe pattern.
- No path traversal (`..`) is allowed in IDs.
- All generated paths are validated to remain under artifact roots.

## Governance Notes

Checks that require non-owned domains are reported as FAIL/WARN with actionable reason. Tooling does not edit restricted core files.

## Maintenance

When adding new commands:

1. Add script file in owned CLI path.
2. Add package script wiring in `apps/keystone/package.json`.
3. Add root wrapper in root `package.json` if cross-workspace invocation is needed.
4. Extend DoD checklist and check logic.
5. Add test coverage under `apps/keystone/tests/pitch-engine-tooling`.

## Version History

- `1.0.0` Initial tooling delivery for deterministic render + triage + retention + DoD.
