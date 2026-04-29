# PRISMA Centro PRISMA UI Shell 03 — Master Spec


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


## Objetivo

Definir el shell Centro PRISMA para PC y Tablet. Esta capa concentra navegación y visibilidad de licencia, plugins, soporte, mensajes, novedades, diagnóstico y actualizaciones. En esta iteración todo lo que no tenga backend real queda como `mock_local`, `read_only` o `disabled_until_package`.

## Principio central

Centro PRISMA no es consola remota, no es panel bancario, no es ejecutor de plugins y no es taller mecánico metido en la caja. Es una superficie de operación controlada: enseña qué existe, qué está listo, qué falta y qué puede hacer cada usuario.

| Superficie | Rol | Detalle permitido | Prohibición principal |
| --- | --- | --- | --- |
| PC | Centro de mando | alto | acciones reales sin contrato |
| Tablet | estado ligero y soporte mínimo | medio/bajo | bloquear venta o meter backoffice pesado |

## Rutas PC

| routeId | pathKey | Título | Permiso | Modo inicial | Paquete relacionado |
| --- | --- | --- | --- | --- | --- |
| pc.center.home | centro-prisma | Centro PRISMA | center.view | mock_local | 03 |
| pc.center.license | centro-prisma/licencia | Mi Plan | license.view | mock_local | 02 |
| pc.center.plugins | centro-prisma/plugins | Plugins | plugins.view | read_only | 07 |
| pc.center.support | centro-prisma/soporte | Soporte | support.view | mock_local | 04/05 |
| pc.center.messages | centro-prisma/mensajes | Mensajes | messages.view | mock_local | 05 |
| pc.center.announcements | centro-prisma/novedades | Novedades | announcements.view | mock_local | 06 |
| pc.center.diagnostics | centro-prisma/diagnostico | Diagnóstico | diagnostics.view | read_only | 04 |
| pc.center.updates | centro-prisma/actualizaciones | Actualizaciones | updates.view | read_only | 08 |

## Rutas Tablet

| routeId | pathKey | Título | Permiso | Modo inicial | Paquete relacionado |
| --- | --- | --- | --- | --- | --- |
| tablet.center.status | estado | Estado | tablet.status.view | read_only | 03 |
| tablet.center.support | soporte | Soporte | tablet.support.view | mock_local | 04 |
| tablet.center.messages | mensajes | Mensajes | tablet.messages.view | mock_local | 05 |
| tablet.center.announcements | novedades | Novedades | tablet.announcements.view | mock_local | 06 |

## Invariantes

1. Tablet sigue vendiendo aunque Centro PRISMA falle, no exista o esté deshabilitado.
2. PC puede mostrar más detalle, pero no convierte a Tablet en cliente tonto.
3. Todo botón sin backend se marca como mock/read-only/deshabilitado.
4. Diagnóstico requiere consentimiento.
5. Mensajes en 05 son locales y mock.
6. Plugins hasta 07 son declarativos/read-only.
7. Actualizaciones hasta 08 son read-only.
8. Licencia no borra datos.
9. Novedades no interrumpen checkout salvo alerta crítica operacional.
10. Nada toca procesamiento bancario.

## Layout conceptual PC

```text
Header
  negocio, plan, estado local, canal, versión
Sidebar
  Centro, Mi Plan, Plugins, Soporte, Mensajes, Novedades, Diagnóstico, Actualizaciones
Main
  cards por módulo, tablas ligeras, estados y links a contratos
Right rail
  alertas, próximos pasos, modo actual
Footer
  package id, build documental, modo runtime detectado
```

## Layout conceptual Tablet

```text
Header compacto
  estado, plan, versión
Cards grandes
  Soporte, Mensajes, Novedades, Estado
Footer
  volver a venta
```

## Estados obligatorios

| Estado | Cuándo usarlo | Qué permite | Qué bloquea |
| --- | --- | --- | --- |
| mock_local | fixtures o flujo sin backend | navegar y validar UX | acciones reales |
| read_only | consulta sin mutación | ver estado | editar/aplicar/enviar |
| disabled_until_package | depende de paquete futuro | explicar dependencia | simular funcionalidad real |
| blocked_by_plan | feature no incluida | explicar plan | borrar/ocultar datos existentes |
| requires_consent | diagnóstico/soporte sensible | pedir autorización | recolectar sin permiso |
| offline_safe | disponible localmente | consulta local | promesa de sync inmediato |


## Límites no negociables

| Límite | Regla |
|---|---|
| Runtime | No se instala código runtime en este paquete. |
| UI real | No se crean componentes React, rutas Next, handlers ni server actions. |
| DB | No se crea, migra, abre, borra ni mueve ninguna base de datos. |
| Remote Ops | No se abre polling, websocket, túnel, puerto ni agente remoto. |
| Mensajes | Mock local solamente. Sin envío remoto, API, SMTP, WhatsApp ni promesa de respuesta humana. |
| Soporte | Diagnóstico futuro solo con allowlist, redacción y consentimiento. |
| Licencia | Puede mostrar límites, jamás borrar ni secuestrar datos del cliente. |
| Plugins | Se muestran como declarativos/read-only; no se cargan ni ejecutan. |
| Updates | Estado read-only hasta paquete 08. Nada de descargar/aplicar update. |
| Pagos | No hay tarjetas, SPEI, transferencia, custodia, validación bancaria ni dinero. |


## Criterio de aceptación

El shell 03 queda documentalmente listo cuando cada ruta declara superficie, permiso, estado inicial, paquete relacionado, copy de límite, estado vacío y prohibiciones.
