# PACKAGING

## Identidad de paquete

- `package_id`: `forge-product-<product_id>`
- `package_type`: `product`
- `channel`: `<experimental|beta|stable|lts>`

## Contenido del paquete

| Componente | Incluido | Obligatorio | Observaciones |
| --- | --- | --- | --- |
| `PRODUCT_MANIFEST.json` | sí | sí | identidad y entrypoints |
| contratos | sí | sí | versionados y validados |
| documentación de gobierno | sí | sí | ownership, lifecycle, state, teardown |
| assets runtime | sí/no | según producto | deben estar en BOM |
| migraciones de estado | sí/no | si hay persistencia | versionadas |
| release notes | sí | sí | cada release |
| rollback plan | sí | sí | cada release |

## Bill of Materials

Todo archivo runtime relevante debe aparecer en `packaging/bom/BOM.md` con:
- ruta;
- tipo;
- hash;
- origen;
- razón de inclusión.

## Instalación

### Preconditions
- compatibilidad con `forge-kernel`;
- capabilities requeridos resueltos;
- permisos aprobados;
- manifest íntegro;
- firmas/hashes válidos.

### Postconditions
- paquete registrado;
- contracts visibles;
- contributions listas para validación;
- migraciones aplicadas o rechazadas con evidencia.

## Uninstall

- retirar contributions;
- dispose completo del runtime;
- decidir si el estado se conserva o purga según política;
- emitir evidencia de uninstall;
- no dejar assets o stores huérfanos.

## Release y rollback

- cada release lleva `RELEASE_NOTES`;
- cada release lleva `ROLLBACK_PLAN`;
- si la migración no es reversible, se documenta compensación;
- ningún rollback ignora estado persistente.
