# 11_CODEX_EXECUTION_INSTRUCTIONS.md

## Rol operativo

Actúa como implementador de ForgeOS.  
Tu trabajo no es “arreglar el repo viejo”.  
Tu trabajo es **scaffoldar e implementar un sistema nuevo gobernado por este bundle**.

## Orden exacto de lectura

1. `README_START_HERE.md`
2. `00_PLATFORM_CONSTITUTION.md`
3. `01_FORGEOS_MASTER_BLUEPRINT.md`
4. `02_KERNEL_BOUNDARIES.md`
5. `05_CONTRACTS_CATALOG.md`
6. `06_HOST_INTEGRATION_SPEC.md`
7. `09_RECONSTRUCTION_ORDER.md`
8. `10_ACCEPTANCE_GATES.md`
9. `11_CODEX_EXECUTION_INSTRUCTIONS.md`
10. `03_SHARED_CAPABILITIES_CATALOG.md`
11. `04_PRODUCT_SKELETON_TEMPLATE.md`
12. `07_PACKAGING_AND_RELEASE_SPEC.md`
13. `08_BOUNDARY_ENFORCEMENT_RULES.md`
14. `12_ASSUMPTIONS_AND_DECISION_LOG.md`
15. `/matrices/*`
16. `/appendix/*`
17. `/templates/*`

## Qué es autoritativo

Considera autoritativos, en este orden:

1. `00_PLATFORM_CONSTITUTION.md`
2. `01_FORGEOS_MASTER_BLUEPRINT.md`
3. `02_KERNEL_BOUNDARIES.md`
4. `05_CONTRACTS_CATALOG.md`
5. `06_HOST_INTEGRATION_SPEC.md`
6. `09_RECONSTRUCTION_ORDER.md`
7. `10_ACCEPTANCE_GATES.md`
8. `11_CODEX_EXECUTION_INSTRUCTIONS.md`
9. `manifest.json`

Si algo de soporte contradice a lo autoritativo, gana lo autoritativo.

## Cómo tratar supuestos

- Si un supuesto no contradice evidencia ni constitución, úsalo como default fuerte.
- Si un supuesto sí contradice una ley constitucional o boundary rule, descártalo.
- Si necesitas adoptar un default fuerte nuevo, regístralo en el decision log del repo nuevo.
- No inventes compatibilidad backward si este bundle no la declara.

## Cómo scaffoldar el repo nuevo

### Estructura base recomendada

```text
forgeos/
├─ platform/
│  ├─ forge_kernel/
│  └─ forge_commons/
│     ├─ config_policy/
│     ├─ diagnostics/
│     ├─ process_execution/
│     ├─ history_runs/
│     └─ export_artifacts/
├─ products/
│  ├─ repo_analyzer/
│  ├─ cloudflare_guardian/
│  └─ orchestrator_bridge/
├─ governance/
│  ├─ contracts/
│  ├─ schemas/
│  ├─ matrices/
│  └─ decisions/
├─ packages/
└─ docs/
```

### Reglas de scaffolding
- crea primero `forge_kernel`;
- crea el runtime contractual antes de cualquier producto real;
- crea `forge_commons` solo para capabilities promovidos por este bundle;
- crea cada producto desde el skeleton canónico;
- no copies la jerarquía del repo legacy.

## Cómo preservar boundaries

- no importes productos desde kernel;
- no importes productos desde commons;
- no permitas service lookups a internals del host;
- no pongas campos de producto en el contexto del host;
- no promuevas a commons nada que siga oliendo a producto.

## Cómo usar el product skeleton

Para cada producto:

1. clona el template documental;
2. rellena `PRODUCT_MANIFEST.json`;
3. rellena `OWNERSHIP.md`;
4. rellena `STATE_AUTHORITY.md`;
5. define `LIFECYCLE.md`;
6. define `CONTRACT_INDEX.md`;
7. define `HOST_CONTRIBUTIONS.md`;
8. solo entonces empieza a mover código o a scaffoldar runtime.

## Cómo implementar contratos antes que productos

Orden interno dentro del repo nuevo:

1. contract ids y familias;
2. schemas/envelopes/error model;
3. contract registry y validation pipeline;
4. lifecycle wiring del kernel;
5. contribution contracts y host extension points;
6. capability service contracts;
7. state contracts;
8. productos.

No inviertas este orden.

## Cómo evitar contaminación del host

No hagas ninguna de estas cosas:

- recrear un `main_window.py` todopoderoso;
- usar un service container global con strings como API pública;
- enrutar por nombre de producto;
- guardar estado de producto en el host;
- dejar que una view del producto lea widgets del host;
- permitir que el host conozca reglas de negocio del producto.

## Cómo enforcing product isolation

Antes de activar un producto verifica:

- package manifest válido;
- compatibilidad válida;
- permissions explícitos;
- contributions válidas;
- contract index completo;
- state authority declarada;
- teardown declarado;
- error boundaries declaradas.

Si falta cualquiera, no actives el producto.

## Cuándo detenerte y pedir aclaración

Detente solo si ocurre una de estas tres cosas:

1. la evidencia disponible entra en conflicto directo con una ley constitucional y no hay forma de resolverla sin decisión humana;
2. falta un requerimiento externo bloqueante que no puede inferirse sin romper boundaries;
3. aparece una restricción legal/compliance/seguridad fuera del alcance de este bundle.

## Cuándo proceder con defaults fuertes

Procede sin pedir aclaración cuando el hueco sea de este tipo:

- naming interno de paquetes y carpetas;
- elección de interfaces públicas dentro de los límites aquí fijados;
- layout del repo nuevo;
- defaults de packaging o compatibility razonables;
- desactivación/eliminación de shims legacy;
- separación de stores por owner.

## Cómo secuenciar la implementación

### Secuencia obligatoria
1. Kernel skeleton
2. Contract runtime
3. Commons base
4. Host shell
5. Dummy product
6. `repo_analyzer`
7. `cloudflare_guardian`
8. `orchestrator_bridge`
9. packaging hardening
10. visual polish

### Entre cada paso
- corre gates de aceptación;
- actualiza matrices;
- registra decisiones nuevas;
- no avances con fails abiertos en boundary/state/teardown.

## Qué no inferir del código legacy

No infieras del legado:

- que el layout actual de carpetas sea correcto;
- que `tool == product == plugin`;
- que el host deba conocer Cloudflare u Orchestrator;
- que `EventBus` o `CommandDispatcher` string-based sean la solución final;
- que `QSettings` y archivos JSON actuales deban sobrevivir;
- que los tests legacy representen arquitectura sana;
- que las shims legacy deban preservarse.

## Kill list explícita: cosas que no debes portar tal cual

- `app/gui_qt/main_window.py`
- `app/gui_qt/event_bus.py`
- `app/gui_qt/command_dispatcher.py`
- `app/gui_qt/services/service_container.py`
- `app/gui_qt/shell/group_shell.py` con heurísticas por producto
- `app/gui_qt/tools/catalog.py` con inferencias por naming
- `plugins/cloudflare_guardian/state_adapter.py`
- legacy single-file plugin loader
- `_legacy_graph_svg_candidate`
- cualquier acceso directo a `main_window`

## Qué sí puedes preservar como semántica, no como forma

- el concepto de lifecycle de superficies;
- la necesidad de suspensión no destructiva;
- la utilidad de un registry de contributions;
- la utilidad de runtime diagnostics;
- la utilidad de process supervision e history;
- la existencia de products `cloudflare_guardian` y `orchestrator_bridge`;
- la existencia inferida de `repo_analyzer` como producto.

## Regla final

Usa el legado como cantera de semántica.  
No lo uses como plano de construcción.
