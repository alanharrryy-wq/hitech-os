# Keystone Scene Studio

## Purpose

Keystone Scene Studio is a production-grade developer workflow for visual iteration with proof:

- define deterministic visual scenes
- preview and compare scenes side-by-side
- validate layer resolution against DOM `data-layer-*` attributes
- generate canonical share URLs
- export/import scene packs
- run Playwright visual evidence and report scorecards

This turns visual changes into reproducible, measurable artifacts.

## Access Control

Route:

- `/dev/scene-studio`

Access requirements:

1. `NODE_ENV !== "production"`
2. and (`debug=1` query parameter OR `NEXT_PUBLIC_SCENE_STUDIO=1`)

Production behavior:

- route returns `404` using server-side `notFound()`
- Scene Studio API endpoints also return `404` in production

## Scene Contract

Runtime schema is versioned and validated in:

- `apps/keystone/lib/scene-studio/scene-schema.ts`
- `apps/keystone/lib/scene-studio/scene-migrations.ts`

Current schema version:

- `2`

A scene contains:

- `id` (stable slug)
- `title`
- `route` (must start with `/`)
- `query` (canonical query string)
- `viewport` (`desktop|mobile|tablet|custom` + optional custom size)
- `layerProfile` (`neutral|fx|perf`)
- `layers` (`none|all|list` + canonical layer IDs)
- `motion` (`on|off`)
- `notes` (optional)
- `tags` (optional)
- `createdAt` / `updatedAt`
- `schemaVersion`
- `expectations` (optional diagnostics constraints)

## Layer + Query Rules

Canonical layer IDs come from:

- `packages/ui-kit/src/layers/layerIds.ts`

Precedence:

1. defaults
2. profile
3. layers
4. motion
5. developer overrides

Backwards compatibility:

- `motion.enabled` in `layers=` is treated as `motion=on` alias
- unknown layer tokens are ignored and surfaced in diagnostics

Canonical query ordering:

1. `layers`
2. `layerProfile`
3. `motion`
4. `debug`
5. `viewport`
6. remaining keys (alphabetical)

## Studio UI

Main workspace sections:

- scene list (search, tags, sorting, keyboard navigation)
- scene preview (iframe + side-by-side compare)
- inspector/editor (route/profile/layers/motion/viewport/tags/notes)
- diagnostics panel (requested vs resolved vs DOM-applied state)
- help panel

Hotkeys:

- `/` focus search
- `n` new scene
- `Ctrl/Cmd+S` save scene
- `c` copy canonical URL
- `r` run visual test

## Diagnostics Bridge

Bridge protocol types:

- `apps/keystone/lib/scene-studio/scene-bridge.ts`

Pitch runtime bridge:

- `apps/keystone/components/pitch/debug/pitch-scene-runtime-bridge.tsx`

Features:

- secure postMessage origin checks
- diagnostics payload with resolved flags/source/profile/unknown tokens
- DOM `data-layer-*` snapshot and missing attribute detection
- scene-ready marker forwarding

## Scene Ready Signal

Pitch runtime sets:

- `document.documentElement[data-scene-ready="1"]`

After:

- font readiness
- transition/animation stabilization loop
- final double `requestAnimationFrame`

Playwright waits for this marker before screenshots.

## Deterministic Visual Runs

Visual helpers:

- `apps/keystone/visual-tests/helpers/deterministic.ts`

Determinism controls:

- fixed viewport presets
- reduced motion forced
- animations/transitions disabled by injected CSS
- stable light color scheme/locale/timezone
- deterministic `Date.now`, `Math.random`, and `performance.now`
- explicit wait for `data-scene-ready="1"`

## Scene Manifest

Manifest file:

- `docs/visual-scenes/SCENES.json`

Scenes must include:

- `route`
- `query`
- `viewport`

Optional:

- `title`
- `tags`
- `notes`
- custom viewport dimensions

## CLI Commands

From repo root:

```powershell
pnpm run keystone:scene:studio
pnpm run keystone:scene:visual:smoke
pnpm run keystone:scene:visual
pnpm run keystone:scene:visual:update
pnpm run keystone:scene:report
pnpm run keystone:scene:proof:gate -- --claim-id=<RUN_ID>
```

## Artifacts

Root:

- `artifacts/keystone-scene-studio/`

Per scene run:

- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/before.png`
- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/after.png`
- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/diff.png`
- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/report.md`
- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/report.json`
- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/console.log`
- `artifacts/keystone-scene-studio/scenes/<sceneId>/<runId>/network.log`

Index:

- `artifacts/keystone-scene-studio/index.md`
- `artifacts/keystone-scene-studio/index.html`

## Improvement Claim Workflow

Claim files:

- `docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md`

Required proof:

- claim file exists
- scene artifacts exist for same `RUN_ID`
- diff + report files exist per claimed scene

Gate script:

- `pnpm run keystone:scene:proof:gate -- --claim-id=<RUN_ID>`

## Troubleshooting

If preview diagnostics fail:

1. confirm Scene Studio URL includes `debug=1`.
2. confirm preview and studio origins match.
3. confirm `data-scene-ready="1"` appears on `html`.
4. verify pitch runtime bridge is mounted.

If visual runs are flaky:

1. verify Chromium installed: `pnpm --filter @hitech/keystone exec playwright install chromium`
2. use smoke run first
3. confirm no non-deterministic data sources on scene route

## Acceptance Checklist

- [ ] `/dev/scene-studio?debug=1` renders in development.
- [ ] `/dev/scene-studio` returns `404` in production.
- [ ] Scene create/edit/save/export/import works.
- [ ] Copy canonical URL reproduces state in a fresh tab.
- [ ] Diagnostics return resolved/source/profile/unknown + DOM snapshot.
- [ ] `data-scene-ready="1"` is present before screenshot capture.
- [ ] Visual smoke/full runs produce before/after/diff/report artifacts.
- [ ] `index.md` / `index.html` summarize latest outputs.
- [ ] Proof gate enforces claim-to-artifact linkage.
