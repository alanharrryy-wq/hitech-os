# Fase 1 — Hardening estructural

## Meta
Blindar el scaffold `tools/hos/git_sentinel_modular` para que deje de depender de wiring frágil, imports permisivos o defaults ambiguos.

## Objetivo operativo
Dejar el modular listo para endurecimiento real sin tocar todavía el package legacy vivo.

## Incluye
- Auditoría y endurecimiento de boundaries entre capas.
- Revisión de imports permitidos vs imports frágiles.
- Definición de contratos mínimos entre `shared`, dominios, `core`, `app` y `legacy/adapters`.
- Limpieza de artefactos temporales, backups y residuos dentro del scaffold.
- Revisión de wiring implícito o dependiente de bootstrap, cwd o side effects.
- Identificación de gaps de tests en paths negativos.

## Riesgos que busca eliminar
- Acoplamiento disfrazado de modularidad.
- Imports laterales no controlados.
- Dependencia accidental de bootstrap o layout actual.
- Basura operativa que puede contaminar CI, packaging o lectura del repo.

## Entregables
- Mapa de boundaries permitidos/prohibidos.
- Lista de imports frágiles y puntos de wiring delicados.
- Inventario de artefactos temporales a purgar o reubicar.
- Lista priorizada de debt útil post-modularización.
- Set inicial de pruebas de hardening pendientes.

## Criterio de salida
La fase termina cuando el scaffold modular tiene límites claros, wiring entendible y un baseline de deuda/riesgo suficientemente aterrizado para pasar a guardrails operativos.
