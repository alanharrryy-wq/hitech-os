# PRISMA Tablet Light Visual Preset Engine

**Paquete:** `PRISMA_TABLET_LIGHT_VISUAL_PRESET_ENGINE_PACKAGE_260525.zip`
**Superficie:** Tablet / POS
**Tema final:** claro, táctil, luminoso, milkglass/pearl/frosted
**Fuente local usada:** `PRISMA_TABLET_LIGHT_PRESET_ENGINE_CONTEXT_20260525_094411.zip`
**Estado:** contrato + mapas machine-readable para siguiente inyector visual. No modifica runtime todavía.

---

## 0. Tesis

PRISMA Tablet no debe aplicar estilos sueltos. Debe aplicar **contratos visuales ejecutables**:

```txt
Ruta real + componentes reales + geometría + layers + adapter del códex + reglas QA
  -> manifiesto validable
  -> inyección visual rápida
  -> verificación
  -> rollback si algo se rompe
```

El resultado esperado es una Tablet clara, rápida, táctil y premium. Nada de Batcueva, nada de cockpit oscuro, nada de “métanle glow a todo y que Dios nos perdone”.

---

## 1. Fuentes técnicas y principios externos

- JSON Schema se usa porque es un lenguaje declarativo para anotar y validar estructura, restricciones y tipos de documentos JSON.
- Playwright se propone para screenshots porque `toHaveScreenshot()` permite generar y comparar capturas visuales entre ejecuciones.
- ECharts necesita contenedores DOM con ancho/alto definidos y debe redimensionarse cuando cambie el contenedor.
- WCAG 2.2 define 24×24 CSS px como tamaño mínimo de target; para PRISMA Tablet POS el contrato sube el piso operativo a 48 px por ergonomía táctil.

URLs de referencia:

```txt
https://json-schema.org/docs
https://playwright.dev/docs/test-snapshots
https://apache.github.io/echarts-handbook/en/concepts/chart-size/
https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
```

---

## 2. Archivos incluidos

| Archivo | Rol |
|---|---|
| `PRISMA_TABLET_LIGHT_VISUAL_PRESET_ENGINE.md` | Documento maestro del motor. |
| `tablet-light-preset.schema.json` | Schema JSON Draft 2020-12 para validar manifiestos de aplicación. |
| `tablet-light-adapter.codex-map.json` | Traducción del códex visual general a Tablet Light. |
| `tablet-preset-application.manifest.json` | Manifiesto aplicable por rutas/componentes reales. |
| `visual-verifier-rules.json` | Reglas QA visual, táctil, contraste, no-dark, customer trust y rollback. |
| `surface-map.generated.json` | Mapa generado desde el ZIP corregido: rutas, componentes, CSS, geometría, layers. |

---

## 3. Política visual no negociable

```txt
Tablet = claro + táctil + legible + rápido + premium controlado.
```

### Permitido

- Daylight Pearl Background.
- Milkglass / Frosted panels.
- Blue action glow suave.
- Pearl hairline rim.
- Motion de toque, confirmación y estado.
- Evidence drawers claros y cerrados.

### Prohibido para Tablet final

- Dark / Night / Obsidian como UI final.
- Graphite dominante.
- Glow fuerte en más de un CTA.
- Hydro rim en cada card.
- WebGL/G5 en CRUD/POS rutinario.
- Texto técnico visible: `payload`, `ack`, `dispatcher`, `canonical`, `debug`.

---

## 4. Layer stack canónico

```txt
L0  Daylight Pearl App Background
L1  Safe Area / Shell Grid
L2  Milkglass Primary Surface
L3  Frosted Content Cards
L4  Pearl Rim / Hairline Borders
L5  Semantic State Tint
L6  Soft Glow only for active/primary state
L7  Motion Response Layer
L8  Evidence / Drawer Overlay
L9  Toast / Modal / Critical Confirmation
L10 Debug/Evidence collapsed by default
```

---

## 5. Motor de aplicación

```txt
Discover
  escanea rutas, componentes, CSS, assets y dependencias
Classify
  asigna dominio, rol visual, densidad, riesgo y usuario
Match
  códex -> Tablet Light Adapter -> route visual budget
Generate
  surface-map + manifest + verifier rules
Apply
  tokens, classes, adapters, wrappers mínimos
Verify
  no-dark, touch, contrast, overflow, screenshots, build
Package
  ZIP único con logs, rollback, reportes y next context
```

---

## 6. Geometría base detectada

El shell actual usa una grilla real detectada en CSS:

```css
.shell {
  grid-template-columns: 220px minmax(0, 1fr);
}
```

El POS actual usa:

```css
.posWorkspace {
  grid-template-columns: minmax(0, 1fr) minmax(400px, 430px);
  gap: 20px;
}
```

El motor respeta esa geometría como base. Una futura inyección puede decidir si conserva sidebar de 220px o migra a rail compacto de 88px, pero no debe inventar geometrías sin verificar overflow.

---

## 7. Rutas detectadas

Se detectaron **32 rutas/páginas** desde `products/tablet`. Las rutas con mayor prioridad de preset:

| Ruta | Preset principal | Pregunta |
|---|---|---|
| `/pos` | `tablet.pos.checkout.daylight-lux.v1` | ¿Qué estoy vendiendo y cómo cobro rápido? |
| `/checkout` | `tablet.pos.checkout.daylight-lux.v1` | ¿Cómo confirmo el cobro sin fricción? |
| `/catalog` | `tablet.catalog.products.frosted-ledger.v1` | ¿Qué productos están listos para venderse? |
| `/stock` | `tablet.catalog.products.frosted-ledger.v1` | ¿Qué existencias requieren atención? |
| `/sales/today` | `tablet.sales.history.pearl-ledger.v1` | ¿Qué se vendió hoy? |
| `/sync` | `tablet.sync.offline.clean-pulse.v1` | ¿Todo está actualizado entre Tablet y PC? |
| `/offline` | `tablet.sync.offline.clean-pulse.v1` | ¿Qué evidencia offline puedo exportar? |
| `/settings/license` | `tablet.settings.soft-form-vault.v1` | ¿La licencia permite operar? |
| `/release-gate` | `tablet.system.release.daylight-gate.v1` | ¿Tablet está lista para operar? |

El detalle completo vive en `surface-map.generated.json`.

---

## 8. Customer Trust Layer

Para POS/checkout se declara una capa especial:

```txt
Cliente puede ver:
- productos
- cantidad
- precio unitario
- descuento
- impuestos
- total
- estado de pago

Cliente jamás debe ver:
- costo/margen
- stock interno sensible
- uuid
- sync internals
- payload
- debug
- notas del operador
```

Esto vuelve PRISMA diferenciador: el cliente entiende y confía, el cajero opera rápido, soporte conserva evidencia sin embarrarla en la pantalla.

---

## 9. Dependencias y regla anti-invención

`package.json` de Tablet detecta runtime con Next, React, React DOM, Prisma Client y Zod. El motor lista librerías visuales como opcionales, pero **no debe generar imports de Radix/Motion/Vaul/Sonner/cmdk/ECharts/TanStack si no están instaladas o si el ZIP de inyección no incluye instalación + verificación**.

Esto evita el clásico “la UI quedó preciosa hasta que hizo build y valió berga”.

---

## 10. Uso recomendado

1. Validar `tablet-preset-application.manifest.json` contra `tablet-light-preset.schema.json`.
2. Usar `surface-map.generated.json` para ubicar rutas/componentes/CSS.
3. Usar `tablet-light-adapter.codex-map.json` para convertir recetas del códex a Tablet Light.
4. Aplicar por ruta con rollback.
5. Correr `visual-verifier-rules.json` como gate.
6. Sólo aceptar si pasa build + no-dark + touch + contrast + overflow.

---

## 11. Próximo salto

Convertir este paquete en inyector:

```txt
PowerShell wrapper + Python engine
  -> lee manifest
  -> aplica tokens/classes/adapters
  -> genera backups
  -> corre verifiers
  -> rollback automático si falla
  -> report ZIP final
```

Frase madre:

> **PRISMA Tablet no aplica decoración. Aplica contratos visuales claros y verificables.**

# PRISMA Tablet Background Presets Extension

## Presets

### pearl-grey-mist

Gris claro premium, sobrio, calmado y legible. Uso recomendado: POS, catálogo, ventas, settings, stock.

### rain-drift-subtle

Fondo lluvioso muy sutil con gotitas y escurrimientos casi imperceptibles. Uso recomendado: sync, idle, ambient states y pantallas donde una sensación fresca ayude sin estorbar.

## Guardrails

- Tablet final sigue siendo claro, táctil y luminoso.
- Nada oscuro dominante.
- Las gotas de lluvia no deben competir con texto, precio, total, CTA o estados críticos.
- `prefers-reduced-motion: reduce` debe dejar el fondo estático o casi estático.
- La lluvia es una capa ambiental, no una atracción de feria.


## Pearl Grey Mist v2 Crystal Code Preset

Preset ID:

```txt
pearl-grey-mist-v2-crystal
```

Installed code assets:

```txt
prisma-tablet-pearl-grey-mist-v2.css
prisma-tablet-pearl-grey-mist-v2.js
pearl-grey-mist-v2-smoke-test.html
```

Purpose:

- Make the background clearly grey/pearl, not just white.
- Add crystal panels with blur, inner highlight, hydro rim and soft depth.
- Add tasteful ambient motion.
- Keep Tablet light-only and touch-first.


## Codex Native Glass Gallery Demo

Installed smoke test:

```txt
tablet-codex-glass-gallery-smoke-test.html
```

Purpose:

- Review many codex presets in a single scrollable Tablet Light demo.
- Compare glass, rim, glow, motion, bundles and library capabilities.
- Keep the demo codex-traceable through `tablet-codex-glass-gallery.demo.json`.

Policy:

- Light-only Tablet adapter.
- Codex preset IDs must remain visible.
- Strong glow and hydro rim are budgeted.
- Reduced motion must pass.


## Codex Background Gallery Demo

Installed smoke test:

```txt
tablet-codex-background-gallery-smoke-test.html
```

Purpose:

- Review codex-native Tablet Light backgrounds as real backgrounds.
- Always test backgrounds with glass panels on top.
- Keep codex traceability through `tablet-codex-background-gallery.demo.json`.
