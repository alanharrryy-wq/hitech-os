# 04_PRODUCT_SKELETON_TEMPLATE.md

Este documento define el esqueleto canónico para **Forge Products**.  
Si un módulo no cabe en este esqueleto, no está listo para entrar al runtime limpio de ForgeOS.

## 1. Anatomía del producto

Todo Forge Product se compone de estas piezas:

1. **Identidad**
   - `product_id`
   - nombre
   - owner
   - package id
   - compatibilidad declarada

2. **Dominio**
   - reglas, entidades, invariantes y decisiones del producto

3. **Aplicación**
   - casos de uso y orquestación del producto

4. **Adapters**
   - puentes a IO, red, subprocess, storage, OS y serialización

5. **Contratos**
   - lifecycle, state, command, event y service contracts

6. **Integración con host**
   - contributions, activation bindings y permissions

7. **Vistas**
   - surfaces internas del producto dentro de slots aprobados

8. **Estado**
   - state authority, schemas, restore y migrations

9. **Packaging**
   - manifest, BOM, release notes, rollback, assets

10. **Gobierno**
   - ownership, dependencies, compatibility, error boundaries y teardown

## 2. Árbol canónico

```text
forge-product-<product_id>/
├─ PRODUCT_MANIFEST.json
├─ OWNERSHIP.md
├─ STATE_AUTHORITY.md
├─ LIFECYCLE.md
├─ DEPENDENCIES.md
├─ HOST_CONTRIBUTIONS.md
├─ PACKAGING.md
├─ COMPATIBILITY.md
├─ ERROR_BOUNDARIES.md
├─ TEARDOWN.md
├─ CONTRACT_INDEX.md
├─ domain/
├─ application/
├─ adapters/
│  ├─ inbound/
│  └─ outbound/
├─ contracts/
│  ├─ events/
│  ├─ commands/
│  ├─ state/
│  ├─ services/
│  └─ lifecycle/
├─ host_integration/
│  ├─ activation/
│  └─ contributions/
├─ views/
│  └─ surfaces/
├─ state/
│  ├─ schemas/
│  └─ migrations/
├─ packaging/
│  ├─ bom/
│  └─ release/
└─ docs/
   └─ README.md
```

`tests/` es altamente recomendado, pero no forma parte del mínimo obligatorio documental.  
El primer gate de arquitectura puede aceptarlo sin pruebas solo para scaffolding, no para migración real.

## 3. Carpetas obligatorias

| Carpeta | Propósito | Owner | Qué puede vivir ahí | Qué nunca debe vivir ahí | Dependencias permitidas | Dependencias prohibidas |
| --- | --- | --- | --- | --- | --- | --- |
| `domain/` | Modelo de dominio, invariantes, entities, value objects, policies puras | Owner del producto | Reglas de negocio, modelos de dominio, validaciones puras | Widgets, IO, subprocess, llamadas al host | módulos del mismo `domain/`, contratos locales inmutables | Kernel internals, Commons internals, otros productos |
| `application/` | Casos de uso y orquestación del producto | Owner del producto | use cases, coordinadores, presenters, handlers | UI toolkit concreto, service locator global | `domain/`, contratos locales, handles públicos de kernel/commons | host internals, views de otro producto |
| `adapters/` | Puentes a FS, red, subprocess, serialización, APIs externas | Owner del producto | repositorios, gateways, mappers, persistence adapters | lógica de negocio central | `application/`, contratos públicos | acceso lateral a otros productos |
| `contracts/` | Contratos públicos y locales del producto | Contract owner del producto | event, command, state, service, lifecycle contracts | implementaciones, widgets, stores | ninguno o referencias documentales | imports a internals |
| `host_integration/` | Bindings declarativos hacia el host | Owner del producto + review del kernel | manifests de contributions, activation bindings, permissions | lógica de negocio, acceso a internals del host | `contracts/`, `views/` entrypoints aprobados | controllers del host, main window |
| `views/` | Surfaces de UI del producto | Owner del producto | widgets, renderers, presenters visuales, layouts internos | service locator global, lógica de dominio central | `application/`, contratos locales, adapters de view | host internals, stores de otro producto |
| `state/` | Schemas, snapshots, migrations y store declarations del producto | State owner del producto | state declarations, migrations, restore policies | estado del host, stores de commons que no le pertenecen | `contracts/`, `application/`, `adapters/` de persistencia | QSettings directos del host, state de otro producto |
| `packaging/` | BOM, release notes, rollback y assets del paquete | Packaging owner del producto | manifests, BOM, notas de release, assets versionados | código de negocio | docs y manifests | dependencias runtime no declaradas |
| `docs/` | Documentación operativa del producto | Owner del producto | README, flujos, limitaciones, decisiones | código ejecutable | referencias a manifests y contracts | inventar comportamiento no declarado |

## 4. Documentos y manifests obligatorios

| Archivo | Propósito | Owner | Qué puede vivir ahí | Qué nunca debe vivir ahí | Dependencias permitidas | Dependencias prohibidas |
| --- | --- | --- | --- | --- | --- | --- |
| `PRODUCT_MANIFEST.json` | Identidad, entrypoints, permissions, dependencies y compatibilidad del producto | Packaging owner | Metadatos de producto y package | lógica ejecutable o comentarios ambiguos | kernel/commons public contracts | internals de host |
| `OWNERSHIP.md` | Quién es dueño de qué | Product owner | owners de dominio, contratos, estado, teardown, packaging | RACI vacío o roles sin nombre | ninguna | N/A |
| `STATE_AUTHORITY.md` | Mapa de state slices del producto | State owner | authority, stores, restore, migrate, purge | estado del host o de otro producto | contracts, state schemas | kernel stores no autorizados |
| `LIFECYCLE.md` | Estados oficiales del producto | Lifecycle owner del producto + kernel review | prepare, activate, suspend, fault, dispose | constructores mágicos como lifecycle | lifecycle contracts | lifecycle oculto |
| `DEPENDENCIES.md` | Dependencias declaradas y justificadas | Product owner | kernel APIs, commons capabilities, externals | dependencias fantasmas | manifest y contracts | otros productos |
| `HOST_CONTRIBUTIONS.md` | Contributions pedidas al host | Product owner + kernel review | slots, acciones, menus, status segments, permissions | manipulación directa de host internals | contribution contracts | controllers del host |
| `PACKAGING.md` | Cómo se empaca el producto | Packaging owner | assets, BOM, release, rollback, migration notes | lógica de negocio | package manifests | host internals |
| `COMPATIBILITY.md` | Rangos soportados | Packaging owner | kernel range, commons ranges, channels | promesas ambiguas | manifest y release data | suposiciones no declaradas |
| `ERROR_BOUNDARIES.md` | Contención de errores | Runtime owner del producto | error domains, degrade behavior, retry rules, evidence | swallow silencioso | observability hooks | errores del host ocultos |
| `TEARDOWN.md` | Secuencia de dispose | Runtime owner | subscriptions, workers, processes, stores, widgets | ‘el GC lo limpia’ | lifecycle y state docs | nada |
| `CONTRACT_INDEX.md` | Índice maestro de contratos del producto | Contract owner | lista de contratos, versiones, producers, consumers | contratos implícitos | contracts/ | N/A |
| `docs/README.md` | Descripción operativa del producto | Product owner | qué hace, qué no hace, boundaries | roadmap vacío | los demás docs del producto | contradecir manifests |

## 5. Manifiestos obligatorios

Todo producto debe incluir y mantener consistentes estos manifiestos:

- `PRODUCT_MANIFEST.json`
- `CONTRACT_INDEX.md`
- `HOST_CONTRIBUTIONS.md`
- `COMPATIBILITY.md`
- `PACKAGING.md`

Y debe alinear esos documentos con:

- contracts reales dentro de `contracts/`
- packaging artifacts dentro de `packaging/`
- ownership real declarado en `OWNERSHIP.md`

## 6. Contratos obligatorios

Un producto no entra a ForgeOS sin estos contratos mínimos:

1. **Lifecycle contract**
   - para prepare, activate, suspend y dispose

2. **State contract**
   - aunque el producto declare “sin persistencia”, debe explicitar su política

3. **Contribution contract**
   - para cualquier slot, acción o status segment que el host renderice

4. **Compatibility contract**
   - para declarar rangos de kernel y commons

5. **Packaging contract**
   - para que install/upgrade/rollback no sean magia negra

### Contratos opcionales según el caso
- command contracts
- event contracts
- capability service contracts
- published context contracts

## 7. Puntos de integración obligatorios

Todo producto debe declarar, como mínimo:

- cómo se activa;
- qué slots de host solicita;
- qué capabilities de Commons consume;
- qué published context expone;
- qué permissions necesita;
- cómo degrada;
- cómo se destruye.

## 8. Archivo obligatorio de lifecycle

`LIFECYCLE.md` debe responder sin rodeos:

- estados del producto;
- autoridad de cada transición;
- triggers válidos;
- qué se conserva en `suspend`;
- qué se purga en `dispose`;
- qué ocurre en `fault`;
- cómo se restaura un snapshot compatible.

## 9. Archivo obligatorio de ownership

`OWNERSHIP.md` debe nombrar al menos:

- product owner;
- contract owner;
- state owner;
- runtime owner;
- packaging owner.

No se aceptan documentos que digan solo “equipo X” sin aclarar responsabilidades.

## 10. Declaración obligatoria de dependencias

`DEPENDENCIES.md` debe listar:

- contratos públicos de kernel consumidos;
- capabilities de Commons consumidos;
- dependencies externas del runtime;
- dependencias opcionales;
- dependencias prohibidas de forma explícita.

Debe existir simetría entre `DEPENDENCIES.md` y `PRODUCT_MANIFEST.json`.

## 11. Declaración obligatoria de packaging

`PACKAGING.md` debe dejar claro:

- package id;
- assets incluidos;
- BOM;
- release channel;
- rollback unit;
- migraciones de estado si existen;
- uninstall expectations.

## 12. Declaración obligatoria de compatibilidad

`COMPATIBILITY.md` debe declarar:

- rango soportado de Forge Kernel;
- capabilities de Commons requeridos y sus rangos;
- release channels permitidos;
- incompatibilidades conocidas;
- comportamiento ante missing capability.

## 13. Declaración obligatoria de error boundary

`ERROR_BOUNDARIES.md` debe cubrir:

- errores del dominio;
- errores de integración;
- errores de IO;
- timeouts;
- degradación visible;
- evidence log requerido;
- condiciones de fault.

## 14. Declaración obligatoria de estado

`STATE_AUTHORITY.md` debe incluir por cada slice:

- nombre;
- owner;
- storage;
- readers;
- writers;
- schema version;
- restore policy;
- purge policy;
- teardown implication.

## 15. Declaración obligatoria de teardown

`TEARDOWN.md` debe cubrir todos los recursos vivos:

- subscriptions;
- background tasks;
- subprocesses;
- sockets o handles externos;
- stores abiertos;
- surfaces y bindings de view;
- caches temporales.

## 16. Minimum viable product module

Un **MVP module** de Forge Product debe tener:

- `PRODUCT_MANIFEST.json`
- `OWNERSHIP.md`
- `STATE_AUTHORITY.md`
- `LIFECYCLE.md`
- `DEPENDENCIES.md`
- `HOST_CONTRIBUTIONS.md`
- `COMPATIBILITY.md`
- `ERROR_BOUNDARIES.md`
- `TEARDOWN.md`
- `CONTRACT_INDEX.md`
- al menos una surface en `views/surfaces/`
- al menos un lifecycle contract
- cero accesos a internals del host
- cero dependencias hacia otros productos

### Lo que sí se permite en el MVP
- una sola surface principal;
- sin persistencia compleja;
- published context mínimo;
- sin capabilities opcionales.

### Lo que no se permite ni en el MVP
- service locator global;
- inferir contracts por nombres de archivos;
- state en widgets;
- lifecycle escondido en constructores.

## 17. Full product module

Un **full product module** añade sobre el MVP:

- múltiples surfaces o contribution types;
- state migrations;
- command/event/service contracts adicionales;
- policies de degradación;
- observability fina;
- assets de packaging completos;
- release notes y rollback plan;
- pruebas de boundaries;
- published contexts múltiples si están justificados.

## 18. Checklist de extracción de un tool legacy embebido a Forge Product limpio

1. Nombrar `product_id`, owner y package id.
2. Delimitar qué parte del legado es dominio del producto y qué parte es host accidental.
3. Crear `PRODUCT_MANIFEST.json`.
4. Crear `OWNERSHIP.md` y `STATE_AUTHORITY.md`.
5. Enumerar todo acceso actual a `main_window`, `self.main`, `service_container` y event strings.
6. Convertir esos accesos en:
   - contracts de kernel;
   - capability service contracts;
   - published context contracts;
   - adapters locales.
7. Mover UI del producto a `views/`.
8. Mover reglas del producto a `domain/` y `application/`.
9. Definir `ERROR_BOUNDARIES.md`.
10. Definir `TEARDOWN.md`.
11. Reescribir contributions hacia `HOST_CONTRIBUTIONS.md`.
12. Declarar compatibilidad y packaging.
13. Eliminar cualquier scraping del host.
14. Pasar gates de boundary, state ownership y teardown antes de activar el producto en el host.

## 19. Regla de oro del skeleton

Un Forge Product existe para **encapsular** dominio y no para **infectar** el host.  
Si al llenar este skeleton alguien necesita “un acceso directo al host nada más para esta parte”, la extracción está mal hecha.
