# LIFECYCLE_CONTRACT

## Identidad

- `contract_id`: `forge.<scope>.lifecycle.<action>.v1`
- `family`: `lifecycle`
- `version_major`: `1`
- `owner`: `<kernel-o-runtime-owner>`
- `producer`: `<generalmente-kernel>`
- `consumer`: `<capability-o-producto>`

## Propósito

Define una transición oficial de lifecycle gobernada y auditable.

## Acción

- `action`: `<prepare|activate|suspend|dispose|resume>`
- `target_id`: `<package-o-runtime-id>`
- `preconditions`: `<lista>`
- `postconditions`: `<lista>`

## Payload semantics

| Campo | Tipo | Requerido | Significado | Restricciones |
| --- | --- | --- | --- | --- |
| `target_id` | string | sí | entidad afectada | debe existir |
| `current_state` | string | sí | estado actual conocido | validado por kernel |
| `requested_state` | string | sí | transición deseada | permitida por FSM |
| `reason` | string | sí/no | motivación | explícita para dispose/fault |
| `deadline_utc` | string | sí/no | momento de timeout | requerido si aplica |

## Invariantes

- La transición debe ser legal según la FSM.
- Debe existir owner del runtime afectado.
- Debe existir timeout o condición de término.
- Debe existir evidence log de resultado.

## Error model

- illegal_transition;
- compatibility_error;
- dependency_unavailable;
- timeout;
- dispose_incomplete.

## Observability hooks

- transition count;
- latency;
- timeout;
- resource cleanup result;
- owner.
