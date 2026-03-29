# ForgeOS Foundation Bundle

## Qué es este bundle

Este bundle define la base de arquitectura y gobierno para una **reconstrucción limpia** de ForgeOS.  
No es una guía de refactor cosmético.  
No es un inventario superficial del legado.  
No autoriza copiar archivos del sistema actual y renombrarlos.

La fuente obligatoria fue el bundle de handoff y, dentro de él, `source_artifacts/repo_analizer.zip`.  
El código actual se trató como **evidencia** de fallas, límites y responsabilidades. No se trató como plantilla de reconstrucción.

## Regla no negociable

> **Kernel de plataforma, capacidades compartidas y productos deben permanecer separados; ningún producto puede inyectar lógica de dominio dentro del host.**
>
> **Kernel of platform, shared capabilities, and products must remain separated; no product may inject domain logic into the host.**

## Orden de lectura

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

## Cómo debe consumirlo Codex

- Leer primero los archivos autoritativos.
- Scaffoldar un repo **nuevo**. No editar el repo legado como base.
- Implementar primero **kernel**, luego **contratos**, luego **commons**, luego **host shell**, luego **skeletons de producto**, y al final migrar productos.
- Usar los templates tal cual como punto de arranque documental y de manifest.
- Registrar cualquier default fuerte en el decision log del nuevo repo.
- No inferir compatibilidad backward salvo donde este bundle lo declare de forma explícita.

## Qué es autoritativo y qué es soporte

### Autoritativo
- `00_PLATFORM_CONSTITUTION.md`
- `01_FORGEOS_MASTER_BLUEPRINT.md`
- `02_KERNEL_BOUNDARIES.md`
- `05_CONTRACTS_CATALOG.md`
- `06_HOST_INTEGRATION_SPEC.md`
- `09_RECONSTRUCTION_ORDER.md`
- `10_ACCEPTANCE_GATES.md`
- `11_CODEX_EXECUTION_INSTRUCTIONS.md`
- `manifest.json`

### Soporte
- `03_SHARED_CAPABILITIES_CATALOG.md`
- `04_PRODUCT_SKELETON_TEMPLATE.md`
- `07_PACKAGING_AND_RELEASE_SPEC.md`
- `08_BOUNDARY_ENFORCEMENT_RULES.md`
- `12_ASSUMPTIONS_AND_DECISION_LOG.md`
- `/matrices/*`
- `/appendix/*`
- `/templates/*`

## Fuente base usada para construir este bundle

### Lectura obligatoria del handoff
- `README_INICIO.md`
- `01_estado_actual.md`
- `02_hallazgos_clave.md`
- `03_plan_recomendado_opcion_3.md`
- `04_reglas_del_usuario_y_forma_de_trabajo.md`
- `handoff_state.json`

### Evidencia primaria
- `source_artifacts/repo_analizer.zip`

### Soporte no autoritativo
- grafo SVG del repo
- manifests auxiliares de sesión
- documentación legacy interna del repositorio

## Qué no debe hacerse

- No portar `main_window.py` como centro del nuevo sistema.
- No conservar `event_bus.py` y `command_dispatcher.py` como contratos finales.
- No conservar `ServiceContainer` string-based.
- No permitir que un producto lea `main_window` ni controllers del host.
- No promover semántica de Cloudflare u Orchestrator al kernel.
- No cargar plugins legacy por compatibilidad “temporal” dentro del target limpio.

## Resultado esperado de este bundle

Después de descomprimirlo, un operador posterior debe poder:

1. entender la doctrina arquitectónica de ForgeOS;
2. scaffoldar un repo nuevo con fronteras limpias;
3. implementar contratos antes que features;
4. migrar productos sin volver a contaminar el host;
5. validar aceptación, compatibilidad y teardown con evidencia.
