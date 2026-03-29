# OWNERSHIP

## Identidad del producto

- `product_id`: `<product_id>`
- `package_id`: `forge-product-<product_id>`
- `display_name`: `<Nombre del producto>`

## Owners obligatorios

| Rol | Responsable nominal | Alcance | Backup | Evidencia de aceptación |
| --- | --- | --- | --- | --- |
| Product owner | `<nombre o equipo>` | dirección funcional y scope | `<backup>` | aceptación de objetivos del producto |
| Contract owner | `<nombre o equipo>` | contratos públicos y su evolución | `<backup>` | revisión de `CONTRACT_INDEX` |
| State owner | `<nombre o equipo>` | stores, snapshots, migraciones y purge | `<backup>` | revisión de `STATE_AUTHORITY` |
| Runtime owner | `<nombre o equipo>` | lifecycle, health, timeouts y teardown | `<backup>` | revisión de `LIFECYCLE` y `TEARDOWN` |
| Packaging owner | `<nombre o equipo>` | manifest, BOM, release, rollback y canal | `<backup>` | revisión de `PACKAGING` y `COMPATIBILITY` |
| Security/policy owner | `<nombre o equipo>` | permisos, policy gates, secretos y compliance | `<backup>` | revisión de permissions |

## Ownership por activo

| Activo | Owner | Puede escribir | Puede leer | Restricción |
| --- | --- | --- | --- | --- |
| Dominio del producto | `<owner>` | sí | application y views derivadas | no exponer al host sin contrato |
| Contratos públicos | `<owner>` | sí | kernel/commons/consumidores autorizados | cambios requieren versioning |
| Estado persistente | `<owner>` | sí | migradores y readers autorizados | no mezclar con estado del host |
| Contributions de host | `<owner>` | sí | kernel host shell | review obligatoria de kernel |
| Assets del paquete | `<owner>` | sí | runtime del producto | deben aparecer en BOM |
| Telemetría del producto | `<owner>` | sí | diagnostics/observability autorizados | no filtrar secretos |

## Reglas

- Ningún activo entra al runtime sin owner nominal.
- Un owner puede delegar operación, no autoridad final, sin documento.
- Si el owner cambia, actualiza este archivo y `PRODUCT_MANIFEST`.
- Si no puedes nombrar al owner de un estado o contrato, ese estado o contrato no existe oficialmente.

## No permitido

- ownership “del equipo” sin nombre responsable;
- ownership compartido sin autoridad final;
- stores sin state owner;
- packaging sin packaging owner;
- runtime sin runtime owner.
