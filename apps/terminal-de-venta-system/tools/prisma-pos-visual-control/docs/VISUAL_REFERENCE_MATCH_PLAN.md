# VISUAL_REFERENCE_MATCH_PLAN

## Objetivo

Preparar el paquete 2 `PRISMA_POS_VISUAL_REFERENCE_MATCH_260503_v01` usando las palancas instaladas aquí.

## Orden recomendado

1. Correr coverage actual.
2. Correr audit computed si `/pos` está arriba.
3. Aplicar preset `reference_match` sobre tokens, no sobre selectores inventados.
4. Convertir hardcodes visuales clave de `pos.module.css` a variables.
5. Priorizar: fondo -> ticket -> CTA -> product stage -> cards -> controles secundarios.
6. Repetir coverage/audit.
7. Capturar screenshot real antes/después.

## Stop condition

No tocar rutas demo ni `prisma-dark-pos-reference` como runtime. Esa referencia es brújula visual, no muleta de producción.
