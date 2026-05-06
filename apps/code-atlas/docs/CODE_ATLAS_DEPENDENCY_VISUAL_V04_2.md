# Code Atlas Dependency Visual V04.2

Black Glass Atlas edition for Code Atlas dependency visualization.

## What it does

- Reads an existing Code Atlas dependency graph JSON and optional summary JSON.
- Renders one standalone offline HTML artifact.
- Provides an elegant dark visual with restrained gold light accents.
- Preserves the existing consumer/analyzer pipeline. It does not scan projects.
- Supports runtime focus, hide tooling, hide stdlib, hide externals, unresolved-only, neighborhood focus, and filtered JSON export.

## Installed files

- `apps/code-atlas/tools/code_atlas_dependency_visual_v04_2.py`
- `apps/code-atlas/docs/CODE_ATLAS_DEPENDENCY_VISUAL_V04_2.md`

## Main render command

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_visual_v04_2.py" render --graph-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_graph.json" --summary-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_summary.json" --output-dir "F:\descargasf" --title "Terminal de Venta Black Glass Atlas"
```

## Verify command

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_visual_v04_2.py" verify --graph-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_graph.json" --summary-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_summary.json" --max-unresolved 3 --forbid-source-prefix tools/prisma-salvage --expect-graph-version 3.1.0
```

## Notes

- This package does not modify Capatch core.
- This package does not modify `code-atlas.py`.
- This package performs no hidden writes beyond its explicit output HTML and installer backup state.
