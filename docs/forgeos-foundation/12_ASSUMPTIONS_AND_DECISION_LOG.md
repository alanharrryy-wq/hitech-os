# 12_ASSUMPTIONS_AND_DECISION_LOG.md

Este log captura lo que se decidió con evidencia incompleta y por qué.

La regla fue: **si faltaba detalle pero el rumbo arquitectónico era claro, se tomó un default fuerte y se siguió.**

## Supuestos adoptados

| ID | Supuesto | Base | Confianza | Impacto |
| --- | --- | --- | --- | --- |
| A-01 | El primer target operativo puede seguir siendo un host de escritorio. | La evidencia fuente es PySide6 desktop y no hay requerimiento contrario. | Media | Afecta scaffolding inicial, no la doctrina de capas. |
| A-02 | No existe obligación de preservar compatibilidad binaria con el sistema de plugins legacy. | El usuario pidió reconstrucción gobernada, no cleanup incremental. | Alta | Permite eliminar loaders legacy. |
| A-03 | Los productos de primera ola son `repo_analyzer`, `cloudflare_guardian` y `orchestrator_bridge`. | Son los dominios/proto-productos más claros en la evidencia. | Media | Afecta plan de migración. |
| A-04 | Los dev/demo plugins no son baseline de la plataforma limpia. | El propio `PluginManager` ya los trata como dev-only o policy-gated. | Alta | Se van a quarantine o delete. |
| A-05 | Un primary workspace slot activo a la vez es un default inicial válido. | El legacy ya operaba con esa semántica y ayuda a simplificar el host shell. | Media | No impide ampliar slots después. |
| A-06 | Forge Commons debe iniciar pequeño y estricto. | La evidencia muestra alto riesgo de sobre-promoción. | Alta | Evita volverlo cajón de utilidades. |
| A-07 | Se puede usar Python package scaffolding como default técnico inicial si no se define otro stack. | Minimiza ambigüedad para una corrida posterior de implementación. | Media | No altera la arquitectura lógica. |
| A-08 | No se necesita migrar keys exactas de `QSettings` ni archivos JSON legacy. | No hay requerimiento de backward persistence compatibility. | Media | Facilita reescritura limpia de state ownership. |

## Apuestas arquitectónicas importantes

| ID | Apuesta | Upside | Downside |
| --- | --- | --- | --- |
| B-01 | Contract-first reconstruction | Reduce coupling oculto y hace visible ownership. | Sube el costo inicial de scaffolding. |
| B-02 | Forge Kernel domain-agnostic y host limpio | Permite múltiples productos sin contaminación. | Exige más disciplina al migrar el primer producto. |
| B-03 | Promotion-by-proof en Forge Commons | Evita shared layer tóxica. | Algunos equipos querrán reutilizar demasiado pronto. |
| B-04 | State authority explícita por slice | Elimina duplicidad y ambigüedad. | Obliga a documentar más antes de implementar. |
| B-05 | Legacy shims se aíslan o se eliminan | Evita que deuda histórica colonice el target. | Puede retrasar paridad funcional puntual. |

## Incertidumbres abiertas

| ID | Incertidumbre | Tratamiento actual |
| --- | --- | --- |
| U-01 | No está definido si habrá distribución multi-host o solo desktop. | La doctrina soporta ambos; el primer scaffold asume desktop por evidencia. |
| U-02 | No está definido el mecanismo final de firma/secure distribution. | El spec de packaging lo deja preparado, no implementado. |
| U-03 | No está definido si habrá marketplace interno de productos/capabilities. | El modelo de package y compatibility ya permite esa evolución. |
| U-04 | No está definido el nivel final de sandboxing de procesos externos. | Se fijó process supervision contractual como base mínima. |


## Decisiones intencionales tomadas

### D-01. Se rechazó el incremental cleanup
- **Razón**: el legado muestra patologías de gobierno, no solo deuda local.
- **Alternativa rechazada**: refactor progresivo sobre `main_window.py`.
- **Por qué se rechazó**: conserva el gravity well y el ownership difuso.

### D-02. Se definió `Forge Kernel`, `Forge Commons` y `Forge Products`
- **Razón**: la mezcla actual de capas hace imposible aislar dominios.
- **Alternativa rechazada**: mantener un host general con plugins libres.
- **Por qué se rechazó**: repite la ambigüedad plugin/tool/product.

### D-03. Search/Indexing no sube a Commons en la primera ola
- **Razón**: la evidencia muestra un solo consumidor claro y vocabulario de repositorio.
- **Alternativa rechazada**: convertir `AnalyzerBackend` en capability compartido desde el arranque.
- **Por qué se rechazó**: sería promoción sin prueba.

### D-04. Process execution sí sube parcialmente a Commons
- **Razón**: timeouts, kill policies, streaming y state machine son neutrales al dominio.
- **Alternativa rechazada**: dejar toda la ejecución incrustada en `orchestrator_bridge`.
- **Por qué se rechazó**: el capability es reusable y operacionalmente transversal.

### D-05. Graph/UI de Cloudflare Guardian se queda product-local
- **Razón**: el vocabulario y la UI son de dominio claro.
- **Alternativa rechazada**: crear un commons de graph visual desde el legacy.
- **Por qué se rechazó**: sería contrabando de semántica de producto.

### D-06. El service container global se elimina
- **Razón**: destruye boundaries y hace invisible el acoplamiento.
- **Alternativa rechazada**: mantenerlo “solo para internals”.
- **Por qué se rechazó**: el legacy ya demostró que termina expuesto a productos.

### D-07. Legacy loaders y compatibility shims no forman parte del target limpio
- **Razón**: el usuario pidió reconstrucción, no arqueología permanente.
- **Alternativa rechazada**: mantener compatibilidad “temporal”.
- **Por qué se rechazó**: lo temporal se vuelve base si entra al kernel.

## Qué proviene de evidencia vs inferencia

### Evidencia directa del código
- `main_window.py` como root hipertrofiado.
- `ToolWorkspaceCoordinator` creado antes del `event_bus`.
- `WorkstationContext` contaminado con campos Cloudflare.
- `ShellGroupRuntime` y `ToolCatalogService` con heurísticas por nombre de producto.
- `PluginManager.shutdown_all()` no llamado en `closeEvent`.
- `state_adapter.py` raspando `main_window`.
- `QSettings` + JSON + configs/histories dispersos.
- legacy shims como `_legacy_graph_svg_candidate`.
- bundle sucio con `__pycache__`, `.pytest_cache` y `.repo_analyzer_settings.json`.

### Inferencias de arquitectura target
- existencia de `repo_analyzer` como producto separado;
- necesidad de un capability broker en lugar del service container global;
- taxonomía de packages;
- slot model del host shell;
- promotion set inicial de Forge Commons;
- orden de migración de productos.

## Alternativas relevantes rechazadas

| Alternativa | Rechazo |
| --- | --- |
| Refactor incremental dentro del repo legacy | Mantiene gravedad y ownership roto |
| Host con “plugins mejor organizados” | Sigue sin distinguir producto, capability y contribución |
| Contexto global rico compartido por todos | Reproduce contaminación y authority blur |
| Commons grande desde el día uno | Riesgo de utility swamp |
| Preservar keys y stores legacy por default | Arrastra fragmentación de persistencia |
| Mantener `tool` como unidad principal del modelo | No alcanza para gobierno multi-producto |

## Qué falta por definir y no bloquea este bundle

- detalles de implementación concreta del runtime contractual;
- tecnología final de distribución y firma;
- detalle exacto de observability backend;
- policy final de sandboxing de procesos externos;
- layout visual definitivo del host.

## Regla del decision log

Si en la implementación futura se toma una decisión que:
- cambie owner,
- cambie source of truth,
- promueva/demueva una capability,
- altere compatibilidad,
- o reabra un boundary,

esa decisión debe agregarse al decision log del repo nuevo.
