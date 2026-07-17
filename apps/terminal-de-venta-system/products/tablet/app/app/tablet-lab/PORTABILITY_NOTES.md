# Tablet Lab Portability Notes

Patch: `tabctl2 0707 1038`

`/tablet-lab` is now a **Tablet Cloudglass Visual Control Atlas**. It is intentionally local, dependency-free and isolated from POS/checkout/cart production surfaces.

## Purpose

The lab is not a final product screen. It is a governed visual workshop for component-driven PRISMA Tablet work:

- panel contracts;
- button/action contracts;
- table contracts;
- form/input contracts;
- POS kit preview;
- checkout rail preview;
- turno/caja kit preview;
- state gallery;
- recipe matrix;
- exportable JSON recipe.

## Source references used for design direction

- Component-driven isolated UI workshop pattern.
- Design tokens as named design-system values.
- Data tables as scannable row/column systems with querying/manipulation tools.
- Table toolbar/actions patterns.
- Tablet touch-target safety.

## No-touch boundary

Do not use this patch to alter real POS, checkout, cart, Prisma, lockfiles, dependency manifests, ports, processes or dev servers.

## Background asset

The Pexels background remains scoped to `public/assets/tablet-lab` and is used only as atmospheric lab background, not as logo, trademark or standalone redistributed asset.

---

## TABCTL3 compact immersive atlas

TABCTL3 convierte `/tablet-lab` en una cabina compacta para experimentar con componentes Tablet Cloudglass. La navegación superior se retira de la composición del laboratorio y se incluye una guardia local de runtime para eliminar barras superiores inyectadas por shell dentro de `/tablet-lab`; la navegación inferior permanece como dock principal con `Vender`, `Turno`, `Inventario`, `Ventas`, `Devol.`, `Pendientes` y `Licencia`.

Incluye dropdowns para presets, secciones, grupos de widgets, grupos de efectos, viewport y estados; perillas por grupos; canvas atmosférico fijo con scroll interno; tabla colapsable de presets persistentes; persistencia en `localStorage` con la llave `prisma.tabletLab.tabctl3.savedPresets.v1`; y contratos trazables con `data-component`, `data-preset`, `data-widget-group`, `data-effect-group`, `data-state-mode` y `data-saved-preset`.

No añade dependencias, no toca lockfiles, no ejecuta Prisma, no toca POS real, checkout real, carrito real, Mobile ni PC.



## TABCTL4 minimal containers / transparent zero refinement

- Controls were moved out of the atmospheric canvas into one dedicated left column.
- The canvas background now belongs only to the preview canvas, not the control column.
- Header keeps logo/title/status only; dropdowns live above the knobs.
- Removed the visual pattern of container inside container inside container for the main atlas layout.
- Nested layers are reserved for intentional optical glass effects only: border, specular edge, refraction/highlight, liquid-glass surface treatment.
- Glass-related sliders now support zero values where practical. When glass alpha, blur, border, highlight, edge and glow are zero, preview surfaces are transparent instead of still showing opaque white panels.
- No dependencies, no Prisma, no lockfiles, no dev server, no ports, no process control.

## tabctl6 safe post-Codex continuation

`tabctl6` preserves the post-Codex Tablet Lab copy changes and adds a predefined effect applicability matrix.

Rules:

- Controls stay outside the atmospheric canvas.
- The preview canvas owns the background image.
- Use the fewest containers possible; nested panels are only allowed for glass optical effects.
- Knobs that do not apply to the selected widget group remain visible but disabled with a `sin impacto` hint.
- `Carga visual` and `Carga mixta` remain the visible labels instead of reintroducing old stress-test copy.
- `Glass alpha = 0`, `blur = 0`, `border = 0`, `inner highlight = 0`, `edge shine = 0`, and `specular glow = 0` must not leave opaque ghost glass.
- No POS real, checkout real, carrito, PC, Mobile, Code Atlas, licscope, Prisma, lockfiles or package manifests are touched.
