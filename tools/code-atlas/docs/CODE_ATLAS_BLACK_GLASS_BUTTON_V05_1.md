# Code Atlas Black Glass Button V05.1

Fix release for the Black Glass Atlas button integration.

## What V05.1 fixes

V05 routed the selected path directly into the dependency consumer. If the user selected a subfolder such as:

```text
apps/terminal-de-venta-system/tools/prisma-visual-os
```

then the consumer searched for:

```text
apps/terminal-de-venta-system/tools/prisma-visual-os/tools/dependency_map/analyze_project.py
```

That is wrong. The analyzer is installed at the real project root:

```text
apps/terminal-de-venta-system/tools/dependency_map/analyze_project.py
```

V05.1 adds project-root discovery for Black Glass only. It walks upward from the selected path and uses the nearest ancestor containing:

```text
tools/dependency_map/analyze_project.py
```

## Scope

- Patches `apps/code-atlas/code-atlas.py` only inside the Black Glass bridge.
- Installs this note under `apps/code-atlas/docs/`.
- Does not modify Capatch core.
- Does not modify dependency-map.
- Does not modify the V03 consumer or V04.2 visual tool.

## Expected result

Selecting any subfolder inside Terminal de Venta should still resolve to:

```text
F:\repos\hitech-os\apps\terminal-de-venta-system
```

and then generate the Black Glass Atlas HTML under:

```text
F:\descargasf
```
