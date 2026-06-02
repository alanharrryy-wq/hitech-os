# ATLAS_SHARED_CORE_RUNTIME_INFRA

**Estado:** borrador inicial trazable
**Alcance:** modos runtime, rutas cliente, soporte, diagnósticos, productización, release bundles, herramientas globales y QA común.

## 1. Modos runtime confirmados

Documento base: `docs/architecture/RUNTIME_MODES_CONTRACT.md`.

| Modo | PC requerido | Internet requerido | Lectura |
| --- | --- | --- | --- |
| standalone | No | No | Tablet opera con DB local y exporta datos. |
| managed | Sí para gobierno/sync | Intermitente o estable | Tablet sincroniza con PC/backoffice. |
| degraded_managed | Sí para gobierno, no para venta básica | No para venta básica | Tablet pertenece a operación managed pero sigue vendiendo si PC/red cae. |

Reglas obligatorias:

- Tablet nunca debe bloquear venta básica porque PC está ausente.
- Si sync falla, la venta local permitida continúa.
- Eventos van a outbox.
- PC resuelve conflictos después.
- No usar `cwd` como raíz confiable.
- No inventar rutas mágicas de DB.

## 2. Runtime path policy

Documento base: `docs/productization/PRISMA_RUNTIME_PATH_POLICY.md`.

Rutas cliente recomendadas:

| Nombre lógico | Ruta |
| --- | --- |
| runtimeRoot | `C:\ProgramData\PRISMA` |
| configRoot | `C:\ProgramData\PRISMA\config` |
| businessRoot | `C:\ProgramData\PRISMA\businesses\<businessId>` |
| tabletDataRoot | `...\tablet\data` |
| pcDataRoot | `...\pc\data` |
| syncRoot | `...\sync` |
| supportRoot | `...\support` |
| updatesRoot | `C:\ProgramData\PRISMA\updates` |
| rollbackRoot | `C:\ProgramData\PRISMA\rollback` |

Cada path resuelto debe incluir:

- `key`
- `resolvedPath`
- `source`
- `mode`
- `isWritable`
- `isCustomerData`
- `isDevOnly`

## 3. Runtime config boundary

Rutas:

- `docs/productization/PRISMA_RUNTIME_CONFIG_BOUNDARY_01.md`
- `docs/productization/PRISMA_RUNTIME_CONFIG_FIELD_CATALOG.md`
- `tooling/productization/schemas/runtime-config.schema.json`
- `tooling/productization/test-cases/runtime-config-boundary-cases.json`

Regla: runtime cliente vive fuera del repo. Rutas de desarrollo pueden existir, pero deben marcarse `devOnly` y no confundirse con cliente final.

## 4. Soporte y diagnósticos

Documento base: `docs/productization/PRISMA_SUPPORT_DIAGNOSTICS_CONTRACT.md`.

Permitido en bundle:

- versión instalada;
- resumen de plan/licencia;
- runtime mode;
- businessId/deviceId;
- estado sync/outbox;
- conteo de eventos pendientes;
- últimos errores sanitizados;
- estado general de DB;
- plugins instalados;
- checksums de configuración no secreta;
- rutas resueltas;
- health report local.

Prohibido:

- tokens, contraseñas, secretos, `.env` completo;
- datos bancarios;
- llaves privadas;
- dumps completos de DB;
- datos personales innecesarios;
- tarjetas o credenciales de proveedores;
- archivos arbitrarios del cliente.

## 5. Tooling global

| Área | Rutas | Función |
| --- | --- | --- |
| Dependency map | `tools/dependency_map/analyze_project.py` | Mapeo de dependencias cruzadas. |
| Visual OS | `tools/prisma-visual-os/*` | Generadores, gates, doctors, scorecards, live preview y verificadores. |
| Verticals | `tools/verticals/*` | Validadores de contratos, registry, data models, eventos/permisos, UX y fixtures. |
| Licensing | `tooling/licensing/*` | Firma, servidor mock/MVP, activación, dispatch, fixtures, scans y smoke cases. |
| Productization | `tooling/productization/*` | Schemas, examples, manifests, test cases, runtime boundary, support bundles. |

## 6. QA transversal confirmada

- Visual OS: gates 00A, 00D/00E, 00L/00M/00N, doctors 00U/00X/00Y, final stabilization 00ZF.
- Verticals: validadores 00A-00F.
- Licensing: signed license verification, state machine cases, tamper cases, activation matrices.
- Productization: schemas/test-cases para runtime config, support bundles, remote commands, plugins, messages, announcements.
- Prisma: `prisma/runtime-smoke.mjs` y seeds/migrations.

## 7. Release bundle y rollback

Reglas comunes del snapshot:

- Toda entrega relevante debe ser reversible y verificable.
- ZIP + installer `.py` aparece como modelo preferido para integraciones empaquetadas cuando el flujo pida paquete.
- El atlas no modifica código funcional existente.
- Para cambios runtime cliente, nunca confiar en rutas repo como destino final.

## 8. Fallos bloqueantes runtime

Bloquear arranque administrado si:

- runtimeMode no es válido;
- customer DB apunta al repo;
- businessId está vacío;
- license file apunta a ruta dentro de git;
- config contiene paths relativos ambiguos.

## 9. Pendientes de confirmar

- Owners humanos de runtime/productización.
- Relación final entre Local Agent futuro y Shared Core.
- Si los schemas de `tooling/productization/schemas/*` son todos contratos activos o algunos son fixtures/documentación de paquete.
