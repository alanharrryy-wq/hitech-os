# SYNAPSE-X :: Flujo de funcionamiento de la interfaz al montar el motor

## Veredicto corto

**Sí existe un flujo base de funcionamiento de la interfaz, pero hoy está en modo blueprint, no en modo implementación completa.**

En otras palabras:

- **Sí hay diseño funcional** de qué debe hacer la UI cuando el motor esté montado.
- **Sí hay superficie real del backend** para sostener ese flujo.
- **No existe todavía el flujo completo ya cableado en código UI** de punta a punta.
- **La shell/consola prefabricada sí alcanza** para alojarlo, siempre que se adapten acciones, slots y visibilidad de paneles.

---

## De dónde sale este flujo

Se ve repartido en varias piezas del proyecto:

### 1) Especificación de UI
Archivo:
- `docs/07-ui-spec.md`

Ahí ya están definidas las áreas principales:
- Controls
- Search
- Results
- Detail
- Metrics
- State

Y también ya aparecen acciones esperadas:
- Ingest
- Full ingest
- Repair
- Watch ON/OFF

Además define qué debe verse en:
- result card
- detail view
- status panel

### 2) Nota de integración PySide6
Archivo:
- `docs/PYSIDE6_INTEGRATION.md`

Ahí ya está la regla arquitectónica:
- no meter parsing, scanning ni SQLite en widgets
- usar adapter/controller alrededor de `SynapseEngine`
- usar workers para operaciones largas

### 3) Backend real ya listo para ser conectado
Archivos:
- `run_engine.py`
- `src/synapse_x/cli.py`
- `src/synapse_x/engine.py`

El motor ya expone operaciones claras:
- `init_storage()`
- `ingest(..., full=False)`
- `search(...)`
- `get_session_detail(session_id)`
- `get_metrics(days=...)`
- `repair()`

### 4) Estructura UI ya sembrada, pero vacía
Archivos:
- `src/synapse_x/ui/main_window.py`
- `src/synapse_x/ui/panels/*.py`

Esto confirma que la intención de arquitectura ya existe, pero todavía está en `TODO`.

### 5) Shell visual prefabricada utilizable
Proyecto original:
- `starter.py`
- `visuals/screens/template_console.py`

La consola ya soporta bien:
- toolbar configurable
- hero/header
- footer con estado
- slots inyectables
- orden de paneles
- mostrar/ocultar sidebar/aux

Eso alcanza para montar la UX de SYNAPSE-X sin rehacer la shell.

---

## Conclusión exacta

### Lo que sí hay hoy
Hay un **flujo objetivo bien insinuado**:

1. abrir interfaz
2. ver estado del motor
3. correr acciones de mantenimiento/ingestión
4. buscar sesiones/registros
5. ver resultados
6. seleccionar un resultado
7. ver detalle completo
8. consultar métricas globales
9. monitorear estado/logs/watcher

### Lo que no hay todavía
No existe todavía una implementación ya amarrada así:

`botón -> controller -> worker -> adapter -> SynapseEngine -> render en panel`

O sea:
- **sí hay flujo de producto**
- **no hay todavía flujo de ejecución UI completo**

---

## Flujo funcional recomendado cuando el motor ya esté montado

Este debería ser el flujo oficial de operación de la interfaz.

---

## 0. Arranque / Boot

### Objetivo
Que la app abra estable, detecte el root y deje claro el estado inicial.

### Pasos
1. Abrir ventana principal.
2. Resolver root activo de SYNAPSE-X.
3. Construir `Settings` / `SynapseEngine` a través de adapter.
4. Verificar si la DB existe o no.
5. Pintar estado inicial en UI.

### Qué debe mostrar la UI
- root activo
- estado del engine: `ready`, `db-missing`, `busy`, `error`
- rutas relevantes
- estado vacío si no hay datos

### Qué no debe hacer
- no correr ingest automática por sorpresa
- no meter lógica pesada en widgets
- no congelarse al abrir

---

## 1. Inicialización de base de datos

### Acción
Botón: `Init DB`

### Flujo
1. Usuario pulsa `Init DB`.
2. Controller dispara worker.
3. Worker llama adapter.
4. Adapter llama `engine.init_storage()`.
5. Al terminar, la UI actualiza estado y footer.

### Resultado esperado
- mensaje tipo `database initialized`
- estado de engine cambia a `ready`
- log de operación visible

---

## 2. Consulta de métricas

### Acción
Botón: `Metrics`

### Flujo
1. Usuario pulsa `Metrics`.
2. Worker llama `engine.get_metrics(days=...)`.
3. La respuesta se normaliza para UI.
4. Se renderiza en:
   - panel de métricas
   - resumen/KPIs
   - gráfica

### Resultado esperado
Aunque no haya inputs reales:
- totales en cero
- lista vacía o gráfica vacía elegante
- mensajes claros, no error falso

---

## 3. Ingest incremental

### Acción
Botón: `Ingest`

### Flujo
1. Usuario elige ruta o usa ruta preconfigurada.
2. Controller dispara `engine.ingest(paths=..., full=False)` en worker.
3. UI entra en estado `busy`.
4. Al terminar:
   - se actualiza status panel
   - se refrescan métricas
   - se registra salida/log

### Resultado esperado
Mostrar:
- archivos vistos
- archivos procesados
- errores
- estatus `ok`, `partial` o `failed`

---

## 4. Ingest completa

### Acción
Botón: `Full Ingest`

### Flujo
Igual al incremental, pero usando `full=True`.

### Precaución
Debe verse más “peligrosa” o de mayor impacto que `Ingest` normal.

---

## 5. Repair

### Acción
Botón: `Repair`

### Flujo
1. Usuario pulsa `Repair`.
2. Worker llama `engine.repair()`.
3. UI muestra progreso/estado ocupado.
4. Se presentan:
   - integrity check
   - estado de índices
   - FTS enabled o no

### Resultado esperado
Se refleja en log, footer y status panel.

---

## 6. Search

### Acción
Panel de búsqueda

### Flujo
1. Usuario escribe query.
2. Ajusta filtros:
   - tipo
   - fecha desde
   - fecha hasta
   - límite
3. Controller ejecuta `engine.search(...)`.
4. Results panel renderiza cards o tabla.

### Resultado esperado
Cada resultado debería mostrar mínimo:
- session_id
- timestamp
- tipo
- resumen corto
- señales de error/herramienta si aplica

### UX importante
- búsqueda vacía no debe explotar
- cero resultados debe verse como estado válido
- búsqueda no debe bloquear la interfaz

---

## 7. Selección de resultado y detalle

### Acción
Click en un resultado

### Flujo
1. Usuario selecciona card/fila.
2. Controller llama `engine.get_session_detail(session_id)`.
3. Detail panel muestra:
   - session metadata
   - timeline
   - events
   - errors
   - tools
   - records
   - insights
   - related sessions

### Resultado esperado
Este es el corazón analítico de la app.

---

## 8. Estado y monitoreo

### Panel fijo
Status/State panel

### Debe mostrar
- engine state
- root actual
- base de datos / tamaño / existencia
- última operación
- último ingest
- watcher state
- último error

### Footer
Debe servir para:
- feedback rápido
- último evento
- tono visual de salud (`good`, `warning`, `error`, `neutral`)

---

## 9. Logs / consola auxiliar

### Objetivo
Que el usuario vea qué pasó sin tener que abrir terminal aparte.

### Debe recibir
- inicio de operaciones
- fin de operaciones
- errores capturados
- salidas resumidas del adapter/worker

### Ideal
Panel inferior o lateral ocultable.

---

## 10. Gráfica

### Cuándo entra
Después de `Metrics`.

### Qué debería representar primero
Lo más útil para la primera versión:
- `daily_activity`
- `top_errors`
- quizá `top_tools`

### Regla
La gráfica es de soporte visual. No debe ser la fuente única de información.
Siempre debe existir también:
- resumen textual
- KPIs
- fallback vacío

---

## Mapeo recomendado a la consola prefabricada

Como la shell se conserva completa, el montaje con menor fricción sería así:

### Hero/header
Usar branding y estado general de SYNAPSE-X.

### Toolbar
Reemplazar acciones visibles por:
- Init DB
- Metrics
- Ingest
- Full Ingest
- Repair
- Toggle Logs / Toggle Sidebar

Ocultar acciones de demo que no sirvan al producto.

### Sidebar slot
Usarlo para:
- status panel
- filtros/search compacto
- rutas activas

### Main slot
Usarlo para:
- results panel
- detail panel
- metrics panel o vista apilada/segmentada

### Aux slot
Usarlo para:
- logs
- JSON raw
- diagnósticos
- related sessions

### Footer
Usarlo para:
- estado corto
- última acción
- salud del sistema

---

## Estados que la UI debe soportar sí o sí

### Empty
Sin datos, sin romperse.

### Ready
Lista para operar.

### Busy
Corriendo init/metrics/ingest/repair/search/detail.

### Partial
Cuando ingest termina con fallos parciales.

### Error
Cuando una operación falla pero la app sigue viva.

### Stale
Cuando la vista mostrada ya no coincide con el estado más reciente.

---

## Lo que falta implementar para que este flujo exista de verdad

1. `main_window.py` real
2. `controls_panel.py` real
3. `search_panel.py` real
4. `results_panel.py` real
5. `detail_panel.py` real
6. `metrics_panel.py` real
7. `state_panel.py` real
8. adapter backend-ui
9. workers/QThread o QRunnable
10. state store/view model
11. binding de toolbar del shell a acciones SYNAPSE-X
12. ocultar features de demo no útiles
13. normalización de payloads para UI
14. manejo consistente de errores, vacío y carga

---

## Respuesta final a la pregunta

### ¿Ya hay flujo de funcionamiento de la interfaz cuando el motor esté montado?

**Sí, pero solo como flujo objetivo/documentado e implícito en el backend.**

### ¿Ya está construido y amarrado?

**No.**
Todavía no existe el flujo funcional completo implementado dentro de la UI real.

### ¿La base actual alcanza para construirlo sin fricción absurda?

**Sí.**
Porque ya tienes estas tres piezas:

- shell visual reutilizable
- backend con API interna clara
- spec de áreas y comportamiento esperado

Lo que falta es el cableado limpio entre esas tres.

---

## Recomendación práctica

Tomar este documento como el **flujo canónico de operación** para la primera integración UI + motor.

La implementación debe buscar que el usuario pueda hacer, en este orden:

1. abrir
2. verificar estado
3. inicializar DB
4. pedir métricas
5. correr ingest/repair
6. buscar
7. seleccionar resultados
8. leer detalle
9. observar logs y estado

Si esa secuencia vive completa y estable, la interfaz ya queda funcional para crecer.
