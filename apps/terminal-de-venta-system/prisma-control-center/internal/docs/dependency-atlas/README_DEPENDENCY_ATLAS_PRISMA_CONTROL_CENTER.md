# PRISMA Control Center Dependency Atlas Bundle

Bundle: `PRISMA_CONTROL_CENTER_DEPENDENCY_ATLAS_BUNDLE_20260521`
Target root: `F:\repos\hitech-os\apps\terminal-de-venta-system`
Module: `prisma-control-center`

## What this installs

This bundle installs the dependency atlas artifacts generated for `prisma-control-center` into:

```text
prisma-control-center/internal/docs/dependency-atlas/
```

It also creates:

```text
prisma-control-center/04_ABRIR_ATLAS_DEPENDENCIAS.cmd
prisma-control-center/internal/wrappers/open_dependency_atlas.ps1
prisma-control-center/internal/py/verify_dependency_atlas_bundle_01.py
```

## Why this exists

The provided atlas reports:

```text
files_scanned: 101
source_files: 25
edges: 163
internal_edges: 45
external_edges: 118
unresolved_edges: 0
languages: JavaScript (8), Python (17)
```

That means this patch is not a runtime surgery. It is a controlled documentation/evidence install: the atlas becomes part of the operator toolkit and can be opened directly from the project.

## How to use after applying

From Windows:

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center
.\04_ABRIR_ATLAS_DEPENDENCIAS.cmd
```

Or directly:

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\internal\wrappers\open_dependency_atlas.ps1
```

To verify:

```powershell
python .\internal\py\verify_dependency_atlas_bundle_01.py --root F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center
```

## Safety

- Does not touch DBs.
- Does not start or stop services.
- Does not weaken Control Center CSP.
- Opens the visual atlas as a local file.
- Designed for idempotent re-application through `APPLY_BUNDLE.ps1`.
