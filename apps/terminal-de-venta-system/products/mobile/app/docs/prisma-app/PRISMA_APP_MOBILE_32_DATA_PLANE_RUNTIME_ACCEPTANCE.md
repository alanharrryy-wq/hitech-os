# PRISMA App Mobile i02 - Data-plane y readiness

## Objetivo

Cerrar i02 para que Mobile/Pulso supervise fuentes reales de forma honesta: PC + Tablet, solo Tablet, solo PC, cache local, offline, stale y error. Mobile no cobra y no reemplaza Tablet ni PC.

## Cambios

- Agrega matriz QA de estados de fuente.
- Agrega verifier `verify_prisma_app_mobile_32_source_states.mjs`.
- Agrega script `verify:source-states`.
- Inserta `verify:source-states` en `check:all`.
- Expone atributos UI: `data-prisma-readiness`, `data-prisma-source`, `data-prisma-stale`.

## READY

READY solo si se instala en `products/mobile/app/**`, pasan checksums, verifier 32, gates disponibles y smoke HTTP o queda caveat explícito por entorno.
