# UI Improvement Validation

## Purpose

Keystone visual changes must be reproducible and measurable.

The validation workflow produces objective evidence:

1. before snapshot
2. after snapshot
3. pixel diff visualization
4. percentage of change
5. route + canonical query
6. layer/profile/motion context
7. timestamp + environment metadata

## No Proof, No Ship

Visual improvements are claims, not assumptions.

If an improvement is claimed, it must be linked to:

- a claim file in `docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md`
- generated artifacts in `artifacts/keystone-scene-studio/scenes/<sceneId>/<RUN_ID>/`

Gate command:

```powershell
pnpm run keystone:scene:proof:gate -- --claim-id=<RUN_ID>
```

## Scene Manifest

Source:

- `docs/visual-scenes/SCENES.json`

Each scene includes:

- `route`
- `query`
- `viewport`

Optional:

- `title`
- `tags`
- `notes`

## Commands

Install Chromium once:

```powershell
pnpm --filter @hitech/keystone exec playwright install chromium
```

Smoke run (subset):

```powershell
pnpm run keystone:scene:visual:smoke
```

Full run (all manifest scenes):

```powershell
pnpm run keystone:scene:visual
```

Intentional baseline update:

```powershell
pnpm run keystone:scene:visual:update
```

Generate / refresh report index:

```powershell
pnpm run keystone:scene:report
```

Legacy compatibility commands still available:

```powershell
pnpm run ui:improvement:test
pnpm run ui:layers:verify
```

## Artifact Outputs

Root:

- `artifacts/keystone-scene-studio/index.md`
- `artifacts/keystone-scene-studio/index.html`

Per scene run:

- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/before.png`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/after.png`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/diff.png`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/report.md`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/report.html`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/report.json`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/console.log`
- `artifacts/keystone-scene-studio/scenes/<scene-id>/<run-id>/network.log`

Baselines:

- `docs/visual-baselines/ui-improvement-scenes/<scene-id>__<viewport>.png`

## Scorecard Model

Categories:

- `NO_CHANGE`: `0%`
- `SMALL_CHANGE`: `>0%` and `<0.5%`
- `SIGNIFICANT_CHANGE`: `>=0.5%`

Bands within significant:

- `moderate`: `0.5%` to `5%`
- `significant`: `>5%`

Evidence score (informational):

- `NO_CHANGE` => `0`
- `SMALL_CHANGE` => `35`
- `SIGNIFICANT_CHANGE (moderate)` => `70`
- `SIGNIFICANT_CHANGE (significant)` => `90`

## Deterministic Controls

Validation uses:

- fixed viewport presets
- UTC timezone + `en-US` locale
- forced reduced motion
- forced light color scheme
- injected CSS to disable transitions/animations
- deterministic `Date.now`, `Math.random`, `performance.now`
- wait for `document.fonts.ready`
- wait for `document.documentElement[data-scene-ready="1"]`

## Updating Baselines Intentionally

1. Confirm change intent with a claim file.
2. Run update command.
3. Review generated diffs and reports.
4. Run proof gate.
5. Commit baseline updates with linked claim.

## Adding New Scenes

1. Add scene entry to `docs/visual-scenes/SCENES.json`.
2. Ensure route/query are deterministic.
3. Run smoke suite.
4. If stable, run full suite.
5. Regenerate index.
