# Live Scene Composer End-to-End Mutation UI Wiring Pack v1

Generated: 2026-03-18T01:29:30.972561Z

## What this pack is

This pack stacks on top of the mutation integration hardening wave and pushes the next real seam:

**canvas / structure tree / inspector / toolbar / hotkeys -> typed mutation intent -> preview / commit / discard -> runtime-mutation-bridge**

The goal is not to bypass existing mutation governance. The goal is to make the UI surfaces speak the same typed mutation language while preserving preview and commit as separate semantics.

## What is included

- inherited `mutation-client` and `mutation-integration` seams from the prior validated pack
- new `source/end-to-end-ui-wiring/` seam with surface contracts and routing helpers
- new docs `90` to `105` for UI wiring, compare/apply bar, state machine, and failure atlas
- new fixtures, traces, telemetry, matrices, and review artifacts
- new installer, runner, verifier, and smoke checks
- a package-local `tsconfig.package.json` so contributors can typecheck the staged bundle

## Primary operator outcome

After installation, the repo gets:

- a staged tools bundle under `tools/live-scene-composer/end-to-end-mutation-ui-wiring-v2-fixed`
- updated docs under `docs/live-scene-composer`
- optional mirror into a detected composer source root when `-AllowInferredPaths` or `-InstallIntoComposerSrc` is used
- verification and smoke evidence written to `F:\OneDrive\Descargas`

## Recommended order

1. run the `run_..._from_zip.ps1` wrapper
2. inspect `install_summary.txt`
3. inspect `verification_report.txt`
4. inspect `smoke_report.txt`
5. only then stack the next wave on top
