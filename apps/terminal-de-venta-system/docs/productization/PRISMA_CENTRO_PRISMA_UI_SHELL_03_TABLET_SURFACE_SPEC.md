# PRISMA Centro PRISMA UI Shell 03 — Tablet Surface Spec


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Versión documental: `1.1.0`  
> Fecha: `2026-04-28`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: docs, schemas, examples, test-cases, manifest y checksums.  
> Restricción: no instala runtime, no crea rutas Next, no toca DB, no toca `.env`, no ejecuta sync remoto y no procesa pagos.

## Base que no se contradice

Este paquete asume que ya existen y quedan como piso:

- `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`: contratos base de customer operations, remote ops, updates, soporte, plugins, licencias y frontera de no procesamiento bancario.
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`: separación repo / release / runtime cliente, reglas de `ProgramData`, logs, backups, config y prohibición de depender de `cwd`.
- `PRISMA_LICENSE_LOCAL_MOCK_02`: planes, feature flags mock, entitlements, offline grace y contrato local de licencia.

Nada de este paquete invalida lo anterior. Esto no viene a patear la mesa, viene a poner mantel, cubiertos y letrero de “no meter los dedos al enchufe”.


## Rol de Tablet

Tablet es POS standalone. Centro PRISMA en Tablet debe ser ligero: soporte, mensajes, novedades y estado. Nada de backoffice pesado. Nada de tablas que parezcan declaración fiscal. Nada que bloquee venta.

## Rutas Tablet

| routeId | pathKey | Título | Permiso | Modo | Paquete |
| --- | --- | --- | --- | --- | --- |
| tablet.center.status | estado | Estado | tablet.status.view | read_only | 03 |
| tablet.center.support | soporte | Soporte | tablet.support.view | mock_local | 04 |
| tablet.center.messages | mensajes | Mensajes | tablet.messages.view | mock_local | 05 |
| tablet.center.announcements | novedades | Novedades | tablet.announcements.view | mock_local | 06 |

## Layout Tablet recomendado

```text
Header compacto
  Estado: OK / Atención / Offline
Cards grandes
  Soporte
  Mensajes
  Novedades
  Estado
Footer
  Volver a venta
```

## Reglas táctiles

| Regla | Motivo |
| --- | --- |
| máximo cuatro accesos principales | evita saturar operador |
| botón volver a venta visible | venta tiene prioridad |
| sin tablas pesadas | Tablet no es backoffice |
| sin adjuntos libres | evita fuga de datos |
| sin configuración avanzada | eso vive en PC |
| sin acciones destructivas | no hay rollback desde Tablet en esta fase |

## Estados Tablet

| Caso | Mensaje | Acción |
| --- | --- | --- |
| sin red | Puedes seguir operando localmente. | volver a venta |
| sin mensajes | No hay mensajes pendientes. | actualizar vista local |
| sin soporte abierto | No hay solicitud activa. | crear borrador local |
| novedad no crítica | Novedad disponible para revisar después. | posponer |
| plan limitado | Algunas capacidades se gestionan desde PC. | ver estado |
| diagnóstico requerido | El diagnóstico se administra con consentimiento. | ver explicación |

## Prohibiciones Tablet

- Bloquear checkout por mensaje.
- Mostrar popup comercial durante cobro.
- Pedir tokens, rutas técnicas o contraseñas al cajero.
- Adjuntar archivos libres.
- Resolver conflictos de sync.
- Instalar plugins.
- Aplicar updates.
- Mostrar logs crudos.

## Criterio de aceptación

Tablet pasa si cada pantalla es entendible en menos de 5 segundos, no bloquea venta y no contiene acciones que pertenezcan al PC backoffice.
