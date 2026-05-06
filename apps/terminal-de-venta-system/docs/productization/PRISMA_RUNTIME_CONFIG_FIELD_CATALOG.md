---
title: PRISMA Runtime Config Field Catalog
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---


# PRISMA Runtime Config Field Catalog

Este catalogo define los campos que mas adelante usaran instaladores, Local Agent, Tablet, PC, Remote Ops y soporte. No implementa codigo; le pone nombre a los tornillos antes de que alguien arme la mesa con clavos.

## 1. `schemaVersion`

**Proposito:** version del contrato runtime.

**Regla:** debe avanzar con compatibilidad explicita.

**Anti regla:** no debe inferirse por nombres de archivo.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
SCHEMAVERSION_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 2. `runtimeMode`

**Proposito:** modo tecnico de ejecucion.

**Regla:** dev, standalone, pro, pc_backoffice, managed, degraded_managed.

**Anti regla:** no debe usarse como feature flag comercial.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
RUNTIMEMODE_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 3. `runtimeRoot`

**Proposito:** raiz de datos cliente.

**Regla:** normalmente C:/ProgramData/PRISMA.

**Anti regla:** no debe apuntar al repo.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
RUNTIMEROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 4. `configRoot`

**Proposito:** raiz de configuracion.

**Regla:** normalmente C:/ProgramData/PRISMA/config.

**Anti regla:** no debe guardar secretos en claro sin control.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
CONFIGROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 5. `businessId`

**Proposito:** identificador del negocio.

**Regla:** separa datos por cliente/negocio.

**Anti regla:** no debe estar vacio.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
BUSINESSID_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 6. `deviceId`

**Proposito:** identificador del dispositivo.

**Regla:** permite licencia, soporte y diagnostico.

**Anti regla:** no debe cambiar en cada arranque.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
DEVICEID_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 7. `packageType`

**Proposito:** paquete comercial instalado.

**Regla:** TABLET_SOLO, TABLET_PRO, PC_BACKOFFICE, TABLET_PC_MANAGED.

**Anti regla:** no debe confundirse con runtimeMode.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
PACKAGETYPE_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 8. `tabletDatabaseUrl`

**Proposito:** conexion SQLite Tablet.

**Regla:** debe apuntar a ProgramData en cliente.

**Anti regla:** no debe apuntar a products/tablet/app/data en cliente.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
TABLETDATABASEURL_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 9. `pcDatabaseUrl`

**Proposito:** conexion PC Backoffice.

**Regla:** debe apuntar a ProgramData en cliente.

**Anti regla:** no debe compartir DB con Tablet sin contrato.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
PCDATABASEURL_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 10. `logsRoot`

**Proposito:** raiz de logs.

**Regla:** debe ser escribible y separada por negocio.

**Anti regla:** no es fuente de verdad.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
LOGSROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 11. `backupsRoot`

**Proposito:** raiz de backups.

**Regla:** debe existir antes de update/migration.

**Anti regla:** no sustituye migraciones.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
BACKUPSROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 12. `exportsRoot`

**Proposito:** raiz de exportaciones.

**Regla:** visible para cliente y soporte.

**Anti regla:** no debe ser backup automatico.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
EXPORTSROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 13. `supportRoot`

**Proposito:** raiz de soporte.

**Regla:** contiene bundles y diagnosticos.

**Anti regla:** no debe incluir secretos.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
SUPPORTROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 14. `updatesRoot`

**Proposito:** raiz de updates.

**Regla:** downloads, staged, applied.

**Anti regla:** no debe aplicar sin verify.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
UPDATESROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 15. `rollbackRoot`

**Proposito:** raiz de rollback.

**Regla:** snapshots y manifests.

**Anti regla:** no debe borrarse hasta cumplir retencion.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
ROLLBACKROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 16. `licenseFile`

**Proposito:** archivo local de licencia.

**Regla:** debe admitir grace offline.

**Anti regla:** no debe bloquear export/backup de datos.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
LICENSEFILE_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 17. `deviceRegistry`

**Proposito:** registro local de dispositivos.

**Regla:** necesario para managed.

**Anti regla:** no debe duplicar identities.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
DEVICEREGISTRY_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 18. `syncRoot`

**Proposito:** raiz de sync.

**Regla:** inbox, outbox, conflicts, archive.

**Anti regla:** no debe bloquear venta local.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
SYNCROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 19. `featureFlags`

**Proposito:** features resueltas.

**Regla:** derivadas de licencia/plan.

**Anti regla:** no deben ocultar datos cliente.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
FEATUREFLAGS_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 20. `remoteOpsBridge`

**Proposito:** puente futuro.

**Regla:** polling saliente.

**Anti regla:** no abrir puertos entrantes por default.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
REMOTEOPSBRIDGE_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 21. `announcementCache`

**Proposito:** cache de anuncios.

**Regla:** control por rol/plan/version.

**Anti regla:** no interrumpir checkout comercialmente.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
ANNOUNCEMENTCACHE_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 22. `messageCache`

**Proposito:** cache de mensajes.

**Regla:** soporte y comunicacion.

**Anti regla:** no mezclar con eventos de venta.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
MESSAGECACHE_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 23. `diagnosticPolicy`

**Proposito:** politica de diagnostico.

**Regla:** requiere consentimiento.

**Anti regla:** no enviar datos sensibles por default.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
DIAGNOSTICPOLICY_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## 24. `pluginRoot`

**Proposito:** raiz de plugins locales.

**Regla:** manifests y assets permitidos.

**Anti regla:** no ejecutar codigo arbitrario.

**Debe aparecer en:**

- runtime config cuando aplique;
- support bundle como metadata saneada;
- manifest de instalacion si afecta rutas;
- reporte de verify si es bloqueante.

**Validacion recomendada:**

1. validar tipo;
2. validar no vacio si es requerido;
3. validar que no apunte al repo si es dato cliente;
4. registrar fuente de resolucion;
5. fallar con mensaje humano si rompe contrato.

**Ejemplo de error bueno:**

```text
PLUGINROOT_INVALID: el valor no cumple el contrato runtime. Revisa runtime.json o ejecuta verify.
```

## Cierre

Este catalogo debe crecer antes de tocar codigo runtime real. Si el campo no tiene regla, todavia no merece entrar al motor.
