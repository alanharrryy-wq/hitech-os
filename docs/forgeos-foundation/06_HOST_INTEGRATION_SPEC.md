# 06_HOST_INTEGRATION_SPEC.md

## Propósito

Definir cómo un producto se integra con el host sin contaminarlo.

El host de ForgeOS es parte de Forge Kernel.  
Su responsabilidad es **alojar, gobernar y aislar**.  
Su responsabilidad no es **contener lógica de dominio**.

## Principio rector

El producto se conecta al host por contratos y contributions declaradas.  
Nunca por reach-through a internals del host.

## Extension points oficiales del host

| Extension point | Tipo | Owner | Qué aporta el producto | Qué entrega el host | Límites |
| --- | --- | --- | --- | --- | --- |
| `primary.workspace.surface` | Surface principal | Host shell | entrypoint visual del producto | slot, lifecycle, focus, suspensión | una surface no cambia el chrome global |
| `secondary.panel.surface` | Surface secundaria | Host shell | panel contextual o auxiliar | slot lateral/inferior aprobado | el producto no crea docks arbitrarios |
| `toolbar.action` | Acción de host | Host shell | acción declarada | render, enable/disable, route | sin callbacks ocultos al host |
| `menu.action` | Acción de menú | Host shell | acción declarada | ubicación aprobada | sin crear menús fuera del árbol permitido |
| `status.segment` | Segmento de estado | Host shell | published context resumido | render compacto y política de refresh | sin apropiarse del status global |
| `background.agent` | Runtime no visual | Kernel lifecycle | task handler o worker entrypoint | supervisor, timeout, observabilidad | no crea loops huérfanos |

## Modelo de contribuciones

Una contribution válida debe declarar:

- `product_id`
- `contribution_id`
- `extension_point`
- `surface_or_action_type`
- `activation_policy`
- `visibility_policy`
- `permissions`
- `compatibility_range`
- `error_boundary_ref`
- `teardown_ref`

### Reglas
- El host no deduce nada de `contribution_id`.
- El producto no puede usar la contribution para tocar internals del host.
- Toda contribution se valida antes de bindearse al slot.
- El host puede rechazar, degradar o diferir una contribution incompatible.

## Modelo de registro

### Secuencia oficial
1. El kernel descubre el paquete del producto.
2. Lee `PRODUCT_MANIFEST.json`.
3. Valida compatibilidad.
4. Valida permissions.
5. Registra los contracts públicos del producto.
6. Registra las contributions declaradas.
7. Prepara el producto.
8. Solo después puede activar surfaces o actions.

### Regla
Registro no equivale a activación.  
Activación no equivale a visibilidad.

## Modelo de activación

La activación del producto se da por lifecycle contract:

- `prepare`
- `activate`
- `suspend`
- `resume`
- `fault`
- `dispose`

### Reglas de activación
- El host no activa productos por side effect de render.
- El producto no se auto-activa desde el constructor.
- La primera activación debe pasar compatibilidad, permissions y contract validation.
- El host puede mantener productos registrados pero no activos.
- El host puede requerir `prepare` previo para surfaces costosas.

## Modelo de suspensión

Suspensión significa:

- conservar state declarado como preservable;
- liberar recursos no esenciales;
- detener tasks o streams no necesarios;
- mantener la capacidad de reactivar sin reinstalar.

### Suspensión no significa
- ocultar widgets y dejar procesos vivos;
- dejar subscriptions colgando;
- conservar handles externos sin policy;
- asumir que el GC resolverá el resto.

## Modelo de disposal

Dispose es obligatorio y explícito.

### Dispose mínimo
- remover subscriptions;
- detener background tasks;
- matar/reap subprocesses;
- flush/close stores del producto;
- unbind de surfaces del host;
- limpiar caches temporales;
- emitir evidence log de teardown.

### Dispose no es opcional en:
- shutdown del runtime;
- uninstall;
- incompatibilidad detectada;
- fault irrecoverable.

## Reglas de sincronización de estado

### El host puede sincronizar
- estado de activación del producto;
- presencia/ausencia de contributions;
- layout/slot binding;
- published context mínimo aprobado;
- health state resumido.

### El host no puede sincronizar
- state de dominio interno;
- formularios internos;
- caches privadas del producto;
- stores locales del producto;
- contexto de negocio no publicado por contrato.

### Regla clave
Si el host necesita leer un dato del producto, ese dato debe existir como:
- published context contract; o
- capability/service contract aprobado.

No por lectura directa de atributos o widgets.

## Reglas de command routing

- Todo command del host al producto usa command contract.
- Toda acción de toolbar/menu se resuelve a command id declarado.
- El host no llama callbacks arbitrarios del producto sin envolverlos en routing y observabilidad.
- El producto no registra commands por string suelto fuera de su contract index.
- Un command puede tener timeout, permission gate y idempotency key según el caso.

## Permissions / policy gates

Todo producto debe declarar qué necesita:

- filesystem read
- filesystem write
- network access
- process execution
- export artifacts
- long-running background agent
- status publishing
- privileged host slots si existieran

### Reglas
- Lo no declarado se niega.
- Lo declarado se revisa.
- Lo concedido se registra.
- Lo usado se observa.

## Reglas de review de contributions

Una contribution se rechaza si:

- introduce lógica de dominio en el host;
- intenta modificar el chrome global fuera de políticas aprobadas;
- requiere acceso directo a internals del host;
- introduce permisos no declarados;
- depende de nombres de producto para comportarse;
- no trae error boundary ni teardown asociado;
- no declara compatibilidad.

## Aislamiento de errores

- Una surface de producto puede faultar sin cerrar el host.
- Un toolbar action defectuoso puede deshabilitarse sin tumbar el menú entero.
- Un background agent defectuoso puede cancelarse y faultar el producto.
- El host debe mostrar degradación estructurada, no stack traces sin control.
- Los errores de integración deben registrarse con `product_id`, `contribution_id`, `contract_id` y `correlation_id`.

## Reglas para timeouts y runaway processes

- Toda tarea background debe tener timeout.
- Todo subprocess debe tener:
  - spawn timeout;
  - run timeout;
  - kill-after-timeout policy;
  - reap confirmation.
- Los procesos externos solo pueden correr desde capabilities o adapters autorizados.
- Un producto no puede lanzar procesos sin pasar por la capability de process execution cuando esa capacidad exista en el runtime.

## Límites de integración UI

### El host es dueño de
- frame y chrome global;
- slots y layout;
- navegación de shell;
- policies de focus;
- show/hide/suspend/dispose de surfaces;
- status global;
- menú y toolbar como contenedores.

### El producto es dueño de
- contenido dentro de su surface;
- estado visual interno;
- componentes internos;
- lógica de presentación propia;
- published context deliberado.

### El producto nunca es dueño de
- estructura interna del host;
- layout global;
- docks arbitrarios;
- store de layout del host;
- focus manager global.

## Cómo un producto puede pedir servicios

Un producto pide servicios de esta manera y solo así:

1. declara la dependency en `PRODUCT_MANIFEST.json` y `DEPENDENCIES.md`;
2. declara el capability service contract que va a consumir;
3. el kernel valida compatibilidad y permissions;
4. el capability broker entrega un handle controlado;
5. toda llamada viaja por contrato observable.

### Queda prohibido
- `get_service("main_window")`
- `get_service("toolbar_controller")`
- `get_service("dock_manager")`
- cualquier service locator que exponga internals del host

## Cómo un producto puede publicar contexto

Un producto puede publicar contexto mediante:

- published context contracts;
- status segment contributions;
- events de producto aprobados;
- snapshots resumidos si el contract lo declara.

### El contexto publicado debe ser
- mínimo;
- deliberado;
- neutral para el host;
- observable;
- versionado.

### El contexto publicado no debe ser
- el store completo del producto;
- un dump de widgets;
- un backdoor para que el host tome decisiones de negocio.

## Qué un producto nunca puede hacer directamente

- meter lógica de dominio dentro del host;
- hacer branching product-specific dentro de servicios del kernel;
- crear side channels ocultos hacia internals del host;
- manipular layout global fuera de contributions;
- leer o escribir state de otro producto;
- leer controllers del host;
- persistir en stores del kernel sin contrato;
- lanzar procesos sin governance;
- silenciar errores de frontera;
- exigir que el host conozca sus modelos internos.

## Prohibiciones explícitas

### Queda prohibido
- lógica de dominio directa dentro del host;
- branching product-specific dentro de servicios del kernel;
- side channels escondidos entre productos y host internals.

## Ejemplos

### Aceptable
- `cloudflare_guardian` publica un status segment resumido de health mediante contract.
- `orchestrator_bridge` solicita `process_execution` y `history_runs` por contracts de Commons.
- el host activa una surface de `repo_analyzer` porque su contribution fue validada.

### Prohibido
- `cloudflare_guardian` raspa widgets y labels del host para armar su snapshot.
- el host decide abrir el grupo `run` porque el id contiene `orchestrator`.
- `orchestrator_bridge` registra un callback y además modifica toolbar/controller por acceso directo.

## Regla de cierre

Si la integración necesita “tocar una tripa del host”, la integration spec está siendo violada.  
No hay excepción de conveniencia.
