# Code Atlas Dependency Visual V04

V04 adds an offline visual viewer for graph JSON produced by `code_atlas_dependency_consumer_v03.py`.

## Purpose

This is a consumer layer only. It does not scan a project, mutate Capatch, or change the main `code-atlas.py` UI. It renders a standalone HTML file that can be opened in a browser.

## Installed files

- `apps/code-atlas/tools/code_atlas_dependency_visual_v04.py`
- `apps/code-atlas/docs/CODE_ATLAS_DEPENDENCY_VISUAL_V04.md`

## Main render command

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_visual_v04.py" render --graph-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_graph.json" --summary-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_summary.json" --output-dir "F:\descargasf" --title "Terminal de Venta Dependency Map"
```

## Verification command

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_visual_v04.py" verify --graph-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_graph.json" --summary-json "F:\descargasf\code_atlas_dependency_consumer_v03_terminal-de-venta-system_260504_2150_summary.json" --max-unresolved 3 --forbid-source-prefix tools/prisma-salvage --expect-graph-version 3.1.0
```

## Exit codes

- `0`: success
- `2`: invalid input JSON/path
- `3`: verification failed
- `4`: output write failed

## Notes

The canvas preview intentionally limits visible nodes by degree and current filters so large monorepos do not freeze the browser. Full node and edge data remain embedded in the HTML model for filtering and detail panels.
