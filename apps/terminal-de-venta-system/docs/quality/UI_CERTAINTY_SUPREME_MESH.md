# PRISMA UI Certainty Supreme Mesh

UI Certainty Supreme Mesh es la compuerta final para cambios visuales de producto en PRISMA. Convierte registro, contratos, anchors, selectores, alcance y reportes en evidencia verificable antes de aprobar una modificación de interfaz.

Regla central:

```text
Sin CERTIFIED, no hay cambio visual final.
```

## Cobertura Final

La certificación cubre estas superficies objetivo:

| App | Puerto | Surface | Ruta base |
| --- | ---: | --- | --- |
| Chart Lab | 3000 | `chart-lab` | `/` |
| PRISMA Web/Edit | 3110 | `web` | `/` |
| PRISMA Tablet Core | 3120 | `tablet` | `/pos` |
| PRISMA PC Backoffice | 3130 | `pc` | `/dashboard` |
| PRISMA Mobile Adder | 3140 | `mobile` | `/` |
| Control Center | 3150 | `control-center` | `/` |

`shared-ui` queda registrado como tooling sin puerto runtime. No reemplaza a ninguna superficie de producto.

## Estados

- `CERTIFIED`: el owner existe, los anchors requeridos están en el owner, los selectores existen, el scope permite los archivos y no hay conflicto activo.
- `BLOCKED`: falta evidencia contractual, anchor, owner, surface, ruta o scope.
- `DRIFT`: el contrato apunta a un archivo o selector que ya no existe.
- `CONFLICT`: hay propiedad duplicada sobre panel id, anchor, selector, ruta u ownership incompatible.

`BLOCKED`, `DRIFT` y `CONFLICT` sirven para diagnóstico. Ninguna superficie objetivo puede llegar así al cierre de producto.

## Por Qué No Se Aceptan Salidas De Ensayo

Una salida de ensayo puede describir intención, pero no prueba ownership real. Esta compuerta sólo acepta evidencia reproducible: contrato registrado, owner localizado, anchors reales, selectores verificables, scope permitido y reportes generados por CLI. El resultado final de cada superficie objetivo debe ser `CERTIFIED`.

## Archivos Autoritativos

- `.prisma-ui/registry.json`: lista surfaces, paneles, hard states, gates y alcance global.
- `.prisma-ui/surfaces.json`: define app, puerto, rutas, owners, panels, scope y runtime opcional.
- `.prisma-ui/panels/*.json`: contrato por panel con owner, anchors, selectores y scope.
- `tools/quality/ui-certainty.mjs`: CLI estable de certificación.
- `.prisma-ui/current/*.json` y `.md`: reportes generados.

## Onboarding De Superficies

1. Agregar la surface en `.prisma-ui/surfaces.json` con `surface`, `app`, `port`, `routes`, `owners`, `panels`, `allowedScope` y `runtimeProbe`.
2. Agregar el id de surface en `.prisma-ui/registry.json` si forma parte de las superficies objetivo.
3. Crear al menos un contrato en `.prisma-ui/panels/`.
4. Agregar anchors al owner real sin alterar layout, copy, estilos ni comportamiento.
5. Ejecutar `node tools/quality/ui-certainty.mjs certify-all-surfaces --strict`.

## Onboarding De Paneles

Cada contrato de panel debe incluir:

```json
{
  "panel_id": "surface.route.panel",
  "surface": "surface",
  "route": "/route",
  "owner_component": "products/app/path/component.tsx",
  "canonical_selectors": ["[data-prisma-panel=\"surface.route.panel\"]"],
  "required_anchors": [
    { "attribute": "data-prisma-panel", "value": "surface.route.panel" },
    { "attribute": "data-prisma-surface", "value": "surface" },
    { "attribute": "data-prisma-route", "value": "/route" }
  ],
  "allowed_files": ["products/app/path/component.tsx"],
  "exclusive": true
}
```

## Anchors Sin Cambio Visual

Los anchors son atributos HTML o JSX. Agregarlos no debe cambiar DOM visible, CSS, layout, copy, navegación, datos, sincronización ni flujo de venta. La forma esperada es:

```tsx
<main
  data-prisma-panel="tablet.pos.workspace"
  data-prisma-surface="tablet"
  data-prisma-route="/pos"
>
```

Para rutas dinámicas se permite mapear el panel desde la ruta actual si el archivo contiene la tabla contractual y el owner sigue siendo único.

## Comandos Antes De Cambios Visuales

```bash
node tools/quality/ui-certainty.mjs self-test --strict
node tools/quality/ui-certainty.mjs certify-all-surfaces --strict
node tools/quality/ui-certainty.mjs inventory --all
node tools/quality/ui-certainty.mjs doctor --all
node tools/quality/ui-certainty.mjs zero-important
node tools/quality/ui-certainty.mjs scope --all
```

## Comandos Antes De PR

```bash
node --check tools/quality/ui-certainty.mjs
node tools/quality/ui-certainty.mjs self-test --strict
node tools/quality/ui-certainty.mjs certify-all-surfaces --strict
node tools/quality/ui-certainty.mjs inventory --all
node tools/quality/ui-certainty.mjs doctor --all
node tools/quality/ui-certainty.mjs report --all
node tools/quality/ui-certainty.mjs zero-important
node tools/quality/ui-certainty.mjs scope --all
pnpm run verify:zero-important
pnpm run ui:certify:all
pnpm run ui:inventory
pnpm run ui:doctor
pnpm run ui:report
git diff --check
git status --short
```

## Comandos Por Surface

```bash
node tools/quality/ui-certainty.mjs certify --surface <surface> --strict
node tools/quality/ui-certainty.mjs contracts --surface <surface> --strict
node tools/quality/ui-certainty.mjs anchors --surface <surface> --strict
node tools/quality/ui-certainty.mjs selectors --surface <surface> --strict
node tools/quality/ui-certainty.mjs drift --surface <surface>
node tools/quality/ui-certainty.mjs conflicts --surface <surface>
```

## Reportes

El CLI genera JSON y Markdown en `.prisma-ui/current/`:

- `UI_CERT_REPORT`
- `UI_ALL_SURFACES_CERT_REPORT`
- `UI_INVENTORY_REPORT`
- `UI_DOCTOR_REPORT`
- `UI_SCOPE_REPORT`
- `UI_VISUAL_CONTROL_REPORT`
- `UI_EDITABLE_SLOTS_REPORT`
- reportes auxiliares de anchors, contratos, drift, conflictos y cero `!important`

`UI_ALL_SURFACES_CERT_REPORT.json` es el reporte de cierre. Para producto, `status` debe ser `CERTIFIED`, `blockedCount` debe ser `0`, `driftCount` debe ser `0` y `conflictCount` debe ser `0`.

## Visual Control System v1

PRISMA Visual Control System v1 extiende esta compuerta sin cambiar UI visible. Produce el registro de rutas, regiones visuales, owners, CSS, assets, capas, riesgos y slots editables para que una solicitud futura se pueda convertir en un patch seguro y owner-aware.

```bash
node tools/quality/ui-certainty.mjs visual-control:inventory --strict
node tools/quality/ui-certainty.mjs visual-control:owners --strict
node tools/quality/ui-certainty.mjs visual-control:slots --strict
node tools/quality/ui-certainty.mjs visual-control:layers --strict
node tools/quality/ui-certainty.mjs visual-control:report --strict
node tools/quality/ui-certainty.mjs visual-control:certify --strict
```

Los artefactos autoritativos viven en `.prisma-ui/visual-control/`; los reportes de cierre viven en `.prisma-ui/current/`. La guia operativa esta en `docs/quality/PRISMA_VISUAL_CONTROL_SYSTEM_V1.md`.

## Scope

`scope --all` revisa los archivos modificados contra:

- alcance global de UI Certainty;
- `allowedScope` de cada surface;
- `allowed_files` de cada panel.

Archivos de reportes bajo `.prisma-ui/current/**` están permitidos. Baseline autorizado de UI Certainty se registra como evidencia, pero no se usa para ocultar cambios fuera de alcance. Un blocker local operable, como un cambio aislado de `generatedAt`, debe respaldarse, normalizarse sin cambiar configuración funcional y registrarse en evidencia.

## Runtime

Los puertos `3000`, `3110`, `3120`, `3130`, `3140` y `3150` pueden consultarse si ya están vivos. La certificación no debe levantar servidores, matar procesos, liberar puertos, reiniciar apps ni regenerar Prisma. Si runtime no responde y el contrato lo marca opcional, la autoridad de cierre es source, registry, contratos, anchors, selectores, scope y reportes.

## Política Anti Downgrade

Antes de PR se revisa que no haya reducción de scripts, gates, cobertura, dependencias, package manager o lockfiles. Un cambio de lockfile requiere razón técnica directa. Esta certificación no agrega dependencias.

## Política Anti `!important`

`zero-important` debe quedar `CERTIFIED` con count `0`. No se aceptan overrides CSS para forzar un verde visual.

## Resolución De Blockers Operables

Un blocker operable se maneja así:

1. detectar;
2. clasificar;
3. respaldar;
4. resolver de forma quirúrgica;
5. guardar evidencia;
6. volver a ejecutar gates.

El cierre sólo se declara cuando cada superficie objetivo queda `CERTIFIED` y los reportes finales respaldan ese estado.
