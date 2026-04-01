# DeltaForge · Core Session Integrity

Este paquete documenta la base congelada para que DeltaForge evolucione sin contradicciones entre sesión, scope, eventos, UI e infraestructura.

## Objetivo del pase
Cerrar la **verdad por sesión** antes de integrar engine real o ampliar features.

## Qué debe quedar cierto
- La unidad del sistema es una **sesión sobre un scope**
- `SessionWorkspace` contiene la verdad operativa visible
- `dirty` y `stale` se gobiernan por políticas, no por widgets
- `refresh` no degrada el estado semántico a ciegas
- la UI renderiza proyecciones, no negocio
- infraestructura transporta o persiste, no decide reglas

## Relación con los docs de handoff
- `MASTER_ARCHITECTURE.md` define el mapa completo
- `FROZEN_CONTRACTS.md` define archivos ley
- `IMPORT_RULES.md` define capas e imports válidos
- `MERGE_GATES.md` define qué debe estar verde antes de abrir lanes
- `ALPHA_SCOPE.md`, `BRAVO_SCOPE.md`, `CHARLIE_SCOPE.md` acotan ownership
- `HANDOFF_TEMPLATE.md` define el formato obligatorio de entrega entre chats

## Regla operativa
No se abre trabajo paralelo serio hasta que:
1. estén congelados los contratos
2. estén cerradas las rutas canónicas
3. la cuarentena legacy esté declarada
4. los merge gates estén en verde
