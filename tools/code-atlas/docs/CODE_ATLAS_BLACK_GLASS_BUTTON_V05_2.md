# Code Atlas Black Glass Button V05.2

Scope fix for the Black Glass Atlas button.

## What V05.2 fixes

V05.1 resolved the real project root before running the dependency consumer. That avoided the missing analyzer error, but it also forced a full project scan when the user selected a subfolder such as:

```text
apps/terminal-de-venta-system/tools
```

That was too broad. If the selected path is `tools`, the generated Black Glass Atlas should map `tools`, not the full `@hitech/terminal-de-venta-system` package.

V05.2 keeps two separate paths:

```text
project_root = nearest ancestor that contains tools/dependency_map/analyze_project.py
selected_scope = the exact folder/file scope selected in Code Atlas
```

It uses `project_root` only to find the analyzer, then runs that analyzer against `selected_scope`.

## Scope

- Patches only the Black Glass bridge inside `apps/code-atlas/code-atlas.py`.
- Installs this note under `apps/code-atlas/docs/`.
- Does not modify Capatch core.
- Does not modify dependency-map.
- Does not modify Code Atlas Consumer V03.
- Does not modify Visual V04.2.

## Expected behavior

Selecting:

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\tools
```

and clicking **Black Glass Atlas** should generate an HTML map for the `tools` scope.

Selecting:

```text
F:\repos\hitech-os\apps\terminal-de-venta-system
```

should generate an HTML map for the full project.
