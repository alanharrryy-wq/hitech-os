# 05_CONTRACTS_CATALOG.md

## Propósito

Este documento define el sistema de contratos de ForgeOS.  
Toda interacción cross-layer queda prohibida si no está descrita aquí o en un derivado compatible.

## Principios del sistema contractual

1. No hay interacción cross-layer sin contrato.
2. Todo contrato tiene owner, producer, consumer y versión.
3. Todo contrato tiene validación antes de ejecutarse.
4. Todo contrato deja huella observable.
5. Los contratos evolucionan por política, no por improvisación.
6. Los strings libres no son suficientes; el string del contract id solo es la llave de un acuerdo formal.

## Envelope contractual canónico

```json
{
  "contract_id": "forge.kernel.lifecycle.product.activate.v1",
  "family": "lifecycle",
  "version_major": 1,
  "producer": "forge-kernel",
  "consumer": "forge-product-<product_id>",
  "owner": "forge-kernel",
  "correlation_id": "<uuid-or-trace-id>",
  "issued_at_utc": "<RFC3339>",
  "payload_schema_id": "forge.kernel.lifecycle.product.activate.payload.v1",
  "payload": {},
  "observability": {
    "trace": true,
    "log_level": "info",
    "emit_metrics": true
  }
}
```

## Invariantes globales

- `contract_id` es único y estable por major version.
- `family` debe coincidir con el catálogo oficial.
- `owner` no puede ser ambiguo.
- `producer` y `consumer` deben ser entidades instalables o registrables.
- `payload_schema_id` debe existir.
- `payload` debe validarse.
- Toda respuesta o evento derivado debe conservar `correlation_id`.
- Todo error debe usar el error envelope oficial.

## Error model estándar

Todo contrato usa un error envelope compatible con estas categorías:

- `validation_error`
- `authorization_error`
- `compatibility_error`
- `dependency_unavailable`
- `timeout`
- `execution_failed`
- `teardown_required`
- `faulted_runtime`
- `migration_required`

### Campos mínimos del error envelope
- `error_code`
- `error_category`
- `owner`
- `retryable`
- `message`
- `correlation_id`
- `details_ref` opcional

## Familias contractuales oficiales

| Familia | Propósito | Owner target | Interacción típica | Observabilidad mínima |
| --- | --- | --- | --- | --- |
| Lifecycle | Activación, suspensión, reanudación y dispose de kernel/capability/product | Forge Kernel | Kernel y el paquete afectado | Request/ack versionado | Correlación, duración, resultado, owner |
| State | Lectura, publicación, snapshot, restore y migración de estado | Dueño del state slice | Dueño y consumidores declarados | Read/write con authority explícita | Schema version, source of truth, restore status |
| Command | Pedidos de acción con intención y respuesta | Quien define la acción | Host, commons o producto | Request/response | Command id, initiator, timeout, outcome |
| Event | Notificaciones inmutables de hechos ocurridos | Actor que posee el hecho | Consumidores suscritos | One-way publish | Event id, producer, correlation, severity |
| Contribution | Declaración de superficies, acciones y extensiones de host | Producto | Host/Kernal | Registration + validation | Contribution id, slot, policy result |
| Capability Service | Consumo de capabilities de Forge Commons | Capability owner | Producto o kernel | Request/response o streaming | Capability id, SLA, timeout, degrade mode |
| Persistence | Serialización, schema, migraciones y ownership de datos | Dueño del store | Dueño + migradores | Read/write/migrate | Store id, schema version, migration path |
| Packaging | Manifest, BOM, firma, assets, instalación y rollback | Package owner | Kernel packaging/runtime | Validation + lifecycle | Package id, version, hashes, compatibility |
| Compatibility | Declaración de rangos soportados entre kernel, commons y producto | Package owner | Kernel install/release gates | Declaration + validation | Version ranges, channel, migration requirement |

---

## Lifecycle contracts

- **Contract name**: `forge.kernel.lifecycle.*`
- **Purpose**: gobernar discover, register, prepare, activate, suspend, resume, fault, dispose.
- **Producer**: normalmente Forge Kernel; el package afectado responde con ack/result.
- **Consumer**: products y capabilities; en algunos flujos el kernel consume acks.
- **Ownership**: Forge Kernel.
- **Directionality**: request/ack; puede emitir events de transición asociados.
- **Payload semantics**:
  - identidad del package;
  - target lifecycle state;
  - trigger;
  - timeout;
  - policy flags (`preserve_state`, `force_dispose`, etc.).
- **Invariants**:
  - no activation sin compatibility validada;
  - no dispose sin teardown plan declarado;
  - no resume sin state policy compatible.
- **Error model**:
  - `compatibility_error`
  - `timeout`
  - `faulted_runtime`
  - `teardown_required`
- **Lifecycle timing**:
  - boot,
  - instalación,
  - activación de producto/capability,
  - suspensión por inactividad,
  - fault handling,
  - shutdown.
- **Versioning strategy**: major al cambiar estados, triggers o semantics de transición.
- **Backward compatibility policy**: el kernel puede soportar dos majors simultáneos solo durante ventana de deprecación declarada.
- **Validation expectations**:
  - package instalado;
  - contract registrado;
  - permissions válidos;
  - timeout definido;
  - precondiciones del estado actual.
- **Observability hooks**:
  - transition started/ended;
  - duration;
  - previous/new state;
  - teardown summary.
- **Failure modes**:
  - package no compatible;
  - handler ausente;
  - timeout de preparación;
  - dispose incompleto.

---

## State contracts

- **Contract name**: `forge.<owner>.state.*`
- **Purpose**: leer, escribir, snapshotear, restaurar y migrar state slices.
- **Producer**: owner del state slice.
- **Consumer**: kernel, commons o productos autorizados.
- **Ownership**: el owner del state slice. Nunca el reader incidental.
- **Directionality**: request/response y event-driven para publicaciones de snapshot o cambios.
- **Payload semantics**:
  - `state_slice_id`
  - `schema_version`
  - `authority`
  - `operation` (`read`, `write`, `snapshot`, `restore`, `migrate`)
  - payload del slice
- **Invariants**:
  - un solo writer authority;
  - schema version explícita;
  - restore solo sobre versiones compatibles.
- **Error model**:
  - `validation_error`
  - `migration_required`
  - `authorization_error`
  - `execution_failed`
- **Lifecycle timing**:
  - durante boot,
  - restore,
  - savepoints,
  - suspend,
  - dispose,
  - migraciones de upgrade/rollback.
- **Versioning strategy**: major al cambiar schema incompatible o semántica de authority.
- **Backward compatibility policy**: migraciones deben declarar from/to; sin migración no hay upgrade.
- **Validation expectations**:
  - state owner coincide;
  - schema conocido;
  - operation permitida;
  - storage disponible.
- **Observability hooks**:
  - bytes/tamaño del snapshot;
  - schema version;
  - migrate duration;
  - restore outcome.
- **Failure modes**:
  - store no montado;
  - snapshot inválido;
  - schema desconocido;
  - conflicto de authority.

---

## Command contracts

- **Contract name**: `forge.<owner>.command.<action>.v<major>`
- **Purpose**: pedir acciones con intención explícita y respuesta observada.
- **Producer**: caller autorizado.
- **Consumer**: owner de la acción.
- **Ownership**: owner funcional de la acción.
- **Directionality**: request/response.
- **Payload semantics**:
  - `command_id`
  - `initiator`
  - `target`
  - `arguments`
  - `timeout`
  - `idempotency_key` si aplica
- **Invariants**:
  - command id único;
  - owner definido;
  - timeout presente para efectos externos;
  - respuesta o error obligatorios.
- **Error model**:
  - `validation_error`
  - `dependency_unavailable`
  - `timeout`
  - `execution_failed`
- **Lifecycle timing**: runtime activo; nunca durante estados no compatibles.
- **Versioning strategy**: major al romper args o semantics de respuesta.
- **Backward compatibility policy**: commands deprecated deben anunciar reemplazo.
- **Validation expectations**:
  - initiator autorizado;
  - target compatible;
  - args válidos;
  - command registrado.
- **Observability hooks**:
  - dispatch time;
  - handler;
  - duration;
  - outcome;
  - retries si hubo.
- **Failure modes**:
  - handler ausente;
  - dependencia caída;
  - timeout;
  - side effect parcial que requiere compensación.

---

## Event contracts

- **Contract name**: `forge.<owner>.event.<fact>.v<major>`
- **Purpose**: notificar hechos inmutables ya ocurridos.
- **Producer**: owner del hecho.
- **Consumer**: suscriptores autorizados.
- **Ownership**: owner del hecho, no del subscriber.
- **Directionality**: one-way publish.
- **Payload semantics**:
  - hecho ocurrido;
  - timestamps;
  - subject ids;
  - metadata de severidad/categoría si aplica.
- **Invariants**:
  - un evento no pide acciones;
  - un evento no contiene callbacks;
  - un evento describe hechos, no intenciones.
- **Error model**:
  - fallos de subscriber no invalidan el hecho, pero sí generan observabilidad;
  - el publication path puede rechazar eventos inválidos por schema.
- **Lifecycle timing**: después del hecho; nunca como mecanismo de request oculto.
- **Versioning strategy**: major al cambiar payload incompatible.
- **Backward compatibility policy**: subscribers deben poder convivir con dos majors durante deprecación aprobada.
- **Validation expectations**:
  - schema válido;
  - owner correcto;
  - event id registrado.
- **Observability hooks**:
  - fanout count;
  - subscriber failures;
  - lag/latency si aplica.
- **Failure modes**:
  - schema inválido;
  - subscriber fault;
  - event flood sin policy.

---

## Contribution contracts

- **Contract name**: `forge.kernel.contribution.<slot_or_action>.v<major>`
- **Purpose**: declarar cómo un producto se integra al host.
- **Producer**: producto.
- **Consumer**: Forge Kernel Host Shell.
- **Ownership**: compartido; el slot lo gobierna el kernel, el contenido lo gobierna el producto.
- **Directionality**: registration/validation/activation.
- **Payload semantics**:
  - `product_id`
  - `contribution_id`
  - `extension_point`
  - `surface_or_action_type`
  - `permissions`
  - `visibility_policy`
  - `activation_policy`
- **Invariants**:
  - `contribution_id` único por producto;
  - extension point existente;
  - host no deduce semantics a partir del naming;
  - toda contribution pasa gate antes de render.
- **Error model**:
  - `compatibility_error`
  - `authorization_error`
  - `validation_error`
- **Lifecycle timing**:
  - install,
  - register,
  - activate,
  - update,
  - uninstall.
- **Versioning strategy**: major al cambiar slot semantics o campos obligatorios.
- **Backward compatibility policy**: el host puede soportar dos majors de contribution contract si lo declara.
- **Validation expectations**:
  - slot válido;
  - permission aprobada;
  - compatibility válida;
  - ownership claro.
- **Observability hooks**:
  - contribution accepted/rejected;
  - slot binding;
  - activation failures.
- **Failure modes**:
  - slot inexistente;
  - permission insuficiente;
  - incompatibilidad con host shell.

---

## Capability service contracts

- **Contract name**: `forge.commons.<capability>.<service>.v<major>`
- **Purpose**: consumir una capability de Forge Commons sin tocar sus internals.
- **Producer**: caller autorizado, usualmente producto o kernel.
- **Consumer**: capability owner.
- **Ownership**: capability owner.
- **Directionality**: request/response o streaming si así se declara.
- **Payload semantics**:
  - `capability_id`
  - `service_id`
  - `request`
  - `timeout`
  - `degrade_policy`
  - `permission_context`
- **Invariants**:
  - el caller no recibe punteros a internals;
  - toda capability declara SLA o política de timeout razonable;
  - los stores del capability siguen siendo privados.
- **Error model**:
  - `dependency_unavailable`
  - `timeout`
  - `authorization_error`
  - `execution_failed`
- **Lifecycle timing**: solo cuando el capability está `ready` o `serving`.
- **Versioning strategy**: major al cambiar schema o degrade semantics.
- **Backward compatibility policy**: si cambia el SLA o el contrato de respuesta, sube major.
- **Validation expectations**:
  - capability instalada;
  - service expuesto;
  - permission concedida;
  - request schema válido.
- **Observability hooks**:
  - latency;
  - saturation;
  - timeout rate;
  - degrade/fallback usage.
- **Failure modes**:
  - capability degradado;
  - store no disponible;
  - saturación;
  - timeout.

---

## Persistence contracts

- **Contract name**: `forge.<owner>.persistence.<store_or_migration>.v<major>`
- **Purpose**: declarar schema, storage backend, migraciones, restore y purge.
- **Producer**: owner del store.
- **Consumer**: kernel packaging/runtime, owner y migradores autorizados.
- **Ownership**: owner del store.
- **Directionality**: declaration + execution de migrate/restore/purge.
- **Payload semantics**:
  - `store_id`
  - `schema_version`
  - `backend_type`
  - `migration_plan`
  - `retention_policy`
  - `purge_policy`
- **Invariants**:
  - store id estable;
  - backend explícito;
  - migración declarada;
  - purge acotado al owner.
- **Error model**:
  - `migration_required`
  - `execution_failed`
  - `validation_error`
- **Lifecycle timing**:
  - install,
  - upgrade,
  - rollback,
  - suspend,
  - shutdown,
  - uninstall.
- **Versioning strategy**: major al cambiar schema o backend incompatible.
- **Backward compatibility policy**: migraciones deben ser idempotentes o declararse no reversibles.
- **Validation expectations**:
  - migration graph completo;
  - storage accesible;
  - backup/rollback policy presente si aplica.
- **Observability hooks**:
  - migrate started/completed;
  - restore outcome;
  - purge result.
- **Failure modes**:
  - migration fallida;
  - rollback parcial;
  - schema huérfano.

---

## Packaging contracts

- **Contract name**: `forge.package.<kind>.v<major>`
- **Purpose**: gobernar manifests, instalación, activación, upgrade, rollback y uninstall.
- **Producer**: package owner.
- **Consumer**: kernel packaging/runtime.
- **Ownership**: package owner + kernel packaging authority.
- **Directionality**: declaration + validation.
- **Payload semantics**:
  - `package_id`
  - `package_type`
  - `version`
  - `artifacts`
  - `dependencies`
  - `compatibility`
  - `permissions`
  - `migrations`
  - `integrity`
- **Invariants**:
  - package id único;
  - version obligatoria;
  - compatibility obligatoria;
  - integrity data obligatoria para releases.
- **Error model**:
  - `validation_error`
  - `compatibility_error`
  - `migration_required`
- **Lifecycle timing**:
  - build,
  - install,
  - upgrade,
  - rollback,
  - uninstall.
- **Versioning strategy**: semver por paquete.
- **Backward compatibility policy**: la instalación puede rechazar paquetes compatibles solo con majors no soportados.
- **Validation expectations**:
  - manifest completo;
  - hashes y firma si aplica;
  - BOM presente;
  - rollback plan presente.
- **Observability hooks**:
  - install duration;
  - validation failures;
  - rollback outcome.
- **Failure modes**:
  - paquete incompleto;
  - incompatibilidad de ranges;
  - integrity failure.

---

## Compatibility contracts

- **Contract name**: `forge.compatibility.<subject>.v<major>`
- **Purpose**: declarar rangos soportados entre kernel, commons y productos.
- **Producer**: package owner.
- **Consumer**: kernel install/release gates.
- **Ownership**: package owner.
- **Directionality**: declaration/validation.
- **Payload semantics**:
  - `subject`
  - `supported_kernel_range`
  - `supported_commons_ranges`
  - `channels`
  - `migration_notes`
- **Invariants**:
  - sin compatibilidad declarada no hay instalación válida;
  - ranges deben ser machine-readable;
  - los channels deben existir.
- **Error model**:
  - `compatibility_error`
  - `validation_error`
- **Lifecycle timing**:
  - install,
  - activate,
  - upgrade,
  - rollback.
- **Versioning strategy**: major al cambiar schema de compatibilidad.
- **Backward compatibility policy**: un package puede ampliar ranges en minor, romperlos en major.
- **Validation expectations**:
  - ranges parseables;
  - dependencias resueltas;
  - conflicts detectados.
- **Observability hooks**:
  - matrix resolution;
  - channel mismatch;
  - blocked installs.
- **Failure modes**:
  - range vacío;
  - dependency incompatible;
  - channel no permitido.

## Reglas de naming

### Regla general
`forge.<scope>.<domain_or_capability>.<noun_or_action>.v<major>`

### Reglas específicas
- todo en minúsculas ASCII;
- separado por punto;
- sin espacios;
- el major va al final como `v1`, `v2`, etc.;
- el prefijo `forge` es obligatorio;
- los contratos de producto deben incluir su `product_id`;
- los contratos de commons deben incluir su `capability_id`;
- los contratos de kernel no pueden incluir nombres de producto.

### Ejemplos válidos
- `forge.kernel.lifecycle.product.activate.v1`
- `forge.kernel.contribution.surface.register.v1`
- `forge.commons.process_execution.execute.v1`
- `forge.product.cloudflare_guardian.context.publish.v1`

### Ejemplos inválidos
- `tool_activated`
- `cloudflare_guardian_run`
- `run.v1`
- `forge.kernel.cloudflare.branch.v1`

## Checklist de review de contratos

1. ¿Tiene owner explícito?
2. ¿Está en la familia correcta?
3. ¿Tiene versionado semántico claro?
4. ¿El payload está definido y validable?
5. ¿La dirección de la interacción está clara?
6. ¿El error model está declarado?
7. ¿La observabilidad mínima está descrita?
8. ¿Existe política de backward compatibility?
9. ¿No introduce semántica de producto en kernel o commons?
10. ¿No reemplaza con eventos algo que en realidad es command?
11. ¿No usa strings derivados por heurística como parte del contrato?
12. ¿Tiene migration/deprecation path si reemplaza uno anterior?

## Política de evolución contractual

- Minor para agregar campos opcionales o comportamientos backward-compatible.
- Major para cambios incompatibles de payload, semantics, lifecycle o ownership.
- No se borran contratos de un día para otro.
- Todo cambio de contract debe actualizar:
  - contract index,
  - compatibility docs,
  - release notes,
  - acceptance evidence.

## Política de deprecación

1. Marcar el contrato como `deprecated`.
2. Declarar reemplazo exacto.
3. Mantener compatibilidad por una ventana definida de releases.
4. Emitir observabilidad de uso del contrato deprecado.
5. Retirar solo después de cumplir la ventana y cerrar migración.

## Regla final

En ForgeOS, un string solo es aceptable como **identificador** de contrato.  
No es aceptable como **sustituto** del contrato.
