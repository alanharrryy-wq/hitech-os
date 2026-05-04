# PRISMA Black Visual Governance Baseline 01E

**Tipo:** entrega no visual / gobierno de capas  
**Objetivo:** poner en cintura el sistema visual antes de volver a tocar estética.  
**Regla madre:** este pass no debe cambiar el look activo de PRISMA. Sólo instala contratos, reglas, checklist y herramientas de verificación.

---

## 1. Por qué existe

PRISMA Black ya tiene una dirección clara: dark glass, premium, ejecutivo, con acentos dorados y sensación de centro de mando. El problema no es falta de efectos. El problema es que los efectos pueden duplicarse por capa: fondo, shell, panel, card, stage y botón.

Este baseline evita que el siguiente pass vuelva a meter haze, blur y glow como si fueran salsa de puesto: todo encima de todo y luego nadie sabe qué estaba sabiendo raro.

---

## 2. No visual change

Este paquete **no modifica CSS activo** de las pantallas.

Instala solamente:

- contrato de gobierno visual;
- checklist QA;
- manifiesto de integración;
- verificador read-only para detectar riesgos de capas;
- documentación de reglas para próximos passes.

Si después de instalar esto la UI se ve diferente, no fue por este paquete. Fue caché, cambios previos o algún gremlin de frontend con licencia vencida.

---

## 3. Modelo de capas autorizado

```text
Capa 1: Fondo global vivo
  - atmósfera
  - haze frío
  - bloom cálido
  - textura/noise
  - motion sutil

Capa 2: Paneles grandes
  - glass fuerte
  - backdrop blur
  - borde direccional
  - sombra profunda
  - highlight interno

Capa 3: Cards
  - glass ligero
  - borde fino
  - contenido legible
  - sin repetir clima global

Capa 4: Product stage
  - vitrina local
  - pedestal
  - sombra del producto
  - glow puntual

Capa 5: Contenido / acciones
  - contraste
  - lectura rápida
  - foco en CTA
```

Regla simple: **el fondo vive, el panel interpreta, la card enmarca, el producto luce y el contenido manda.**

---

## 4. Presupuesto de efectos por pantalla

```yaml
glows_fuertes_maximos: 3
motion_hero_maximo: 1
noise_global: 1
haze_global: 1
specular_fuerte: solo_paneles_grandes
blur_fuerte: paneles_grandes
blur_moderado: cards
blur_minimo: chips_y_botones_densos
```

Prohibido:

- haze por card;
- noise por card;
- motion por card;
- fondo duplicado en body + shell + panel;
- blur igual en panel y card;
- border dorado uniforme en todo;
- glow fuerte en todas las cards.

Si todo brilla, nada brilla. Si todo tiene niebla, ya no es premium: es sauna con inventario.

---

## 5. Perfiles visuales oficiales

### neutral

Uso: default seguro para trabajo diario.

```yaml
haze: on_suave
vignette: on
noise: on_suave
motion: off
panel_blur: on
card_blur: moderado
glows: minimos
```

### fx

Uso: demo, marketing, captura, pitch.

```yaml
haze: on
vignette: on
noise: on
motion: on_sutil
panel_blur: on
card_blur: on_moderado
product_glow: on
cta_glow: on
```

### perf

Uso: equipo lento, tablet limitada, operación pesada.

```yaml
haze: on_bajo
vignette: on
noise: off
motion: off
panel_blur: reducido
card_blur: off_o_reducido
specular: off
glows: minimos
```

---

## 6. Flags visuales autorizadas

```text
stage.haze
stage.vignette
stage.noise
stage.motion
panel.blur
panel.innerStroke
panel.specular
card.blur
card.innerStroke
card.specular
card.shadowAmbient
product.glow
product.pedestal
cta.glow
```

Estas flags no obligan a que todo exista ya en código. Son el contrato para próximos passes.

---

## 7. Reglas por zona

### Fondo

- Debe existir en una sola capa root.
- Puede tener motion sutil.
- No debe repetirse en cada panel.
- Debe verse bien aun sin paneles.

### Paneles grandes

- Pueden usar el glass más rico.
- Pueden tener specular y edge lighting.
- No deben competir todos con la misma intensidad.

### Cards

- No deben duplicar atmósfera global.
- Deben usar glass ligero.
- Sólo product stage puede tener glow local.

### CTAs

- El CTA principal puede usar glow dorado.
- Los secundarios no deben parecer deshabilitados.
- Estados active/disabled/focus deben distinguirse por contraste, no sólo por glow.

### Motion

- Sólo en fondo o hero muy controlado.
- Debe respetar `prefers-reduced-motion`.
- Debe poder apagarse sin romper el look.

---

## 8. Archivos bajo gobierno

```text
products/shared-ui/prisma/tokens/prisma-theme.css
products/shared-ui/prisma/components/prisma-components.css
products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css
products/tablet/app/components/pos/pos.module.css
products/pc/app/app/globals.css
products/tablet/app/app/globals.css
```

Este pass no los modifica. Sólo declara que cualquier cambio visual futuro en esos archivos debe respetar este contrato.

---

## 9. Criterios de aceptación para el siguiente pass estético

```text
[ ] Fondo centralizado en una capa.
[ ] No hay haze local repetido por card.
[ ] Paneles grandes tienen más glass que cards.
[ ] Cards enmarcan, no protagonizan.
[ ] Product stage concentra glow local.
[ ] Máximo 3 glows fuertes por pantalla.
[ ] Motion sólo global o hero.
[ ] reduced-motion apaga animaciones.
[ ] Perfil perf conserva legibilidad.
[ ] CTA principal se lee como acción activa.
[ ] Texto secundario no queda atrapado en neblina.
```

---

## 10. Decisión final

Este baseline es el cinturón antes del traje. Sin esto, cada nuevo pass visual puede ponerse creativo y terminar con otro caldo de capas.

Primero gobernar. Después embellecer. Así hasta el CSS deja de comportarse como colonia sin comité vecinal.
