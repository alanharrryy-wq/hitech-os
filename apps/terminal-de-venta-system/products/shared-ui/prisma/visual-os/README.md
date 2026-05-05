
# PRISMA Visual OS

Carpeta dueña del control plane visual compartido.

## Archivos

- `prisma-visual-os.controls.json`: perillas maestras.
- `prisma-visual-os.presets.json`: presets oficiales.
- `prisma-visual-os.recipes.json`: recetas por familia de componente.
- `prisma-visual-os.scorecard.json`: criterios de aprobación visual-operativa.
- `prisma-visual-os.tokens.css`: bridge CSS no invasivo.

## Regla

Este directorio define el contrato visual. Las superficies concretas (`products/tablet`, `products/pc`, `products/mobile`) deben adoptar el contrato por paquetes separados para evitar cambios silenciosos.
