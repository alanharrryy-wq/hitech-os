# Code Atlas dependency-map bridge

This bridge lets Code Atlas consume the reusable Capatch `dependency-map` capability without hardcoding Code Atlas-only behavior into Capatch core.

## Main command

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_map_bridge.py" --project-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --capatch-root "F:\repos\hitech-os\apps\code-atlas\capatch_system" --downloads-root "F:\descargasf" --install-if-missing --verify-first --format both
```

## What it does

1. Runs Capatch plugin health.
2. Runs `dependency-map` profile for the target project.
3. Installs the reusable analyzer only when missing and only through Capatch.
4. Runs `dependency-map` verify.
5. Runs the installed analyzer.
6. Writes raw dependency-map JSON/Markdown plus Code Atlas-friendly JSON/Markdown under `F:\descargasf`.

## Non-goals

- It does not modify Capatch core.
- It does not rewrite the existing Code Atlas Python graph engine.
- It does not run `pip install -e .`.
- It does not write reports into random folders.
