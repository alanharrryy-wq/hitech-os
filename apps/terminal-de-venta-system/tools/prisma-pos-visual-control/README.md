# PRISMA POS Visual Control Tools

Infraestructura para gobernar `/pos` de Tablet como tablero de palancas, no como CSS a machetazos, que aparentemente es deporte olímpico en proyectos frontend.

## Herramientas

```powershell
python tools/prisma-pos-visual-control/report_prisma_pos_visual_coverage.py --target-root F:\repos\hitech-os\apps\terminal-de-venta-system --output-dir F:\descargasf --json --markdown
python tools/prisma-pos-visual-control/audit_prisma_pos_computed_styles.py --url http://127.0.0.1:3120/pos --target-root F:\repos\hitech-os\apps\terminal-de-venta-system --output-dir F:\descargasf --json --markdown
```

## Alcance

Solo Tablet `/pos`. No toca PC, Mobile, backend, shared ni checkout contracts.
