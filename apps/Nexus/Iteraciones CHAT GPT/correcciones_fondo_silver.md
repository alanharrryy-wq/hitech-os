# Correcciones 1:1 para eliminar por completo fondos azules o negros y replicar el **silver case** en toda la app

## Cambio de criterio confirmado
**No quitar el silver case.**  
Se toma como referencia visual y se debe **replicar en todos los objetos**.

## Qué está pasando hoy
El azul/negro aparece por 4 frentes a la vez:

1. **La paleta base** ya nace oscura o azulada.
2. **El backdrop** pinta un canvas azul-negro detrás de todo.
3. **El stylesheet global** mete muchos `rgba(140, 235, 255, ...)` y varios fondos oscuros hardcodeados.
4. **Los ejemplos/workbench** vuelven a inyectar overrides propios, aunque arregles la base.

Si corriges solo una capa, el azul/negro vuelve a salir por otra. Hay que cerrar **las 4**.

---

## Paleta maestra recomendada para unificar todo en silver
Usa esta base como idioma visual único. La idea es **silver / graphite neutral**, sin cyan y sin negro puro.

### Reemplazo recomendado para `SILVER_FROST_CYAN`
Archivo: `pyside6_glass/theme.py`

```python
SILVER_FROST_CYAN = GlassPalette(
    shell_top="rgba(106, 112, 120, 0.36)",
    shell_bottom="rgba(72, 77, 84, 0.34)",
    shell_border="rgba(245, 248, 252, 0.22)",
    shell_border_hover="rgba(245, 248, 252, 0.34)",
    chrome_top="rgba(255, 255, 255, 0.060)",
    chrome_bottom="rgba(210, 216, 224, 0.028)",
    chrome_border="rgba(245, 248, 252, 0.12)",
    card_top="rgba(255, 255, 255, 0.055)",
    card_bottom="rgba(214, 220, 228, 0.022)",
    card_border="rgba(245, 248, 252, 0.10)",
    text_primary="#eef2f6",
    text_muted="#c8d0d8",
    text_inverse="#1a1d21",
    accent="#e3e8ee",
    accent_soft="rgba(245, 248, 252, 0.10)",
    button_top="rgba(255, 255, 255, 0.040)",
    button_bottom="rgba(214, 220, 228, 0.018)",
    button_border="rgba(245, 248, 252, 0.14)",
    danger_top="rgba(218, 170, 156, 0.17)",
    danger_bottom="rgba(145, 98, 86, 0.13)",
    danger_border="rgba(225, 182, 168, 0.26)",
    warning_top="rgba(219, 191, 145, 0.16)",
    warning_bottom="rgba(148, 120, 80, 0.12)",
    warning_border="rgba(226, 198, 157, 0.25)",
    success_top="rgba(151, 199, 176, 0.16)",
    success_bottom="rgba(96, 134, 116, 0.12)",
    success_border="rgba(171, 209, 189, 0.26)",
    input_bg="rgba(244, 247, 251, 0.085)",
    input_border="rgba(245, 248, 252, 0.15)",
    input_border_hover="rgba(245, 248, 252, 0.30)",
    progress_bg="rgba(244, 247, 251, 0.11)",
    progress_chunk_top="#edf1f5",
    progress_chunk_bottom="#d7dde4",
    tab_bg="rgba(255, 255, 255, 0.040)",
    tab_active_bg="rgba(255, 255, 255, 0.080)",
    tab_hold_bg="rgba(255, 255, 255, 0.055)",
    tab_pending_bg="rgba(181, 162, 124, 0.24)",
    tab_warning_bg="rgba(176, 137, 106, 0.24)",
    tab_border="rgba(245, 248, 252, 0.16)",
    tab_text="#eef2f6",
    tab_text_muted="#bcc5ce",
    panel_form_border="rgba(245, 248, 252, 0.14)",
    panel_data_border="rgba(245, 248, 252, 0.16)",
    panel_metrics_border="rgba(245, 248, 252, 0.15)",
    panel_detail_border="rgba(245, 248, 252, 0.16)",
    panel_summary_border="rgba(245, 248, 252, 0.15)",
    panel_aux_border="rgba(245, 248, 252, 0.14)",
)
```

---

## Correcciones 1:1

### 1) Cambiar la paleta base que hoy mete negro y azul
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `84-131`

#### Qué corregir
- `shell_top="rgba(13, 14, 18, 0.9)"`
- `shell_bottom="rgba(7, 8, 11, 0.93)"`
- `input_bg="rgba(5, 6, 10, 0.56)"`
- `progress_bg="rgba(5, 6, 10, 0.76)"`
- todos los bordes `rgba(140, 235, 255, ...)`

#### Qué hacer
Reemplazar esos tokens por la paleta silver neutral de arriba.  
**Esta es la corrección más importante** porque alimenta casi todos los objetos.

---

### 2) Matar la variante azul-negra alternativa o dejarla aliasada a silver
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `134-182`

#### Qué corregir
La variante `OBSIDIAN_ICE` sigue siendo azul/negra:
- `shell_top="rgba(21, 29, 44, 0.93)"`
- `shell_bottom="rgba(8, 13, 24, 0.95)"`
- `input_bg="rgba(18, 25, 39, 0.75)"`
- `progress_bg="rgba(16, 24, 38, 0.84)"`
- `tab_bg="rgba(30, 40, 56, 0.66)"`

#### Qué hacer
Tienes 2 opciones válidas:

**Opción A, la más limpia:**
- eliminar `obsidian_ice` del registro si ya no quieres que exista visualmente.

**Opción B, cero riesgo funcional:**
- dejar el id `obsidian_ice`, pero apuntarlo a la **misma paleta silver** para no romper nada que lo invoque.

Ejemplo:

```python
OBSIDIAN_ICE = SILVER_FROST_CYAN
```

Si no haces esto, siempre habrá alguna pantalla que pueda volver a verse azul/negra.

---

### 3) Cambiar el shell principal para que use silver y no highlight cyan
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `470-476`

#### Qué corregir
```python
QFrame#Shell {
    background: {_gradient(p.shell_top, p.shell_bottom)};
    border: ... rgba(140, 235, 255, 0.14);
}
QFrame#Shell:hover {
    border: ... rgba(140, 235, 255, 0.24);
}
```

#### Qué hacer
Cambiar todos los `rgba(140, 235, 255, ...)` por silver neutral.

#### Reemplazo recomendado
```python
border: 1px solid rgba(245, 248, 252, 0.16);
# hover
border: 1px solid rgba(245, 248, 252, 0.28);
```

---

### 4) Cambiar cards para que todas hereden el mismo silver case
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `494-500`, `850-858`

#### Qué corregir
Las cards usan gradiente de `card_top/card_bottom`, pero el borde sigue con cyan:
```python
border: ... rgba(140, 235, 255, 0.12)
```

#### Qué hacer
Cambiar borde a silver y dejar que **todas** las superficies tipo card usen la misma familia visual.

#### Reemplazo recomendado
```python
border: 1px solid rgba(245, 248, 252, 0.14)
```

Esto aplica a:
- `QFrame[card="true"]`
- `QFrame[card="muted"]`
- `QFrame[card="footer"]`
- `QFrame[assetRole="stat_pill"]`
- `QFrame[assetRole="control_card"]`
- `QFrame[assetRole="collapsible_section"]`
- `QFrame[assetRole="enhanced_slider"]`
- `QFrame[assetRole="parameter_panel"]`

---

### 5) Inputs: quitar el fondo casi negro
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `601-624`

#### Qué corregir
```python
background: {p.input_bg};
border: ... rgba(140, 235, 255, 0.16);
```

#### Qué hacer
- cambiar `input_bg` a silver translúcido
- quitar borde cyan

#### Reemplazo recomendado
```python
background: rgba(244, 247, 251, 0.085);
border: 1px solid rgba(245, 248, 252, 0.16);
# hover/focus
border: 1px solid rgba(245, 248, 252, 0.30);
```

Esto aplica a:
- `QLineEdit`
- `QComboBox`
- `QTextEdit`
- `QPlainTextEdit`
- `QListWidget`
- `QTreeWidget`
- `QTableWidget`

---

### 6) Botones: quitar el cyan de hover/pressed/primary
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `626-688`

#### Qué corregir
Hoy hay cyan en:
- `QPushButton:hover`
- `QPushButton:pressed`
- `QPushButton:focus`
- `QPushButton[variant="primary"]`
- `QPushButton[variant="ghost"]:hover`

#### Qué hacer
Todos esos fondos deben pasar a silver translúcido.

#### Reemplazo recomendado
```python
QPushButton {
    background: rgba(255, 255, 255, 0.030);
}
QPushButton:hover {
    border: 1px solid rgba(245, 248, 252, 0.28);
    background: rgba(255, 255, 255, 0.055);
}
QPushButton:pressed {
    border: 1px solid rgba(245, 248, 252, 0.36);
    background: rgba(255, 255, 255, 0.080);
}
QPushButton:focus {
    border: 1px solid rgba(245, 248, 252, 0.34);
    background: rgba(255, 255, 255, 0.070);
}
QPushButton[variant="primary"] {
    background: rgba(255, 255, 255, 0.060);
}
QPushButton[variant="ghost"]:hover {
    background: rgba(255, 255, 255, 0.050);
}
```

---

### 7) Tabs: quitar el azul del estado activo
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `691-747`

#### Qué corregir
- `tab_bg`
- `tab_active_bg`
- `tab_hold_bg`
- borde `rgba(140, 235, 255, ...)`

#### Qué hacer
Dejar tabs en silver translúcido.

#### Reemplazo recomendado
```python
QTabWidget#GlassWorkspaceTabs QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.080);
    border-color: rgba(245, 248, 252, 0.30);
}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:hover {
    border-color: rgba(245, 248, 252, 0.22);
}
QTabWidget#GlassWorkspaceTabs[tabVariant="segmented"] QTabBar::tab {
    border: 1px solid rgba(245, 248, 252, 0.16);
}
```

---

### 8) Progress bar: quitar el fondo oscuro
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `749-758`

#### Qué corregir
```python
background: {p.progress_bg};
border: ... rgba(140, 235, 255, 0.16)
```

#### Qué hacer
Usar silver glass también aquí.

#### Reemplazo recomendado
```python
background: rgba(244, 247, 251, 0.11);
border: 1px solid rgba(245, 248, 252, 0.16);
```

---

### 9) Icon buttons, chips, search bars, status pills: quitar cyan residual
**Archivo:** `pyside6_glass/theme.py`  
**Líneas:** `761-847`

#### Qué corregir
Aquí todavía vive mucho cyan:
- `QToolButton[assetRole="icon_button"]`
- `segment_button`, `filter_chip`, `toggle_pill`
- `QFrame[assetRole="search_bar"]`
- `QLabel[assetRole="status_pill"][statusKind="info"]`

#### Qué hacer
Cambiar todos esos estados de cyan a silver.

#### Reemplazo recomendado
```python
border: 1px solid rgba(245, 248, 252, 0.16)
background: rgba(255, 255, 255, 0.040)

# checked / info / hover fuerte
background: rgba(255, 255, 255, 0.075)
border: 1px solid rgba(245, 248, 252, 0.30)
```

---

### 10) Window chrome: el header ya es silver, pero los botones todavía nacen oscuros
**Archivo:** `pyside6_glass/atlas_styles.py`  
**Líneas:** `5-30`, sobre todo `18-30`

#### Qué corregir
```python
background: rgba(12, 21, 32, 0.20);
```

Y también los hovers/pressed cyan.

#### Qué hacer
Dejar el chrome en la misma familia silver que el shell.

#### Reemplazo recomendado
```python
QFrame#WindowChrome QPushButton {
    background: rgba(255, 255, 255, 0.040);
    border: 1px solid rgba(245, 248, 252, 0.12);
}
QFrame#WindowChrome QPushButton:hover {
    background: rgba(255, 255, 255, 0.070);
    border: 1px solid rgba(245, 248, 252, 0.26);
}
QFrame#WindowChrome QPushButton:pressed {
    background: rgba(255, 255, 255, 0.090);
    border: 1px solid rgba(245, 248, 252, 0.34);
}
```

---

### 11) El backdrop es la fuente más grande del azul-negro de fondo
**Archivo:** `pyside6_glass/backdrop.py`  
**Líneas clave:** `82-97`, `510-559`, `605-608`

#### Qué corregir
Hoy el silver backdrop realmente usa esto:
- `canvas_top="#04070d"`
- `canvas_bottom="#0f1824"`
- líneas/orbs cyan
- vignette negra al final

#### Qué hacer
Neutralizarlo a silver graphite, o apagarlo si no lo quieres.

#### Reemplazo recomendado si lo quieres conservar
```python
canvas_top=_qcolor_from_value("#6e747c", 1.0)
canvas_bottom=_qcolor_from_value("#4b5057", 1.0)
wash=_qcolor_from_value("#ffffff", 0.030)
border=_qcolor_from_value("#f1f4f7", 0.18)
line=_qcolor_from_value("#f1f4f7", 0.035)
sheen=_qcolor_from_value("#ffffff", 0.08)
orb_a=_qcolor_from_value("#ffffff", 0.10)
orb_b=_qcolor_from_value("#dfe5eb", 0.08)
orb_c=_qcolor_from_value("#c9d0d8", 0.06)
sparkle=_qcolor_from_value("#ffffff", 0.55)
star_soft=_qcolor_from_value("#f1f4f7", 0.14)
star_bright=_qcolor_from_value("#ffffff", 0.40)
```

#### Además
En el vignette final, quitar negro:
```python
vignette.setColorAt(1.0, QColor(0, 0, 0, 76 ...))
```
Debe quedar en silver gris suave, por ejemplo:
```python
vignette.setColorAt(1.0, QColor(120, 126, 134, 38))
```

Si este archivo no se toca, seguirás viendo fondo oscuro aunque todo lo demás quede silver.

---

### 12) El puente atlas también trae fallbacks oscuros/azules
**Archivo:** `pyside6_glass/atlas_theme_bridge.py`  
**Líneas:** `94-100`, `118-130`

#### Qué corregir
Fallbacks actuales:
- `#0f1824`
- `#1a2836`
- `#1f2f42`
- `#22d3ee`

#### Qué hacer
Cambiar esos fallbacks a neutrales:
```python
"canvas_bg" -> "#4b5057"
"header_fill" -> "#6e747c"
"legend_fill" -> "#7f858d"
"focus" -> "#eef2f6"
"halo_a" -> "#f1f4f7"
"halo_b" -> "#d9e0e7"
```

---

### 13) La escena crea el backdrop siempre; si quieres cero riesgo, deja opción de apagarlo
**Archivo:** `pyside6_glass/scene.py`  
**Líneas:** `53-62`

#### Qué hacer
Agregar una bandera tipo:
```python
use_backdrop: bool = True
```

Y si está en `False`, no montar `FrostedGlassBackdrop`.  
Esto te deja una salida rápida si en algún entorno el backdrop vuelve a ensuciar el fondo.

---

### 14) Demo app: tiene overrides propios que reintroducen oscuro y cyan
**Archivo:** `pyside6_glass/examples/demo_app.py`  
**Líneas:** `12-108`, sobre todo `25-58` y `83-103`

#### Qué corregir
El shell/card visual aquí sí va en dirección silver, **pero** el chrome button vuelve a meter oscuro:
```python
background: rgba(12, 21, 32, 0.44);
```

#### Qué hacer
Cambiarlo por silver:
```python
background: rgba(255, 255, 255, 0.050);
```

Y cambiar todos los estados cyan de hover/pressed a silver.

---

### 15) Catalog shell / workbench: todavía mete muchos selected/hover cyan
**Archivo:** `pyside6_glass/examples/catalog_shell.py`  
**Líneas:** `1814-2033`

#### Qué corregir
Aquí siguen vivos fondos cyan en:
- `1822`
- `1842`
- `1845`
- `1856`
- `1919`
- `1937`
- `1957`
- `2006`
- `2026`

#### Qué hacer
Cambiar todo lo que sea:
```python
rgba(140, 235, 255, ...)
```
por:
```python
rgba(245, 248, 252, ...)
```
o por silver translúcido equivalente.

#### Traducción práctica
- selected chips -> silver brillante
- hover -> silver medio
- separators -> silver tenue
- metric chips -> silver tenue
- dialogs internos -> silver glass

---

### 16) Quitar de la UI cualquier entrada que permita volver al modo obsidian
**Archivos:**
- `pyside6_glass/examples/catalog_builtin.py` líneas `439-442`
- `pyside6_glass/examples/compositions.py` líneas `157-167`

#### Qué corregir
Todavía se promociona `obsidian_ice` como tema válido.

#### Qué hacer
- cambiar descripción para que solo exista silver
- o reemplazar el ejemplo `obsidian_ice` por silver

Ejemplo:
```python
subtitle="Using silver_frost_cyan theme with compact density."
theme_id="silver_frost_cyan"
```

---

## Orden correcto de implementación
Hazlo en este orden para que no te engañe el resultado visual:

1. `theme.py` paleta base
2. `theme.py` stylesheet global
3. `atlas_styles.py` chrome
4. `backdrop.py`
5. `atlas_theme_bridge.py`
6. `examples/demo_app.py`
7. `examples/catalog_shell.py`
8. quitar/aliasar `obsidian_ice`

---

## Regla simple para que no vuelva a aparecer
Después de la corrección, en código productivo ya no deberían quedar estos patrones:

```bash
grep -RIn "rgba(140, 235, 255|#04070d|#0f1824|rgba(12, 21, 32|rgba(5, 6, 10|rgba(18, 25, 39|rgba(16, 24, 38)|obsidian_ice" pyside6_glass
```

Lo ideal es que solo sobrevivan en docs viejos o archivos históricos, no en la UI activa.

---

## Resultado esperado
Si aplicas todo lo anterior:
- el **silver case se conserva**
- se **replica en shell, cards, inputs, tabs, chips, dialogs, chrome y backdrop**
- desaparecen los fondos **azules**
- desaparecen los fondos **negros**
- no queda ninguna ruta visual que vuelva a activar `obsidian_ice`

---

## Resumen corto
La app no tiene "un" fondo azul/negro. Tiene un pequeño ejército.  
La solución correcta es:

- **mantener el silver case**
- **convertir la paleta base a silver neutral**
- **quitar cyan hardcodeado del stylesheet**
- **neutralizar el backdrop**
- **borrar o aliasar `obsidian_ice`**
- **limpiar overrides de demo/workbench**

Con eso sí se elimina **por completo** el azul/negro de los objetos y todo queda hablando el mismo idioma visual: **silver**.
