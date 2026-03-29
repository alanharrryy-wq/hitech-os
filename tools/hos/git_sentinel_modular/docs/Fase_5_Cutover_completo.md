# Fase 5 — Cutover completo

## Meta
Convertir `git_sentinel_modular` en el motor operativo principal de Git Sentinel, dejando el legacy como compatibilidad/fallback.

## Objetivo operativo
Cerrar la transición de forma segura, reversible y observable, sin reintroducir acoplamiento ni deuda estructural.

## Incluye
- Modular como camino principal por default.
- Legacy preservado como fallback controlado.
- Estabilización de adapters de compatibilidad.
- Revisión final de observabilidad, defaults, rollout y rollback.
- Confirmación de que los boundaries no se degradaron durante el cutover.
- Cierre de deuda operativa crítica restante.

## Riesgos que busca eliminar
- Dependencia crónica del legacy.
- Cutover final incompleto o sin fallback real.
- Regresiones estructurales por presión de entrega.
- Operación híbrida indefinida que encarece mantenimiento.

## Entregables
- Propuesta de activación final del modular como default.
- Plan de fallback del legacy ya reducido a compatibilidad.
- Lista de criterios de estabilidad post-cutover.
- Checklist final de operabilidad y mantenibilidad.
- Declaración de cierre de transición modular.

## Criterio de salida
La fase termina cuando el modular es la ruta principal, el legacy queda como respaldo controlado y la operación puede continuar sin depender del paquete anterior para el flujo normal.
