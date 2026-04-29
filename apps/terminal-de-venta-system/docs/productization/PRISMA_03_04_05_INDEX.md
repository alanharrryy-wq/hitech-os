# PRISMA 03-04-05 — Índice maestro del paquete 03 ampliado


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


## Qué se está entregando

Este ZIP rehace `PRISMA_CENTRO_PRISMA_UI_SHELL_03` como paquete documental robusto y mete dentro todos los documentos correspondientes a:

| Iteración | Nombre | Qué queda documentado |
| --- | --- | --- |
| 03 | Centro PRISMA UI Shell | rutas, pantallas mock, PC/Tablet, navegación, permisos, estados vacíos, cards y límites |
| 04 | Support Bundle Local | diagnóstico local, allowlist, denylist, redacción de secretos, consentimiento y manifest de bundle |
| 05 | Customer Messaging Mock | threads, mensajes, categorías, estados, adjuntos controlados, storage local y outbox mock |

## Por qué 04 y 05 van dentro del ZIP 03

Porque `Centro PRISMA` es el shell que va a mostrar soporte y mensajes. Si 04 y 05 se documentan aparte sin amarrarse a la navegación, luego cada pantalla crece como puesto de mercado invadiendo banqueta. Este ZIP deja todo alineado desde el arranque: Centro muestra soporte y mensajes, soporte respeta diagnóstico seguro, mensajes no fingen servidor real.

## Inventario documental

### Documentos 03

- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_MASTER_SPEC.md`
- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md`
- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_PC_SURFACE_SPEC.md`
- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_TABLET_SURFACE_SPEC.md`
- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_NAVIGATION_AND_PERMISSIONS.md`
- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_EMPTY_STATES_AND_MOCK_POLICY.md`
- `PRISMA_CENTRO_PRISMA_UI_SHELL_03_ACCEPTANCE_MATRIX.md`

### Documentos 04

- `PRISMA_SUPPORT_BUNDLE_LOCAL_04_MASTER_SPEC.md`
- `PRISMA_SUPPORT_BUNDLE_LOCAL_04_DATA_ALLOWLIST.md`
- `PRISMA_SUPPORT_BUNDLE_LOCAL_04_SECRET_REDACTION_POLICY.md`
- `PRISMA_SUPPORT_BUNDLE_LOCAL_04_DIAGNOSTIC_FIELDS.md`
- `PRISMA_SUPPORT_BUNDLE_LOCAL_04_ACCEPTANCE_MATRIX.md`

### Documentos 05

- `PRISMA_CUSTOMER_MESSAGING_MOCK_05_MASTER_SPEC.md`
- `PRISMA_CUSTOMER_MESSAGING_MOCK_05_THREAD_CONTRACT.md`
- `PRISMA_CUSTOMER_MESSAGING_MOCK_05_LOCAL_STORAGE_POLICY.md`
- `PRISMA_CUSTOMER_MESSAGING_MOCK_05_ACCEPTANCE_MATRIX.md`

### Documentos transversales

- `PRISMA_03_04_05_CROSS_PACKAGE_CONTRACT.md`
- `PRISMA_03_04_05_ROLLOUT_PLAN.md`
- `PRISMA_03_04_05_STOP_CONDITIONS.md`
- `PRISMA_03_04_05_TEST_PLAN.md`
- `PRISMA_03_04_05_TRACEABILITY_MATRIX.md`
- `PRISMA_03_04_05_FIELD_CATALOG.md`
- `PRISMA_03_04_05_IMPLEMENTATION_HANDOFF.md`


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


## Decisión de ingeniería

Este paquete es grande a propósito: documenta de una vez el shell, soporte local y mensajería local mock. Pero sigue siendo seguro porque no mete side effects. Avanzar rápido no significa meterle nitro a una carreta, significa empaquetar la definición completa antes de implementar.
