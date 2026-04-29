# PRISMA Runtime Config Implementation Backlog

**Paquete:** PRISMA_RUNTIME_CONFIG_BOUNDARY_01  
**Estado:** backlog compacto corregido  
**Alcance:** tareas reales para pasar de contrato documental a implementación segura.

---

## Backlog canónico

| ID | Tarea | Resultado esperado |
|---|---|---|
| RCB-01 | Resolver runtime root | función única que resuelve repo/dev/customer sin depender de `cwd` |
| RCB-02 | Separar dev/customer mode | `dev` puede usar repo; cliente usa `C:\ProgramData\PRISMA` |
| RCB-03 | Bloquear DB cliente dentro del repo | verify falla si DB cliente apunta a `F:\repos\hitech-os` |
| RCB-04 | Validar ProgramData layout | carpetas requeridas existen o se crean controladamente |
| RCB-05 | Validar logs/backups escribibles | prueba de escritura antes de aplicar cambios |
| RCB-06 | Resolver license path | licencia local se lee desde config/runtime, no desde repo commiteado |
| RCB-07 | Resolver businessId/deviceId | ambos obligatorios fuera de dev |
| RCB-08 | Smoke verify de paths | reporte claro de rutas resueltas y modo activo |
| RCB-09 | Definir degraded managed | Tablet sigue vendiendo si PC/red cae, acciones sensibles quedan controladas |
| RCB-10 | Runtime-safe rollback | rollback no borra datos vivos del cliente |
| RCB-11 | Sanitizar diagnósticos de rutas | diagnóstico muestra rutas sin secretos |
| RCB-12 | Documentar migración DB cliente | plan futuro para mover DB fuera del repo sin pérdida |

---

## Fuera de alcance en este paquete

- modificar `DATABASE_URL` real;
- mover `tablet-pos.db`;
- tocar Prisma schema;
- tocar rutas Next;
- crear Local Agent;
- activar Remote Ops;
- cambiar scripts de arranque.

---

## Criterio de aceptación

Este backlog queda listo cuando cada tarea tenga:

- dueño futuro;
- paquete destino;
- criterio de verify;
- rollback esperado;
- riesgo principal.

No se aceptan 300 tareas clonadas con nombre distinto. Eso es confeti de Jira, no planeación.
