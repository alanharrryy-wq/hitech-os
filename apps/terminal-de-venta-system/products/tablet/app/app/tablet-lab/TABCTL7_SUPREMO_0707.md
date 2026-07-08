# TABCTL7 SUPREMO — Matriz de Capas, Roles, Estados y Controles

**Proyecto:** PRISMA / hitech-os / Tablet original / `/tablet-lab`
**Archivo base:** `LAYER_ROLE_MATRIX_TABCTL7_0707.md`
**Versión propuesta:** TABCTL7 SUPREMO 0707
**Propósito:** convertir `/tablet-lab` en una cabina visual intuitiva, poderosa y segura para diseñar por objetivo humano, no por perilla críptica.
**Superficie permitida:** laboratorio visual.
**Superficies excluidas:** POS real, checkout real, carrito real, PC, Mobile, Cloud Center, deploy, D1, Prisma, puertos, procesos, lockfiles.
**Regla madre visual:** **los menos contenedores posibles**. Sólo se permite panel sobre panel cuando sea necesario para un efecto óptico real: borde, brillo especular, refracción, gota/liquid glass, máscara, highlight, sombra óptica o tratamiento de borde.

---

## 0. Resumen brutalmente simple

TABCTL7 ya no debe sentirse como cabina de avión soviética con 700 interruptores sin etiqueta.

Debe sentirse así:

```txt
1. Elige qué estás editando:
   Grupo visual → Componente → Capa → Rol → Parte fina

2. Elige estado:
   Base / Hover / Focus / Pressed / Selected / Active / Disabled / Loading / Error / Success

3. Elige qué quieres cambiar:
   Material / Color / Tipografía / Forma / Luz / Movimiento / Estado / Layout / Datos

4. Ajusta sólo controles aplicables:
   Si es texto: texto.
   Si es botón: botón.
   Si es fondo: fondo.
   Si es tabla: tabla.
   Si es número: número.

5. Decide alcance:
   Sólo esta parte / roles iguales / capa / componente / grupo / preset completo

6. Guarda receta:
   Preset humano + tokens técnicos + rollback visual
```

**Objetivo final:** que el usuario pueda decir “quiero el botón más vidrio mint, con texto más compacto y hover más vivo” y la cabina muestre exactamente esas perillas, no una piñata de sliders.

---

## 1. Principios de diseño que mandan

### 1.1 No controles fantasma

Cada control debe explicar:

| Campo | Significado |
|---|---|
| `controlId` | Nombre técnico estable |
| `nombreHumano` | Etiqueta entendible |
| `aplicaA` | Tipos donde aparece |
| `noAplicaA` | Tipos donde se oculta |
| `estado` | Base, hover, selected, disabled, etc. |
| `alcance` | Parte, tipo, capa, componente, grupo |
| `valorCero` | Qué significa 0 de verdad |
| `fallback` | Qué pasa si no hay soporte |
| `riesgoVisual` | Bajo, medio, alto |
| `preview` | Qué cambia en vivo |
| `tokenCSS` | Variable CSS que toca |

### 1.2 Cada perilla debe tener una frase humana

Ejemplos:

| Control técnico | Etiqueta humana | Frase humana |
|---|---|---|
| `backdropBlur` | Blur del fondo | “Qué tanto se derrite lo que está detrás.” |
| `glassAlpha` | Transparencia del vidrio | “Qué tanto deja pasar el fondo.” |
| `edgeShine` | Brillo de borde | “La rayita premium del canto.” |
| `stateHoverTone` | Color al pasar encima | “Cómo responde cuando el dedo lo ronda.” |
| `fontMood` | Personalidad tipográfica | “Compacta, elegante, técnica, amable o contundente.” |
| `gradientStops` | Paradas del degradado | “Cuántos colores lleva la salsa.” |

### 1.3 El valor cero debe apagar de verdad

| Control | 0 significa |
|---|---|
| `glassAlpha = 0` | Fondo transparente real, sin velo blanco residual |
| `backdropBlur = 0` | `backdrop-filter: none` |
| `textGlow = 0` | Sin sombra/glow fantasma |
| `borderAlpha = 0` | Sin borde visible ni pseudo-borde |
| `shadowDepth = 0` | Sin sombra |
| `edgeShine = 0` | Sin highlight especular |
| `noiseAmount = 0` | Sin textura/noise |
| `stateOverlayAlpha = 0` | Sin overlay de estado |
| `motionAmount = 0` | Sin animación ni transform |
| `hoverLift = 0` | Sin elevación al hover |

### 1.4 Nada de cochinero estructural

1. No meter contenedores extra por flojera.
2. Usar `data-widget-group`, `data-component`, `data-layer`, `data-role`, `data-part`, `data-kind`, `data-state`.
3. Usar variables CSS por target.
4. Usar pseudo-elementos sólo para efectos ópticos reales.
5. No usar `!important`.
6. No dependencias nuevas.
7. No tocar POS real.
8. No correr Prisma.
9. No matar procesos.
10. No tocar puertos.
11. No modificar `package.json`.
12. No modificar lockfiles.

---

## 2. Gramática visual TABCTL7

La matriz correcta queda así:

```txt
Grupo visual
→ Componente
→ Capa
→ Rol
→ Parte fina
→ Tipo
→ Estado
→ Variante
→ Controles aplicables
→ Alcance
→ Herencia / override
→ Preset / receta
```

### 2.1 Definiciones

| Nivel | Qué es | Ejemplo |
|---|---|---|
| Grupo visual | Familia grande | `POS Product Set` |
| Componente | Pieza repetible | `Product Card` |
| Capa | Zona visual | `Card base` |
| Rol | Función | `Price number` |
| Parte fina | Subparte interna | `Currency cents` |
| Tipo | Clase técnica | `numericText` |
| Estado | Interacción o status | `hover`, `selected`, `disabled` |
| Variante | Estilo macro | `premium`, `danger`, `ghost` |
| Control | Perilla aplicable | `numberGlow` |
| Alcance | Cuánto afecta | `Sólo esta parte` |
| Preset | Receta guardable | `Promo Card Mint Glow` |

### 2.2 Ruta ejemplo

```txt
POS Product Set
→ Product Card
→ Price zone
→ Price number
→ Currency integer
→ numericText
→ selected
→ promo
→ numberColor, numberSize, numberGlow, tabularMode
→ Sólo esta parte
→ Override local
→ Guardar preset de rol
```

---

## 3. Modelo de selección para usuario

### 3.1 Selector principal

```txt
[Grupo visual]       POS Product Set
[Componente]         Product Card
[Capa]               Price zone
[Rol]                Price number
[Parte fina]         Currency integer
[Estado]             Base / Hover / Selected
[Qué cambiar]        Número / Color / Glow
[Alcance]            Sólo esta parte
```

### 3.2 Selector rápido por intención

El usuario no siempre piensa en capas. A veces piensa en intenciones.

| Intención humana | TABCTL7 traduce a |
|---|---|
| “Quiero que se vea más premium” | Material + glass + borde + sombra + tipografía |
| “Quiero que el botón mande más” | Botón + CTA + hover + glow + altura |
| “Quiero que el precio grite menos” | Numeric text + tamaño + peso + glow + opacidad |
| “Quiero más aire” | Spacing + padding + gap + line height |
| “Quiero más contraste” | Color + veil + shadow + accessibility check |
| “Quiero que parezca desactivado” | Disabled state + frost + opacity + cursor + contrast |
| “Quiero que sólo cambie al seleccionar” | State = selected, base intacto |
| “Quiero mezclar colores” | Color Studio + gradient + color-mix |
| “Quiero otra textura/material” | Material Studio |
| “Quiero fondo borroso” | Background/Backdrop Studio |
| “Quiero neon glass” | Glow + glass + border + highlight |
| “Quiero non-gaussian glow” | Glow avanzado con caída custom, no blur común |

### 3.3 Modo novato y modo pro

| Modo | Qué muestra |
|---|---|
| `Simple` | 5 a 8 controles humanos por target |
| `Pro` | Controles avanzados por familia |
| `Forense` | Tokens, variables, herencia, origen del valor |
| `Receta` | Presets y combinación de estilos |
| `Comparar` | Antes/después y diff de tokens |
| `Seguro` | Sólo controles de bajo riesgo |

---

## 4. Estados visuales obligatorios

Todo target interactivo debe poder editar estados sin contaminar el base.

### 4.1 Estados base

| Estado | Aplica a | Qué controla |
|---|---|---|
| `base` | Todos | Apariencia normal |
| `hover` | Botones, chips, rows, cards, inputs | Color, lift, glow, border, cursor |
| `focus` | Inputs, botones, tabs, links | Ring, contraste, outline interno/externo |
| `focusVisible` | Navegación teclado | Ring accesible sin invadir mouse |
| `pressed` | Botones, chips, cards tocables | Profundidad, escala, sombra, tono |
| `selected` | Cards, chips, tabs, rows | Estado elegido |
| `active` | Navigation, tabs, filters | Ruta o filtro activo |
| `disabled` | Controles | Opacidad, frost, cursor, contraste |
| `loading` | Botones, paneles, tablas | Skeleton, shimmer, spinner, bloqueo |
| `error` | Inputs, rows, panels, modals | Coral, icono, borde, helper |
| `warning` | Status, alertas | Amber, borde, micro-glow |
| `success` | Confirmaciones | Mint, check, calma visual |
| `critical` | Acciones destructivas | Danger fuerte, confirmación |
| `empty` | Tablas/listas | Ilustración, texto guía, CTA |
| `dragging` | Reorder, cards | Sombra, lift, ghost |
| `dropTarget` | Drop zones | Borde, fill, hint |
| `expanded` | Accordions, rows | Icono, spacing, reveal |
| `collapsed` | Accordions, sidebars | Compactación |
| `dirty` | Formularios | Marca de cambio sin guardar |
| `readonly` | Inputs, paneles | Lectura sin editable |
| `locked` | Licencias/permisos | Candado, frost, explanation |

### 4.2 Reglas de estados

1. `hover` no debe cambiar layout de forma que brinque la UI.
2. `focusVisible` debe ser más importante que el glow decorativo.
3. `disabled` no debe parecer activo aunque tenga vidrio.
4. `selected` debe diferenciarse de `hover`.
5. `pressed` debe sentirse táctil, no roto.
6. `loading` debe impedir doble acción si aplica.
7. `error` debe ser visible sin depender sólo del color.
8. `success` no debe gritar más que el CTA principal.
9. `critical` debe pedir confirmación si destruye o revoca.
10. Cambios de estado deben vivir en tokens de estado, no hacks de clase suelta.

### 4.3 Controles por estado

| Control | Base | Hover | Focus | Pressed | Selected | Disabled |
|---|---:|---:|---:|---:|---:|---:|
| `stateTone` | Sí | Sí | Sí | Sí | Sí | Sí |
| `stateOverlayAlpha` | Sí | Sí | Sí | Sí | Sí | Sí |
| `stateBorderAlpha` | Sí | Sí | Sí | Sí | Sí | Sí |
| `stateGlow` | Sí | Sí | Sí | Sí | Sí | No recomendado |
| `stateLift` | No | Sí | No | Sí | Sí | No |
| `stateScale` | No | Sí | No | Sí | No | No |
| `focusRingWidth` | No | No | Sí | No | No | No |
| `pressDepth` | No | No | No | Sí | No | No |
| `disabledFrost` | No | No | No | No | No | Sí |
| `disabledOpacity` | No | No | No | No | No | Sí |

---

## 5. Tipos visuales soportados

TABCTL7 debe soportar más que panel/text/botón. La cabina debe tener catálogo amplio y aplicabilidad clara.

| Tipo | Para qué sirve |
|---|---|
| `canvas` | Fondo general del preview |
| `background` | Imagen, gradient, veil, atmósfera |
| `panel` | Superficie de vidrio/sólida |
| `surface` | Superficie simple sin vidrio completo |
| `text` | Texto general |
| `headingText` | Títulos |
| `bodyText` | Texto de lectura |
| `labelText` | Labels compactos |
| `helperText` | Ayuda, error, nota |
| `numericText` | Precio, total, métricas |
| `button` | Botón completo |
| `buttonText` | Texto interno del botón |
| `iconButton` | Botón sólo ícono |
| `icon` | Ícono independiente |
| `chip` | Badge, tag, estado |
| `badge` | Etiqueta pequeña |
| `input` | Campo de texto |
| `select` | Selector |
| `switch` | Toggle binario |
| `slider` | Control de rango |
| `stepper` | Más/menos |
| `segmentedControl` | Grupo de opciones |
| `tab` | Tab individual |
| `navItem` | Item de navegación |
| `dock` | Barra/dock |
| `table` | Tabla completa |
| `tableHeader` | Header |
| `tableRow` | Fila |
| `tableCell` | Celda |
| `numericCell` | Celda numérica |
| `divider` | Separador |
| `imageFrame` | Marco de imagen |
| `imageOverlay` | Velo sobre imagen |
| `modal` | Panel modal |
| `popover` | Popover |
| `tooltip` | Tooltip |
| `toast` | Notificación |
| `alert` | Alerta |
| `skeleton` | Loading placeholder |
| `progress` | Barra/anillo de avance |
| `avatar` | Avatar |
| `chart` | Gráfica |
| `chartAxis` | Ejes de gráfica |
| `chartSeries` | Serie de datos |
| `emptyState` | Pantalla vacía |
| `errorState` | Error visible |
| `loadingState` | Estado de carga |
| `qr` | QR / setup code visual |
| `timeline` | Pasos/eventos |
| `kanbanCard` | Card arrastrable |
| `drawer` | Panel lateral |
| `sheet` | Panel deslizante |
| `commandPalette` | Buscador/comandos |

---

## 6. Packs de controles universales

Los controles se organizan por “packs”. Un target puede activar varios packs según su tipo.

### 6.1 Pack: Material Studio

Sirve para cambiar “de qué está hecha” la cosa.

| Control | Nombre humano | Aplica a |
|---|---|---|
| `materialKind` | Material | panel, button, chip, input, modal, dock |
| `materialMix` | Mezcla de material | panel, button, chip |
| `materialOpacity` | Presencia del material | panel, button, chip |
| `materialRoughness` | Rugosidad visual | panel, surface |
| `materialSpecular` | Brillo especular | glass, liquid, metal |
| `materialDepth` | Profundidad material | panel, modal, button |
| `materialWarmth` | Temperatura del material | panel, background |
| `materialTint` | Tinte | panel, button, chip |
| `materialTexture` | Textura | panel, background |
| `materialNoiseAmount` | Grano | panel, background |
| `materialNoiseScale` | Tamaño de grano | panel, background |
| `materialEdgeBehavior` | Canto | panel, button |
| `materialLightResponse` | Respuesta a luz | glass, liquid, metal |
| `materialFallback` | Fallback sin blur | panel, modal |

#### Materiales permitidos

| Material | Descripción | Riesgo |
|---|---|---|
| `clear-glass` | Vidrio limpio, transparente | Medio |
| `frosted-glass` | Vidrio lechoso, legible | Bajo |
| `liquid-glass` | Gota, canto óptico, highlight | Alto |
| `soft-plastic` | Plástico premium suave | Bajo |
| `ceramic` | Blanco/sólido con sombra suave | Bajo |
| `enamel` | Superficie brillante tintada | Medio |
| `brushed-metal` | Metal sutil, no cyberpunk barato | Medio |
| `carbon` | Oscuro técnico con textura mínima | Medio |
| `paper` | Mate, limpio, administrativo | Bajo |
| `ink` | Contraste editorial | Bajo |
| `neon-glass` | Vidrio + glow + borde de luz | Alto |
| `holographic` | Gradiente iridiscente controlado | Alto |
| `danger-glass` | Vidrio coral/rojo para acciones críticas | Alto |
| `mint-operational` | Verde operativo calmado | Bajo |
| `amber-warning` | Ámbar para alerta | Medio |
| `ghost` | Transparente con borde leve | Bajo |

#### Reglas de material

1. `liquid-glass` sólo se permite si hay fondo visible detrás.
2. `neon-glass` debe tener límite de glow para no parecer feria de pueblo con motherboard RGB.
3. `brushed-metal` no debe usarse en texto.
4. `holographic` no debe usarse en contenido crítico o tablas densas.
5. `danger-glass` sólo para acciones destructivas o alertas reales.
6. Si `materialOpacity = 0`, el material desaparece de verdad.

---

### 6.2 Pack: Color Studio

Sirve para color sólido, degradado, mezcla, paleta y estados.

| Control | Nombre humano | Aplica a |
|---|---|---|
| `colorRole` | Rol de color | Todos |
| `solidColor` | Color sólido | Todos |
| `colorToken` | Token semántico | Todos |
| `colorMode` | Modo de color | Todos |
| `colorMixA` | Color A | Fondos, botones, chips, texto |
| `colorMixB` | Color B | Fondos, botones, chips |
| `colorMixRatio` | Mezcla | Fondos, botones, chips |
| `gradientType` | Tipo de degradado | background, panel, button, chip |
| `gradientAngle` | Ángulo | background, panel, button |
| `gradientStops` | Paradas | background, panel, button |
| `gradientSoftness` | Suavidad | background, panel, button |
| `gradientNoise` | Antibanding/noise | background, panel |
| `blendMode` | Modo de mezcla | background, panel overlays |
| `stateColorOverride` | Color por estado | interactivos |
| `contrastTarget` | Meta de contraste | texto, botones |
| `autoContrast` | Ajuste automático | texto sobre fondo |
| `colorLock` | Bloquear color | tokens/presets |

#### Roles de color

| Rol | Uso |
|---|---|
| `surface` | Superficies |
| `surfaceMuted` | Fondos secundarios |
| `textPrimary` | Texto principal |
| `textSecondary` | Texto secundario |
| `textMuted` | Texto suave |
| `accent` | Acento general |
| `cta` | Acción principal |
| `success` | Confirmación |
| `warning` | Advertencia |
| `danger` | Acción destructiva |
| `info` | Información |
| `selected` | Selección |
| `focus` | Accesibilidad/focus |
| `divider` | Separadores |
| `shadow` | Sombras |
| `glow` | Luces |

#### Tipos de degradado

| Degradado | Aplica a | Comentario |
|---|---|---|
| `linear` | background, button, chip | Básico |
| `radial` | background, panel | Luz focal |
| `conic` | badges, rings, premium | Usar con cuidado |
| `mesh` | background | Simulado con capas/pseudo-elementos |
| `aurora` | background | Suave, atmosférico |
| `edge-light` | panel, button | Sólo canto |
| `state-sweep` | hover/selected | Movimiento mínimo |
| `data-heat` | chart, table rows | Basado en datos |
| `danger-fade` | alerts | Rojo/coral controlado |
| `mint-calm` | success | Verde suave |

#### Reglas de color

1. Color crudo (`#00ffcc`) sólo en modo pro/forense.
2. Por defecto usar tokens semánticos.
3. Mezclas deben poder guardarse como receta.
4. El texto debe poder activar contraste automático.
5. La cabina debe advertir si fondo y texto no cumplen legibilidad.
6. Degradados en texto sólo para títulos especiales, no para body denso.
7. Los colores por estado no deben romper el contraste.

---

### 6.3 Pack: Glass & Backdrop Studio

Sirve para vidrio, blur de fondo, velo, refracción y canto.

| Control | Nombre humano | Aplica a |
|---|---|---|
| `glassAlpha` | Transparencia de vidrio | panel, modal, button, chip |
| `backdropBlur` | Blur de fondo | panel, modal, dock, popover |
| `backdropSaturation` | Saturación de fondo | glass |
| `frostVeil` | Velo lechoso | glass |
| `frostColor` | Color del frost | glass |
| `refractionAmount` | Refracción | liquid-glass |
| `refractionScale` | Escala de refracción | liquid-glass |
| `edgeShine` | Brillo de canto | panel, button |
| `edgeShinePosition` | Posición del brillo | panel, button |
| `innerHighlight` | Brillo interno | panel, button |
| `innerShadow` | Sombra interna | panel, input |
| `specularHotspot` | Punto de luz | liquid, metal |
| `dropHighlight` | Gota de luz | liquid-glass |
| `causticHint` | Cáustica mínima | liquid-glass |
| `glassFallbackAlpha` | Fallback sin blur | panel |

#### Reglas de glass

1. Para que `backdropBlur` se vea, el fondo del elemento debe ser transparente o semitransparente.
2. Blur alto exige contraste alto en texto.
3. Liquid glass requiere borde/highlight, no otro panel extra sin propósito.
4. Si el usuario pone blur en 0, se apaga `backdrop-filter`.
5. Frost no debe tapar contenido como niebla de baño público, chingue su madre.

---

### 6.4 Pack: Typography Studio

Sirve para tipografía, tamaño, peso, glow, legibilidad y números.

| Control | Nombre humano | Aplica a |
|---|---|---|
| `fontFamilyRole` | Familia por rol | text, buttonText, numericText |
| `fontMood` | Personalidad tipográfica | text |
| `fontSize` | Tamaño | text |
| `fontScale` | Escala | text |
| `fontWeight` | Peso | text |
| `fontStyle` | Estilo | text |
| `letterSpacing` | Tracking | text |
| `lineHeight` | Alto de línea | text |
| `textTransform` | Mayúsculas/minúsculas | label, buttonText |
| `textWrap` | Comportamiento de corte | text |
| `textBalance` | Balance de título | headingText |
| `textColor` | Color | text |
| `textOpacity` | Opacidad | text |
| `textShadow` | Sombra de texto | text |
| `textGlow` | Glow texto | text |
| `textGlowColor` | Color glow | text |
| `textNeonGlass` | Neon glass texto | headings, buttonText |
| `textNonGaussianGlow` | Glow no-gaussiano | headings, price |
| `readabilityVeil` | Velo detrás de texto | text sobre imagen |
| `maxLines` | Máximo de líneas | text |
| `truncateMode` | Corte | text |
| `numericTabular` | Números tabulares | numericText |
| `currencyFormatStyle` | Estilo moneda | numericText |
| `decimalEmphasis` | Centavos | numericText |
| `negativeNumberStyle` | Negativos | numericText |
| `dataDeltaStyle` | Subida/bajada | numericText |

#### Font moods

| Mood | Descripción |
|---|---|
| `compact` | Caben más datos |
| `soft` | Amable, redondeada |
| `technical` | Operativa, precisa |
| `premium` | Elegante, respirada |
| `loud` | Titular que manda |
| `quiet` | Texto secundario |
| `cashier-fast` | Lectura rápida de caja |
| `admin-dense` | Denso pero usable |
| `receipt` | Numérico/monoespaciado |
| `marketing` | Promo y cards |

#### Reglas tipográficas

1. Botón no hereda tamaño de body si rompe touch target.
2. Precio puede usar tabular para no bailar al cambiar.
3. Body largo no debe tener glow fuerte.
4. Texto en glass necesita contraste y/o veil.
5. Labels pueden ser compactos, pero no ilegibles.
6. Si `textGlow = 0`, se apaga completamente.
7. El usuario debe poder cambiar tamaño sólo del texto o sólo de la figura.

---

### 6.5 Pack: Shape & Geometry Studio

Sirve para forma, tamaño, radio, recorte y proporción.

| Control | Nombre humano | Aplica a |
|---|---|---|
| `shapeKind` | Forma | panel, button, chip, imageFrame |
| `radius` | Redondeo | panel, button, chip |
| `radiusTopLeft` | Radio sup. izq. | panel |
| `radiusTopRight` | Radio sup. der. | panel |
| `radiusBottomLeft` | Radio inf. izq. | panel |
| `radiusBottomRight` | Radio inf. der. | panel |
| `pillAmount` | Qué tan cápsula | button, chip |
| `notchAmount` | Muesca | panels especiales |
| `cutCorner` | Esquina cortada | cards/admin |
| `squircleAmount` | Squircle | premium panels |
| `aspectRatio` | Proporción | imageFrame, card |
| `widthMode` | Ancho | components |
| `heightMode` | Alto | components |
| `minHeight` | Alto mínimo | button, row |
| `maxWidth` | Ancho máximo | text, cards |
| `paddingX` | Aire horizontal | panel, button |
| `paddingY` | Aire vertical | panel, button |
| `gap` | Separación | containers |
| `density` | Densidad | table, form, rail |
| `alignment` | Alineación | text, layout |
| `anchorPoint` | Punto ancla | popover, tooltip |
| `overflowBehavior` | Desborde | panels, text |
| `clipStyle` | Recorte visual | image, panel |

#### Formas permitidas

| Forma | Uso |
|---|---|
| `rounded-rect` | Default |
| `pill` | Botones/chips |
| `squircle` | Premium |
| `cut-corner` | Admin/técnico |
| `ticket` | Promos/cupones |
| `capsule-tab` | Tabs |
| `floating-island` | Dock/popover |
| `drop` | Liquid glass especial |
| `badge-shield` | Estado/seguridad |
| `receipt-strip` | Ticket/checkout |
| `metric-tile` | Métricas |
| `image-card` | Productos |

---

### 6.6 Pack: Shadow, Glow & Depth Studio

Sirve para sombras, glow, profundidad, contacto y luz.

| Control | Nombre humano | Aplica a |
|---|---|---|
| `shadowDepth` | Profundidad | panel, button, modal |
| `shadowSoftness` | Suavidad | panel, modal |
| `shadowSpread` | Expansión | panel |
| `shadowYOffset` | Caída vertical | panel |
| `contactShadow` | Sombra de contacto | floating elements |
| `ambientShadow` | Sombra ambiental | panel |
| `innerShadowAlpha` | Sombra interna | input, panel |
| `glowAmount` | Glow | button, chip, text |
| `glowColor` | Color glow | glowing elements |
| `glowRadius` | Tamaño glow | glowing elements |
| `glowSpread` | Expansión glow | glowing elements |
| `nonGaussianGlow` | Glow no-gaussiano | premium, neon |
| `haloAmount` | Halo suave | selected/focus |
| `elevationLevel` | Nivel elevación | material system |
| `zLayer` | Capa visual | overlays |
| `liftOnHover` | Levantar al hover | buttons/cards |
| `pressSink` | Hundir al presionar | buttons |
| `selectedDepth` | Profundidad seleccionado | selected |

#### Reglas de profundidad

1. Sombra no debe reemplazar jerarquía real.
2. Glow no debe sustituir focus ring.
3. Hover lift máximo pequeño para no marear.
4. Press debe reducir profundidad, no aumentar como resorte loco.
5. En tablas densas, sombras por fila son deuda visual.
6. Contact shadow sólo en flotantes.
7. Neon en body text queda prohibido salvo experimento.

---

### 6.7 Pack: Border & Stroke Studio

| Control | Nombre humano | Aplica a |
|---|---|---|
| `borderWidth` | Grosor de borde | panel, button, input |
| `borderAlpha` | Intensidad | panel, button, input |
| `borderColor` | Color | panel, button, input |
| `borderGradient` | Borde degradado | premium |
| `borderStyle` | Estilo | panel, divider |
| `hairlineMode` | Línea fina | tables, dividers |
| `focusBorderColor` | Borde focus | inputs/buttons |
| `selectedBorderColor` | Borde seleccionado | selected |
| `dangerBorderColor` | Borde peligro | danger |
| `edgeHighlightColor` | Color canto | glass |
| `separatorAlpha` | Separadores | table/list |
| `outlineOffset` | Separación outline | focus |

#### Estilos de borde

| Estilo | Uso |
|---|---|
| `none` | Sin borde |
| `hairline` | Sutil |
| `solid` | Claro |
| `frost-line` | Glass |
| `specular-edge` | Premium |
| `gradient-stroke` | Promos |
| `dashed` | Drop target |
| `danger-rail` | Error/critical |
| `focus-ring` | Accesibilidad |

---

### 6.8 Pack: Motion & Interaction Studio

| Control | Nombre humano | Aplica a |
|---|---|---|
| `motionEnabled` | Movimiento activo | interactivos |
| `motionAmount` | Intensidad | interactivos |
| `transitionDuration` | Duración | interactivos |
| `transitionCurve` | Curva | interactivos |
| `hoverLift` | Elevación hover | buttons/cards |
| `hoverGlowBoost` | Más glow en hover | buttons/chips |
| `hoverColorShift` | Cambio color hover | interactivos |
| `pressScale` | Escala al presionar | buttons |
| `pressDepth` | Profundidad al presionar | buttons |
| `selectedPulse` | Pulso al seleccionar | selected |
| `loadingShimmer` | Shimmer loading | skeleton/buttons |
| `successFlash` | Flash éxito | success |
| `errorShake` | Shake error | error |
| `parallaxTiny` | Parallax mínimo | backgrounds |
| `reducedMotionFallback` | Fallback sin motion | todos |

#### Reglas de movimiento

1. El movimiento debe ser corto, útil y reversible.
2. Error shake debe ser mínimo, no telenovela.
3. Loading shimmer no debe competir con CTA.
4. Respetar modo reduced motion si existe.
5. En Tablet POS, la interacción debe sentirse rápida.

---

### 6.9 Pack: Layout & Density Studio

| Control | Nombre humano | Aplica a |
|---|---|---|
| `density` | Densidad | table, forms, rails |
| `padding` | Aire interno | panels |
| `gap` | Separación | stacks |
| `rowHeight` | Alto fila | table |
| `columnGap` | Separación columnas | table/forms |
| `stackGap` | Separación vertical | stacks |
| `contentWidth` | Ancho contenido | panels |
| `responsiveMode` | Modo responsivo | preview |
| `compactStrategy` | Compactación | dense tables |
| `overflowMode` | Desborde | text/table |
| `stickyMode` | Sticky visual | headers/rails |
| `safeTouchSize` | Tamaño táctil mínimo | interactivos |
| `hitAreaPadding` | Área tocable invisible | buttons/icons |

#### Densidades

| Densidad | Uso |
|---|---|
| `relaxed` | Demo/premium |
| `comfortable` | Default |
| `cashier-fast` | POS rápido |
| `admin-dense` | Muchas columnas |
| `audit-compact` | Logs |
| `touch-large` | Operación tablet |
| `kiosk` | Público |
| `modal-focus` | Decisión crítica |

---

### 6.10 Pack: Accessibility & Safety Studio

| Control | Nombre humano | Aplica a |
|---|---|---|
| `contrastCheck` | Checar contraste | text |
| `autoContrast` | Auto contraste | text |
| `focusVisibleEnabled` | Focus visible | interactivos |
| `focusRingWidth` | Grosor focus | interactivos |
| `focusRingColor` | Color focus | interactivos |
| `minTouchTarget` | Target mínimo | buttons/inputs |
| `colorOnlyWarning` | No sólo color | status |
| `reducedMotionMode` | Reducir movimiento | motion |
| `legibilityVeil` | Velo de lectura | text sobre imagen |
| `dangerConfirmHint` | Indicar confirmación | danger |
| `disabledReasonVisible` | Razón disabled | disabled |
| `stateLabel` | Texto de estado | status |

#### Reglas de accesibilidad

1. Estado no debe depender sólo del color.
2. Focus visible no es decorativo.
3. Texto sobre glass requiere contraste real.
4. Touch targets deben seguir siendo tocables aunque el botón sea visualmente pequeño.
5. Disabled debe explicar por qué si es una acción importante.
6. Danger debe diferenciarse de warning.

---

## 7. Controles por tipo

### 7.1 `panel`

| Pack | Controles principales |
|---|---|
| Material | materialKind, materialOpacity, materialTint |
| Glass | glassAlpha, backdropBlur, frostVeil, refractionAmount |
| Color | solidColor, gradientType, colorMixRatio |
| Border | borderAlpha, borderGradient, edgeShine |
| Shadow | shadowDepth, contactShadow, ambientShadow |
| Shape | radius, squircleAmount, cutCorner |
| Layout | padding, gap, density |
| State | selectedBorderColor, hoverLift, disabledFrost |

Acciones:

1. Cambiar material.
2. Mezclar colores.
3. Agregar degradado.
4. Agregar capa óptica mediante pseudo-elemento.
5. Cambiar forma.
6. Ajustar glass.
7. Ajustar blur de fondo.
8. Apagar glass real.
9. Copiar estilo.
10. Guardar receta de superficie.

---

### 7.2 `text`

| Pack | Controles principales |
|---|---|
| Typography | fontMood, fontSize, fontWeight, lineHeight |
| Color | textColor, colorToken, autoContrast |
| Glow | textGlow, textNeonGlass, textNonGaussianGlow |
| Layout | maxLines, truncateMode, textBalance |
| Accessibility | contrastCheck, legibilityVeil |
| State | hoverColorShift, selectedTextColor, disabledOpacity |

Acciones:

1. Cambiar tipografía.
2. Cambiar color.
3. Hacer más pequeño/grande.
4. Cambiar peso.
5. Poner glow suave.
6. Poner neon glass.
7. Aplicar non-gaussian glow.
8. Ajustar tracking.
9. Hacerlo más compacto.
10. Bloquear contraste automático.
11. Aplicar estado sólo hover.
12. Aplicar estado sólo selected.

---

### 7.3 `numericText`

| Pack | Controles principales |
|---|---|
| Typography | fontSize, fontWeight, numericTabular |
| Color | numberColor, stateColorOverride |
| Glow | numberGlow, nonGaussianGlow |
| Format | currencyFormatStyle, decimalEmphasis, negativeNumberStyle |
| Layout | alignment, widthMode |
| State | deltaUpColor, deltaDownColor, selectedNumberGlow |

Acciones:

1. Hacer precio protagonista.
2. Hacer precio discreto.
3. Separar símbolo y centavos.
4. Usar números tabulares.
5. Colorear por delta.
6. Poner glow sólo si hay promo.
7. Poner color por estado.
8. Convertir negativo en coral.
9. Reducir centavos.
10. Guardar preset de precio.

---

### 7.4 `button`

| Pack | Controles principales |
|---|---|
| Material | materialKind, materialMix, materialTint |
| Color | buttonTone, gradientType, colorMixRatio |
| Glass | glassAlpha, backdropBlur, frostVeil |
| Border | borderAlpha, borderGradient |
| Shape | buttonRadius, pillAmount, height |
| Shadow | buttonGlow, shadowDepth, pressDepth |
| Motion | hoverLift, pressScale, transitionCurve |
| State | hover, focus, pressed, selected, disabled, loading |
| Accessibility | minTouchTarget, focusRingWidth |

Acciones:

1. Cambiar material.
2. Cambiar color sólido.
3. Crear degradado.
4. Mixar dos colores.
5. Agregar segunda capa óptica.
6. Cambiar blur de fondo.
7. Cambiar tipografía interna desde `buttonText`.
8. Cambiar forma cápsula/rectángulo/squircle.
9. Poner glow.
10. Poner neon glass.
11. Cambiar hover.
12. Cambiar selected.
13. Cambiar disabled.
14. Cambiar loading.
15. Ajustar altura táctil.
16. Ajustar press depth.
17. Cambiar borde.
18. Guardar receta CTA.
19. Copiar estilo a todos los botones del grupo.
20. Reset sólo del estado hover.

---

### 7.5 `buttonText`

| Pack | Controles principales |
|---|---|
| Typography | fontMood, fontSize, fontWeight, letterSpacing |
| Color | textColor, autoContrast |
| Glow | textGlow, textNeonGlass |
| Layout | iconSpacing, textTransform |
| State | hoverTextColor, selectedTextColor, disabledTextOpacity |

Regla:

```txt
Editar buttonText nunca cambia fondo del botón.
Editar button sí puede sugerir editar buttonText, pero no lo toca sin permiso/alcance.
```

---

### 7.6 `chip` / `badge`

| Pack | Controles principales |
|---|---|
| Material | materialKind, chipAlpha |
| Color | chipTone, statusColor |
| Border | chipBorder, selectedBorderColor |
| Shape | chipSize, pillAmount |
| Typography | labelSize, labelWeight |
| Icon | chipIcon, iconPosition |
| State | active, selected, disabled, warning |

Acciones:

1. Cambiar tono por estado.
2. Agregar icono.
3. Quitar icono.
4. Compactar.
5. Hacer pill.
6. Convertir a badge.
7. Aplicar estado warning/success/danger.
8. Crear chip ghost.
9. Crear chip filled.
10. Guardar receta de status.

---

### 7.7 `input`

| Pack | Controles principales |
|---|---|
| Material | inputMaterial, inputAlpha |
| Color | inputSurfaceColor, valueTextColor |
| Border | inputBorder, focusBorder |
| Shape | inputRadius, inputHeight |
| Typography | placeholderStyle, valueTextStyle |
| State | focus, error, success, disabled, readonly |
| Accessibility | focusVisible, errorTextVisible |

Acciones:

1. Cambiar superficie.
2. Cambiar placeholder.
3. Cambiar texto capturado.
4. Cambiar focus ring.
5. Cambiar error.
6. Cambiar success.
7. Cambiar disabled.
8. Cambiar prefijo/sufijo.
9. Cambiar helper text.
10. Guardar receta de formulario.

---

### 7.8 `table`

| Pack | Controles principales |
|---|---|
| Layout | density, rowHeight, columnGap |
| Color | headerTone, zebraSoftness |
| Border | dividerAlpha, hairlineMode |
| Typography | headerTextStyle, cellTextStyle |
| Numeric | numericAlign, tabularNumbers |
| State | hoverRow, selectedRow, errorRow |
| Sticky | stickyHeader, stickyShadow |
| Actions | actionColumnMode, compactActions |

Acciones:

1. Compactar.
2. Hacer más cómoda.
3. Encender zebra.
4. Apagar zebra.
5. Cambiar header.
6. Cambiar celdas numéricas.
7. Cambiar filas selected.
8. Cambiar error rows.
9. Cambiar action column.
10. Guardar receta de tabla.

---

### 7.9 `background`

| Pack | Controles principales |
|---|---|
| Color | gradientType, gradientStops, blendMode |
| Image | backgroundImage, imageScale, imagePosition |
| Atmosphere | atmosphericVeil, vignette, lightLeak |
| Blur | backgroundBlur, foregroundBlur |
| Motion | parallaxTiny, motionAmount |
| Legibility | readabilityVeil, contrastOverlay |

Acciones:

1. Cambiar fondo sólido.
2. Cambiar degradado.
3. Mixar colores.
4. Agregar aurora.
5. Agregar viñeta.
6. Agregar light leak.
7. Blur del fondo.
8. Cambiar escala.
9. Cambiar horizonte.
10. Apagar todo fondo a transparente real.

---

### 7.10 `icon`

| Pack | Controles principales |
|---|---|
| Shape | iconSize, strokeWidth |
| Color | iconColor, iconTone |
| Glow | iconGlow, iconShadow |
| State | hoverIconColor, selectedIconColor |
| Layout | iconSpacing, iconAlignment |

Acciones:

1. Cambiar tamaño.
2. Cambiar color.
3. Cambiar stroke.
4. Poner glow.
5. Cambiar estado hover.
6. Cambiar selected.
7. Cambiar separación con texto.
8. Ocultar/mostrar.

---

### 7.11 `modal`, `popover`, `tooltip`, `toast`

| Tipo | Controles clave |
|---|---|
| `modal` | backdropVeil, shellGlass, radius, titleStyle, actionButtons |
| `popover` | anchorPoint, arrow, shadowDepth, glassAlpha |
| `tooltip` | delay, surface, textSize, maxWidth |
| `toast` | tone, icon, timeout, actionButton, progress |

Reglas:

1. Modal debe priorizar legibilidad sobre glass.
2. Tooltip no debe tener efectos pesados.
3. Toast debe diferenciar info/success/warning/error.
4. Popover debe anclarse sin meter wrappers extra.

---

### 7.12 `chart`

| Pack | Controles principales |
|---|---|
| Color | seriesPalette, dataColor, gradientFill |
| Typography | axisLabelStyle, legendStyle |
| Grid | gridAlpha, dividerStyle |
| Shape | lineTension, barRadius, pointRadius |
| State | hoverPoint, selectedSeries |
| Data | positiveColor, negativeColor, thresholdColor |
| Accessibility | contrastCheck, patternMode |

Acciones:

1. Cambiar paleta.
2. Cambiar color por serie.
3. Agregar fill degradado.
4. Cambiar grid.
5. Cambiar ejes.
6. Cambiar labels.
7. Cambiar hover.
8. Cambiar selected.
9. Activar patrón además de color.
10. Guardar receta de chart.

---

## 8. Grupos visuales y componentes

## 8.1 POS Product Set

### Componentes

| Componente | Capas |
|---|---|
| `Product Card` | Canvas, Card base, Image area, Text stack, Price zone, Badges layer, Action area |
| `Mini Product Card` | Card base, Thumb, Title, Price, Quick add |
| `Promo Product Card` | Card base, Promo ribbon, Price zone, CTA |
| `Out-of-stock Product Card` | Card base, Disabled veil, Badge, CTA disabled |
| `Favorite Product Tile` | Tile base, Icon, Label, Count |

### Matriz detallada

| Capa | Rol | Parte fina | Tipo | Controles |
|---|---|---|---|---|
| Canvas | Fondo atmosférico | Aurora | `background` | gradient, veil, blur, vignette |
| Card base | Superficie primaria | Base material | `panel` | material, glass, border, shadow |
| Card base | Superficie primaria | Edge optical layer | `panel` | edgeShine, borderGradient |
| Card base | Superficie primaria | State overlay | `panel` | hover/selected overlay |
| Image area | Marco imagen | Frame | `imageFrame` | radius, aspect, veil |
| Image area | Imagen | Image crop | `background` | scale, position, blur |
| Image area | Overlay | Readability veil | `imageOverlay` | alpha, gradient |
| Text stack | Nombre producto | Heading | `headingText` | size, weight, color, balance |
| Text stack | Descripción | Body | `bodyText` | opacity, lineHeight, maxLines |
| Text stack | Meta | Footer | `labelText` | tracking, muted color |
| Price zone | Precio | Integer | `numericText` | size, color, glow, tabular |
| Price zone | Precio | Decimals | `numericText` | size ratio, opacity |
| Price zone | Precio | Currency symbol | `numericText` | baseline, opacity |
| Price zone | Precio anterior | Old price | `numericText` | strikethrough, muted |
| Badges layer | Stock badge | Pill | `chip` | status tone, icon, border |
| Badges layer | Promo badge | Ribbon/pill | `badge` | gradient, glow, icon |
| Action area | Add button | Button shell | `button` | material, tone, hover, press |
| Action area | Add button | Button text | `buttonText` | font, color, glow |
| Action area | Add button | Plus icon | `icon` | size, color, stroke |
| Action area | Quantity stepper | Minus/plus | `stepper` | shape, state, press |

### Estados POS Product

| Estado | Cambios sugeridos |
|---|---|
| `base` | Card calma, precio claro, CTA visible |
| `hover` | Edge shine + lift mínimo |
| `selected` | Border/accent + selected overlay |
| `pressed` | CTA se hunde |
| `disabled` | Frost + imagen desaturada |
| `promo` | Badge y precio con glow controlado |
| `lowStock` | Chip amber/coral, CTA normal |
| `outOfStock` | CTA disabled + veil |
| `favorite` | Icon accent sin contaminar card |

### Presets humanos

1. `Producto vidrio premium`
2. `Producto promo mint glow`
3. `Producto agotado elegante`
4. `Producto foto protagonista`
5. `Producto admin compacto`
6. `Producto alto contraste`
7. `Producto dark glass`
8. `Producto sin glass`
9. `Producto neon moderado`
10. `Producto caja rápida`

---

## 8.2 Checkout Rail Set

| Componente | Capas |
|---|---|
| `Checkout Rail` | Shell, Header, Cart lines, Totals, Payment, Actions |
| `Cart Line` | Row, Product info, Qty, Total, Actions |
| `Payment Summary` | Totals, Tax, Discount, Tender |
| `Charge CTA` | Button shell, Button text, Icon, Loading |

### Matriz

| Capa | Rol | Tipo | Controles |
|---|---|---|---|
| Rail shell | Panel lateral | `panel` | strong glass, blur, shadow |
| Rail header | Title | `headingText` | weight, size, color |
| Rail header | Customer badge | `chip` | tone, active state |
| Cart line | Row surface | `tableRow` | hover, selected, density |
| Cart line | Product name | `text` | size, maxLines |
| Cart line | Quantity | `numericText` | tabular, alignment |
| Cart line | Line total | `numericText` | weight, glow |
| Cart line | Remove action | `iconButton` | danger hover |
| Totals | Total label | `labelText` | opacity, tracking |
| Totals | Total number | `numericText` | size, glow, color |
| Payment | Tender pill | `chip` | selected, disabled |
| Actions | Charge button | `button` | CTA tone, loading, press |
| Actions | Charge text | `buttonText` | strong contrast |
| Actions | Hold/Void | `button` | ghost/danger |

### Reglas

1. `Charge button` siempre debe ser el CTA visual más fuerte.
2. `Void` peligroso, pero sin modo sirena de patrulla.
3. Totales con números tabulares.
4. Rail puede ser más sólido que cards.
5. Loading de cobro debe bloquear doble click/toque.
6. Estados de tender deben diferenciar selected y hover.

---

## 8.3 Turno/Caja Set

| Capa | Rol | Tipo | Controles |
|---|---|---|---|
| Status shell | Panel principal | `panel` | material, status border |
| Status shell | Estado caja | `headingText` | status color, glow |
| Status shell | Operador | `labelText` | muted, compact |
| Command area | Open shift | `button` | success CTA |
| Command area | Close shift | `button` | danger controlled |
| Command area | Count cash | `button` | warning/neutral |
| Cash metrics | Expected cash | `numericText` | tabular |
| Cash metrics | Counted cash | `numericText` | focus/value |
| Cash metrics | Difference | `numericText` | state color |
| Alert zone | Warning panel | `alert` | amber/coral |
| Alert zone | Warning text | `helperText` | legible |

### Estados

1. `closed`
2. `ready-to-open`
3. `open`
4. `counting`
5. `difference-ok`
6. `difference-warning`
7. `difference-critical`
8. `closed-success`
9. `locked`
10. `audit-required`

---

## 8.4 Table Set

### Variantes

| Variante | Uso |
|---|---|
| `KeyValueTable` | Resumen/config |
| `MiniOpsTable` | 3-4 columnas |
| `ActionTable` | 5-7 columnas |
| `LedgerTable` | 8-10 columnas |
| `DenseAdminTable` | 10+ columnas |
| `CardListTable` | Fallback tablet |
| `ExceptionTable` | Errores/bloqueos |
| `ReconciliationTable` | Conciliación |
| `AuditTrailTable` | Eventos |
| `InventoryTable` | Inventario |
| `CustomerFollowUpTable` | Clientes/licencias |

### Controles extra

| Control | Uso |
|---|---|
| `columnPriority` | Decide qué columnas sobreviven en compacto |
| `cellWrapMode` | Cortar, envolver, tooltip |
| `rowStateTone` | Color por fila |
| `rowHoverSurface` | Hover de fila |
| `selectedRowRail` | Línea lateral selected |
| `numericCellEmphasis` | Números importantes |
| `dangerCellTreatment` | Celda con alerta |
| `emptyTableTreatment` | Estado sin datos |
| `stickyHeaderBlur` | Header fijo con blur |
| `horizontalScrollHint` | Indicio de scroll |
| `actionDensity` | Botones por fila |
| `bulkSelectionStyle` | Checkbox/selected |

---

## 8.5 Button Set

### Familias de botones

| Familia | Uso |
|---|---|
| `Primary CTA` | Acción principal |
| `Secondary` | Acción normal |
| `Tertiary/Text` | Acción ligera |
| `Ghost` | Sobre glass |
| `Danger` | Acción destructiva |
| `Warning` | Acción preventiva |
| `Success` | Confirmación |
| `Icon` | Sólo ícono |
| `Split` | Botón con menú |
| `Segmented` | Toggle group |
| `Floating Action` | Acción flotante |
| `Command` | Botón de comando |
| `Payment` | Cobro |
| `License` | Setup/revoke/renew |
| `Disabled with reason` | Acción no disponible |

### Controles de botón extendidos

| Control | Nombre humano |
|---|---|
| `buttonMaterial` | Material del botón |
| `buttonTone` | Tono |
| `buttonGradient` | Degradado |
| `buttonColorMix` | Mezcla de colores |
| `buttonGlassAlpha` | Transparencia |
| `buttonBackdropBlur` | Blur detrás |
| `buttonRadius` | Forma |
| `buttonHeight` | Altura |
| `buttonMinTouch` | Área táctil |
| `buttonGlow` | Glow |
| `buttonNeonGlass` | Neon glass |
| `buttonBorderMode` | Borde |
| `buttonStateLayer` | Capa de estado |
| `buttonHoverTone` | Tono hover |
| `buttonSelectedTone` | Tono selected |
| `buttonPressedDepth` | Hundimiento |
| `buttonDisabledFrost` | Disabled frost |
| `buttonLoadingTreatment` | Loading |
| `buttonIconPlacement` | Posición icono |
| `buttonTextPreset` | Texto interno |
| `buttonDangerConfirm` | Requiere confirmación |

---

## 8.6 Form Widgets

| Componente | Roles |
|---|---|
| `Text Input` | surface, label, value, placeholder, helper, icon |
| `Money Input` | surface, currency, integer, decimals, helper |
| `Search Input` | surface, icon, value, clear button |
| `Select` | trigger, value, chevron, menu |
| `Checkbox` | box, check, label |
| `Radio` | circle, dot, label |
| `Switch` | track, thumb, label |
| `Slider` | track, fill, thumb, marks |
| `Stepper` | minus, value, plus |
| `Date/Time` | surface, value, icon |
| `Validation Message` | icon, text, panel |

### Estados de form

1. `empty`
2. `filled`
3. `focus`
4. `dirty`
5. `valid`
6. `invalid`
7. `disabled`
8. `readonly`
9. `loading`
10. `locked`

---

## 8.7 Modal States

| Componente | Capas |
|---|---|
| `Confirm Modal` | backdrop, shell, title, body, actions |
| `Danger Modal` | backdrop, danger shell, warning icon, confirm |
| `Setup Modal` | shell, QR, code, copy button |
| `License Modal` | customer info, devices, actions |
| `Payment Modal` | amount, tender, status |
| `Error Modal` | error details, support actions |

### Reglas

1. Backdrop no debe borrar contexto totalmente si el usuario necesita entender origen.
2. Danger modal debe diferenciar Cancel y Confirm con claridad.
3. QR/setup code debe priorizar legibilidad, no glass encima.
4. Modal de error debe permitir copiar diagnóstico si aplica.

---

## 8.8 Metric Widgets

| Componente | Roles |
|---|---|
| `Metric Tile` | shell, label, value, delta, sparkline |
| `KPI Row` | icon, label, value, trend |
| `Cash Metric` | label, money, difference |
| `License Metric` | count, status, warning |
| `Inventory Metric` | current, threshold, alert |
| `Sales Metric` | amount, delta, period |

### Controles específicos

| Control | Uso |
|---|---|
| `metricValueSize` | Tamaño del dato |
| `metricDeltaStyle` | Subida/bajada |
| `metricTrendColor` | Color de tendencia |
| `sparklineTone` | Mini gráfica |
| `thresholdWarning` | Estado por umbral |
| `metricCardDensity` | Compacto/respirado |

---

## 8.9 Navigation / Dock

| Componente | Roles |
|---|---|
| `Bottom Dock` | shell, item, icon, label, active indicator |
| `Side Nav` | rail, item, group label, badge |
| `Tabs` | tablist, tab, active pill, divider |
| `Breadcrumbs` | item, separator, current |
| `Command Palette` | shell, input, result row, shortcut |

### Controles

1. Material del dock.
2. Blur de fondo.
3. Active indicator.
4. Ícono activo.
5. Label activo.
6. Hover de item.
7. Selected pill.
8. Badge.
9. Compactación.
10. Focus ring.

---

## 8.10 Alerts, Toasts & Empty States

| Tipo | Controles |
|---|---|
| `alert` | tone, icon, border, panel, text, action |
| `toast` | tone, timeout, icon, progress, action |
| `emptyState` | illustration, headline, body, CTA |
| `errorState` | code, message, details, action |
| `loadingState` | skeleton, shimmer, progress |
| `successState` | check, message, next action |

---

## 8.11 Mixed Stress Test Supremo

Debe renderizar a la vez:

1. Product Card normal.
2. Product Card promo.
3. Product Card disabled.
4. Checkout mini rail.
5. Tabla compacta.
6. Form con error.
7. Modal mini.
8. Toast success.
9. Alert warning.
10. Metric tile.
11. Dock/nav.
12. Button group.
13. Chart mini.
14. Empty state.
15. Loading skeleton.
16. QR/setup visual.
17. Danger confirmation.
18. Selected row.
19. Hover simulation.
20. Focus visible simulation.

### Indicadores del stress test

| Indicador | Qué valida |
|---|---|
| `contrastPass` | Texto legible |
| `zeroMeansZero` | 0 apaga de verdad |
| `noExtraContainers` | Estructura limpia |
| `stateSeparation` | Base/hover/selected separados |
| `tokenTrace` | Valor rastreable |
| `scopeGuard` | No contaminó otros targets |
| `densityFit` | No se desbordó |
| `touchTargetSafe` | Tocabilidad |
| `reducedMotionSafe` | Movimiento reducible |
| `glassLegibility` | Glass usable |

---

## 9. Herencia, overrides y cascada visual

### 9.1 Modelo humano

```txt
Este rol está usando:
- Material heredado de: Card base
- Texto heredado de: Product Card
- Color local: Sí
- Estado hover local: No
- Estado selected local: Sí
```

### 9.2 Acciones

| Acción | Qué hace |
|---|---|
| `Usar herencia` | Borra override local de ese paquete |
| `Crear override` | Copia valor heredado y lo vuelve local |
| `Resetear rol` | Limpia sólo rol |
| `Resetear estado` | Limpia sólo estado elegido |
| `Resetear capa` | Limpia capa |
| `Copiar estilo` | Copia tokens aplicables |
| `Pegar estilo compatible` | Pega sólo controles compatibles |
| `Guardar receta` | Guarda preset |
| `Comparar con padre` | Muestra diff |
| `Ver origen del valor` | Ruta del token |
| `Bloquear token` | Evita cambios accidentales |
| `Desbloquear token` | Permite edición |

### 9.3 Prioridad de valores

```txt
default system tokens
→ theme tokens
→ group tokens
→ component tokens
→ layer tokens
→ role tokens
→ part tokens
→ state tokens
→ local override
→ temporary preview draft
```

### 9.4 Ejemplo CSS variable path

```css
[data-widget-group="pos-product-set"] {
  --tabctl7-panel-glass-alpha: 0.28;
}

[data-component="product-card"][data-layer="card-base"] {
  --tabctl7-panel-radius: 22px;
}

[data-role="price-number"] {
  --tabctl7-number-color: var(--tabctl7-color-success-strong);
  --tabctl7-number-glow: 0.32;
}

[data-role="price-number"][data-state~="selected"] {
  --tabctl7-number-glow: 0.55;
}
```

---

## 10. Presets y recetas

### 10.1 Tipos de preset

| Tipo | Guarda |
|---|---|
| `Global Theme` | Tema completo lab |
| `Group Preset` | Grupo visual |
| `Component Preset` | Product Card, Rail, Table |
| `Layer Preset` | Card base, Price zone |
| `Role Preset` | Price number, Add button |
| `State Preset` | Hover, selected, disabled |
| `Material Recipe` | Material glass/metal/etc. |
| `Color Recipe` | Paleta/degradado/mix |
| `Typography Recipe` | Font mood |
| `Motion Recipe` | Hover/press |
| `Accessibility Recipe` | Contraste/focus |

### 10.2 Metadata de preset

```json
{
  "schema": "tabctl7.preset.v2",
  "name": "POS promo mint neon moderado",
  "humanIntent": "Producto en promoción con CTA protagonista sin perder legibilidad",
  "createdAt": "2026-07-07",
  "scope": "component",
  "widgetGroup": "POS Product Set",
  "component": "Product Card",
  "modifiedTargets": [
    "card-base",
    "price-number",
    "promo-badge",
    "add-button",
    "add-button-text"
  ],
  "risk": "medium",
  "requiresContrastCheck": true,
  "requiresStressTest": true,
  "tokens": {}
}
```

### 10.3 Recetas iniciales sugeridas

| Receta | Descripción |
|---|---|
| `Clear Glass POS` | Vidrio limpio y legible |
| `Frosted Cashier` | Operación rápida, alto contraste |
| `Mint CTA Premium` | Botón principal elegante |
| `Amber Warning Soft` | Advertencia sin alarma falsa |
| `Danger Coral Confirm` | Destructivo claro |
| `Admin Dense Paper` | Tablas densas sin glass pesado |
| `Dark Neon Minimal` | Oscuro con glow medido |
| `Photo Hero Card` | Imagen protagonista |
| `No Glass Transparent` | Transparencia real sin panel |
| `License Setup Calm` | QR/setup legible |
| `Audit Ledger Dense` | Auditoría compacta |
| `Mobile-ish Tablet Large Touch` | Touch grande |
| `Holographic Promo Controlled` | Promo con iridiscencia limitada |
| `Liquid Glass Edge Only` | Sólo canto óptico, sin panel extra |
| `NonGaussian Price Glow` | Precio con glow premium no-gaussiano |

---

## 11. UI del inspector

### 11.1 Layout recomendado

```txt
┌──────────────────────────────────────┬────────────────────────────────────────────┐
│ Inspector visual                      │ Canvas preview fijo                        │
│ Scroll independiente                  │                                            │
│                                      │  Barra de preview states                    │
│ Buscar control...                    │  Base | Hover | Focus | Selected | Error   │
│                                      │                                            │
│ Grupo visual ▼                       │  Preview interactivo                         │
│ Componente ▼                         │                                            │
│ Capa ▼                               │                                            │
│ Rol ▼                                │                                            │
│ Parte fina ▼                         │                                            │
│ Estado ▼                             │                                            │
│ Alcance ▼                            │                                            │
│                                      │                                            │
│ Packs aplicables:                    │                                            │
│ [Material] [Color] [Text] [State]    │                                            │
│                                      │                                            │
│ Controles favoritos                  │                                            │
│ Controles principales                │                                            │
│ Controles pro                        │                                            │
│ Tokens/diff                          │                                            │
│                                      │                                            │
│ Guardar preset                       │                                            │
│ Copiar JSON                          │                                            │
└──────────────────────────────────────┴────────────────────────────────────────────┘
```

### 11.2 Features de usabilidad

| Feature | Valor |
|---|---|
| Buscar controles | Para no scrollear como condenado |
| Favoritos | Perillas frecuentes arriba |
| Chips de aplicabilidad | “Afecta: sólo Add button / hover” |
| Preview de estado | Ver hover sin tener que hover real |
| Antes/después | Comparar |
| Undo local | Deshacer último cambio |
| Reset por pack | Reset sólo Color/Glass/Text |
| Diff de tokens | Ver qué cambió |
| Modo receta | Guardar intención humana |
| Modo seguro | Oculta controles de alto riesgo |
| Indicador cero real | Muestra si quedó apagado |
| Indicador contraste | PASS/WARN/FAIL |
| Indicador scope | Evita contaminar todo el grupo |
| Indicador herencia | Ver de dónde viene valor |
| Copiar JSON por rol | Debug cómodo |
| Exportar preset | JSON técnico |
| Importar preset | Con validación |

### 11.3 Orden de controles por target

1. Estado actual.
2. Alcance.
3. Controles favoritos.
4. Pack principal del tipo.
5. Packs secundarios.
6. Estados.
7. Herencia.
8. Presets.
9. Tokens/diff.
10. Diagnóstico.

---

## 12. Alcances de cambio

| Alcance | Descripción | Riesgo |
|---|---|---|
| `Sólo esta parte` | Target exacto | Bajo |
| `Todos los estados de esta parte` | Base + hover + etc. | Medio |
| `Sólo este estado` | Ej. sólo hover | Bajo |
| `Todos los roles de este tipo` | Todos `button` del componente | Medio |
| `Toda esta capa` | Ej. `Action area` | Medio |
| `Todo este componente` | Product Card completa | Alto |
| `Todo este grupo visual` | POS Product Set | Alto |
| `Preset completo` | Aplica receta | Alto |
| `Sólo preview temporal` | No persiste | Bajo |
| `Comparación A/B` | Prueba sin guardar | Bajo |

### Confirmaciones

Debe pedir confirmación si:

1. Alcance es grupo completo.
2. Reset global.
3. Cambiar todos los estados.
4. Sobrescribir preset existente.
5. Aplicar receta de alto riesgo.
6. Cambiar tokens base compartidos.
7. Activar material experimental.

---

## 13. Matriz de aplicabilidad resumida

| Target | Mostrar | Ocultar |
|---|---|---|
| Panel | Material, glass, color, border, shape, shadow | Font avanzado de botón |
| Texto | Typography, color, glow, contrast | Blur de fondo, row height |
| Número | Numeric, color, glow, tabular | Body line height global |
| Botón | Material, color, state, shape, press | Table zebra |
| Texto de botón | Font, color, icon spacing | Fondo del botón |
| Chip | Tone, status, icon, pill, state | Big layout |
| Input | Surface, border, focus, validation | Product image crop |
| Tabla | Density, header, rows, cells | Button press depth global |
| Row | Hover, selected, divider, density | Modal backdrop |
| Cell | Text/numeric/status | Panel glass global |
| Background | Gradient, image, blur, veil | Button text font |
| Modal | Backdrop, shell, title, actions | Table row zebra |
| Toast | Tone, icon, progress, timeout | Product card image crop |
| Chart | Palette, axis, grid, series | Button radius |
| Icon | Size, stroke, color, glow | Panel padding |
| Skeleton | Shimmer, radius, density | Text content |
| QR | Contrast, quiet zone, size | Glass overlay pesado |

---

## 14. Validadores visuales

### 14.1 Validaciones automáticas

| Validador | Bloquea si |
|---|---|
| `zeroMeansZero` | Un valor 0 deja residuo visual |
| `contrastGuard` | Texto queda ilegible |
| `scopeGuard` | Cambió target fuera de alcance |
| `containerGuard` | Se agregó wrapper innecesario |
| `importantGuard` | Aparece `!important` |
| `dependencyGuard` | Cambia package/lock |
| `stateGuard` | Hover/selected contaminan base |
| `fallbackGuard` | Sin blur queda roto |
| `touchGuard` | Botón demasiado pequeño |
| `motionGuard` | No respeta reduced motion |
| `tableDensityGuard` | Tabla se desborda |
| `glassLegibilityGuard` | Glass tapa contenido |
| `tokenTraceGuard` | Valor no rastreable |
| `presetSchemaGuard` | Preset inválido |
| `realSurfaceGuard` | Tocó POS real |

### 14.2 Resultado por cambio

```txt
Cambio aplicado en preview:
- Target: POS Product Set → Product Card → Action area → Add button
- Estado: hover
- Alcance: sólo esta parte
- Packs tocados: Color, State, Shadow
- Tokens modificados: 5
- Contraste: PASS
- Scope: PASS
- Zero semantics: PASS
- Riesgo: Medio
```

---

## 15. Data attributes sugeridos

```html
<button
  data-widget-group="pos-product-set"
  data-component="product-card"
  data-layer="action-area"
  data-role="add-button"
  data-part="button-shell"
  data-kind="button"
  data-state="base"
  data-variant="primary-cta"
>
  <span
    data-role="add-button-text"
    data-part="label"
    data-kind="button-text"
  >
    Agregar
  </span>
</button>
```

### 15.1 Reglas

1. `data-kind` decide controles aplicables.
2. `data-role` decide intención.
3. `data-state` decide estado visual.
4. `data-layer` decide herencia.
5. `data-component` decide preset.
6. `data-widget-group` decide familia.
7. `data-part` permite granularidad sin wrappers.

---

## 16. Schema de control

```json
{
  "controlId": "buttonGradient",
  "label": "Degradado del botón",
  "description": "Permite mezclar colores del fondo del botón sin tocar el texto.",
  "pack": "Color Studio",
  "appliesTo": ["button", "iconButton", "segmentedControl"],
  "hiddenFor": ["buttonText", "text", "numericText"],
  "states": ["base", "hover", "pressed", "selected", "disabled"],
  "scopes": ["part", "role", "layer", "component", "group"],
  "valueType": "gradientRecipe",
  "defaultValue": {
    "type": "none"
  },
  "zeroSemantics": "No background image; no residual overlay.",
  "cssTargets": [
    "--tabctl7-button-bg",
    "--tabctl7-button-gradient"
  ],
  "risk": "medium",
  "requiresContrastCheck": true,
  "requiresPreview": true
}
```

---

## 17. Schema de target seleccionado

```json
{
  "selection": {
    "widgetGroup": "POS Product Set",
    "component": "Product Card",
    "layer": "Action area",
    "role": "Add button",
    "part": "Button shell",
    "kind": "button",
    "state": "hover",
    "variant": "primary-cta"
  },
  "inheritance": {
    "inheritsFrom": ["Action area", "Product Card", "POS Product Set"],
    "localOverride": true,
    "overriddenPacks": ["Color Studio", "Shadow Studio"]
  },
  "availablePacks": [
    "Material Studio",
    "Color Studio",
    "Glass & Backdrop Studio",
    "Shape & Geometry Studio",
    "Shadow, Glow & Depth Studio",
    "Motion & Interaction Studio",
    "Accessibility & Safety Studio"
  ]
}
```

---

## 18. Ejemplo de preset completo

```json
{
  "schema": "tabctl7.preset.v2",
  "name": "POS Product Premium Mint CTA",
  "humanIntent": "Card clara con precio protagonista y botón mint con hover vivo.",
  "widgetGroup": "POS Product Set",
  "component": "Product Card",
  "risk": "medium",
  "tokens": {
    "layers": {
      "card-base": {
        "parts": {
          "surface": {
            "kind": "panel",
            "base": {
              "materialKind": "frosted-glass",
              "glassAlpha": 0.28,
              "backdropBlur": 18,
              "frostVeil": 0.18,
              "radius": 22,
              "borderAlpha": 0.22,
              "edgeShine": 0.34,
              "shadowDepth": 0.28
            },
            "hover": {
              "edgeShine": 0.48,
              "hoverLift": 2
            },
            "selected": {
              "borderAlpha": 0.52,
              "stateOverlayAlpha": 0.12
            }
          }
        }
      },
      "price-zone": {
        "roles": {
          "price-number": {
            "kind": "numericText",
            "base": {
              "numberColor": "success-strong",
              "numberSize": "xl",
              "numberWeight": 760,
              "numericTabular": true,
              "numberGlow": 0.18
            },
            "promo": {
              "numberGlow": 0.38,
              "textNonGaussianGlow": 0.22
            }
          }
        }
      },
      "action-area": {
        "roles": {
          "add-button": {
            "kind": "button",
            "base": {
              "materialKind": "neon-glass",
              "buttonTone": "mint",
              "buttonGradient": {
                "type": "linear",
                "angle": 135,
                "stops": ["mint-500", "cyan-400"]
              },
              "buttonGlow": 0.38,
              "buttonRadius": 999,
              "buttonHeight": 44
            },
            "hover": {
              "buttonGlow": 0.55,
              "hoverLift": 2,
              "stateOverlayAlpha": 0.1
            },
            "pressed": {
              "pressDepth": 2,
              "pressScale": 0.98
            },
            "disabled": {
              "disabledFrost": 0.4,
              "disabledOpacity": 0.56
            }
          },
          "add-button-text": {
            "kind": "buttonText",
            "base": {
              "fontMood": "compact",
              "fontSize": "sm",
              "fontWeight": 720,
              "textColor": "ink-inverse",
              "letterSpacing": 0.01
            }
          }
        }
      }
    }
  }
}
```

---

## 19. Recetas rápidas por intención

### 19.1 “Hazlo más premium”

```txt
Targets sugeridos:
- panel surface
- border/edge
- heading text
- CTA button

Cambios:
- materialKind: frosted-glass o ceramic
- edgeShine: medio
- shadowDepth: bajo/medio
- fontMood: premium
- letterSpacing: ligero
- gradient: muy suave
- glow: bajo
```

### 19.2 “Haz el botón más poderoso”

```txt
Targets sugeridos:
- button shell
- button text
- hover state
- pressed state

Cambios:
- buttonTone: CTA
- buttonHeight: +4px
- buttonGlow: medio
- hoverLift: 2px
- pressDepth: 2px
- fontWeight: +1 nivel
- focusRing: visible
```

### 19.3 “Haz el precio más protagonista”

```txt
Targets:
- price number
- currency symbol
- decimal part

Cambios:
- numberSize: +1/+2
- numberWeight: 760
- numericTabular: true
- numberColor: success/accent
- decimalEmphasis: softer
- numberGlow: bajo/medio
```

### 19.4 “Hazlo más limpio”

```txt
Targets:
- panel
- borders
- shadows
- text

Cambios:
- glassAlpha: bajo
- shadowDepth: bajo
- borderAlpha: bajo
- glow: 0
- density: comfortable
- typography: quiet/technical
```

### 19.5 “Quiero más vidrio, pero legible”

```txt
Targets:
- panel
- background
- text

Cambios:
- backdropBlur: medio
- frostVeil: medio
- textContrast: auto
- readabilityVeil: on si hay imagen
- edgeShine: bajo/medio
- avoid holographic text
```

### 19.6 “Quiero que cambie sólo al seleccionar”

```txt
Targets:
- selected state only

Cambios:
- selectedBorderColor
- selectedOverlayAlpha
- selectedGlow
- selectedTextColor opcional

No tocar:
- base
- hover
- disabled
```

---

## 20. Definition of Done TABCTL7 SUPREMO

1. El usuario puede navegar por Grupo → Componente → Capa → Rol → Parte fina.
2. Cada target declara `data-kind`.
3. Los controles se filtran por tipo.
4. Los controles se filtran por estado.
5. Hay estados base/hover/focus/pressed/selected/disabled/loading/error/success.
6. Hay alcance explícito antes de aplicar cambios.
7. Hay herencia visible.
8. Hay override local por pack.
9. Hay reset por estado.
10. Hay reset por pack.
11. Hay preset por rol/capa/componente/grupo.
12. Hay copy JSON por selección.
13. Hay diff de tokens.
14. Hay búsqueda de controles.
15. Hay favoritos.
16. Hay modo simple/pro/forense.
17. Hay validación de contraste.
18. Hay validación de cero real.
19. Hay validación de scope.
20. Hay validación anti contenedores extra.
21. Hay validación anti `!important`.
22. Hay stress test con componentes mixtos.
23. No toca POS real.
24. No toca checkout real.
25. No toca PC/Mobile/Cloud.
26. No toca package/lock.
27. No corre Prisma.
28. No mata procesos.
29. No toca puertos.
30. Si algo no aplica, no aparece o aparece desactivado con explicación.
31. Si un control es peligroso, muestra riesgo.
32. Si un cambio rompe legibilidad, advierte.
33. Si una receta es experimental, se marca.
34. Si el usuario pone 0, se apaga de verdad.
35. Si visual knobs están en 0, el glass/background queda realmente transparente.
36. No hay panel-inside-panel salvo efecto óptico justificado.
37. Se mantiene canvas fijo y panel izquierdo scrollable.
38. Se puede comparar antes/después.
39. Se puede exportar/importar preset.
40. El sistema se siente diseñado, no parchado con cinta canela.

---

## 21. Fuentes técnicas y criterio aplicado

Estas referencias respaldan el enfoque de tokens, estados, controles condicionales, CSS variables, materiales/blur y accesibilidad:

1. Design Tokens Community Group Format Module 2025.10
   https://www.designtokens.org/TR/2025.10/format/

2. W3C Design Tokens Community Group
   https://www.w3.org/community/design-tokens/

3. MDN — CSS custom properties
   https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties

4. MDN — `@property` custom property registration
   https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40property

5. MDN — `backdrop-filter`
   https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter

6. MDN — `linear-gradient()`
   https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/gradient/linear-gradient

7. MDN — CSS filter effects
   https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Filter_effects

8. MDN — `background-blend-mode`
   https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/background-blend-mode

9. Material Design 3 — Buttons
   https://m3.material.io/components/buttons/specs

10. Material Design 3 — Interaction states
   https://m3.material.io/foundations/interaction-states

11. Storybook — ArgTypes
   https://storybook.js.org/docs/api/arg-types

12. Storybook — Controls
   https://storybook.js.org/docs/essentials/controls

13. Apple Human Interface Guidelines — Materials
   https://developer.apple.com/design/human-interface-guidelines/materials

14. Fluent 2 — Design tokens
   https://fluent2.microsoft.design/design-tokens

15. W3C WAI — WCAG 2 overview
   https://www.w3.org/WAI/standards-guidelines/wcag/

16. W3C WAI — WCAG quick reference
   https://www.w3.org/WAI/WCAG22/quickref/

---

## 22. Frase guía para futuros agentes

```txt
TABCTL7 no es un set de sliders globales.
TABCTL7 es un editor visual por intención, target, estado, alcance y receta.
Si no sabes qué target toca una perilla, esa perilla no existe.
Si 0 no apaga de verdad, el control está roto.
Si agregas contenedores para maquillar, ya valió berga.
```
