# PRISMA Liquid Glass Capsules 0206

Este paquete agrega un sistema real de cápsulas superiores tipo Liquid Glass para PRISMA PC UI:

- `PrismaGlassCapsule`
- `PrismaGlassTopDock`
- CSS Module con blur, saturación, borde especular, highlight, sombra interna, shimmer y fallback
- ruta demo/reference: `/referencia-visual/liquid-glass-capsules`
- verificador focalizado: `node tools/verify_prisma_glass_capsules_0206.mjs`

## Criterios de aceptación

También llamados criterios visuales mínimos para esta iteración.

PASS visual solo si:

- la cápsula se separa del layout,
- el contenido detrás se difumina,
- el borde no parece plano,
- el highlight superior se percibe como reflejo,
- el estado `thinking` tiene vida sin distraer,
- funciona sobre superficie clara y fondo atmosférico,
- tiene fallback si `backdrop-filter` no existe.

## Referencias técnicas

- Apple Liquid Glass: material translúcido que refleja y refracta el entorno.
- CSS `backdrop-filter`: efectos gráficos sobre el área detrás del elemento.
- `prefers-reduced-motion`: el shimmer debe apagarse si el usuario pide menos movimiento.
