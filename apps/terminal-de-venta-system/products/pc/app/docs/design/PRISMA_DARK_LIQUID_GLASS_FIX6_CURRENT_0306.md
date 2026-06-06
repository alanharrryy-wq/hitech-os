# PRISMA Dark Liquid Glass Fix6 Current 0306

Este paquete parte del código fresco `glassfresh 0306 0452.zip`, no del fix5 fix1 anterior.

## Contrato visual

- Tema oscuro solamente.
- Texto de fondo fijo, detrás de las pills.
- Figuras geométricas pequeñas, sólidas, con más colores.
- Figuras agrupadas en pares cercanos con `--pair-gap: .72cm`.
- Separación entre pares con `--pair-space: 5cm`.
- Seis pills en una fila horizontal.
- Blur casi cero: `--pgc-blur: 0.06px`; lóbulo localizado `blur(.08px)`.
- Sin tinte azul global permanente en `thinking`.
- Tres marcos reales: `edgeFrame`, `volumeFrame`, `innerFrame`.
- Fondo visible: `.motionBackplate { position: fixed; z-index: 0; }` y contenido sobre `z-index: 2+`.

## Regla óptica

La pill no debe inventar color ambiental. El color tiene que percibirse por proximidad real con figuras/texto detrás: borde exterior saturado, lóbulo izquierdo más expresivo, centro oscuro neutral.
