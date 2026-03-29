# EVENT_CONTRACT

## Identidad

- `contract_id`: `forge.<owner-scope>.event.<event_name>.v1`
- `family`: `event`
- `version_major`: `1`
- `owner`: `<contract-owner>`
- `producer`: `<event-producer>`
- `consumers`: `<lista-de-consumidores-declarados-o-clase-de-consumidor>`

## Propósito

Describe un hecho que ya ocurrió y que no debe requerir respuesta síncrona obligatoria.

## Payload semantics

| Campo | Tipo | Requerido | Significado | Restricciones |
| --- | --- | --- | --- | --- |
| `event_id` | string | sí | identidad del evento | único por emisión |
| `correlation_id` | string | sí | correlación con comando/lifecycle | se conserva de origen |
| `<campo>` | `<tipo>` | sí/no | `<significado>` | `<restricción>` |

## Invariantes

- Un event no ordena acciones imperativas.
- Un event no muta estado remoto por sí mismo.
- El payload es inmutable.
- El schema debe ser versionado.

## Error model

El producer puede fallar al emitir; los consumers pueden fallar al procesar.  
Ninguna falla de consumer debe tumbar al producer o al host.

## Lifecycle timing

- emitido en: `<estado o momento>`
- no emitido antes de: `<momento mínimo>`
- caducidad/retención observacional: `<policy>`

## Observability hooks

- log level: `<info|warning|error>`
- métricas mínimas: count, latency de dispatch, failure count
- tags: producer, owner, contract_id, correlation_id

## Failure modes

- payload inválido;
- consumer incompatible;
- timeout del pipeline de entrega;
- observability emit fallida.

## Versioning

- cambio breaking: subir major;
- campos opcionales backward-compatible: minor del schema si aplica;
- no reutilizar `contract_id` para otra semántica.
