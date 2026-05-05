# Dependency Map Clean Scan V02.2

This patch upgrades the dependency-map analyzer to v1.2.0.

## What changed

- Keeps the V02/V02.1 clean scan exclusions.
- Fixes dotted virtual module resolution such as:
  - `module.manifest` -> `module.manifest.ts`
  - `repository.prisma` -> `repository.prisma.ts`
  - `product-queries.prisma` -> `product-queries.prisma.ts`
- Adds safer candidate probing for `.d.ts`, `.css`, `.json`, `.mts`, and `.cts` targets.
- Keeps Capatch generic. It does not hardcode Code Atlas or Terminal-only logic.

## Recommended Terminal de Venta run

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\dependency_map\analyze_project.py" --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --format json --output "F:\descargasf\terminal_dependency_map_clean_v02_2.json" --max-files 5000 --exclude-dir prisma-salvage
```

Use `--exclude-dir prisma-salvage` for Terminal de Venta because that folder is a project salvage archive, not live runtime source.
