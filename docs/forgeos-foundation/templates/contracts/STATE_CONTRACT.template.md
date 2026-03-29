# STATE_CONTRACT

## Identidad

- `contract_id`: `forge.<owner-scope>.state.<state_operation>.v1`
- `family`: `state`
- `version_major`: `1`
- `owner`: `<state-owner>`
- `producer`: `<state-authority>`
- `consumer`: `<lector, restaurador o migrador autorizado>`

## Propósito

Formaliza lectura, snapshot, restore, migrate o publication de un state slice con authority explícita.

## State slice

- `state_slice_id`: `<slice-id>`
- `source_of_truth`: `<store-o-runtime-authority>`
- `schema_id`: `<schema-id>`
- `write_authority`: `<owner>`
- `read_authorities`: `<lista>`

## Payload semantics

| Campo | Tipo | Requerido | Significado | Restricciones |
| --- | --- | --- | --- | --- |
| `state_slice_id` | string | sí | identificador del slice | estable |
| `schema_version` | string | sí | versión del schema | obligatoria |
| `operation` | enum | sí | `read`, `snapshot`, `restore`, `migrate`, `publish` | cerrado |
| `payload` | object | sí | contenido del estado o delta | validado |
| `checksum` | string opcional | integridad | requerido si packaging/export lo exige |

## Invariantes

- Solo el owner escribe.
- Un restore nunca corre sin validar schema.
- Una migración nunca corre sin `from` y `to`.
- Un published context no reemplaza el store source-of-truth.

## Error model

- schema mismatch;
- migration required;
- restore blocked;
- persistence unavailable;
- integrity failure.

## Lifecycle timing

- `snapshot` en `<momento>`;
- `restore` en `<momento>`;
- `publish` en `<momento>`;
- `purge` en `<momento>`.

## Observability hooks

- schema version;
- migration path;
- restore result;
- purge result;
- owner.
