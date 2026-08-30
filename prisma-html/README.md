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

`ready <surface>` is fail-closed. It returns blockers unless the entire governed readiness chain is proven. Compiled/source-ready is not runtime visual certification.

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
```

A functional or static PASS is not a visual PASS. Runtime/browser visual evidence remains a separate gate.

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

Do not maintain an exhaustive tree or file hashes by hand.
