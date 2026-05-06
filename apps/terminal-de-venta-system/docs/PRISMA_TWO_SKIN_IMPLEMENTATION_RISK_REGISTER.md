# PRISMA Two Skin Implementation Risk Register

**Propósito:** enumerar riesgos de implementar Dark/Light como skins y cómo resolverlos antes de romper PRISMA como piñata en posada.

---

## Riesgo 1: Crear dos componentes por cada skin

### Síntoma

`DarkProductCard.tsx` y `LightProductCard.tsx` empiezan a duplicarse.

### Problema

La UI se parte en dos codebases visuales.

### Solución

Un componente, tokens por skin:

```text
ProductCard + data-prisma-skin
```

---

## Riesgo 2: Hardcodear gold y blue en componentes

### Síntoma

`#e8bd67` y `#1557ff` aparecen en JSX/CSS local de componentes.

### Solución

Usar:

```css
var(--prisma-action-primary)
```

---

## Riesgo 3: El selector cambia layout

### Síntoma

Al cambiar skin, se mueve grid, cart, sidebar o alturas.

### Solución

Tokens estructurales compartidos para layout. El skin solo cambia materiales, colores y sombras.

---

## Riesgo 4: FOUC

### Síntoma

La pantalla parpadea al cargar.

### Solución

Resolver `data-prisma-skin` antes del primer paint. Mantener fallback CSS estable.

---

## Riesgo 5: Light queda plano

### Síntoma

Se ve como dashboard blanco sin profundidad.

### Solución

Usar frosted panels, sombras suaves, radial blue atmosphere e inner highlights.

---

## Riesgo 6: Dark queda gamer/neon

### Síntoma

Demasiado glow, saturación o cyberpunk.

### Solución

Gold cálido, glass controlado, sombras premium y nada de neon chillón.

---

## Riesgo 7: Se rompe la jerarquía de COBRAR

### Síntoma

El CTA deja de dominar.

### Solución

`PayButton` usa `--prisma-action-primary`, altura fija, shadow primaria y ancho completo.

---

## Riesgo 8: Incompatibilidad con tokens viejos

### Síntoma

Ya existen `--prisma-light-*` y `--prisma-gold-*`, y al meter nuevos tokens se duplican criterios.

### Solución

No borrar legacy al inicio. Mapear legacy a semánticos y migrar por etapas.

---

## Riesgo 9: QA visual subjetivo

### Síntoma

“Se ve bien” pero no se parece a la referencia.

### Solución

Capturas obligatorias y checklist por skin. La imagen gana sobre opinión.

---

## Riesgo 10: Meter PC/Slate en esta fase

### Síntoma

El contrato se infla con PC Backoffice, Slate y Mobile.

### Solución

Esta fase es solo:

```text
Dark POS + Light POS
```

Nada de PC Backoffice. Nada de Slate. Esa fiesta es otra calle.
