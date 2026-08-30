# tools/prisma-governance

## Canonical runner

Use `authority_mesh_run.py` for human, CI and agent preflights:

```powershell
python tools/prisma-governance/authority_mesh_run.py --task "describe the requested PRISMA change" --output .governance/current
```

For a full cross-surface visual/authority scan:

```powershell
python tools/prisma-governance/authority_mesh_run.py --task "GLOBAL ALL APPS ALL SURFACES AUTHORITY PREFLIGHT" --full --output .governance/current
```

The runner guarantees:

- the governance output directory is cleaned before generation;
- stale `.governance/current` artifacts cannot be mistaken for current evidence;
- visual/full runs snapshot the tracked canonical Layer Map as `LAYERS_MAP.json` and `LAYERS_MAP.md`;
- `LAYERS_MAP_SOURCE.json` records source paths, SHA-256, task and source commit;
- required Mesh outputs are verified before PASS is returned.

`authority_mesh.py` remains the low-level GovMesh3 analysis engine. It is intentionally retained for compatibility and self-tests, but it does **not** provide the clean-output + Layer Map guarantees by itself and is not the canonical operational entrypoint.

`--keep-output` on the canonical runner is debug-only and must not be used for governed task evidence.
