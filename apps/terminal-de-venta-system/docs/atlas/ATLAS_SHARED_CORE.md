<!-- Generated from ATLAS_CHAT_SHARED_CORE.zip on 2026-05-08. Do not treat this as source code. -->


# ATLAS_SHARED_CORE

Estado: atlas inicial mejorado, trazable y listo para validación coordinada.
App: `shared`.
Raíz documental esperada: `docs/atlas`.
Fuente única usada: `ATLAS_CHAT_SHARED_CORE.zip`.

## Propósito

`ATLAS_SHARED_CORE` documenta la capa común que cambia el comportamiento de Mobile, Tablet y PC sin pertenecer por completo a ninguna de esas apps. Es el mapa de drenaje, gas y luz del edificio: cuando alguien toca una válvula compartida, no basta con mirar el departamento donde salió la fuga.

El atlas está diseñado para responder, por cada intención de cambio:

1. Qué quiere cambiar alguien en lenguaje humano.
2. Qué rutas compartidas toca.
3. Qué rutas consumidoras deben revisarse primero.
4. Qué verificadores o QA confirman el cambio.
5. Qué dependencias cruzadas hay.
6. Qué rollback aplica.
7. Qué incertidumbre sigue abierta.


## Alcance y anti-alcance

| Clasificación | Incluido en Shared Core | No incluido aquí |
|---|---|---|
| Contratos | API, error envelope, eventos, sync, permisos/auditoría, UI state, screen, schema compatibility, vertical contracts | Implementación local de pantallas Tablet, PC o Mobile |
| Visual OS | Tokens, componentes compartidos, control plane, presets, layers, release gates, QA cross-surface | Rediseño interno de una pantalla puntual |
| Datos | Prisma root/backoffice, compatibilidad de schema, seeds, migraciones, tri-db status/bridge evidence | Queries específicas de una app salvo como consumidores documentados |
| Motores | Licensing, feature gates, plan catalog, signed license, local store, twin-kernel, vertical registry, validation fixtures | Lógica de caja o backoffice que pertenezca a un producto individual |
| Runtime común | Modos runtime, paths policy, release/support/productization contracts, herramientas globales | Launchers locales no compartidos o parches temporales |

Regla madre confirmada en `shared/README.md`, `packages/shared-kernel/README.md` y docs de arquitectura:

```text
Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.
```



## Evidencia base usada

| Fuente dentro del ZIP | Uso en este atlas |
|---|---|
| `README_PACKAGE.md` | Regla de oro: cada entrada debe mapear intención humana, rutas, dependencias, verificación y rollback. |
| `START_HERE_PROMPT.md` | Alcance de Shared Core: `shared/*`, `packages/shared-kernel/*`, `products/shared-ui/*`, `config/prisma-visual-os/*`, `styles/prisma-visual-os/*`, `prisma/*`, docs globales, herramientas y `analysis/all_app_shared_dependency_hits.json`. |
| `EXPECTED_OUTPUTS.md` | Lista canónica de archivos de atlas esperados. |
| `VERIFICATION_SHARED_ATLAS_NEEDED.md` | Justificación formal de por qué Shared Core necesita atlas propio. |
| `analysis/*_inventory.csv` | Inventario de raíces compartidas seleccionadas. |
| `analysis/all_app_shared_dependency_hits.json` | 109 referencias cruzadas desde mobile, tablet y PC hacia recursos compartidos. |
| `source_snapshot/**` | Snapshot documental y de contratos usado como única evidencia técnica. |

### Conteo de cobertura del paquete

| Área | Conteo confirmado |
|---|---:|
| Archivos totales en ZIP | 693 |
| `shared` inventariado | 153 |
| `packages` inventariado | 1 |
| `products/shared-ui` inventariado | 17 |
| `config/prisma-visual-os` inventariado | 13 |
| `styles/prisma-visual-os` inventariado | 3 |
| `prisma` inventariado | 8 |
| Dependencias cruzadas detectadas | 109 |

### Dependencias cruzadas por app

| App | Hits hacia Shared Core |
|---|---:|
| Mobile | 10 |
| Tablet | 58 |
| PC | 41 |


## Mapa ejecutivo de Shared Core

| Bloque | Rutas fuente | Responsabilidad compartida | Riesgo de cambio |
|---|---|---|---|
| Shared contracts | `shared/contracts/**`, `docs/contracts/**` | Envelopes API, errores, eventos, sync, permisos, UI state, schema compatibility y contratos verticales | Crítico: cambia semántica para apps consumidoras |
| Shared Kernel | `packages/shared-kernel/**`, `shared/twin-kernel/**`, `docs/architecture/SHARED_KERNEL_CONTRACT.md` | Identidad compartida, naming, eventos, sync contracts, registry/capabilities y regla twin | Alto/crítico: puede crear drift entre Tablet y PC |
| Visual OS | `products/shared-ui/prisma/**`, `config/prisma-visual-os/**`, `styles/prisma-visual-os/**`, `docs/design/PRISMA_VISUAL_OS_*` | Tokens, componentes, layers, presets, control plane, release gates y QA visual tri-superficie | Alto: tokens compartidos impactan Mobile, Tablet y PC |
| Prisma / DB global | `prisma/**`, `shared/tri-db/status.latest.json`, `docs/architecture/PRISMA_SCHEMA_OWNERSHIP.md` | Schema canónico/backoffice, migraciones, seeds, smoke, evidencia de bridge tri-db | Alto: afecta consolidación, sync, migraciones y reportes |
| Licensing | `shared/licensing/**`, `tooling/licensing/**`, docs productization de license | Planes, feature gates, estado local, firma, refresh, fixtures y operación de licencia | Alto: puede bloquear o permitir funciones incorrectamente |
| Productization/runtime | `docs/productization/**`, `tooling/productization/**` | Runtime config, support bundles, remote ops, customer runtime, schemas y test cases | Medio/alto: afecta distribución, soporte y seguridad |
| Verticals | `shared/verticals/**`, `tools/verticals/**`, `docs/architecture/PRISMA_VERTICALS_*` | Registry, profiles, capabilities, permisos, eventos, modelos, UX y fixtures por vertical | Alto: cambios mal clasificados contaminan core POS |

## Dependencias cruzadas confirmadas

`analysis/all_app_shared_dependency_hits.json` confirma 109 referencias desde apps hacia Shared Core.

| Dependencia compartida | Hits detectados | Lectura del riesgo |
|---|---:|---|
| `shared/licensing` | 14 | Tablet y PC consumen tipos/estado/resolución de licencia; cambios deben validar continuidad de venta básica. |
| `shared/twin-kernel` / `packages/shared-kernel` | 23 | Identidad, capability y sync pueden cambiar paridad operativa; requiere regla twin. |
| `prisma/*` | 23 | Prisma aparece como eje de schema, seeds, migrations o runtime; no sustituye contratos. |
| `styles/prisma-visual-os/*` | 12 | CSS generado/layers se importa en superficies; drift visual puede ser tri-superficie. |
| `config/prisma-visual-os/*` | 4 | Control plane y guardrails bloquean o habilitan releases visuales. |
| `products/shared-ui/prisma/visual-os/*` | 5 | Presets, QA matrix y release gate gobiernan cambios visuales. |
| `products/shared-ui/prisma/tokens` | 3 | Tokens canónicos compartidos; no usar colores sueltos si existe token. |
| `products/shared-ui/prisma/components` | 3 | Componentes declarativos compartidos por `data-prisma-component`. |
| `shared/tri-db` | 5 | PC lee estado bridge; no debe convertirse en ruta mágica para venta local. |

## Principios operativos confirmados

1. **Shared no es utilería genérica.** `shared/README.md` y `SHARED_KERNEL_CONTRACT.md` prohíben helpers locales, queries específicas, UI específica, lógica touch POS, backoffice logic y parches temporales.
2. **Tablet vende sola.** `RUNTIME_MODES_CONTRACT.md` define `standalone`, `managed` y `degraded_managed`; en todos los casos la venta básica local no debe bloquearse por ausencia de PC/red.
3. **Eventos son verdad operacional.** `EVENT_CONTRACT.md` y `sync-event-contract.v1.json` fijan topics, envelope, outbox states y conflict codes.
4. **PC gobierna cuando existe.** PC es backoffice/control tower, especialmente para catálogo avanzado, auditoría, compras, receiving, reconciliación y gobierno.
5. **Visual OS gobierna identidad y QA, no negocio.** Los contratos 00A, 00D/00E, 00J/00K y 00L/00M/00N declaran dependencia, release gate y prohibiciones de payload.
6. **Prisma ordena datos, no reemplaza arquitectura.** `PRISMA_SCHEMA_OWNERSHIP.md` exige que cada cambio de schema responda módulo, pantalla, evento, permiso, offline, reporte y plugin.
7. **Licensing no mata venta básica.** `feature-resolver.ts` permite `BASIC_POS_FEATURES` en missing/invalid/suspended/revoked/expired mediante fallback policy, mientras bloquea funciones avanzadas.

## Matriz de intención humana a rutas

| ID | Intención humana | Inspeccionar primero | Normalmente toca | Verificar con | Riesgo |
|---|---|---|---|---|---|
| SC-CONTRACT-EVENTS | Cambiar o agregar evento compartido | `shared/contracts/sync-event-contract.v1.json`, `shared/contracts/event-contract.md`, `docs/contracts/EVENT_CONTRACT.md` | `shared/twin-kernel/src/sync/**`, vertical event policies, docs de sync | Validadores de vertical events/permissions y revisión de outbox conflict codes | Crítico |
| SC-CONTRACT-API | Ajustar formato de respuesta o error | `docs/contracts/API_RESPONSE_CONTRACT.md`, `shared/contracts/api-response-contract.md`, `shared/contracts/error-contract.md` | Docs contract, tipos compartidos si existen, pruebas API consumidoras | QA de aceptación y consumers Tablet/PC/Mobile | Alto |
| SC-SYNC-RUNTIME | Cambiar outbox, reconciliation o conflict states | `docs/contracts/SYNC_RECONCILIATION_CONTRACT.md`, `shared/contracts/sync-contract.md`, `sync-event-contract.v1.json` | `shared/twin-kernel/src/sync/**`, tri-db evidence, docs runtime | Sync validators, tri-db status, pruebas offline/degraded | Crítico |
| SC-VISUAL-TOKENS | Cambiar tokens Visual OS o theme | `products/shared-ui/prisma/README.md`, `GOLDEN_VISUAL_SPEC.md`, `products/shared-ui/prisma/tokens/prisma-theme.css` | `styles/prisma-visual-os/**`, `config/prisma-visual-os/**` | Visual OS release gate 00N, cross-surface QA 00L | Alto |
| SC-VISUAL-PRESET | Ajustar preset o control plane | `prisma-visual-os.controls.json`, `presets.json`, `prisma-visual-controls.active.json` | Config active controls, generated CSS, docs design | `verify_prisma_visual_os_core_00d_00e.mjs`, release gate | Alto |
| SC-LICENSE-GATE | Cambiar planes, permisos comerciales o feature gates | `shared/licensing/plan-catalog.ts`, `feature-keys.ts`, `feature-resolver.ts` | `license-gate.ts`, fixtures, docs productization | License resolution matrix, verify signed license, pro readiness | Alto |
| SC-PRISMA-SCHEMA | Cambiar modelo canónico o migración | `prisma/schema.prisma`, `PRISMA_SCHEMA_OWNERSHIP.md`, migration SQL | Prisma migration/seed/smoke, schema compatibility contract | `prisma/runtime-smoke.mjs`, backups, migration validation | Crítico |
| SC-VERTICALS | Agregar/editar vertical | `shared/verticals/registry/vertical-registry.v0.json`, profiles, contracts | vertical manifests, data extensions, event/permission policies, validation fixtures | `tools/verticals/validate_vertical_*` | Alto |
| SC-PRODUCTIZATION | Cambiar runtime config, support bundle o remote ops | `docs/productization/**`, `tooling/productization/schemas/**` | schemas, fixtures, test cases, manifests | contract casebooks and schema validation | Medio/alto |

## Archivos de atlas generados

| Archivo | Rol |
|---|---|
| `docs/atlas/ATLAS_SHARED_CORE.md` | Vista ejecutiva, scope, dependencias cruzadas e intención humana. |
| `docs/atlas/ATLAS_SHARED_CORE_CONTRACTS.md` | Contratos compartidos, canon machine-readable y reglas de cambio. |
| `docs/atlas/ATLAS_SHARED_CORE_VISUAL_OS.md` | Visual OS, shared UI, tokens, presets, release gate y QA visual. |
| `docs/atlas/ATLAS_SHARED_CORE_FUNCTIONAL_ENGINES.md` | Licensing, twin-kernel, verticals, tri-db y motores comunes. |
| `docs/atlas/ATLAS_SHARED_CORE_RUNTIME_INFRA.md` | Runtime modes, Prisma/global DB, productization, tools y rollback. |
| `docs/atlas/atlas.shared-core.json` | Fuente estructurada inicial para automatización. |
| `docs/atlas/ATLAS_MASTER_INDEX.md` | Borrador coordinador para Mobile/Tablet/PC/Shared. |
| `docs/atlas/atlas.registry.json` | Registro inicial de atlas y ownership por dominio. |


## Niveles de certeza usados

| Nivel | Significado |
|---|---|
| Confirmado | El ZIP contiene archivo, inventario o contrato explícito que sostiene la afirmación. |
| Inferido desde evidencia | La relación aparece por imports, rutas, manifests o docs, pero falta ownership formal o runtime final. |
| Pendiente de confirmar | El ZIP menciona el tema, pero no trae suficiente evidencia para cerrar owner, estado final o comando definitivo. |

Este atlas evita inventar rutas. Cuando una ruta no existe en el ZIP, queda fuera o marcada como pendiente. Mejor una duda honesta que una brújula pintada con marcador.


## Rollback general

- Cambios documentales del atlas: revertir los archivos `docs/atlas/**` agregados por este paquete.
- Cambios reales futuros en Shared Core: revertir el paquete/commit que modificó rutas compartidas y re-ejecutar verificadores de la superficie afectada.
- Visual OS: restaurar `config/prisma-visual-os/prisma-visual-controls.active.json`, regenerar CSS y correr release gate.
- Prisma/schema: rollback sólo con backup, migración inversa o snapshot validado; no borrar datos a ciegas.
- Licensing: restaurar fixtures/catálogos previos y correr matrices de resolución antes de liberar.

## Pendientes principales

Los pendientes completos están en `meta/OPEN_QUESTIONS.md`. Los más importantes son:

1. Confirmar ownership final por dominio: Visual OS, licensing, Prisma schema, verticals y runtime productization.
2. Confirmar comandos oficiales finales para cada verificador, porque varios docs contienen rutas Windows con caracteres de escape dañados.
3. Validar `ATLAS_MASTER_INDEX.md` contra los atlas Mobile, Tablet y PC cuando existan.
4. Confirmar si el naming canónico debe usar `CashSession` o `Shift` en todos los contratos, porque hay divergencia documental.
