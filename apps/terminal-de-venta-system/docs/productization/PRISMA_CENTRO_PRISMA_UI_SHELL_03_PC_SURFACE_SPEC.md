# PRISMA Centro PRISMA UI Shell 03 — PC Surface Spec


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


## Rol de PC

PC es centro de mando. Puede mostrar módulos completos, estados, matrices, historial y contratos. Pero en este paquete todo sigue siendo shell documental/mock. PC no ejecuta remote ops, no aplica updates, no instala plugins y no genera diagnóstico real.

## Layout PC recomendado

```text
┌────────────────────────────────────────────────────────────────┐
│ Header: PRISMA / negocio / plan / estado / canal / versión     │
├─────────────────┬──────────────────────────────────┬───────────┤
│ Sidebar         │ Main                             │ Right rail │
│ Centro          │ Cards y tablas ligeras           │ Alertas    │
│ Mi Plan         │ Estados mock/read-only           │ Paquetes   │
│ Plugins         │ Contratos y límites              │ Próximos   │
│ Soporte         │                                  │ pasos      │
└─────────────────┴──────────────────────────────────┴───────────┘
```

## Módulos PC


### Centro PRISMA

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.home` |
| pathKey | `centro-prisma` |
| permiso | `center.view` |
| modo inicial | `mock_local` |
| paquete relacionado | `03` |

**Propósito:** mostrar el estado y acceso controlado de `Centro PRISMA` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Mi Plan

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.license` |
| pathKey | `centro-prisma/licencia` |
| permiso | `license.view` |
| modo inicial | `mock_local` |
| paquete relacionado | `02` |

**Propósito:** mostrar el estado y acceso controlado de `Mi Plan` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Plugins

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.plugins` |
| pathKey | `centro-prisma/plugins` |
| permiso | `plugins.view` |
| modo inicial | `read_only` |
| paquete relacionado | `07` |

**Propósito:** mostrar el estado y acceso controlado de `Plugins` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Soporte

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.support` |
| pathKey | `centro-prisma/soporte` |
| permiso | `support.view` |
| modo inicial | `mock_local` |
| paquete relacionado | `04/05` |

**Propósito:** mostrar el estado y acceso controlado de `Soporte` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Mensajes

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.messages` |
| pathKey | `centro-prisma/mensajes` |
| permiso | `messages.view` |
| modo inicial | `mock_local` |
| paquete relacionado | `05` |

**Propósito:** mostrar el estado y acceso controlado de `Mensajes` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Novedades

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.announcements` |
| pathKey | `centro-prisma/novedades` |
| permiso | `announcements.view` |
| modo inicial | `mock_local` |
| paquete relacionado | `06` |

**Propósito:** mostrar el estado y acceso controlado de `Novedades` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Diagnóstico

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.diagnostics` |
| pathKey | `centro-prisma/diagnostico` |
| permiso | `diagnostics.view` |
| modo inicial | `read_only` |
| paquete relacionado | `04` |

**Propósito:** mostrar el estado y acceso controlado de `Diagnóstico` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.

### Actualizaciones

| Elemento | Decisión |
| --- | --- |
| routeId | `pc.center.updates` |
| pathKey | `centro-prisma/actualizaciones` |
| permiso | `updates.view` |
| modo inicial | `read_only` |
| paquete relacionado | `08` |

**Propósito:** mostrar el estado y acceso controlado de `Actualizaciones` dentro de Centro PRISMA.

**Cards mínimas:**

| Card | Dato visible | Acción permitida en 03 | Acción prohibida |
| --- | --- | --- | --- |
| Resumen | estado local/mock | abrir detalle | mutar runtime |
| Contrato | paquete y límites | ver documentación | ejecutar backend |
| Riesgo | alertas de configuración | leer explicación | auto-corregir |
| Siguiente paso | paquete futuro | ver plan | instalar sin instalador |

**Copy de límite recomendado:**

> Esta sección está preparada bajo contrato documental. Las acciones reales se habilitarán solo cuando exista implementación, permisos, auditoría y rollback.

**Riesgo principal:** activar interacción real antes de que el paquete correspondiente exista.


## Estados de error PC

| Caso | Mensaje | Acción segura |
| --- | --- | --- |
| sin licencia local | No se encontró licencia local. Tus datos no se eliminan. | ver contrato de licencia |
| sin plugins | No hay plugins declarativos instalados. | ver catálogo read-only |
| sin mensajes | No hay threads locales. | crear borrador mock |
| diagnóstico no autorizado | El diagnóstico requiere consentimiento. | ver allowlist |
| updates sin bridge | Actualizaciones en modo consulta hasta paquete 08. | ver estado read-only |
| runtime no resuelto | No se pudo resolver runtime root. | ver contrato Runtime 01 |

## Prohibiciones PC

- Botón `Aplicar actualización` activo.
- Botón `Instalar plugin` activo.
- Botón `Enviar mensaje` remoto.
- Botón `Generar diagnóstico` sin consentimiento.
- Botón `Borrar datos por licencia`.
- Cualquier botón que diga `Ejecutar comando`.

PC manda, sí, pero no se pone a disparar desde la azotea.
