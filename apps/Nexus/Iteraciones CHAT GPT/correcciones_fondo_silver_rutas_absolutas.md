# Corrección 1:1 para eliminar fondo azul o negro y replicar el **silver case** en toda la app

## Base real que tomé
Tu proyecto descomprimido trae este módulo visual como núcleo:

`F:\repos\hitech-os\forgeos\shared\pyside6_glass`

## Regla principal
- **NO quitar `silver_frost_cyan`.**
- **Sí usar `silver_frost_cyan` como look maestro para toda la app.**
- **Sí eliminar todo fondo azul fuerte o negro duro de cualquier objeto visible.**
- **Sí convertir esos fondos a plata, graphite suave, humo claro o blanco translúcido.**

---

## Paleta objetivo única que debes replicar
Usa esta idea como referencia para todos los objetos, fondos, chrome, cards, inputs, tabs y backdrop:

```python
SILVER_CASE_MASTER = dict(
    shell_top="rgba(244, 246, 249, 0.88)",
    shell_bottom="rgba(218, 223, 229, 0.84)",
    shell_border="rgba(255, 255, 255, 0.42)",
    shell_border_hover="rgba(255, 255, 255, 0.62)",
    chrome_top="rgba(255, 255, 255, 0.54)",
    chrome_bottom="rgba(231, 235, 240, 0.36)",
    chrome_border="rgba(255, 255, 255, 0.30)",
    card_top="rgba(255, 255, 255, 0.44)",
    card_bottom="rgba(226, 231, 237, 0.30)",
    card_border="rgba(255, 255, 255, 0.28)",
    text_primary="#1f2329",
    text_muted="#5b6470",
    text_inverse="#ffffff",
    accent="#f7f9fb",
    accent_soft="rgba(255, 255, 255, 0.22)",
    button_top="rgba(255, 255, 255, 0.42)",
    button_bottom="rgba(226, 231, 237, 0.28)",
    button_border="rgba(255, 255, 255, 0.34)",
    input_bg="rgba(255, 255, 255, 0.34)",
    input_border="rgba(255, 255, 255, 0.26)",
    input_border_hover="rgba(255, 255, 255, 0.44)",
    progress_bg="rgba(224, 229, 235, 0.48)",
    progress_chunk_top="#f7f9fb",
    progress_chunk_bottom="#d8dde4",
    tab_bg="rgba(255, 255, 255, 0.26)",
    tab_active_bg="rgba(255, 255, 255, 0.38)",
    tab_hold_bg="rgba(236, 239, 243, 0.34)",
    tab_pending_bg="rgba(214, 205, 190, 0.34)",
    tab_warning_bg="rgba(219, 206, 189, 0.34)",
    tab_border="rgba(255, 255, 255, 0.30)",
    tab_text="#20252b",
    tab_text_muted="#67717d",
    panel_form_border="rgba(255, 255, 255, 0.24)",
    panel_data_border="rgba(245, 247, 250, 0.26)",
    panel_metrics_border="rgba(236, 239, 243, 0.26)",
    panel_detail_border="rgba(230, 234, 239, 0.26)",
    panel_summary_border="rgba(240, 243, 247, 0.26)",
    panel_aux_border="rgba(255, 255, 255, 0.22)",
)
```

---

# Qué corregir 1:1

## 1) Mantener el tema default en silver
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\contracts.py`

**Estado actual:**
- Línea 5 ya trae `DEFAULT_THEME_ID = "silver_frost_cyan"`

**Qué hacer:**
- **No moverlo.**
- **No cambiarlo a `obsidian_ice`.**

**Resultado esperado:**
- Toda la app sigue arrancando en silver case.

---

## 2) Rehacer la paleta `SILVER_FROST_CYAN` para que sea silver de verdad, no negro/cian
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\theme.py`

**Bloque actual a corregir:**
- Líneas aproximadas **84 a 131**
- El problema es que el tema “silver” trae fondos casi negros:
  - `shell_top="rgba(13, 14, 18, 0.9)"`
  - `shell_bottom="rgba(7, 8, 11, 0.93)"`
  - `input_bg="rgba(5, 6, 10, 0.56)"`
- También trae bordes/acento cian:
  - `panel_*_border="rgba(140, 235, 255, ...)"`

**Qué hacer:**
- Reemplaza todo ese bloque por una variante basada en la paleta `SILVER_CASE_MASTER` de arriba.
- En especial:
  - quita negros duros del shell
  - quita azul/cian de paneles
  - deja bordes blancos/plata translúcidos

**Resultado esperado:**
- El “silver case” ya no se va a ver como plateado sobre fondo negro.
- Shell, cards, inputs y tabs van a verse plateados de forma uniforme.

---

## 3) No usar `obsidian_ice` como referencia visual para nada que deba quedar final
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\theme.py`

**Bloque a vigilar:**
- Líneas aproximadas **134 a 181**
- Existe el tema `OBSIDIAN_ICE`, que sí es azul oscuro / negro.

**Qué hacer:**
- No lo borres necesariamente.
- Pero **no lo uses como default**, ni como variante visual final del producto si tu meta es quitar azul/negro.
- Déjalo solo como tema alterno de laboratorio o demo.

**Resultado esperado:**
- No se te cuela el look azul oscuro por un preset secundario.

---

## 4) Quitar los hardcodes cian del stylesheet principal
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\theme.py`

**Bloques actuales a corregir:**
- Líneas aproximadas **472, 476, 498, 509, 512, 516, 519, 523, 526, 532, 609, 623, 637, 638, 641, 642, 645, 646, 654, 668, 675, 676, 712, 716, 733, 751, 763, 768, 769, 793, 794, 799, 811, 819, 824, 830, 831, 847, 857**
- Todas esas líneas usan `rgba(140, 235, 255, ...)`

**Qué hacer:**
- Cambia esos hardcodes por tokens del palette `p.*`.
- Donde hoy tienes borde cian, usa estos equivalentes silver:

```python
p.shell_border
p.shell_border_hover
p.card_border
p.input_border
p.input_border_hover
p.button_border
p.accent_soft
```

**Regla práctica:**
- `rgba(140, 235, 255, 0.12)` → `rgba(255, 255, 255, 0.22)`
- `rgba(140, 235, 255, 0.16)` → `rgba(255, 255, 255, 0.26)`
- `rgba(140, 235, 255, 0.58)` → `rgba(255, 255, 255, 0.44)`
- `rgba(140, 235, 255, 0.86)` → `rgba(255, 255, 255, 0.62)`
- backgrounds cian suaves → `rgba(255, 255, 255, 0.08)` o `rgba(236, 239, 243, 0.16)`

**Resultado esperado:**
- Se eliminan halos azules de cards, panels, inputs, botones, tabs y estados hover/focus.

---

## 5) Arreglar el chrome superior para que no meta azul ni negro en botones
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\atlas_styles.py`

**Líneas actuales a corregir:**
- 13
- 34
- 35
- 38
- 39
- 42
- 43
- 46
- 47
- 50

**Problema actual:**
- Usa bordes cian directos `rgba(140, 235, 255, ...)`
- Usa fondo oscuro en botones del chrome: `rgba(12, 21, 32, 0.20)`

**Qué hacer:**
- Cambia el borde del chrome por plata translúcida.
- Cambia el fondo oscuro de botones por un vidrio claro.

**Reemplazos sugeridos:**
```python
background: rgba(255, 255, 255, 0.18);
border: 1px solid rgba(255, 255, 255, 0.22);
```

Hover:
```python
background: rgba(255, 255, 255, 0.28);
border: 1px solid rgba(255, 255, 255, 0.42);
```

Pressed:
```python
background: rgba(236, 239, 243, 0.34);
border: 1px solid rgba(255, 255, 255, 0.56);
```

**Resultado esperado:**
- Los controles de la ventana dejan de verse azul-neón o negro humo.
- Se integran al mismo silver case.

---

## 6) Quitar el canvas oscuro del bridge visual
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\atlas_theme_bridge.py`

**Líneas actuales a corregir:**
- 94
- 119
- 120
- 123
- 126

**Problema actual:**
- Para el silver theme se inyecta fondo oscuro:
  - `#04070d`
  - `#0f1824`
- También mete línea/acento cian:
  - `#8cefff`

**Qué hacer:**
- Cambia esos valores por plata/gris claro.

**Reemplazos sugeridos:**
```python
canvas_top = _qcolor_from_value("#f6f8fb", 1.0)
canvas_bottom = _qcolor_from_value("#d9dee5", 1.0)
wash = _qcolor_from_value("#ffffff", 0.20 if selector_variant else 0.24)
border = _qcolor_from_value("#ffffff", 0.30 if selector_variant else 0.24)
line = _qcolor_from_value("#ffffff", 0.14)
sheen = _qcolor_from_value("#ffffff", 0.22)
orb_a = _qcolor_from_value("#ffffff", 0.20 if selector_variant else 0.16)
orb_b = _qcolor_from_value("#eef2f6", 0.18 if selector_variant else 0.14)
orb_c = _qcolor_from_value("#d9dee5", 0.14 if selector_variant else 0.10)
star_soft = _qcolor_from_value("#ffffff", 0.20)
star_bright = _qcolor_from_value("#ffffff", 0.70)
```

**Resultado esperado:**
- El bridge deja de reinyectar fondo azul/negro aunque el resto del theme ya esté plateado.

---

## 7) Quitar el canvas oscuro del backdrop real
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\backdrop.py`

**Líneas actuales a corregir:**
- 84
- 85
- 88
- 91

**Problema actual:**
- El backdrop de silver trae otra vez:
  - `#04070d`
  - `#0f1824`
  - `#8cefff`

**Qué hacer:**
- Igual que en `atlas_theme_bridge.py`, sustitúyelo por la misma paleta silver clara.
- El criterio aquí es: **si el objeto es silver, el fondo no puede regresar a azul/negro por debajo**.

**Resultado esperado:**
- El fondo base deja de contaminar todos los objetos visibles.

---

## 8) Quitar los lavados cian y el viñeteado negro del backdrop pintado
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\backdrop.py`

**Bloque actual a corregir:**
- Método `_paint_silver_field(...)`
- Aproximadamente líneas **507 a 559**

**Problemas actuales:**
- top wash con cian:
  - `QColor(156, 224, 255, 8)`
- segunda banda con cian:
  - `QColor(140, 239, 255, ...)`
- viñeta negra:
  - `QColor(0, 0, 0, 76)`
  - `QColor(0, 0, 0, 58)`

**Qué hacer:**
- Reemplaza el cian por blanco/plata.
- Reemplaza la viñeta negra por gris plata translúcido o elimínala casi por completo.

**Reemplazos sugeridos:**
```python
top_wash.setColorAt(0.0, QColor(255, 255, 255, 28))
top_wash.setColorAt(0.38, QColor(240, 243, 247, 16))
top_wash.setColorAt(1.0, QColor(255, 255, 255, 0))
```

Segunda banda:
```python
color=QColor(255, 255, 255, 22 if self._variant == "selector" else 16)
```

Viñeta:
```python
vignette.setColorAt(0.0, QColor(255, 255, 255, 0))
vignette.setColorAt(0.78, QColor(255, 255, 255, 0))
vignette.setColorAt(1.0, QColor(210, 216, 224, 26 if self._variant == "selector" else 18))
```

**Resultado esperado:**
- El backdrop sigue dando profundidad, pero ya no “ensucia” con negro o azul.

---

## 9) Quitar cualquier borde o relleno cian de widgets interactivos
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\theme.py`

**Bloques actuales a corregir:**
- Inputs: aprox. líneas **609 a 623**
- Buttons: aprox. líneas **627 a 676**
- Tabs / estados / otros widgets: aprox. líneas **712 a 857**

**Qué hacer:**
- Todo `hover`, `focus`, `pressed`, `selected`, `active` debe cambiar de cian a plata.
- No metas azul para indicar interacción.
- Usa contraste por brillo, no por color.

**Guía visual:**
- normal = vidrio blanco suave
- hover = vidrio blanco más brillante
- pressed = plata ligeramente más densa
- focus = borde blanco limpio
- selected = plata clara, no azul

**Resultado esperado:**
- Ningún objeto cambia a azul al interactuar.

---

## 10) Si quieres cero azul en gráficas, también corrige la paleta de charts
**Ruta absoluta:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass\charts.py`

**Línea actual a corregir:**
- 146

**Problema actual:**
- La paleta `silver_frost` todavía incluye `#8cefff`

**Qué hacer:**
- Sustituye esa paleta por tonos silver neutrales.

**Reemplazo sugerido:**
```python
("#f8fafc", "#d9dee5", "#bcc4ce", "#eef2f6")
```

**Resultado esperado:**
- Las gráficas ya no van a romper el lenguaje silver con cyan.

---

## 11) Si usas demos o composiciones, quítales el tema oscuro para que no te confundan
**Rutas absolutas:**
- `F:\repos\hitech-os\forgeos\shared\pyside6_glass\examples\compositions.py`
- `F:\repos\hitech-os\forgeos\shared\pyside6_glass\examples\demo_app.py`

**Puntos actuales a corregir:**
- `examples\compositions.py` líneas 160 y 166 hablan de `obsidian_ice`
- `examples\demo_app.py` línea 90 usa fondo oscuro en chrome buttons

**Qué hacer:**
- Cambia demos a `silver_frost_cyan`
- Quita backgrounds oscuros de botones demo

**Resultado esperado:**
- Tus ejemplos ya no te devuelven visualmente a azul/negro y no confunden la validación manual.

---

## 12) Revisión final obligatoria
**Ruta base a revisar:**
`F:\repos\hitech-os\forgeos\shared\pyside6_glass`

**Busca y elimina estos valores visibles del look final:**

```text
rgba(140, 235, 255,
rgba(12, 21, 32,
#8cefff
#04070d
#0f1824
obsidian_ice
```

**Ojo:**
- `obsidian_ice` puede existir como tema alterno técnico.
- Lo que no debe pasar es que siga participando en el look final que estás buscando.

---

# Orden de implementación recomendado
1. `contracts.py` → confirmar que silver sigue como default
2. `theme.py` → rehacer `SILVER_FROST_CYAN`
3. `theme.py` → quitar hardcodes cian del stylesheet principal
4. `atlas_styles.py` → neutralizar chrome
5. `atlas_theme_bridge.py` → quitar canvas oscuro/cian
6. `backdrop.py` → quitar canvas oscuro/cian
7. `backdrop.py` → quitar viñeta negra y wash cian
8. `charts.py` → neutralizar charts si también quieres cero azul en data viz
9. `examples\*.py` → alinear demos al silver real

---

# Resumen brutalmente claro
Lo que hoy te mantiene el azul/negro vivo **no es el nombre del tema**, sino estos tres focos:

1. `silver_frost_cyan` todavía trae bases casi negras
2. el stylesheet principal trae un montón de `rgba(140, 235, 255, ...)` hardcodeado
3. el backdrop / bridge vuelve a inyectar `#04070d`, `#0f1824` y `#8cefff`

Si corriges esos 3 frentes con la paleta silver clara, el fondo azul o negro desaparece de manera real y consistente en toda la app, **sin quitar el silver case**, sino más bien **replicándolo bien en todo**.
