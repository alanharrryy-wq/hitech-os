# Atlas parity visual 1:1 para todo `shared/pyside6_glass`

## Veredicto corto
No está **1:1 con Atlas** todavía.

La paridad base ya mejoró mucho en:
- `backdrop.py`
- `chrome.py`
- `effects.py`
- `frameless.py`
- `controls.py`
- `scene.py`

Pero el paquete completo **sigue sin verse igual** porque el problema ya no está solo en el shell. Ahora el desfase vive en:
- los **componentes reutilizables**
- los **widgets crudos** que siguen saliendo sin skin Atlas
- los **examples/compositions** que siguen armando UI con Qt nativo
- los **overrides locales** que pisan el look correcto
- los **dashboards/workbench** que no están usando el mismo pipeline visual que `code-atlas`

---

## Qué está pasando en una línea
Ya arreglaste el **cascarón**. Falta arreglar el **contenido**.

Hoy `shared/pyside6_glass` ya se parece a Atlas en:
- vidrio
- chrome
- resize
- glow base

Pero no se parece en:
- botones dentro de herramientas y workbench
- cards internas
- formularios
- listas/tablas/text editors
- toolbar real
- dashboard surface
- examples que siguen pintando widgets nativos

---

## Regla de oro para cerrar la paridad
Si un widget se construye con:
- `QPushButton(...)`
- `QLineEdit(...)`
- `QTextEdit(...)`
- `QListWidget(...)`
- `QTableWidget(...)`
- `QProgressBar(...)`

sin pasar por una capa visual Atlas o sin recibir el mismo stylesheet exacto que Atlas, **no va a verse igual**.

---

## Matriz exacta de cambios restantes

| Prioridad | Archivo | Estado vs Atlas | Qué hacer | ¿Crear algo nuevo? | Cómo conectarlo |
|---|---|---|---|---|---|
| 1 | `examples/demo_app.py` | **Rompe la paridad** | quitar shell overrides locales y dejar solo pipeline Atlas exacto | No | usar `build_stylesheet_exact_atlas(...)`; no mezclar `build_stylesheet(...) + overrides manuales` |
| 2 | `template.py` | **No exacto** | cambiar cualquier uso de stylesheet base por stylesheet Atlas exacto | No | donde hoy usa `build_stylesheet(...)`, usar `build_stylesheet_exact_atlas(...)` |
| 3 | `examples/catalog_shell.py` | **Muy lejos de Atlas** | dejar de construir UI con widgets Qt crudos y helpers privados | No, pero sí extraer wrappers reutilizables | reemplazar botones/inputs/listas/tablas/toolbars por capa shared ya atlasizada |
| 4 | `examples/compositions.py` | **Muy lejos de Atlas** | reemplazar formularios, tablas, listas, botones y progress bars crudos por componentes shared | Sí, conviene crear wrappers de fields/data surfaces | todas las composiciones deben usar esos wrappers, no Qt puro |
| 5 | `assets.py` | **Incompleto** | atlasizar toolbar, segmented controls, search bars, pills, chips y form assets | Sí, conviene crear submódulo `asset_styles.py` o `fields.py` | `catalog_shell.py`, `dashboard.py` y `compositions.py` deben consumirlos |
| 6 | `primitives.py` | **Incompleto** | atlasizar panel headers, stat cards, state cards y progress shell | No | agregar shadow/hover/card roles exactos y usarlo en dashboards/compositions |
| 7 | `dashboard.py` | **No exacto** | dejar de renderizar data surfaces desnudas y envolverlas en shells Atlas | Sí, conviene crear `data_surfaces.py` | dashboard debe montar tablas/listas/textos/progreso mediante esos shells |
| 8 | `theme.py` | **Todavía corto** | extender stylesheet exacto para assets internos y widgets de data surface | Sí, conviene crear `atlas_component_styles.py` | `build_stylesheet_exact_atlas()` concatena base + atlas shell + atlas components |
| 9 | `atlas_styles.py` | **Todavía corto** | hoy cubre shell/chrome hover, pero no cubre todo el resto | No o mover parte a `atlas_component_styles.py` | agregar selectors exactos para toolbar, chips, cards internas, segmented, search, tables, lists, editors, progress |
| 10 | `charts.py` | **Probable desfase** | normalizar superficies de chart host, legend, labels y toolbars al pipeline Atlas | No obligatorio si no salen en demo actual | dashboards/charts deben usar host cards atlasizadas |
| 11 | `assets.py` + `controls.py` | **Casi bien** | unificar tamaños/márgenes/radius de botones pequeños y toolbar buttons | No | todos los botones auxiliares deben salir por la misma fábrica, no por `QPushButton(...)` directo |
| 12 | `examples/catalog_builtin.py` y `examples/catalog_dashboard_entries.py` | **No exacto** | cambiar widgets crudos por wrappers visuales | No | usar wrappers creados en `fields.py` / `data_surfaces.py` |

---

# 1) `examples/demo_app.py`

## Archivo a cambiar
`shared/pyside6_glass/examples/demo_app.py`

## Problema real
Este archivo **sigue metiendo overrides manuales** con `_workbench_shell_overrides()` y además arma el style con:
- `build_stylesheet(...)`
- luego concatena CSS local

Eso rompe la paridad porque ya no estás viendo el sistema visual Atlas real, sino una mezcla.

## Qué está mal
- redefine `QFrame#Shell`
- redefine `QFrame[card="hero"]`, `QFrame[card="true"]`, `QFrame[card="muted"]`, `QFrame[card="footer"]`
- redefine `QFrame#WindowChrome`
- redefine botones del chrome
- usa `QToolButton` selectors aunque el chrome nuevo ya va por otro camino

## Cambio exacto
Eliminar `_workbench_shell_overrides()` del flujo principal.

## Qué debe quedar
Usar solo:
- `build_stylesheet_exact_atlas(...)`
- `build_glass_dialog_scene(...)`
- `WindowChromeBar(...)`
- `FramelessResizeController(...)`

## Conexión
Si hace falta un override de demo, debe ir aparte y **nunca** pisar:
- shell
- chrome
- card base
- buttons base

## Veredicto
Este archivo hoy es uno de los principales culpables de que el workbench izquierdo no se vea como Atlas.

---

# 2) `template.py`

## Archivo a cambiar
`shared/pyside6_glass/template.py`

## Problema real
Todavía trae uso directo de `build_stylesheet(...)`.

## Qué rompe
Aunque el shell general ya sea Atlas, cualquier plantilla que vuelva a pintar su propio stylesheet base se te regresa a la versión “shared reusable”, no a la versión Atlas final.

## Cambio exacto
Buscar cualquier sitio donde hoy haga:
- `build_stylesheet(...)`

y cambiarlo por:
- `build_stylesheet_exact_atlas(...)`

## Conexión
Importar desde `.theme`:
- `build_stylesheet_exact_atlas`

No dejar conviviendo ambos en rutas activas.

---

# 3) `examples/catalog_shell.py`

## Archivo a cambiar
`shared/pyside6_glass/examples/catalog_shell.py`

## Veredicto
Este archivo **sigue muy lejos de Atlas**.

## Problema real
Tiene demasiado UI construido con Qt crudo y con helpers privados viejos:
- `_apply_shadow`
- `_repolish`
- `_enable_card_hover`
- muchísimos `QPushButton(...)`
- muchos `QLineEdit(...)`
- muchos `QListWidget(...)`
- muchos `QTextEdit(...)`
- `setStyleSheet(...)` locales

## Qué significa
Aunque el paquete base ya esté atlasizado, este example sigue armando otra interfaz encima.

## Cambio exacto
### A. borrar helpers visuales privados
No debe vivir aquí nada de:
- shadow
- repolish
- hover filter

Debe importar desde:
- `effects.py`
- `controls.py`
- `assets.py`
- `primitives.py`

### B. reemplazar botones crudos
Todo botón de toolbar, acción, diálogo o panel debe salir por una fábrica shared atlasizada.

### C. reemplazar entradas crudas
Donde hoy usa `QLineEdit`, `QTextEdit`, `QListWidget`, `QTableWidget`, etc., debe pasar por wrappers Atlas o por hosts que ya les apliquen el shell correcto.

### D. eliminar `setStyleSheet(...)` locales de composición
No deben existir estilos locales que redefinan cards, shell o toolbar.

## Recomendación exacta
No conviene “parchar” 200 botones a mano aquí. Conviene crear wrappers y luego reemplazar llamadas.

---

# 4) `examples/compositions.py`

## Archivo a cambiar
`shared/pyside6_glass/examples/compositions.py`

## Veredicto
Aquí está otro pedo grande.

## Qué está mal
Las composiciones siguen armadas con widgets nativos crudos:
- formularios con `QLineEdit`
- notas con `QTextEdit`
- sidebars con `QListWidget`
- tablas con `QTableWidget`
- progreso con `QProgressBar`
- acciones con `QPushButton`

Eso hace que el interior de cada demo se vea como “Qt con glass encima”, no como Atlas.

## Cambio exacto
Toda composición debe usar wrappers visuales shared, por ejemplo:
- fields Atlas
- data surfaces Atlas
- buttons Atlas
- card shells Atlas
- state cards Atlas

## Archivo nuevo recomendado
`shared/pyside6_glass/fields.py`

## Qué debe vivir ahí
Wrappers exactos para:
- `GlassLineField`
- `GlassTextArea`
- `GlassSelectField`
- `GlassSearchField`
- `GlassFormSection`

## Cómo conectarlo
`examples/compositions.py` deja de instanciar widgets Qt directos y usa esos wrappers.

---

# 5) `assets.py`

## Archivo a cambiar
`shared/pyside6_glass/assets.py`

## Veredicto
Base útil, pero todavía no Atlas exacto.

## Qué piezas traen desfase
- `GlassIconButton`
- `StatusPill`
- `StatPill`
- `GlassSegmentedControl`
- `TogglePill`
- `FilterChipBar`
- `SearchCommandBar`
- `CompactToolbar`

## Problemas reales
### A. tamaños/márgenes/radius
Todavía se sienten más “kit reusable” que “app Atlas”.

### B. toolbar
El workbench izquierdo se ve demasiado compacto y angosto en la parte alta. La fila de acciones no tiene la misma presencia visual que Atlas.

### C. search bar y chips
Se siguen viendo más utilitarios que Atlas.

### D. icon buttons
Siguen usando una estética más de toolbutton genérico.

## Cambio exacto
### CompactToolbar
Debe volverse una toolbar Atlas real:
- más altura visual
- más padding horizontal
- botones con la misma familia que Atlas
- misma separación
- misma jerarquía entre primaria/secundaria

### SearchCommandBar
Debe dejar de ser solo `QLineEdit + icon button` y volverse un host Atlas con:
- shell propio
- paddings correctos
- icon spacing correcto
- clear button correcto

### FilterChipBar / Segmented / Pills
Unificar radius, padding, border y hover al mismo sistema Atlas.

## Archivo nuevo recomendado
`shared/pyside6_glass/asset_component_styles.py`

## Cómo conectarlo
`atlas_styles.py` o `theme.py` debe concatenar sus selectors.

---

# 6) `primitives.py`

## Archivo a cambiar
`shared/pyside6_glass/primitives.py`

## Veredicto
No está roto, pero todavía no se siente Atlas real en:
- panel headers
- stat cards
- state cards
- progress areas

## Problema real
Los primitives existen, pero no traen todo el remate visual:
- shadows correctos
- hover correcto
- estructura de jerarquía Atlas
- spacing de header y acciones como Atlas

## Cambio exacto
### `PanelHeader`
Debe tener spacing, icon sizing, subtitle cadence y action alignment iguales a Atlas.

### `StatCard`
Debe tener:
- shell correcto
- glow/shadow correcto
- value hierarchy correcta
- padding correcto

### `_StateCardBase`
Debe sentirse como state card Atlas, no solo un frame con texto.

### progress shell
Si el progreso vive aquí, debe tener el mismo host visual que Atlas.

## Conexión
`dashboard.py` y `compositions.py` deben consumir estos primitives ya atlasizados.

---

# 7) `dashboard.py`

## Archivo a cambiar
`shared/pyside6_glass/dashboard.py`

## Veredicto
Hoy renderiza data, pero no la envuelve en la misma gramática visual de Atlas.

## Qué está mal
- usa `QTableWidget` directo
- usa `QListWidget` directo
- usa `QTextEdit` directo
- los KPI y data zones no siempre pasan por un shell Atlas fuerte

## Resultado
Se ve funcional, pero más “inspector genérico” que Atlas.

## Cambio exacto
Crear un nivel reusable para superficies de datos.

## Archivo nuevo recomendado
`shared/pyside6_glass/data_surfaces.py`

## Qué debe vivir ahí
Wrappers tipo:
- `GlassDataTable`
- `GlassDataList`
- `GlassDataViewer`
- `GlassMetricsStrip`
- `GlassDashboardSection`

## Cómo conectarlo
`dashboard.py` usa esos wrappers en vez de instanciar widgets Qt crudos.

---

# 8) `theme.py`

## Archivo a cambiar
`shared/pyside6_glass/theme.py`

## Veredicto
Ya mejoró mucho, pero todavía no cubre todos los componentes internos.

## Problema real
El stylesheet exacto Atlas ya amarra shell/chrome/base controls, pero no alcanza para:
- toolbar real
- chips/segmented exactos
- search bars exactas
- data surfaces exactas
- state cards internas
- dashboard cards complejas

## Cambio exacto
Expandir `build_stylesheet_exact_atlas(...)` para concatenar otra capa de componentes.

## Archivo nuevo recomendado
`shared/pyside6_glass/atlas_component_styles.py`

## Qué debe vivir ahí
Selectors para:
- `CompactToolbar`
- `SearchCommandBar`
- `FilterChipBar`
- `GlassSegmentedControl`
- `StatusPill`
- `StatPill`
- `PanelHeader`
- `StatCard`
- `StateCard`
- `GlassDataTable`
- `GlassDataList`
- `GlassDataViewer`
- `QHeaderView` de tablas
- cards internas de dashboard

## Cómo conectarlo
`build_stylesheet_exact_atlas()` debe quedar así, conceptualmente:
- base shared
- atlas shell overrides
- atlas component overrides

---

# 9) `atlas_styles.py`

## Archivo a cambiar
`shared/pyside6_glass/atlas_styles.py`

## Veredicto
Hoy cubre solo una parte del remate Atlas.

## Qué sí cubre
- chrome
- hoverable cards
- shell básico

## Qué no cubre todavía
- toolbar family
- compact action rows
- assetRole widgets
- search bars
- segmented controls
- pills
- dashboard cards
- data tables/lists/viewers
- inner cards y surfaces del workbench

## Cambio exacto
O amplías este archivo, o creas `atlas_component_styles.py` y lo concatenas.

## Recomendación exacta
Separarlo:
- `atlas_styles.py` = shell y chrome
- `atlas_component_styles.py` = componentes internos

Porque ya se volvió demasiado grande el problema para meterlo todo en un solo archivo de overrides.

---

# 10) `charts.py`

## Archivo a cambiar
`shared/pyside6_glass/charts.py`

## Estado
No es el culpable principal del screenshot actual, pero sí te puede romper dashboards 1:1 si lo ignoras.

## Qué revisar
- host frame del chart
- paddings de legend
- tipografía de labels
- glow / grid / line alpha
- integración con cards y metric shells

## Recomendación
No tocarlo primero si el objetivo inmediato es que el workbench base se vea idéntico. Pero sí meterlo en fase 2.

---

# 11) `catalog_builtin.py` y `catalog_dashboard_entries.py`

## Archivos a cambiar
- `shared/pyside6_glass/examples/catalog_builtin.py`
- `shared/pyside6_glass/examples/catalog_dashboard_entries.py`

## Problema real
Siguen sembrando widgets crudos dentro del catálogo.

## Cambio exacto
Cambiar todos los objetos insertables para que usen:
- wrappers de fields
- wrappers de data surfaces
- buttons atlasizados
- cards atlasizadas

## Resultado
El catálogo ya no te mete elementos “medio Qt” dentro de una shell Atlas.

---

# Lo que NO hace falta tocar primero
No abriría primero:
- `runtime.py`
- `persistence.py`
- `contracts.py`
- `release_gate.py`
- `data.py`
- `data_providers.py`
- `integration/*`

Eso no es lo que está rompiendo el look.

---

# Orden exacto de implementación

## Fase 1. Quitar lo que rompe la paridad visible hoy
1. `examples/demo_app.py` -> quitar overrides locales y dejar pipeline Atlas exacto
2. `template.py` -> dejar solo `build_stylesheet_exact_atlas(...)`
3. `examples/catalog_shell.py` -> quitar helpers privados y estilos locales, enrutar a shared atlasizado
4. `examples/compositions.py` -> dejar de usar widgets Qt crudos

## Fase 2. Atlasizar componentes reutilizables
5. `assets.py` -> toolbar, search, pills, segmented, chips
6. `primitives.py` -> headers, state cards, stat cards, progress shells
7. crear `fields.py`
8. crear `data_surfaces.py`
9. crear `atlas_component_styles.py`

## Fase 3. Cerrar dashboards y catálogo
10. `dashboard.py` -> usar data surfaces atlasizadas
11. `catalog_builtin.py` y `catalog_dashboard_entries.py` -> insertar solo wrappers visuales Atlas
12. `charts.py` -> revisar host/legend/grid si todavía hay drift visual

---

# Resumen ejecutable

## Cambiar ya
- `shared/pyside6_glass/examples/demo_app.py`
- `shared/pyside6_glass/template.py`
- `shared/pyside6_glass/examples/catalog_shell.py`
- `shared/pyside6_glass/examples/compositions.py`
- `shared/pyside6_glass/assets.py`
- `shared/pyside6_glass/primitives.py`
- `shared/pyside6_glass/dashboard.py`
- `shared/pyside6_glass/theme.py`
- `shared/pyside6_glass/atlas_styles.py`
- `shared/pyside6_glass/examples/catalog_builtin.py`
- `shared/pyside6_glass/examples/catalog_dashboard_entries.py`
- opcional fase 2: `shared/pyside6_glass/charts.py`

## Crear
- `shared/pyside6_glass/fields.py`
- `shared/pyside6_glass/data_surfaces.py`
- `shared/pyside6_glass/atlas_component_styles.py`

## Conectar
- `demo_app.py` -> pipeline Atlas exacto sin overrides manuales
- `template.py` -> stylesheet Atlas exacto
- `catalog_shell.py` -> usar helpers shared, no privados
- `compositions.py` -> usar wrappers visuales, no Qt crudo
- `dashboard.py` -> usar `data_surfaces.py`
- `theme.py` -> concatenar `atlas_component_styles.py`
- `assets.py` / `primitives.py` -> usar mismos roles/spacing/shadow del sistema Atlas

---

# Criterio de aceptación
Solo considéralo “igual a Atlas” si ya cumple esto:
- mismo shell
- mismo chrome
- mismos botones de toolbar y acciones
- mismas cards internas
- mismos headers de panel
- mismos inputs y text areas
- mismas listas/tablas/viewers
- mismos dashboard shells
- mismas pills/chips/segmented/search bars
- cero overrides locales que pisen Atlas
- cero composiciones armadas con Qt crudo sin wrapper visual

Si falta uno, todavía no es Atlas completo.

---

# Mi recomendación final
Si quieres cerrar esto **de verdad**:

No sigas parchando example por example.

La jugada correcta es:
1. arreglar el pipeline central (`demo_app.py`, `template.py`, `theme.py`)
2. crear wrappers visuales faltantes (`fields.py`, `data_surfaces.py`, `atlas_component_styles.py`)
3. reemplazar todas las instancias de widgets Qt crudos en examples/catalog/dashboard por esos wrappers

## Traducción brutal
- si arreglas solo backdrop y chrome: tienes vidrio bonito
- si arreglas también buttons/cards/fields/data surfaces: tienes Atlas real

