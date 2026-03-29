# SERVICE_CONTRACT

## Identidad

- `contract_id`: `forge.commons.<capability_id>.service.<service_name>.v1`
- `family`: `capability_service`
- `version_major`: `1`
- `owner`: `<capability-owner>`
- `producer`: `<capability-runtime>`
- `consumer`: `<kernel-o-producto-autorizado>`

## Propósito

Describe cómo se solicita una capability de Forge Commons sin exponer internals del capability.

## Service semantics

| Campo | Tipo | Requerido | Significado | Restricciones |
| --- | --- | --- | --- | --- |
| `service_request_id` | string | sí | identidad de la llamada | único |
| `capability_id` | string | sí | capability requerida | instalada y compatible |
| `operation` | string/enum | sí | operación del servicio | declarada |
| `payload` | object | sí/no | parámetros de la operación | schema validado |
| `timeout_ms` | integer | sí | timeout máximo | política del capability |

## Invariantes

- El consumidor no recibe referencias a internals privados.
- El capability conserva autoridad de estado.
- Todo acceso requiere compatibilidad y permiso.
- La degradación se declara.

## Error model

- capability unavailable;
- capability degraded;
- incompatible request;
- timeout;
- execution failed.

## Lifecycle timing

- disponible desde: `<ready-state>`
- rechaza requests en: `<disposing|faulted>`
- comportamiento en suspensión: `<deny|queue|degrade>`

## Observability hooks

- request count;
- latency;
- timeout count;
- degrade count;
- owner.
