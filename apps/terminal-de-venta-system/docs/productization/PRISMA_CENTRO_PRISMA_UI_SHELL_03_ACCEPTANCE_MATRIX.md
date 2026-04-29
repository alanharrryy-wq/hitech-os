# PRISMA Centro PRISMA UI Shell 03 — Acceptance Matrix


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


| Área | Acepta si | Bloquea si |
| --- | --- | --- |
| boundary | solo docs/schemas/examples/test-cases | incluye runtime, DB, env o código UI real |
| PC routes | 8 rutas documentadas con permiso y modo | ruta sin permiso o acción real |
| Tablet routes | 4 rutas ligeras y no bloqueantes | ruta que bloquee venta |
| mock policy | todo mock está etiquetado | botón vivo sin backend |
| license | Mi Plan consume contrato 02 | licencia borra datos |
| support | soporte apunta a 04 | diagnóstico sin consentimiento |
| messages | mensajes apuntan a 05 | envío remoto prometido |
| announcements | novedades no interrumpen checkout | popup comercial en cobro |
| plugins | read-only hasta 07 | ejecución de plugin |
| updates | read-only hasta 08 | aplicar update |
