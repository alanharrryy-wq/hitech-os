# DeltaForge · Frozen Contracts

Estos archivos son **ley**. Se congelan por Maestro antes de abrir lanes.

## Archivos ley
| Path | Propósito | Motivo de congelamiento |
|---|---|---|
| `domain/ids.py` | IDs tipados (`SessionId`, `ScopeId`) | evita strings libres y colisiones de identidad |
| `domain/events.py` | catálogo de eventos y payload mínimo | toda sincronización inter-capas depende de esto |
| `domain/session_states.py` | estados oficiales | evita transiciones contradictorias |
| `domain/models/scope.py` | modelo tipado de scope | raíz de single/multi/directory/filtered selection |
| `domain/models/session.py` | verdad de `SessionWorkspace` | evita doble verdad en manager/UI/watcher |
| `domain/models/ops_document.py` | semántica de ops, revision/hash | dirty semántico estable |
| `domain/models/plan.py` | resultado de planeación | UI y engine lo comparten |
| `domain/models/diff.py` | preview/diff | centro de la workstation |
| `domain/models/results.py` | validation/apply/rollback/event result | trazabilidad por sesión |
| `application/contracts/engine_adapter.py` | frontera única con engine | desacople real con mock/engine |
| `application/contracts/event_bus.py` | contrato del bus | evita acoplar UI e infra |
| `application/contracts/session_repository.py` | contrato de persistencia | prepara bootstrap/infra |
| `ui/theme/tokens.py` | fuente única de verdad visual | evita colores hardcodeados |
| `ui/theme/semantic_roles.py` | roles semánticos de UI | evita estilos por ocurrencia |

## Ownership y regla de cambio
- Maestro es owner inicial de los law files y los congela antes de lanes.
- Alpha, Bravo y Charlie **no pueden** modificar law files mientras gates estén cerrados.
- Si un lane necesita cambiar un law file, deja de ser trabajo de lane y se escala como reapertura de gate de contrato.

## Protocolo de escalación de gate
1. Lane reporta necesidad de cambio y motivo técnico.
2. Se pausa el lane.
3. Maestro reabre gate de contrato explícitamente.
4. Se aplica cambio en rama controlada y se actualizan handoffs.
5. Se vuelve a congelar con hash actualizado.

## Hash discipline
| Path | SHA256 |
|---|---|
| `domain/events.py` | `PENDIENTE` |
| `domain/session_states.py` | `PENDIENTE` |
| `domain/models/scope.py` | `PENDIENTE` |
| `domain/models/session.py` | `PENDIENTE` |
| `domain/models/ops_document.py` | `PENDIENTE` |
| `domain/models/plan.py` | `PENDIENTE` |
| `domain/models/diff.py` | `PENDIENTE` |
| `domain/models/results.py` | `PENDIENTE` |
| `application/contracts/engine_adapter.py` | `PENDIENTE` |
| `application/contracts/event_bus.py` | `PENDIENTE` |
| `application/contracts/session_repository.py` | `PENDIENTE` |
| `ui/theme/tokens.py` | `PENDIENTE` |
| `ui/theme/semantic_roles.py` | `PENDIENTE` |
