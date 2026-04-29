# PRISMA Centro PRISMA UI Shell 03 — Empty States and Mock Policy


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


## Propósito

Evitar pantallas vacías confusas y mocks mentirosos. Una pantalla vacía debe orientar. Un mock debe decir que es mock. Un botón deshabilitado debe explicar por qué.

## Estados vacíos PC

| Módulo | Estado vacío | CTA permitido | CTA prohibido |
| --- | --- | --- | --- |
| Centro | No hay alertas activas. | ver contratos | resolver todo |
| Mi Plan | No se encontró licencia local. | ver ejemplo local | comprar/pagar |
| Plugins | No hay plugins instalados. | ver catálogo declarativo | instalar |
| Soporte | No hay tickets locales. | crear borrador local | enviar remoto |
| Mensajes | No hay threads. | crear mensaje mock | enviar al proveedor |
| Novedades | No hay avisos. | ver historial mock | forzar popup |
| Diagnóstico | No hay bundle generado. | ver allowlist | generar sin consentimiento |
| Actualizaciones | No hay update disponible. | ver canal | aplicar update |

## Estados vacíos Tablet

| Módulo | Mensaje | Acción segura |
| --- | --- | --- |
| Estado | Todo tranquilo por ahora. | volver a venta |
| Soporte | No hay solicitud abierta. | crear borrador |
| Mensajes | Sin mensajes pendientes. | actualizar local |
| Novedades | Sin novedades nuevas. | ver anteriores |

## Etiquetas obligatorias

| Etiqueta | Uso |
| --- | --- |
| Modo mock local | flujo sin servidor real |
| Solo lectura | vista sin mutación |
| Requiere paquete posterior | depende de 04/05/06/07/08 |
| Requiere permiso | usuario no autorizado |
| Requiere consentimiento | diagnóstico o datos sensibles |
| No disponible durante checkout | mensajes/novedades no críticas |

## Copy recomendado

### Mock local

> Esta sección funciona en modo mock local. Sirve para validar flujo y contrato antes de conectar servicios reales.

### Read-only

> Esta vista es de consulta. Las acciones se habilitarán cuando exista implementación verificada, permisos, auditoría y rollback.

### Plan limitado

> Tu plan actual no incluye esta capacidad. Tus datos siguen siendo tuyos y no se eliminan.

### Diagnóstico

> Para generar diagnóstico se necesita autorización. El bundle debe excluir secretos y datos no permitidos.

## Rechazo inmediato

- Mock sin etiqueta.
- Botón activo sin backend.
- “Error” para estado vacío normal.
- Copy que diga “enviado” cuando es local.
- Novedad comercial en checkout.
