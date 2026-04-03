# Atlas parity visual 1:1 para `shared/pyside6_glass`

## Veredicto corto
No está **1:1 con Atlas** todavía.

Lo más cerca está en:
- `scene.py`
- gran parte de `backdrop.py`

Lo que **sí rompe la igualdad exacta** hoy es esto:
1. `backdrop.py` todavía trae valores distintos a Atlas en el branch `silver`.
2. `backdrop.py` para temas no-silver usa un sistema de tokens simplificado, distinto al pipeline real de Atlas.
3. `chrome.py` no es el mismo componente que Atlas.
4. falta la capa reusable de `apply_shadow + repolish + enable_card_hover`.
5. falta el controlador reusable de resize frameless.
6. `theme.py` no trae la capa de overrides finales que Atlas sí aplica encima del stylesheet base.
7. `controls.py` no aplica el remate visual final de Atlas a los botones.

---

## Lo más importante
Si quieres que quede **exactamente igual a Atlas**, no basta con mover unos alpha.

La ruta correcta es:
- **copiar exacto el sistema visual final de Atlas**
- y dejar `shared/pyside6_glass` como el lugar único donde viva esa paridad

Si solo corriges colores, vas a quedar “parecido”.
Si corriges **backdrop + chrome + effects + frameless resize + stylesheet override**, ahí sí quedas **Atlas real**.

---

## Matriz exacta de cambios

| Prioridad | Archivo | Estado vs Atlas | Qué hacer | ¿Crear algo nuevo? | Cómo conectarlo |
|---|---|---|---|---|---|
| 1 | `shared/pyside6_glass/backdrop.py` | **No exacto** | corregir constantes `silver` y portar la lógica no-silver de Atlas | No, pero sí requiere apoyo de tema | `scene.py` ya lo usa; al corregirlo, pega directo |
| 2 | `shared/pyside6_glass/chrome.py` | **No exacto** | reemplazar el chrome actual por el de Atlas | No | lo siguen usando las ventanas/dialogs que importan `WindowChromeBar` |
| 3 | `shared/pyside6_glass/theme.py` | **Base correcta, final no exacta** | agregar capa de overrides estilo Atlas | Sí, conviene crear `atlas_styles.py` | `scene.py` o `theme.py` deben concatenar base + overrides |
| 4 | `shared/pyside6_glass/controls.py` | **Base correcta, acabado no exacto** | aplicar shadow/repolish como Atlas | No, o crear helper pequeño | quien llame `create_button()` recibe el acabado Atlas |
| 5 | `shared/pyside6_glass/frameless.py` | **Falta** | crear controlador de resize frameless | **Sí** | los dialogs deben instanciar `FramelessResizeController(self, margin=8)` |
| 6 | `shared/pyside6_glass/effects.py` | **Falta** | mover `apply_shadow`, `repolish`, `enable_card_hover` | **Sí** | `controls.py`, dialogs y cards deben importarlo |
| 7 | `shared/pyside6_glass/scene.py` | **Casi bien** | solo conectar backdrop exacto + stylesheet exacto | No | aquí se activa la paridad real |
| 8 | `shared/pyside6_glass/__init__.py` | **Incompleto para Atlas** | exportar lo nuevo | No | re-exportar `FramelessResizeController`, helpers y overrides |

---

## 1) `backdrop.py`

## Archivo a cambiar
`shared/pyside6_glass/backdrop.py`

## Qué está mal hoy
En el branch `silver`, estos valores **no coinciden** con Atlas:

### Hoy en `shared`
- `border = "#f0f5ff"` con alpha `0.19 / 0.15`
- `line = "#ffffff"` con alpha `0.034`
- `orb_b = "#d8e2f1"` con alpha `0.13 / 0.10`

### En Atlas debe ser
- `border = "#e8f6ff"` con alpha `0.20 / 0.16`
- `line = "#8cefff"` con alpha `0.05`
- `orb_b = "#8cefff"` con alpha `0.15 / 0.12`

## Cambio exacto
Cambia **solo** esos tres bloques primero.

## Resultado
Con eso, el tema `silver_frost_cyan` deja de verse lavado y recupera el feeling Atlas en:
- borde del glass
- líneas de sheen
- orb secundaria

## Pero ojo
Eso **no alcanza** para 1:1 completo.

### El otro problema real en `backdrop.py`
Para temas no-silver, `shared` usa esto:
- `get_theme_manifest(theme_id).palette`
- `shell_top`, `shell_bottom`, `accent_soft`, `button_border`, etc.

Atlas usa otro pipeline visual:
- mezcla de tokens tipo `canvas_bg`, `header_fill`, `legend_fill`, `focus`, `legend_stroke`, `header_stroke`, `halo_a`, `halo_b`
- con mezclas tipo `_mix_hex(...)`
- y reglas distintas para `dark` / `silver` / `selector` / `progress`

## Si quieres 1:1 real
Dentro de este mismo archivo haz esto:
- deja `_qcolor_from_value()` y `FrostedGlassBackdrop` como base
- reemplaza la rama no-silver de `_glass_palette()` por la lógica exacta de Atlas

## Si no quieres ensuciar `backdrop.py`
Crea este archivo nuevo:
- `shared/pyside6_glass/atlas_theme_bridge.py`

## Qué debe vivir ahí
Una función tipo:
- `resolve_atlas_glass_palette(theme_id: str, variant: str) -> _GlassPalette`

## Cómo conectarlo
En `backdrop.py`:
- importas `resolve_atlas_glass_palette`
- `_glass_palette()` delega ahí para el branch no-silver

## Recomendación exacta
Si el objetivo es **igualdad total**, yo **sí** lo separaría así:
- `backdrop.py` = renderer
- `atlas_theme_bridge.py` = traducción exacta del sistema de color Atlas

Porque ahí está el corazón del look.

---

## 2) `chrome.py`

## Archivo a cambiar
`shared/pyside6_glass/chrome.py`

## Estado actual
Está funcional, pero **no es el mismo componente que Atlas**.

## Diferencias reales
### `shared` hoy
- usa `QToolButton`
- usa icon pack (`minus`, `square`, `x`)
- el icono de la barra también viene por `apply_icon(...)`
- no actualiza título en `WindowTitleChange`
- no replica exactamente el comportamiento de drag/max/restore de Atlas

### Atlas
- usa `QPushButton`
- usa texto literal: `—`, `□`, `×`
- usa `❐` al restaurar
- usa `QLabel("▣")` como icono de chrome
- escucha `WindowTitleChange` y `WindowStateChange`
- la lógica de drag está cerrada exactamente al comportamiento frameless que Atlas espera

## Cambio exacto
Reemplaza `WindowChromeBar` completo por la versión Atlas.

## No lo medio adaptes
Aquí no conviene “parchar”.

Si quieres paridad exacta:
- cambia toda la clase
- deja los mismos tamaños
- deja los mismos textos
- deja la misma lógica de eventos

## Conexión
No hay que cambiar `scene.py`.
Solo asegúrate de que los dialogs/ventanas sigan importando:
- `from shared.pyside6_glass.chrome import WindowChromeBar`

---

## 3) `frameless.py` **nuevo**

## Archivo a crear
`shared/pyside6_glass/frameless.py`

## Por qué
En Atlas existe esto y en `shared` **no está**:
- `_FramelessResizeCorner`
- `FramelessResizeController`
- helpers `_global_point_from_event`, `_local_point_from_event`
- constantes `_EDGE_NONE`, `_EDGE_LEFT`, `_EDGE_TOP`, `_EDGE_RIGHT`, `_EDGE_BOTTOM`

Sin eso, el comportamiento visual/interactivo de la ventana **no es Atlas completo**.

## Qué meter ahí
Mueve desde Atlas:
- `_EDGE_NONE`, `_EDGE_LEFT`, `_EDGE_TOP`, `_EDGE_RIGHT`, `_EDGE_BOTTOM`
- `_global_point_from_event`
- `_local_point_from_event`
- `_FramelessResizeCorner`
- `FramelessResizeController`

## Cómo conectarlo
En cada dialog/ventana frameless:

```python
self._resize_controller = FramelessResizeController(self, margin=8)
```

## Además
Re-exporta en `__init__.py`:
- `FramelessResizeController`

---

## 4) `effects.py` **nuevo**

## Archivo a crear
`shared/pyside6_glass/effects.py`

## Por qué
Atlas usa estos helpers por todos lados y en `shared` no están como pieza core:
- `apply_shadow(...)`
- `repolish(...)`
- `_HoverCardFilter`
- `enable_card_hover(...)`

Hoy eso solo aparece regado en examples, no como contrato central reusable.

## Qué meter ahí
Desde Atlas mueve:
- `apply_shadow`
- `repolish`
- `_HoverCardFilter`
- `_CARD_HOVER_FILTER`
- `enable_card_hover`

## Cómo conectarlo
### En `controls.py`
para rematar botones con el mismo shadow final Atlas.

### En tus dialogs/pantallas
para:
- hero cards
- footer cards
- paneles
- preview cards
- body cards

## Re-exportar
En `__init__.py` exporta:
- `apply_shadow`
- `repolish`
- `enable_card_hover`

---

## 5) `controls.py`

## Archivo a cambiar
`shared/pyside6_glass/controls.py`

## Estado actual
Correcto como fábrica base, pero **no trae el acabado final Atlas**.

## Qué le falta
Después de crear el botón, Atlas aplica:
- `button.setEnabled(...)`
- `button.setAutoDefault(...)`
- shadow por variante
- `repolish(button)`

## Valores exactos Atlas
### Shadow alpha
- `primary`: `28`
- `secondary`: `14`
- `success`: `22`
- `danger`: `16`
- fallback: `14`

### Shadow blur
- `primary`: `16.0`
- resto: `12.0`

### Offset
- `y_offset = 4.0`

## Cambio exacto
Tienes dos opciones.

### Opción correcta para 1:1
Modificar `create_button()` dentro de `controls.py` para que ya salga con el acabado Atlas.

### Opción más limpia
Crear:
- `shared/pyside6_glass/controls_atlas.py`

con una función:
- `create_button(...)`

que envuelva a la de `controls.py` y luego aplique:
- `apply_shadow(...)`
- `repolish(...)`

## Cómo conectarlo
Si creas wrapper:
- en `__init__.py` re-exporta el wrapper Atlas en vez del base

Si no creas wrapper:
- mete el acabado directamente en `controls.py`

## Mi recomendación
Para evitar dos sabores de botón, **sí lo metería directo en `controls.py`**.

---

## 6) `theme.py`

## Archivo a cambiar
`shared/pyside6_glass/theme.py`

## Estado actual
Sirve como stylesheet base reusable.
Pero Atlas **no termina ahí**.

Atlas hace esto:
- toma `shared_build_stylesheet(theme_id)`
- y luego le concatena `build_app_stylesheet(theme_id)`
- esa segunda capa es la que deja la UI “Atlas final”

## Entonces el problema
`theme.py` hoy da una base buena,
pero **no da el remate exacto Atlas**.

## Archivo nuevo recomendado
`shared/pyside6_glass/atlas_styles.py`

## Qué debe vivir ahí
Porta desde Atlas:
- `build_app_stylesheet(theme_id)`

No metas ahí el backdrop.
Solo la capa de overrides finales de stylesheet.

## Cómo conectarlo
### Ruta simple
Modificar `theme.py` para agregar una función nueva:

- `build_stylesheet_exact_atlas(theme_id, ...)`

que haga:
- `base = build_stylesheet(...)`
- `overrides = build_app_stylesheet(...)`
- `return base + "\n" + overrides`

### Ruta más limpia
Dejar `build_stylesheet()` intacta
y en `scene.py` usar:
- `build_stylesheet_exact_atlas(theme_id)`

## Mi recomendación
Haz esto:
- `theme.py` se queda como base
- `atlas_styles.py` guarda la capa final Atlas
- `scene.py` decide si aplica base o exacta

Eso mantiene orden y no rompe consumers genéricos.

---

## 7) `scene.py`

## Archivo a cambiar
`shared/pyside6_glass/scene.py`

## Estado actual
La estructura está bien.
Este archivo **ya es el punto correcto de conexión**.

## Lo que debe hacer para quedar Atlas
### 1. aplicar stylesheet exacto Atlas
No solo `build_stylesheet(theme_id)`.
Debe usar la versión que concatena base + overrides Atlas.

### 2. usar el `FrostedGlassBackdrop` ya corregido
Eso ya pasa aquí.

## Cambio exacto
Cambia esta parte conceptual:
- donde hoy aplica `build_stylesheet(theme_id)`

por:
- `build_stylesheet_exact_atlas(theme_id)`

## Resultado
Con eso, cualquier dialog construido por `build_glass_dialog_scene(...)` ya sale con el look correcto.

---

## 8) `__init__.py`

## Archivo a cambiar
`shared/pyside6_glass/__init__.py`

## Qué falta exportar si haces la portación correcta
Si creas los archivos nuevos, exporta:
- `FramelessResizeController`
- `apply_shadow`
- `repolish`
- `enable_card_hover`
- `build_stylesheet_exact_atlas`

Si no los exportas, el paquete queda funcional pero mal amarrado.

---

## Lo que NO hace falta tocar
No toques esto para la paridad Atlas visual:
- `catalog.py`
- `contracts.py`
- `data.py`
- `dashboard.py`
- `persistence.py`
- `runtime.py`
- docs varias

La paridad real está concentrada en:
- `backdrop.py`
- `chrome.py`
- `theme.py`
- `scene.py`
- `controls.py`
- `frameless.py` nuevo
- `effects.py` nuevo

---

## Orden exacto de implementación

## Fase 1. Lo obligatorio para que deje de verse distinto
1. corregir `backdrop.py` silver constants
2. reemplazar `chrome.py` por la versión Atlas
3. crear `frameless.py`
4. crear `effects.py`
5. ajustar `controls.py`

## Fase 2. Lo que lo vuelve realmente 1:1
6. crear `atlas_styles.py`
7. conectar esa capa desde `theme.py` o `scene.py`
8. portar la lógica no-silver exacta de `_glass_palette()` usando bridge Atlas

---

## Mi recomendación final
Si tu objetivo literal es:

> “quiero asegurarme de que sea exactamente igual a Atlas”

entonces haz esto **sin inventar**:

- `backdrop.py` = copiar la lógica final de Atlas
- `chrome.py` = copiar la clase Atlas
- `frameless.py` = extraer desde Atlas
- `effects.py` = extraer desde Atlas
- `theme.py` + `atlas_styles.py` = reproducir base + overrides Atlas
- `controls.py` = meter acabado final Atlas
- `scene.py` = solo conectar todo

## Traducción brutal
- si solo corriges color: queda “parecido”
- si corriges solo backdrop: queda “mucho más cerca”
- si haces los 7 puntos de arriba: queda **Atlas de verdad**

---

## Resumen ejecutable

### Cambiar ya
- `shared/pyside6_glass/backdrop.py`
- `shared/pyside6_glass/chrome.py`
- `shared/pyside6_glass/controls.py`
- `shared/pyside6_glass/theme.py`
- `shared/pyside6_glass/scene.py`
- `shared/pyside6_glass/__init__.py`

### Crear
- `shared/pyside6_glass/frameless.py`
- `shared/pyside6_glass/effects.py`
- `shared/pyside6_glass/atlas_styles.py`
- opcional: `shared/pyside6_glass/atlas_theme_bridge.py`

### Conectar
- dialogs -> `FramelessResizeController(self, margin=8)`
- cards/buttons -> `apply_shadow`, `repolish`, `enable_card_hover`
- `scene.py` -> stylesheet exacto Atlas
- `backdrop.py` -> palette exacta Atlas
- `__init__.py` -> exportar todo lo nuevo

---

## Criterio de aceptación
Solo considéralo “igual a Atlas” si cumples esto:
- mismo backdrop
- mismo chrome
- mismo resize frameless
- mismo shadow behavior
- mismo hover behavior
- mismo stylesheet final
- misma lógica de tema para default silver

Si falta uno, todavía no es Atlas exacto.
