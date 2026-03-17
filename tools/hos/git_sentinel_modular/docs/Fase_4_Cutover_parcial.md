# Fase 4 — Cutover parcial

## Meta
Mover una capacidad real y de bajo blast radius al modular como primer ownership operativo.

## Objetivo operativo
Hacer la primera migración real sin exponer todavía superficies destructivas o de mayor riesgo.

## Incluye
- Selección de una superficie de bajo riesgo para migrar primero.
- Prioridad sugerida: `scanning`, `analysis` o `reporting`.
- Activación controlada por flag/entrada explícita.
- Fallback inmediato al camino legacy.
- Observación de estabilidad, equivalencia y comportamiento operativo.
- Cierre de gaps detectados en shadow mode antes de ampliar alcance.

## No incluye todavía
- Remediation destructiva.
- Scheduler como ownership primario.
- Reemplazo total del package legacy.

## Riesgos que busca eliminar
- Migración demasiado amplia demasiado pronto.
- Falta de reversibilidad.
- Dependencia del modular en caminos de alto riesgo antes de estar listo.

## Entregables
- Definición de la primera capacidad a cortar.
- Condiciones de habilitación/deshabilitación.
- Criterios de éxito del primer ownership parcial.
- Regla de fallback inmediato.
- Lista de issues observados durante el primer cutover real.

## Criterio de salida
La fase termina cuando una capacidad concreta y no destructiva ya puede correr desde el modular con rollback claro y sin tocar todavía el reemplazo completo del legacy.
