# STATE_AUTHORITY

## Regla central

Todo state slice del producto tiene un único owner de escritura.  
Los demás actores leen, observan o consumen snapshots. No escriben.

## State slices oficiales

| State slice | Descripción | Owner de escritura | Consumidores permitidos | Medio de persistencia | Schema version | Restore policy | Purge policy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<product_id>.runtime_session` | estado efímero de sesión del producto | `<state-owner>` | application, views | memory-only | `v1` | rehidratar si aplica | al suspender o dispose |
| `<product_id>.user_preferences` | preferencias propias del producto | `<state-owner>` | application, views | `<store>` | `v1` | restore on prepare | conservar entre releases compatibles |
| `<product_id>.workspace_snapshot` | snapshot recuperable del flujo del producto | `<state-owner>` | application | `<store>` | `v1` | restore on activate | purge por política declarada |
| `<product_id>.history` | ledger o historial propio si existe | `<state-owner>` | application, export | `<store>` | `v1` | append-only o migrado | purge por retención |

## Publicación al host

Solo se publica al host el contexto mínimo aprobado.

| Published context | Fuente | Owner | Frecuencia | Consumidor | Campos permitidos | Campos prohibidos |
| --- | --- | --- | --- | --- | --- | --- |
| `forge.product.<product_id>.summary.v1` | state projection | `<state-owner>` | on-change | kernel host shell | status, title, counters, health resumido | objetos internos, handles, secretos, payloads de dominio completos |

## Reglas de restore

- El restore nunca corre en constructor.
- El restore corre durante `prepare` o `activate` según el contrato lifecycle.
- Todo restore valida schema antes de tocar runtime.
- Toda migración de schema queda versionada y con owner.
- Si un snapshot es incompatible, el producto debe degradarse de forma explícita, no colapsar el host.

## Reglas de autoridad

- El host no escribe estado del producto.
- Forge Commons no escribe estado del producto salvo capability owner explícitamente contratado.
- Otros productos no leen ni escriben este estado.
- Los views pueden leer proyecciones, no convertirse en source of truth.

## Evidencia mínima por state slice

- schema documentado;
- owner nominal;
- strategy de backup/export si aplica;
- restore path;
- migrate path;
- purge path;
- observability hooks.
