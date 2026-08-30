# PRISMA HTML · Visual Authority + Atlasfin

`prisma-html` is PRISMA's governed visual-authority workspace. It is not only a static site and it is not a second copy of the product apps.

## Current model

PRISMA uses one editable visual authority and multiple deterministic projections:

`neutral meaning -> identity profile -> surface adapter -> certified binding -> compiled projection -> governed runtime -> visual evidence -> READY`

The canonical roles are:

- **Identity Dictionary**: `authority/rifat/identity/` owns neutral visual meaning, profiles, semantic tokens, recipes, assets and surface adapters.
- **RIFAT / prisma-ui**: `authority/rifat/prisma-ui/` owns surface, route, owner, region, editable-slot and layer location truth.
- **Projection manifest**: `authority/rifat/visual-source-manifest.json` declares deterministic source-to-product projections and forbids manual edits to generated outputs.
- **Atlasfin**: `extras/atlasfin/index.html` is the canonical human visual-control cockpit. It is a consumer/operator of authority, not a competing authority.
- **Product apps**: Tablet, PC, Mobile, Web, Chart Lab and Control Center consume governed projections. A runtime file does not become visual authority merely because it renders.

The detailed contract lives in `authority/rifat/identity/contract/PRISMA_VISUAL_CORE_CONTRACT.md`.

## Operator documentation

Start with `docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md` for the complete operating flow: Authority Mesh preflight, what is editable, projection/reconciliation rules, validator semantics, deterministic `FILES_MANIFEST.json`, no-fake-green boundaries, CI certification, troubleshooting and safe PR closure.

`docs/ops/README.md` indexes all operator-facing documentation.

Important operating rule: if RIFAT and a product runtime disagree, do not overwrite the runtime merely to make validation green. Inspect current authority and Git history first, reconcile without downgrade, validate exact-byte-copy state, then refresh manifest hashes and `FILES_MANIFEST.json` mechanically.

## Open the visual system

- Canonical cockpit: `extras/atlasfin/index.html`
- Identity source authority: `authority/rifat/identity/`
- Reference catalog: `sistema-ui/catalogo/index.html`
- Legacy compatibility workbench: `sistema-ui/identidad/index.html`

Atlasfin currently contains **27 public pages, 26 A–Z sections and 418 catalogued elements**. Current structural truth comes from its manifest and validators, not from historical prose.

## One-command status

From `prisma-html/`:

```powershell
python tools/visual_core.py status
python tools/visual_core.py check
python tools/visual_core.py ready tablet
python tools/visual_core.py write --atlas-export
```

Equivalent package scripts:

```powershell
npm run visual:status
npm run visual:check
npm run visual:write
```

`ready <surface>` is fail-closed. It returns blockers unless the entire governed readiness chain is proven. Compiled/source-ready is not runtime visual certification. A `ready` command that exits `2` is a truthful blocked state, not a failed architecture check to be bypassed.

## Identity commands

```powershell
python tools/identity_dictionary.py status
python tools/identity_dictionary.py list
python tools/compile_identity_dictionary.py --check
python tools/validate_identity_dictionary.py
python tools/identity_binding_resolver.py coverage
```

Profile activation changes authority only. It does not directly mutate product runtime.

## Validation

```powershell
python tools/visual_core.py check
python tools/validate_rifat_authority.py
python tools/validate_identity_dictionary.py
python tools/compile_identity_dictionary.py --check
python extras/atlasfin/generator/validate_atlas.py extras/atlasfin
python tools/validate_project.py --root . --report reports/source-validator-current.json
python tools/refresh_files_manifest.py --check
```

A functional or static PASS is not a visual PASS. Runtime/browser visual evidence remains a separate gate.

## Governed change order

For authority or runtime visual work, use this order:

1. Generate a fresh task-scoped Authority Mesh with Layer Map.
2. Review the readset, app-impact matrix, contract/gate matrix and unmapped-risk report.
3. Change only the authorized authority layer.
4. Validate Identity/RIFAT/Atlasfin as applicable.
5. Reconcile deterministic product projections without downgrading legitimate newer runtime changes.
6. Refresh `FILES_MANIFEST.json` only after all `prisma-html` edits are final.
7. Run certification on one exact PR head SHA.
8. If `main` moved, reconcile it and certify a new head SHA.
9. Once the final SHA is green, do not add another cosmetic closing commit before merge.

The detailed commands and failure cases are in `docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md`.

## Duplication rule

The goal is **not zero copies**. The goal is **zero competing editable copies**.

Allowed:

- deterministic generated projections;
- evidence snapshots;
- public/reference views derived from authority;
- compatibility exports with provenance.

Forbidden:

- two editable registries for the same visual meaning;
- hand-maintained counters that contradict route/manifest authority;
- manual edits to generated product projections;
- Atlasfin, catalog pages or README prose overriding machine-readable authority;
- `!important` priority overrides in governed visual authority.

## Public/narrative pages

- Main narrative: `index.html`
- Page 1: `paginas/pagina-1-prisma/index.html`
- Page 2: `paginas/pagina-2-inversionistas/index.html`
- Page 3: `paginas/pagina-3-por-que-prisma/index.html`
- Page 4: `paginas/pagina-4-ecosistema-producto/index.html`
- UI reference catalog: `sistema-ui/catalogo/index.html`
- Visual cockpit: `extras/atlasfin/index.html`

Cloudflare Pages tooling remains under `tools/cloudflare/`. Deployment, DNS and cloud publication are separate gates and are not implied by visual-source readiness.

## Historical migration material

`BASELINE-MANIFEST.json`, `SOURCE-INTEGRITY.json`, old completion batches and Cloudflare migration notes preserve provenance/history. They are not allowed to override the current authority registry, Identity Dictionary, RIFAT/prisma-ui, projection manifest or VISCORE status.

## Deterministic repository inventory

`TREE.md` is intentionally conceptual. The exhaustive file inventory is `FILES_MANIFEST.json` and must be generated/checked mechanically:

```powershell
python tools/refresh_files_manifest.py --write
python tools/refresh_files_manifest.py --check
```

Do not maintain an exhaustive tree or file hashes by hand. Generate `FILES_MANIFEST.json` after all other `prisma-html` changes are complete, because any later documentation or authority edit makes it stale again.
