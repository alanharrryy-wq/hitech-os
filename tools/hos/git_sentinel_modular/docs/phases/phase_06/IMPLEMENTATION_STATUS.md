# Phase 6 implementation status

## Objetivo cumplido en esta entrega
- Se agregó una base real de core + app integration sin hacer cutover destructivo.
- Orchestrator quedó como columna vertebral de ejecución única.
- CLI y dashboard modular quedaron encima de contratos estables.
- Legacy adapters quedaron como puente reversible para consumo gradual.

## Archivos principales
- `core/orchestrator.py`
- `app/cli.py`
- `app/dashboard.py`
- `legacy/adapters.py`

## Propósito de diseño
- Wiring explícito
- Entrada por CLI reproducible
- Dashboard como proyección de datos, no motor de negocio
- Compatibilidad legacy reversible
- Tests unitarios e integración para detectar wiring roto rápido

## Qué sigue después
- Fase 7: instalador/validador final y comprobación de ensamblado
- Preparar cutover parcial cuando el import graph y smoke tests estén estables
