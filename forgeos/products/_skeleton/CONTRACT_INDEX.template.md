# CONTRACT_INDEX

## Índice maestro de contratos del producto

| Contract id | Familia | Versión | Producer | Consumer | Owner | Payload schema | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `forge.product.<product_id>.lifecycle.prepare.v1` | lifecycle | 1 | forge-kernel | forge-product-<product_id> | `<owner>` | `<schema-id>` | draft |
| `forge.product.<product_id>.lifecycle.activate.v1` | lifecycle | 1 | forge-kernel | forge-product-<product_id> | `<owner>` | `<schema-id>` | draft |
| `forge.product.<product_id>.lifecycle.suspend.v1` | lifecycle | 1 | forge-kernel | forge-product-<product_id> | `<owner>` | `<schema-id>` | draft |
| `forge.product.<product_id>.lifecycle.dispose.v1` | lifecycle | 1 | forge-kernel | forge-product-<product_id> | `<owner>` | `<schema-id>` | draft |
| `forge.product.<product_id>.state.snapshot.v1` | state | 1 | forge-product-<product_id> | forge-kernel/restore tooling | `<owner>` | `<schema-id>` | draft |
| `forge.product.<product_id>.command.primary_action.v1` | command | 1 | host o producto | producto | `<owner>` | `<schema-id>` | draft |
| `forge.product.<product_id>.event.primary_state_changed.v1` | event | 1 | producto | consumidores declarados | `<owner>` | `<schema-id>` | draft |

## Reglas

- todo contrato listado aquí debe existir en `contracts/`;
- ningún contrato entra a runtime si no está versionado;
- todo contrato cross-layer requiere review;
- si un contrato se depreca, anótalo aquí y en release notes.

## Dependencias cruzadas aceptables

- lifecycle hacia kernel;
- service contracts hacia commons;
- contribution contracts hacia host;
- state/publication contracts hacia consumers autorizados.

## Dependencias cruzadas prohibidas

- contratos privados con otro producto;
- contratos basados en strings libres sin schema;
- contratos sin owner;
- contratos que exijan acceso a internals del host.
