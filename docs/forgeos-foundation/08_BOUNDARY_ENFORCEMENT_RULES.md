# 08_BOUNDARY_ENFORCEMENT_RULES.md

## Propósito

Definir cómo se mantiene limpia la arquitectura de ForgeOS una vez reconstruida.

Sin enforcement, la plataforma volvería a llenarse de cables pelados:
- un `if` con nombre de producto aquí,
- un `get_service("main_window")` allá,
- un store prestado por “practicidad”,
- y otra vez aparece el monstruo.

## Reglas estructurales

1. Todo módulo pertenece a una sola capa.
2. Todo paquete declara owner.
3. Todo contrato cross-layer vive en un índice contractual.
4. Todo state slice tiene authority documentada.
5. Todo package tiene teardown documentado.
6. Todo package tiene compatibilidad declarada.
7. Todo dependency hacia Commons o Kernel usa surface pública, no internals.
8. Ningún producto depende de otro producto.
9. Ningún Commons depende de un producto.
10. Ningún Kernel contiene branching por nombre de producto.

## Reglas de review

Toda revisión de PR, patch o corrida de Codex debe responder:

- ¿qué owner cambia?
- ¿qué contrato cambia?
- ¿qué state authority cambia?
- ¿qué teardown cambia?
- ¿qué compatibilidad cambia?
- ¿qué package manifest cambia?
- ¿qué evidencia de gate acompaña el cambio?

Si la respuesta es “ninguna” y el cambio sí cruza capas, el cambio está incompleto.

## Ideas de linting/validación a nivel gobierno

### Static checks recomendados
- validador de import graph por capa;
- escáner de símbolos prohibidos;
- validador de manifests;
- validador de contract ids y familias;
- validador de state authority matrix;
- validador de teardown completeness;
- detector de `except Exception: pass` en fronteras críticas;
- detector de strings de producto dentro de kernel/commons.

### Banned symbol checks sugeridos
- `main_window`
- `self.main`
- `get_service("main_window")`
- `get_service('main_window')`
- `cloudflare_guardian` dentro de kernel/commons
- `orchestrator_bridge` dentro de kernel/commons
- `QSettings` fuera de adapters/capabilities aprobados
- event names string literals fuera del registry contractual

## Architectural gate checks

| Gate | Pregunta | Pass | Fail |
| --- | --- | --- | --- |
| AG-01 Layer map | ¿El módulo pertenece claramente a una capa? | owner y capa declarados | módulo híbrido |
| AG-02 Contract-first | ¿Toda interacción cross-layer tiene contrato? | contract index actualizado | llamada directa sin contrato |
| AG-03 Host agnostic | ¿El host sigue sin lógica de producto? | cero nombres/branches de producto en kernel | aparece branching product-specific |
| AG-04 State authority | ¿Cada state slice tiene owner? | owner y store declarados | state duplicado o sin authority |
| AG-05 Teardown | ¿Todo recurso nuevo tiene dispose? | teardown doc + evidence | recursos vivos sin cierre |

## Dependency gate checks

- prohibir imports de `products/*` desde kernel o commons;
- prohibir imports de internals privados de kernel desde productos;
- prohibir imports de internals privados de commons desde productos;
- prohibir service locator global como surface oficial;
- bloquear cadenas de dependencia entre commons si no están declaradas.

## Ownership gate checks

- todo contrato nuevo tiene contract owner;
- todo store nuevo tiene state owner;
- todo package nuevo tiene packaging owner;
- toda capability nueva tiene capability owner;
- todo published context nuevo tiene owner y retention policy.

## Teardown gate checks

- nuevas subscriptions tienen unsubscribe nominativo;
- nuevas tasks tienen cancel policy;
- nuevos subprocesses tienen timeout y kill policy;
- nuevos stores tienen flush/close policy;
- nuevas surfaces tienen unbind/dispose;
- uninstall no toca stores ajenos.

## Patrones de acoplamiento prohibidos

- host leyendo atributos de productos;
- productos leyendo controllers del host;
- commons llamando a productos;
- productos escribiendo en stores del kernel;
- heurísticas por naming para decidir categoría, grupo o slot;
- contextos globales contaminados con semántica de producto;
- callbacks opacos sin routing contractual;
- payloads polimórficos sin schema.

## Smells que indican contaminación del kernel

- aparecen ids o nombres de producto dentro del kernel;
- el kernel requiere campos de dominio para renderizar una surface;
- un layout o menú del host cambia de manera distinta según producto por branching interno;
- el kernel guarda config específica de un producto;
- el kernel necesita importar módulos del producto para “resolver algo simple”.

## Smells que indican abuso de Forge Commons

- capability con un solo consumidor y semántica local;
- capability que expone widgets o UI product-specific;
- capability que depende del host para vivir;
- capability que guarda payloads de dominio que no son neutrales;
- capability que no puede nombrarse sin mencionar un producto;
- capability con lifecycle implícito.

## Smells que indican fuga de producto hacia el host

- lectura directa de labels, docks o controllers del host;
- published context demasiado grande o que parece dump del store interno;
- actions de producto que mutan el chrome global;
- stores de producto guardados en config global del host;
- side channels por señales internas o service lookups.

## Checklist de enforcement para futuros PRs o corridas de Codex

1. ¿El cambio agrega o modifica un contrato?
2. ¿El contract index cambió?
3. ¿La compatibilidad cambió?
4. ¿El ownership cambió?
5. ¿La state authority matrix cambió?
6. ¿Se agregó un store?
7. ¿Se agregó un proceso o task?
8. ¿El teardown fue actualizado?
9. ¿El package manifest cambió?
10. ¿Se introdujo un símbolo prohibido?
11. ¿Aparece algún nombre de producto dentro de kernel o commons?
12. ¿El cambio requiere un capability nuevo o solo una utilidad local?
13. ¿La evidencia de gates acompaña el cambio?

## Regla de enforcement

El enforcement no es una recomendación.  
Es una condición de supervivencia de la plataforma.
