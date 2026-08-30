# PRISMA HTML · Authority tree

This file intentionally documents the **stable authority topology**, not an exhaustive file inventory. Exhaustive hand-maintained trees become stale and must not be used as source truth.

```text
prisma-html/
├── authority/
│   └── rifat/
│       ├── identity/                 # ONE editable visual meaning authority
│       │   ├── activation/
│       │   ├── adapters/
│       │   ├── bindings/
│       │   ├── compiled/current/     # generated authority projections
│       │   ├── contract/
│       │   ├── profiles/
│       │   ├── recipes/
│       │   └── registries/
│       ├── prisma-ui/                # route/owner/region/slot/layer binding authority
│       └── visual-source-manifest.json
├── extras/
│   └── atlasfin/                     # canonical human visual cockpit
│       ├── assets/data/
│       ├── assets/js/
│       ├── generator/
│       ├── governance/
│       ├── schemas/
│       └── *.html                    # 27 materialized public pages
├── sistema-ui/
│   ├── catalogo/                     # reference/showcase view, not authority
│   ├── identidad/                    # legacy compatibility workbench, not authority
│   └── css/                          # prisma-html site presentation system
├── tools/
│   ├── visual_core.py                # canonical status/readiness orchestration
│   ├── refresh_files_manifest.py     # deterministic exhaustive file inventory
│   ├── identity_dictionary*.py
│   ├── identity_binding_resolver*.py
│   ├── compile_identity_dictionary.py
│   ├── validate_rifat_authority.py
│   └── ...
├── reports/
│   └── visual-core/                  # generated VISCORE status reports
├── paginas/                          # public narrative pages
├── docs/                             # runbooks, history and evidence
└── README.md                         # current human entrypoint
```

## Product projection side

The app/runtime copies live outside `prisma-html` under `apps/terminal-de-venta-system/`. Their governed relationship to this authority is declared by:

`authority/rifat/visual-source-manifest.json`

Generated product copies are allowed. Competing editable visual truths are not.

## Current inspection commands

```powershell
python tools/visual_core.py tree
python tools/visual_core.py status
python tools/visual_core.py check
python tools/refresh_files_manifest.py --check
```

For a real filesystem inventory, query `FILES_MANIFEST.json`, the filesystem or Code Atlas at runtime. Do not extend this file into another manually maintained 500-line snapshot.
