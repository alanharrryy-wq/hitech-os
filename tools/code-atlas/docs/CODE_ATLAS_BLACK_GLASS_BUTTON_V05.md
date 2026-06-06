# Code Atlas Black Glass Button V05

Adds a real **Black Glass Atlas** button to the Code Atlas PySide selector.

## What the button does

When clicked, the selector returns `output_mode="black_glass"`. The main pipeline then:

1. Resolves the selected folder or file to a project root.
2. Runs `apps/code-atlas/tools/code_atlas_dependency_consumer_v03.py analyze`.
3. Uses the generated graph and summary JSON under `F:\descargasf`.
4. Runs `apps/code-atlas/tools/code_atlas_dependency_visual_v04_2.py render`.
5. Opens the generated standalone Black Glass HTML.

## Boundaries

- Does not modify Capatch core.
- Does not add a visual theme to module 09.
- Does not alter the old Python SVG graph behavior.
- Does not hardcode Terminal de Venta into Code Atlas.
- Writes generated reports/HTML under `F:\descargasf`.

## Required existing tools

- `apps/code-atlas/tools/code_atlas_dependency_consumer_v03.py`
- `apps/code-atlas/tools/code_atlas_dependency_visual_v04_2.py`

If either tool is missing, the button shows a clear runtime error.
