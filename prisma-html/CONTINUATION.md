# PRISMA HTML · Continuation

## Current status

`VISCORE1_CANONICAL_AUTHORITY_CONSOLIDATION_MERGED`

PR #475 completed the VISCORE1 source/governance consolidation on 2026-08-30. The old `SOURCE_READY_CANONICAL_MIGRATION_AND_PAGES_READINESS` state is retained as historical provenance only. Current visual work must start from VISCORE, Identity Dictionary and RIFAT/prisma-ui authority.

The merge proves the source/governance architecture and certification gates are installed. It does **not** auto-promote every surface to runtime visual `READY`; runtime/browser evidence remains a separate fail-closed boundary.

## Current operating model

1. `authority/rifat/identity` is the single editable visual-meaning authority.
2. `authority/rifat/prisma-ui` owns exact surface/route/owner/region/slot/layer location truth.
3. `authority/rifat/visual-source-manifest.json` owns deterministic product projection declarations.
4. `extras/atlasfin` is the canonical human cockpit.
5. `tools/visual_core.py` computes readiness and blockers without claiming fake READY.
6. `FILES_MANIFEST.json` is deterministic generated inventory and must not be hand-maintained.

## Operator handoff

The complete operating guide is:

`docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md`

Use it for:

- Authority Mesh preflight and required readset;
- safe edit boundaries;
- Identity/RIFAT/Atlasfin validation;
- deterministic product projection rules;
- no-downgrade reconciliation when runtime and RIFAT differ;
- stale hash versus exact-copy drift diagnosis;
- `FILES_MANIFEST.json` regeneration;
- CI certification and exact-SHA PR closure.

## Resume commands

From `prisma-html/`:

```powershell
python tools/visual_core.py status
python tools/visual_core.py check
python tools/visual_core.py ready tablet
python tools/refresh_files_manifest.py --check
```

For a visual/runtime mutation, or an authority/governance change that changes operating truth, generate a fresh task-scoped Authority Mesh with the canonical runner first:

```powershell
python ..\apps\terminal-de-venta-system\tools\prisma-governance\authority_mesh_run.py --task "<exact task>" --full --output ..\apps\terminal-de-venta-system\.governance\current
```

From `apps/terminal-de-venta-system/` the equivalent is:

```powershell
python tools/prisma-governance/authority_mesh_run.py --task "<exact task>" --full --output .governance/current
```

The runner cleans stale governance output and snapshots the canonical Layer Map with provenance.

## Projection reconciliation rule

If `validate_rifat_authority.py` reports source/output hash mismatches, do not automatically overwrite product runtime.

- If `exact-copy visual projection drift` is also present, source and output bytes differ. Inspect Git history and current authority, then reconcile without downgrading a legitimate newer runtime.
- If hash mismatches exist **without** exact-copy drift, source and output bytes already match; only manifest digests are stale. Refresh the declared hashes from actual bytes.

After all `prisma-html` changes are final:

```powershell
python tools/validate_rifat_authority.py
python tools/refresh_files_manifest.py --write
python tools/refresh_files_manifest.py --check
```

## Certification boundary

Source-ready, compiled, projected and functional-smoke states are not runtime visual certification. `READY` requires explicit runtime/browser visual evidence plus the governed rollback/evidence chain.

For final PR closure, certify one exact head SHA. If `main` moves, reconcile and certify a new SHA. Do not add a cosmetic closing commit after the final green certification unless you intend to rerun the gates.

## Historical material

Cloudflare migration, old baseline packages and previous Atlas completion batches remain evidence/history. They no longer define current visual authority.
