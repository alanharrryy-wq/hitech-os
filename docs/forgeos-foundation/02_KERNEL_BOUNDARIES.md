# 02_KERNEL_BOUNDARIES.md

## Definición formal del kernel

**Forge Kernel** es la capa que gobierna la plataforma sin cargar semántica de producto.  
Su trabajo es ordenar el runtime, no opinar sobre el dominio de cada producto.

## Kernel scope

Forge Kernel incluye exclusivamente:

- bootstrap del proceso y de la sesión;
- contract runtime y validación contractual;
- lifecycle authority;
- session state del host;
- host shell domain-agnostic;
- extension registry y activation gates;
- capability broker;
- observability y fault isolation;
- packaging y compatibility gates;
- políticas de timeout y shutdown del runtime.

## Responsabilidades del kernel

1. Descubrir paquetes instalados y validar compatibilidad.
2. Registrar contracts, contributions y permissions.
3. Activar, suspender, reanudar y disponer products/capabilities.
4. Renderizar contributions aprobadas en extension points declaradas.
5. Mantener el estado de sesión del host y del layout global.
6. Enrutar commands y events contractuales.
7. Aislar fallas, aplicar timeouts y cerrar recursos.
8. Proveer telemetría estructurada del sistema.

## Lo que está explícitamente excluido del kernel

- lógica de dominio de productos;
- stores de dominio de productos;
- heurísticas por nombre de producto;
- semántica de Cloudflare, Orchestrator o Repo Analyzer;
- pipelines de negocio;
- payloads de proceso con semántica de un producto;
- configuración interna de productos;
- reportes con lenguaje específico de un dominio.

## Servicios del kernel

| Servicio kernel | Propósito | Inputs | Outputs | No puede hacer |
| --- | --- | --- | --- | --- |
| Bootstrap Orchestrator | Levantar sesión ForgeOS y ordenar boot | manifests, config runtime, release metadata | sesión activa | cargar lógica de dominio |
| Lifecycle Authority | Gobernar activate/suspend/dispose | lifecycle contracts | estados y transiciones oficiales | delegar lifecycle a constructores |
| Contract Runtime | Validar y enrutar contratos | contract registry, envelopes | dispatch validado | aceptar payloads no versionados |
| State Authority Registry | Asignar ownership y store por state slice | state declarations | source-of-truth map | mezclar estado de capas |
| Extension Registry | Registrar contributions y extension points | product manifests, contribution contracts | slots y bindings aprobados | derivar tool IDs por string hacks |
| Capability Broker | Entregar handles a commons y validar permisos | service contracts, permissions | handles controlados | funcionar como service locator global |
| Host Shell Runtime | Administrar slots, layout y chrome | contributions válidas | surfaces renderizadas | contener lógica de producto |
| Observability Runtime | Trazar eventos, comandos, errores y latencias | todos los contratos críticos | logs y métricas estructuradas | silenciar fallas de frontera |
| Packaging Gate | Validar instalación/activación/rollback | package manifests, compatibility contracts | decisión installable/no installable | asumir compatibilidad implícita |

## Autoridad de lifecycle

La autoridad de lifecycle pertenece a Forge Kernel y no se delega a:

- constructores;
- callbacks de UI;
- side effects de import;
- watchers casuales;
- el cierre del proceso del OS.

### El kernel decide
- cuándo un producto pasa de `registered` a `prepared`;
- cuándo una capability puede servir requests;
- cuándo una surface puede unirse a un slot;
- cuándo suspender un producto inactivo;
- cuándo forzar teardown por falla o incompatibilidad.

### El kernel exige
- contractos lifecycle por paquete;
- teardown declarativo;
- timeout policy para tareas y procesos;
- evidence log de dispose.

## Autoridad de estado

Forge Kernel solo es autoridad de:

- estado de sesión de plataforma;
- layout del host;
- registro de paquetes instalados;
- compatibilidad resuelta del runtime;
- permisos concedidos a packages;
- health/fault state del runtime.

Forge Kernel **no** es autoridad de:

- índice de repositorio;
- queries, preview, bookmarks y navegación de Repo Analyzer;
- contexto Cloudflare;
- run payloads del Orchestrator;
- historial de dominio de un producto.

## Autoridad de persistencia

### El kernel puede persistir
- sesión y layout del host;
- registry de paquetes instalados;
- compatibility resolution cache;
- fault ledger del runtime;
- configuración global mínima de plataforma.

### El kernel no puede persistir
- state slices de dominio de productos;
- configuración interna de capabilities que no le pertenecen;
- caches o snapshots privados de productos;
- reportes de producto en stores globales.

## Autoridad de extensiones

Forge Kernel es dueño del pipeline de extensibilidad:

1. descubrir paquete;
2. leer manifest;
3. validar compatibilidad;
4. validar permissions;
5. validar contributions y contratos;
6. registrar package;
7. preparar package;
8. activar package;
9. suspender o disponer package.

Un producto no puede auto-insertarse en el host sin pasar por ese pipeline.

## Autoridad de eventing

Forge Kernel gobierna el spine de eventos del sistema, pero bajo estas reglas:

- todo evento cross-layer tiene contract id, family, version y owner;
- todo payload se valida antes de publicarse;
- todo subscriber es conocido por registry o wiring explícito;
- todo evento relevante deja correlation id y resultado observable;
- los strings libres no son contratos.

## Política de aislamiento de fallas

- Una falla de producto degrada o faulta al producto, no al kernel.
- Una falla de capability degrada el capability y notifica a sus consumidores; no tumba la sesión completa salvo que sea capability obligatoria del boot.
- El host shell debe poder seguir vivo con cero productos activos.
- Los timeouts de procesos y tareas background se resuelven con kill/dispose explícito.
- Los errores de frontera deben generar evidence log. Silenciarlos es incumplimiento.

## Política de observabilidad

Toda interacción crítica debe registrar al menos:

- `contract_id`
- `version`
- `producer`
- `consumer`
- `owner`
- `correlation_id`
- `started_at`
- `ended_at`
- `outcome`
- `duration_ms`
- `failure_code` si aplica

No se acepta observabilidad basada solo en prints dispersos o snapshots oportunistas.

## Qué puede saber el kernel sobre los productos

El kernel puede conocer únicamente:

- `product_id`
- nombre y versión declarados;
- package type;
- compatibility ranges;
- permissions solicitados;
- contributions declaradas;
- lifecycle contracts;
- contracts públicos del producto;
- published context que el producto decida exponer.

El kernel no puede conocer:

- campos internos del state del producto;
- widgets privados del producto;
- stores internos del producto;
- rutas de archivos privadas del producto;
- reglas de negocio;
- strings de branching del producto;
- categorías, grupos o iconos inferidos por heurística.

## Qué pueden pedir los productos al kernel

Los productos pueden pedir al kernel únicamente:

- activación/suspensión/disposal según lifecycle contracts;
- registro de contributions;
- access handles a capabilities autorizadas;
- estado de sesión del host permitido por contrato;
- command routing y event publication contractuales;
- packaging/compatibility checks;
- observability hooks.

Los productos **no** pueden pedir al kernel:

- un puntero al main window;
- acceso directo a controllers del host;
- acceso directo al store de otro producto;
- bypass de validación contractual;
- creación de extension points no declaradas;
- permisos ocultos.

## Boundary matrix

| Desde | Hacia | Permitido | Mecanismo | Comentario |
| --- | --- | --- | --- | --- |
| Forge Kernel | Forge Kernel | Sí | APIs internas del kernel | La implementación interna puede acoplarse solo al kernel. |
| Forge Kernel | Forge Commons | Sí, pero solo vía interfaces/contratos de capability | Service contracts declarados | Sin importar módulos product-specific ni semántica de capability. |
| Forge Kernel | Forge Products | No directo | Solo discovery, manifests y lifecycle contracts | El kernel no importa lógica de dominio del producto. |
| Forge Commons | Forge Kernel | Sí | Kernel contracts y abstracciones públicas | Nunca por internals privados. |
| Forge Commons | Forge Commons | Sí, con declaración explícita | Service contracts versionados | Evitar cadenas de dependencias largas. |
| Forge Commons | Forge Products | No | N/A | Un capability no conoce productos concretos. |
| Forge Products | Forge Kernel | Sí | Lifecycle, contribution, state, command, event, capability broker | Siempre mediante contratos declarados. |
| Forge Products | Forge Commons | Sí | Capability service contracts | Nunca por imports a internals privados del capability. |
| Forge Products | Forge Products | No | N/A | Cero llamadas laterales; solo intercambio mediado por kernel/commons si se aprueba. |
| Cualquier capa | Runtime externo / OS / red / FS | Sí, solo desde adapters declarados | Adapters y permissions | Nada de side effects escondidos en domain/application. |

## Imports/dependencias permitidos por capa

| Capa | Dependencias permitidas | Dependencias prohibidas | Racional |
| --- | --- | --- | --- |
| Kernel | Solo módulos kernel, abstracciones del runtime/UI, manifiestos de paquete, observabilidad base | Productos, nombres de producto, contratos privados de commons, stores de dominio | Kernel debe compilar/vivir sin ningún producto instalado. |
| Commons | Kernel public APIs, propios módulos, otros commons aprobados | Productos, host internals, widgets o semántica de producto | Commons solo expone capabilities neutrales. |
| Products | Kernel public APIs, commons contratados, propios módulos | Otros productos, host internals, stores de kernel | Todo acceso cross-layer es contractual. |
| Adapters | OS, red, FS, subprocess, serialización, APIs externas | Domain/application de otra capa | Los side effects viven aquí. |
| Domain | Solo domain y contratos locales | UI, host, OS, network, kernel internals | Domain debe seguir seco y portable. |
| Views | Application presenters, contratos de host_contribution | Service container global, estado de otro producto | La view no es service locator. |

## Dependencias prohibidas por capa

| Capa | Patrón prohibido | Ejemplo legacy | Motivo |
| --- | --- | --- | --- |
| Kernel | Branching por nombre de producto | `ShellGroupRuntime` y `ToolCatalogService` contienen `cloudflare_guardian` y `orchestrator_bridge` | Contamina el host |
| Kernel | Contexto global con campos de producto | `WorkstationContext` incluye datos Cloudflare | Rompe host agnostic |
| Commons | Dependencia hacia producto | Promover `guardian_contract.py` o payloads Orchestrator a Commons | Smuggling de semántica de producto |
| Products | Leer internals del host | `cloudflare_guardian/state_adapter.py` raspa `main_window` | Hidden coupling |
| Products | Mutar stores de kernel sin contrato | escribir layout/estado host por acceso directo | Autoridad rota |
| Cualquier capa | Service locator string-based como superficie oficial | `ServiceContainer.get('main_window')` | No hay contrato real |

## Ejemplos de interacción aceptable vs prohibida

### Aceptable
- Un producto solicita ejecución de proceso mediante `forge.commons.process_execution.execute.v1.service`.
- Un producto publica un resumen de contexto mediante un `published context contract` aprobado.
- El host renderiza una surface en `primary.workspace.surface` porque el producto la declaró en `HOST_CONTRIBUTIONS`.
- El kernel suspende un producto inactivo y conserva su state solo si el producto declaró restore policy.

### Prohibida
- El producto pide `main_window` al container y manipula docks del host.
- El kernel decide que un grupo es “graph” porque el tool id contiene `cloudflare`.
- Una capability compartida guarda payloads con semántica de Cloudflare o Orchestrator dentro de su schema público.
- Un producto escribe en el store de layout del host para forzar chrome o focus.
- Un producto llama directo a otro producto para pedirle datos.

## Regla de cierre

Si una decisión necesita que el kernel “sepa demasiado” sobre un producto, la decisión es inválida.  
Si un producto necesita “asomarse” a internals del host para funcionar, el contrato está mal definido.
