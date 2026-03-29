# COMMAND_CONTRACT

## Identidad

- `contract_id`: `forge.<owner-scope>.command.<command_name>.v1`
- `family`: `command`
- `version_major`: `1`
- `owner`: `<contract-owner>`
- `producer`: `<command-originator>`
- `consumer`: `<command-handler>`

## Propósito

Describe una intención de acción que sí espera handling explícito y outcome observable.

## Payload semantics

| Campo | Tipo | Requerido | Significado | Restricciones |
| --- | --- | --- | --- | --- |
| `command_id` | string | sí | identidad del request | único por request |
| `correlation_id` | string | sí | trazabilidad | conservarse en respuesta/eventos derivados |
| `requested_by` | string | sí | actor originador | explícito |
| `<campo>` | `<tipo>` | sí/no | `<significado>` | `<restricción>` |

## Outcome contract

| Campo | Tipo | Significado |
| --- | --- | --- |
| `status` | enum | `accepted`, `completed`, `rejected`, `failed`, `timed_out` |
| `result_ref` | string opcional | referencia a resultado o recurso |
| `error` | envelope opcional | error contractual si falla |

## Invariantes

- Un command tiene un solo consumer authority.
- Debe existir timeout explícito.
- Debe existir owner del side effect.
- Debe existir validación antes de ejecutar.

## Error model

- `validation_error`
- `authorization_error`
- `dependency_unavailable`
- `timeout`
- `execution_failed`

## Lifecycle timing

- estado mínimo para aceptarlo: `<prepared|active>`
- estado que lo rechaza: `<suspended|faulted|disposing>`
- timeout máximo: `<segundos>`

## Observability hooks

- count de commands;
- latency de handling;
- timeout count;
- owner;
- initiator.

## Failure modes

- command duplicado;
- payload fuera de schema;
- consumer no activo;
- dependencia faltante;
- side effect externo falla.
