# PRISMA Dark Liquid Glass Bench 0306

Estado: dark-only benchmark.

Objetivo:
- Mantener el componente PrismaGlassCapsule en tema oscuro.
- Probarlo sobre figuras geometricas de color solido y texto fijo.
- Hacer que las pills hagan scroll encima del fondo fijo para evaluar refraccion, borde optico, brillo especular y legibilidad.

Criterio optico:
- El shell/root no debe usar backdrop-filter.
- La zona central `.refraction` conserva el unico backdrop-filter controlado.
- Blur central: 1.5px, maximo permitido 3px.
- El fondo de benchmark es dark-only: `#05070d`.
- El foreground text de la pill debe quedar nitido y sobre todos los layers.
- El underGlow deja de ser una barra solida y se convierte en campo caustic local.

Validacion:
- `node tools/verify_prisma_glasscaps_dark_liquid_0306.mjs`
- `node tools/verify_prisma_glass_capsules_optical_bench_0206.mjs`
