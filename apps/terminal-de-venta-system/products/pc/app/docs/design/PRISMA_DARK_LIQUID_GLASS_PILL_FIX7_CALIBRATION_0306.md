# PRISMA Dark Liquid Glass Pill · Fix7 Calibration 0306

Estado: implementación de la última calibración aprobada para **pills dark liquid glass**.

## Objetivo

Ajustar la pill actual sin cambiar arquitectura: menos tinte oscuro, borde reactivo más brillante, orillas ópticas más notorias, pills más largas y sheen/glint premium en reposo.

## Cambios de calibración

| Área | Antes | Fix7 |
|---|---:|---:|
| Blur base | `0.06px` | se mantiene casi cero |
| Root dark fill | `rgba(4, 6, 14, .42)` | `rgba(4, 6, 14, .34)` |
| Refraction overlay | `rgba(3,6,14,.105)` | `rgba(3,6,14,.070)` |
| Volume frame overlay | `rgba(0,0,0,.18)` | `rgba(0,0,0,.125)` |
| Volume frame opacity | `.78` | `.62` |
| Edge brightness | `1.34` | `1.74` |
| Edge saturation | `2.05` | `2.36` |
| Edge opacity | `.82` | `.98` |
| Specular opacity | `.64` | `.78` |
| Regular min-width | `46px` | `136px` |
| Spacious min-width | `46px` | `152px` |
| Status pill width | `184px` | `208px` |
| Surface sheen | sólo Thinking | default suave + Thinking más fuerte |

## Contrato visual

1. No subir blur. El efecto premium debe venir de borde, refracción local y volumen.
2. La pill no debe agarrar azul global de la nada.
3. La orilla debe verse aproximadamente 30% más presente.
4. El centro debe seguir oscuro, pero menos ahogado.
5. La longitud mínima debe dejar respirar el centro.
6. El sweep/glint debe existir incluso en reposo, pero suave; Thinking conserva versión más visible.

## Archivos modificados

- `products/pc/app/components/prisma-glass-capsule/prisma-glass-capsule.module.css`
- `products/pc/app/app/referencia-visual/liquid-glass-capsules/page.tsx`
- `products/pc/app/referencia-visual/liquid-glass-capsules/page.tsx`
- `products/pc/app/tools/verify_prisma_glasscaps_dark_fix7_calibration_0306.mjs`

## Nota para surfaces/panels

Esta calibración es sólo para pills. Para panels/cards/frames/containers, reutilizar tokens conceptuales:
- tint reducido
- borde reactivo
- volumen de marco
- sheen premium
- centro calmado

Pero no copiar literalmente el lóbulo ni el ritmo de sheen de pill.
