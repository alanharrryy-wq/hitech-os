# Legacy Core Migration Report

- Generated at UTC: `2026-03-14T10:16:03+00:00`
- Repo root: `F:\repos\hitech-os`
- Mode: `WRITE`
- Result: **PASS**

## Summary

- Legacy path existed before: `True`
- Console-core existed before: `False`
- Files scanned: `186`
- Hits before: `15`
- Hits after: `0`
- Files rewritten: `10`
- Files moved: `11`
- Files removed as duplicate: `0`
- Legacy path exists after: `False`
- Guard return code: `0`

## Migration Scope Before

### runtime-debug-console
- `apps/keystone/components/dev-console/DevConsole.tsx` :: `./core/console-core-layout` -> `./console-core/console-core-layout`
- `apps/keystone/components/dev-console/DevConsole.tsx` :: `./core/console-core-lifecycle` -> `./console-core/console-core-lifecycle`
- `apps/keystone/components/dev-console/DevConsole.tsx` :: `./core/console-core-shell` -> `./console-core/console-core-shell`
- `apps/keystone/components/dev-console/DevConsoleContext.tsx` :: `./core/console-core-diagnostics` -> `./console-core/console-core-diagnostics`
- `apps/keystone/components/dev-console/DevConsoleContext.tsx` :: `./core/console-core-events` -> `./console-core/console-core-events`
- `apps/keystone/components/dev-console/DevConsoleRegistry.tsx` :: `./core/console-core-registry` -> `./console-core/console-core-registry`
- `apps/keystone/components/dev-console/DevConsoleRegistry.tsx` :: `./core/core-console-panels` -> `./console-core/core-console-panels`
- `apps/keystone/components/dev-console/index.ts` :: `./core` -> `./console-core`
- `apps/keystone/components/dev-console/domains/inspect/InspectEventMonitorPanel.tsx` :: `../../core/console-core-contracts` -> `../../console-core/console-core-contracts`
- `apps/keystone/components/dev-console/domains/inspect/InspectEventMonitorPanel.tsx` :: `../../core/console-core-events` -> `../../console-core/console-core-events`
### pitch-debug
- `apps/keystone/components/pitch/debug/pitch-dev-console-stability-helpers.tsx` :: `../../dev-console/core/console-core-events` -> `../../dev-console/console-core/console-core-events`
- `apps/keystone/components/pitch/debug/pitch-layer-dev-tools.tsx` :: `../../dev-console/core/console-core-runtime-invariants` -> `../../dev-console/console-core/console-core-runtime-invariants`
- `apps/keystone/components/pitch/debug/pitch-scene-look-runtime.tsx` :: `../../dev-console/core/console-core-events` -> `../../dev-console/console-core/console-core-events`
- `apps/keystone/components/pitch/debug/pitch-scene-runtime-bridge.tsx` :: `../../dev-console/core/console-core-events` -> `../../dev-console/console-core/console-core-events`
### tests
- `apps/keystone/tests/dev-console-platform-architecture.test.ts` :: `../components/dev-console/core/console-core-contracts` -> `../components/dev-console/console-core/console-core-contracts`

## Residual Hits After

- No residual legacy hits after migration.

## Notes

- This script only performs deterministic path migration from `core` to `console-core`.
- It does not invent missing modules or overwrite conflicting files.
- If conflicts remain, manual review is required before the guard can go green.

