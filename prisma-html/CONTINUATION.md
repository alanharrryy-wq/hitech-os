# PRISMA HTML · Continuation

## Current status

`VISCORE1_CANONICAL_AUTHORITY_CONSOLIDATION`

The old `SOURCE_READY_CANONICAL_MIGRATION_AND_PAGES_READINESS` state is retained as historical provenance only. Current visual work must start from VISCORE, Identity Dictionary and RIFAT/prisma-ui authority.

## Current operating model

1. `authority/rifat/identity` is the single editable visual-meaning authority.
2. `authority/rifat/prisma-ui` owns exact surface/route/owner/region/slot/layer location truth.
3. `authority/rifat/visual-source-manifest.json` owns deterministic product projection declarations.
4. `extras/atlasfin` is the canonical human cockpit.
5. `tools/visual_core.py` computes readiness and blockers without claiming fake READY.

## Resume commands

```powershell
python tools/visual_core.py status
python tools/visual_core.py check
python tools/visual_core.py ready tablet
```

For a visual/runtime mutation, generate a fresh task-scoped Authority Mesh with the canonical runner first:

```powershell
python ..\apps\terminal-de-venta-system\tools\prisma-governance\authority_mesh_run.py --task "<exact task>" --full --output .governance/current
```

Use the repo root/working directory appropriate for the command. The runner cleans stale governance output and snapshots the canonical Layer Map with provenance.

## Certification boundary

Source-ready, compiled, projected and functional-smoke states are not runtime visual certification. `READY` requires explicit runtime/browser visual evidence plus the governed rollback/evidence chain.

## Historical material

Cloudflare migration, old baseline packages and previous Atlas completion batches remain evidence/history. They no longer define current visual authority.
