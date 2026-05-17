# PRISMA ChartOps Layer v0.1

## Propósito

PRISMA ChartOps es la capa de gobierno, edición y trazabilidad visual para todas las gráficas de PRISMA.

Su objetivo no es solo saber dónde vive cada gráfica, sino hacer que cada gráfica sea:

- **Encontrable**: saber exactamente qué archivo tocar.
- **Editable**: saber qué perillas visuales puede mover un diseñador o agente.
- **Explicable**: saber qué pregunta operativa responde.
- **Portable**: poder llevarla de PC a Tablet o Mobile con perfiles controlados.
- **Gobernada**: evitar datos falsos, imports peligrosos, estilos duplicados y hacks de runtime.

Frase madre:

> Cada gráfica debe ser encontrable, editable, explicable y portable.

---

## Contexto actual del pack

El pack actual de gráficas ya tiene base correcta:

- `shared/prisma-charts` como motor compartido.
- Wrapper ECharts común.
- Loader único.
- Contratos de datos.
- Theme.
- Registry.
- Mocks determinísticos.
- Adapters.
- Option builders.
- Formatters.
- Quality helpers.
- 14 gráficas preview repartidas entre PC, Tablet y Mobile.

La siguiente evolución no debe ser solo conectar datos reales. Debe ser crear una capa ChartOps para que las gráficas puedan crecer, editarse y auditarse sin volverse un tianguis de archivos sueltos.

---

# 1. Componentes de ChartOps

## 1.1 Chart Atlas

El **Chart Atlas** es el mapa central de todas las gráficas.

Debe responder:

- Qué gráficas existen.
- Dónde viven.
- Qué contrato usan.
- Qué option builder las dibuja.
- Qué adapter las alimenta.
- Qué rutas las muestran.
- Qué familia visual tienen.
- Qué estados soportan.
- Qué tan listas están para producción.

Ejemplo de archivo propuesto:

```txt
shared/prisma-charts/prismaChartAtlas.ts
```

---

## 1.2 Chart Passport

El **Chart Passport** es la ficha individual de una gráfica.

Cada gráfica debe tener un pasaporte obligatorio.

Debe permitir que alguien diga:

> “Quiero editar el radar.”

Y el sistema responda:

> “Toca estos archivos, estas perillas, estos estados y cuidado con estos límites.”

---

## 1.3 Visual Knobs

Los **Visual Knobs** son perillas explícitas para editar el look de una gráfica sin romper datos ni contratos.

Ejemplos:

- `radius`
- `lineWidth`
- `areaOpacity`
- `gridOpacity`
- `axisLabelWeight`
- `tooltipDensity`
- `statusPalette`
- `ringThickness`
- `sparklineGlow`

Regla:

> Si una edición visual común requiere tocar 5 lugares, falta un knob.

---

## 1.4 Visual Recipes

Las **Visual Recipes** son recetas por familia de gráfica.

No se debe repetir estilo premium en 14 lugares distintos. Debe existir una receta para cada familia visual.

Ejemplos:

```txt
shared/prisma-charts/recipes/radarRecipe.ts
shared/prisma-charts/recipes/treemapRecipe.ts
shared/prisma-charts/recipes/waterfallRecipe.ts
shared/prisma-charts/recipes/timelineRecipe.ts
shared/prisma-charts/recipes/ringsRecipe.ts
shared/prisma-charts/recipes/sparkCardsRecipe.ts
```

Cada receta debe definir:

- tokens visuales base.
- defaults premium.
- overrides por superficie.
- estados visuales.
- densidad de etiquetas.
- tooltip style.
- motion/interacción segura.

---

## 1.5 Design Token Contract

Los tokens deben ser semánticos, no colores sueltos.

Ejemplos:

```txt
status.live
status.partial
status.stale
status.offline
status.unknown

risk.critical
risk.high
risk.medium
risk.low

chart.axis.subtle
chart.grid.soft
chart.line.premium
chart.area.crystal
chart.tooltip.glass
chart.glow.primary

surface.pc.background
surface.tablet.background
surface.mobile.background
```

Regla:

> No decir “azul bonito”; decir `chart.line.premium`.

---

## 1.6 Chart Lab Inspector

El **Chart Lab Inspector** es una vista en PC para ver, comparar e inspeccionar gráficas.

Ruta conceptual:

```txt
/prisma-insights/chart-lab?preview=charts
```

Debe mostrar las 14 gráficas y permitir inspeccionar:

- chartId.
- familia visual.
- componente.
- option builder.
- contrato.
- adapter.
- mock.
- quality state.
- rutas donde aparece.
- visual knobs disponibles.
- estados disponibles.

---

## 1.7 Human Intent Dictionary

El **Human Intent Dictionary** traduce frases humanas a acciones técnicas.

Ejemplos:

```txt
“haz el radar más premium”
-> chartId: mobile.healthRadarCompact
-> edit: radar visual recipe
-> knobs: lineWidth, areaOpacity, splitLineOpacity, labelWeight, pointGlow

“la gráfica de frescura se ve equis”
-> chartId: mobile.freshnessRings
-> edit: rings recipe
-> knobs: ringThickness, ringGap, statusPalette, centerLabelSize

“el waterfall debe verse más ejecutivo”
-> chartId: pc.financialOperationalWaterfall
-> edit: waterfall recipe
-> knobs: connectorStyle, totalBarEmphasis, labelFormatter, valueDensity
```

Regla:

> El lenguaje humano debe llevar directo al archivo correcto.

---

## 1.8 State Gallery

Cada gráfica debe tener estados visuales oficiales:

- `happy`
- `empty`
- `partial`
- `stale`
- `offline`
- `unknown`
- `dense`
- `critical`

Esto evita diseñar solo el “caso bonito”. PRISMA debe verse confiable incluso cuando faltan datos.

---

## 1.9 Handoff Pack

El ZIP futuro para editar gráficas debe incluir:

```txt
chart-atlas.json
chart-passports/
visual-recipes/
design-tokens/
human-intent-dictionary.md
state-gallery.md
source-map.md
edit-guide.md
routes.md
validation-report.json
```

Regla:

> Un ZIP de gráficas debe ser autoexplicable.

---

## 1.10 Guardrails

Reglas no negociables:

- No importar ECharts fuera de `shared/prisma-charts`.
- No tocar aliases runtime de React.
- No mapear `react/jsx-runtime` a `@types/react`.
- No inventar datos.
- No hacer queries directas a DB desde cliente.
- No meter secretos en frontend.
- No activar feature flags por default.
- No tocar el clean score principal del Control Center con gauges/donuts/meters.
- No duplicar lógica visual entre PC, Tablet y Mobile.

---

# 2. Chart Passport Standard

Cada gráfica debe tener un pasaporte con esta estructura.

## 2.1 Campos obligatorios

```txt
chartId:
displayName:
shortName:
family:
surface:
status:
questionAnswered:
primaryUser:
routePreview:
routeProduction:
componentFile:
cardWrapperFile:
optionBuilderFile:
optionBuilderName:
contractFile:
contractType:
adapterFile:
adapterName:
mockFile:
mockName:
registryFile:
qualityModel:
visualRecipe:
visualKnobs:
states:
interactions:
accessibility:
knownRisks:
doNotTouch:
editPlaybook:
validation:
```

---

## 2.2 Definición de campos

### `chartId`

Identificador estable, único y buscable.

Formato recomendado:

```txt
<surface>.<family>.<name>
```

Ejemplos:

```txt
mobile.radar.healthCompact
pc.risk.inventoryTreemap
pc.timeline.decisionLedger
mobile.rings.freshness
```

---

### `displayName`

Nombre visible de la gráfica.

Ejemplo:

```txt
Health Radar Compact
```

---

### `shortName`

Nombre corto para labels internos o UI compacta.

Ejemplo:

```txt
Health Radar
```

---

### `family`

Familia visual.

Opciones iniciales:

```txt
flow
density
network
treemap
timeline
waterfall
strip
matrix
stack
radar
rings
sparks
bands
```

---

### `surface`

Superficie original.

Opciones:

```txt
pc
tablet
mobile
shared
```

---

### `status`

Estado de madurez.

Opciones:

```txt
preview_mock
partial_real
real_data
production_ready
deprecated
```

---

### `questionAnswered`

Pregunta que responde la gráfica.

Ejemplo:

```txt
¿Qué dimensión de salud operativa está débil y por qué?
```

---

### `primaryUser`

Quién la usa.

Opciones sugeridas:

```txt
owner
operator
manager
auditor
admin
system
```

---

### `routePreview`

Ruta para verla en preview.

Ejemplo:

```txt
/prisma-command?preview=charts
```

---

### `routeProduction`

Ruta donde vive en producción, si aplica.

---

### `componentFile`

Archivo React/TSX de la gráfica.

---

### `cardWrapperFile`

Archivo de la card visual que la envuelve.

---

### `optionBuilderFile`

Archivo donde vive la configuración ECharts.

---

### `optionBuilderName`

Función que construye las opciones ECharts.

---

### `contractFile`

Archivo del contrato de datos.

---

### `contractType`

Tipo TypeScript de entrada.

---

### `adapterFile`

Archivo que transforma datos reales en view model de la gráfica.

---

### `adapterName`

Función adapter.

---

### `mockFile`

Archivo donde vive el mock determinístico.

---

### `mockName`

Función o constante mock.

---

### `registryFile`

Archivo donde se registra metadata, propósito e interacciones.

---

### `qualityModel`

Qué calidad/frescura/confianza reporta.

Debe incluir:

```txt
sourceLabel
freshness
confidence
emptyState
staleSources
```

---

### `visualRecipe`

Receta visual usada.

Ejemplo:

```txt
radarRecipe
```

---

### `visualKnobs`

Perillas visuales editables.

Cada knob debe tener:

```txt
name
purpose
safeRange
whereApplied
risk
```

---

### `states`

Estados visuales soportados.

---

### `interactions`

Interacciones permitidas.

Ejemplos:

```txt
hoverTooltip
clickFocus
legendToggle
drawerDrilldown
```

---

### `accessibility`

Requisitos de accesibilidad.

Debe incluir:

```txt
ariaLabel
textDescription
nonColorSignal
keyboardFocus
```

---

### `knownRisks`

Riesgos técnicos o visuales.

---

### `doNotTouch`

Cosas peligrosas.

---

### `editPlaybook`

Guía rápida para editar.

Debe separar:

```txt
visualEdit
dataEdit
contractEdit
layoutEdit
```

---

### `validation`

Cómo validar esa gráfica.

Debe incluir:

```txt
previewRoute
expectedSelectors
verifier
manualChecks
```

---

# 3. Pasaporte ejemplo: MobileHealthRadarCompact

## 3.1 Ficha

```txt
chartId: mobile.radar.healthCompact
displayName: Health Radar Compact
shortName: Health Radar
family: radar
surface: mobile
status: preview_mock
questionAnswered: ¿Qué dimensiones de salud operativa están débiles y por qué?
primaryUser: owner
routePreview: /prisma-command?preview=charts
routeProduction: /prisma-command
componentFile: products/mobile/app/app/prisma-command/charts/MobileHealthRadarCompact.tsx
cardWrapperFile: products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx
optionBuilderFile: shared/prisma-charts/prismaChartOptions.ts
optionBuilderName: healthRadarCompactOption
contractFile: shared/prisma-charts/prismaChartContracts.ts
contractType: HealthRadarAxis[]
adapterFile: shared/prisma-charts/prismaChartAdapters.ts
adapterName: buildHealthRadarCompactViewModel
mockFile: shared/prisma-charts/prismaChartMocks.ts
mockName: mockHealthRadarAxes
registryFile: shared/prisma-charts/prismaChartRegistry.ts
qualityModel: PrismaChartQuality
visualRecipe: radarRecipe
```

---

## 3.2 Pregunta que responde

```txt
¿Qué dimensión de salud está débil: data quality, sync, alertas, inventario, uptime o cashflow?
```

No debe responder “todo está bien” si faltan datos. Debe mostrar honestamente:

- confianza.
- frescura.
- fuente.
- razón principal.

---

## 3.3 Contrato de datos

```txt
HealthRadarAxis = {
  axis: data_quality | sync | alerts | inventory | uptime | cashflow
  label: string
  value: number
  status: PASS | DEGRADED | FAIL | UNKNOWN
  confidence: number
  staleMinutes: number
  topReason?: string
}
```

---

## 3.4 Visual knobs del radar

```txt
radius
  purpose: controla tamaño del radar dentro de la card
  safeRange: 52% - 72%
  whereApplied: radar.radius
  risk: si sube demasiado, corta labels

axisNameColor
  purpose: color de nombres de ejes
  safeRange: token chart.axis.label
  whereApplied: radar.axisName.color
  risk: bajo contraste en mobile

axisNameWeight
  purpose: jerarquía tipográfica de ejes
  safeRange: 600 - 850
  whereApplied: radar.axisName.fontWeight
  risk: exceso de peso visual

splitLineOpacity
  purpose: presencia de líneas internas
  safeRange: 0.08 - 0.28
  whereApplied: radar.splitLine.lineStyle.color
  risk: ruido visual

splitAreaOpacity
  purpose: profundidad cristalina del área interna
  safeRange: 0.02 - 0.12
  whereApplied: radar.splitArea.areaStyle.color
  risk: se puede ver lodoso si sube demasiado

areaFillOpacity
  purpose: relleno de la figura radar
  safeRange: 0.10 - 0.32
  whereApplied: series.data.areaStyle.color
  risk: puede tapar grid y labels

lineColor
  purpose: color principal de la silueta
  safeRange: token chart.line.premium
  whereApplied: series.data.lineStyle.color
  risk: rompe identidad si usa color random

lineWidth
  purpose: grosor de línea del radar
  safeRange: 2 - 4
  whereApplied: series.data.lineStyle.width
  risk: demasiado grueso se ve juguete

pointColor
  purpose: color de nodos/ejes
  safeRange: token chart.point.accent
  whereApplied: series.data.itemStyle.color
  risk: bajo contraste

pointSize
  purpose: tamaño de puntos
  safeRange: 3 - 8
  whereApplied: series.symbolSize
  risk: clutter en mobile

tooltipDensity
  purpose: cantidad de info mostrada en tooltip
  safeRange: compact | standard | rich
  whereApplied: tooltip.formatter
  risk: tooltip enorme en mobile
```

---

## 3.5 Estados visuales del radar

```txt
happy
  condición: todos los valores >= 80 y confianza alta
  visual: línea azul limpia, área cristalina suave

partial
  condición: alguna fuente parcial o confianza media
  visual: chip partial, tooltip explica fuentes incompletas

stale
  condición: staleMinutes excede máximo aceptable
  visual: eje afectado con acento ámbar, footer muestra stale source

offline
  condición: fuente crítica sin datos
  visual: no inventar valor; eje UNKNOWN o placeholder honesto

critical
  condición: uno o más ejes < 50
  visual: acento naranja/rojo controlado, no alarmismo barato

empty
  condición: data.length === 0
  visual: empty state textual, sin radar falso
```

---

## 3.6 Edit playbook del radar

### Visual edit

Tocar:

```txt
shared/prisma-charts/recipes/radarRecipe.ts
shared/prisma-charts/prismaChartOptions.ts
products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx
products/mobile/app/app/prisma-command/prisma-mobile-command.module.css
```

No tocar:

```txt
HealthRadarAxis
adapter real
tsconfig
ECharts loader
```

---

### Data edit

Tocar:

```txt
shared/prisma-charts/prismaChartAdapters.ts
mobile snapshot/source view model
```

No tocar:

```txt
option builder visual
CSS
React runtime aliases
```

---

### Contract edit

Tocar:

```txt
shared/prisma-charts/prismaChartContracts.ts
adapter
mock
verifier
atlas
```

Solo hacerlo si realmente cambió la semántica de datos.

---

### Layout edit

Tocar:

```txt
products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx
products/mobile/app/app/prisma-command/prisma-mobile-command.module.css
MobileChartCard.tsx
```

No tocar:

```txt
healthRadarCompactOption
```

---

## 3.7 Phrases to edit mapping

```txt
“haz el radar más premium”
-> visual edit
-> radarRecipe
-> lineWidth, areaFillOpacity, splitAreaOpacity, axisNameWeight, pointGlow

“el radar se ve muy chico”
-> visual edit
-> radius, chart height, card spacing

“los labels del radar se leen mal”
-> visual edit
-> axisNameColor, axisNameWeight, label formatter, radius

“el radar trae datos falsos”
-> data edit
-> adapter, mock fallback, quality state

“quiero otro eje en el radar”
-> contract edit
-> HealthRadarAxis axis union, adapter, mock, option builder, verifier

“en mobile ocupa mucho espacio”
-> layout edit
-> card height, compact profile, chart deck layout
```

---

# 4. Familias visuales iniciales

## 4.1 Flow

Gráficas:

- `PcCausalFlowRibbon`

Perillas:

- ribbon width.
- ribbon opacity.
- node spacing.
- flow color by status.
- tooltip richness.

---

## 4.2 Density

Gráficas:

- `PcOperationalDensityField`

Perillas:

- heat intensity.
- gradient palette.
- cell radius.
- grid opacity.
- time label density.

---

## 4.3 Network

Gráficas:

- `PcServiceDependencyGraph`

Perillas:

- node size.
- edge thickness.
- edge opacity.
- critical halo.
- layout force.

---

## 4.4 Treemap

Gráficas:

- `PcInventoryRiskTreemap`

Perillas:

- tile padding.
- label density.
- severity palette.
- breadcrumb depth.
- impact emphasis.

---

## 4.5 Timeline

Gráficas:

- `PcDecisionLedgerTimeline`
- `MobileOwnerPulseTimeline`

Perillas:

- marker size.
- line smoothness.
- event density.
- threshold style.
- date label density.

---

## 4.6 Waterfall

Gráficas:

- `PcFinancialOperationalWaterfall`

Perillas:

- connector style.
- total bar emphasis.
- positive/negative palette.
- label formatter.
- y-axis density.

---

## 4.7 Strip

Gráficas:

- `TabletShiftPulseStrip`

Perillas:

- segment height.
- gap.
- time tick density.
- status palette.
- touch target size.

---

## 4.8 Matrix

Gráficas:

- `TabletSyncOutboxStatusMatrix`

Perillas:

- cell size.
- status icon style.
- row density.
- column density.
- offline emphasis.

---

## 4.9 Stack

Gráficas:

- `MobileActionInboxPriorityStack`

Perillas:

- bar thickness.
- stack gap.
- priority palette.
- label visibility.
- legend density.

---

## 4.10 Radar

Gráficas:

- `MobileHealthRadarCompact`

Perillas:

- radius.
- axis label style.
- split line opacity.
- area fill opacity.
- line width.
- point glow.

---

## 4.11 Rings

Gráficas:

- `MobileFreshnessRings`

Perillas:

- ring thickness.
- ring gap.
- center label size.
- status palette.
- stale emphasis.

---

## 4.12 Sparks

Gráficas:

- `MobileIncidentSparkCards`

Perillas:

- sparkline width.
- area fill.
- endpoint dot.
- delta badge.
- severity color.

---

## 4.13 Bands

Gráficas:

- `MobileConfidenceMeterBands`

Perillas:

- band height.
- track opacity.
- fill gradient.
- handle size.
- percentage pill style.

---

# 5. Human Intent Dictionary v0.1

## 5.1 Intenciones visuales

```txt
“hazla más premium”
-> editar visual recipe de la familia
-> subir profundidad, jerarquía, glass, glow controlado, label polish

“se ve muy cargada”
-> bajar label density, grid opacity, legends, tooltip default

“se ve muy plana”
-> subir depth, area gradient, shadows, line emphasis, card inner glow

“se ve muy juguete”
-> bajar saturación, reducir glow, aumentar spacing, usar tokens silver/blue sobrios

“se ve muy técnica”
-> mejorar título, subtitle, explanation chips, tooltip narrativo

“no se entiende”
-> revisar questionAnswered, labels, legend, tooltip, state chips

“quiero que se vea ejecutiva”
-> compactar detalles, subir KPIs, bajar ruido, enfatizar impacto y decisión

“quiero que se vea operativa”
-> enfatizar estado, acción, urgencia, offline/partial, touch readability

“quiero que se vea mobile premium”
-> compact profile, menos labels, más estados, card hierarchy, bottom action
```

---

## 5.2 Intenciones de datos

```txt
“está mostrando datos falsos”
-> revisar adapter y mock fallback

“quiero datos reales”
-> conectar adapter a fuente segura server/API

“quiero agregar una métrica”
-> revisar contrato, adapter, mock, option builder y atlas

“quiero quitar una métrica”
-> revisar contrato si es semántica o solo visual filter
```

---

## 5.3 Intenciones de layout

```txt
“quiero moverla a PC”
-> surface profile desktop/lab, no copiar lógica

“quiero moverla a Mobile”
-> crear mobile profile compacto, no usar versión desktop cruda

“quiero verla junto con todas”
-> Chart Lab

“quiero compararla con otra”
-> Chart Lab grouping by family/status/source
```

---

# 6. Estructura futura de archivos

```txt
shared/prisma-charts/
  PrismaEChart.tsx
  prismaEchartsLoader.ts
  prismaChartContracts.ts
  prismaChartAdapters.ts
  prismaChartMocks.ts
  prismaChartOptions.ts
  prismaChartFormatters.ts
  prismaChartQuality.ts
  prismaChartRegistry.ts
  prismaChartAtlas.ts
  prismaChartTokens.ts
  prismaChartIntentDictionary.ts

  passports/
    mobile.radar.healthCompact.passport.ts
    mobile.rings.freshness.passport.ts
    mobile.bands.confidence.passport.ts
    pc.treemap.inventoryRisk.passport.ts
    pc.timeline.decisionLedger.passport.ts

  recipes/
    radarRecipe.ts
    treemapRecipe.ts
    waterfallRecipe.ts
    timelineRecipe.ts
    ringsRecipe.ts
    sparkCardsRecipe.ts
    densityRecipe.ts
    networkRecipe.ts
    matrixRecipe.ts
    stripRecipe.ts
    stackRecipe.ts
    flowRecipe.ts

  state-gallery/
    radarStates.ts
    treemapStates.ts
    timelineStates.ts
```

---

# 7. Reglas de edición futura

## 7.1 Si la edición es visual

Primero buscar:

```txt
chartId -> passport -> visualRecipe -> visualKnobs -> optionBuilder
```

No tocar adapters ni contracts.

---

## 7.2 Si la edición es de datos

Primero buscar:

```txt
chartId -> passport -> adapter -> contract -> quality state
```

No tocar CSS ni recipes salvo que cambie semántica visual.

---

## 7.3 Si la edición es de layout

Primero buscar:

```txt
chartId -> passport -> route -> cardWrapper -> page/deck layout
```

No tocar option builder salvo que cambie tamaño interno.

---

## 7.4 Si la edición es de contrato

Primero buscar:

```txt
chartId -> contract -> adapter -> mock -> optionBuilder -> verifier -> atlas
```

Debe ser la edición menos frecuente.

---

# 8. Definition of Done para ChartOps

ChartOps queda listo cuando:

- Las 14 gráficas tienen pasaporte.
- Existe `prismaChartAtlas.ts`.
- Existe `PRISMA_CHART_ATLAS.md`.
- Existe `Human Intent Dictionary`.
- Existen recipes por familia.
- Existe token contract centralizado.
- Existe Chart Lab Inspector.
- El ZIP futuro incluye metadata autoexplicable.
- El verificador falla si una gráfica no tiene pasaporte o chartId.
- Un agente puede encontrar cómo editar una gráfica en menos de 2 minutos.

---

# 9. Agregar nuevas gráficas en el futuro

## 9.1 Respuesta corta

Con ChartOps, agregar nuevas gráficas debe ser sencillo, pero no debe ser informal.

La meta es que una nueva gráfica no nazca como archivo suelto, sino como una pieza gobernada.

Frase clave:

> Nueva gráfica = nuevo pasaporte + contrato + adapter + mock + recipe/profile + atlas + estado visual + verificador.

---

## 9.2 Lo que el MD actual resuelve

El estándar actual ya ayuda a:

- encontrar dónde vive cada gráfica.
- saber qué archivos tocar.
- separar visual/data/contract/layout.
- definir knobs visuales.
- mapear intención humana a edición técnica.
- evitar hacks de runtime.
- mantener consistencia visual.

Pero para agregar gráficas nuevas de forma realmente fácil, hace falta una capa extra: **Chart Creation Kit**.

---

## 9.3 Chart Creation Kit

El **Chart Creation Kit** es el conjunto de plantillas y herramientas para crear una gráfica nueva sin empezar desde cero.

Debe incluir:

```txt
1. chart-type decision tree
2. chart scaffold generator
3. chart passport template
4. data contract template
5. adapter template
6. mock data template
7. option builder template
8. visual recipe selector
9. state gallery template
10. verifier registration checklist
```

---

## 9.4 Flujo ideal para crear una gráfica nueva

Cuando el usuario diga:

```txt
Necesito una gráfica nueva para X.
```

El sistema debe seguir este flujo:

```txt
1. Definir pregunta operativa
2. Elegir familia visual
3. Crear chartId
4. Crear contrato de datos
5. Crear mock determinístico
6. Crear adapter real o placeholder honesto
7. Crear option builder ECharts
8. Crear componente React
9. Crear pasaporte
10. Registrar en atlas
11. Agregar estado gallery
12. Agregar verificación
13. Mostrar en Chart Lab
```

---

## 9.5 Decision Tree para elegir tipo de gráfica

```txt
¿Quieres mostrar relación causa -> efecto -> acción?
-> flow / ribbon / sankey

¿Quieres mostrar concentración o presión por tiempo/zona?
-> density / heatmap

¿Quieres mostrar dependencias entre entidades?
-> network / graph

¿Quieres mostrar composición jerárquica con impacto?
-> treemap / sunburst

¿Quieres mostrar decisiones o eventos en el tiempo?
-> timeline / scatter timeline

¿Quieres mostrar impacto positivo/negativo acumulado?
-> waterfall

¿Quieres mostrar turnos/estados operativos por tiempo?
-> strip

¿Quieres mostrar estado por entidad vs sistema?
-> matrix

¿Quieres priorizar colas o carga por severidad?
-> stack

¿Quieres comparar dimensiones de salud?
-> radar

¿Quieres mostrar frescura/confianza por fuente?
-> rings / gauges controlados

¿Quieres mostrar microtendencias por categoría?
-> sparks

¿Quieres mostrar niveles de confianza por dimensión?
-> bands

¿Quieres mostrar distribución geográfica?
-> map, pero solo si hay semántica territorial real

¿Quieres mostrar ranking simple?
-> bar/list hybrid, no inventar chart complejo
```

---

## 9.6 New Chart Request Contract

Para pedir una gráfica nueva, el usuario o agente debe llenar como mínimo:

```txt
name:
questionAnswered:
primaryUser:
surface:
dataSource:
entities:
timeRange:
statusStates:
interactionNeeded:
visualFamilyGuess:
productionRisk:
```

Ejemplo:

```txt
name: Supplier Reliability Drift
questionAnswered: ¿Qué proveedores están perdiendo confiabilidad y desde cuándo?
primaryUser: manager
surface: pc
surfaceSecondary: mobile compact
entity: supplier
timeRange: 30d
statusStates: live, partial, stale, unknown
interactionNeeded: click supplier -> evidence drawer
visualFamilyGuess: timeline + bands
productionRisk: medium
```

---

## 9.7 Archivos que debe crear una gráfica nueva

Mínimo:

```txt
shared/prisma-charts/passports/<chartId>.passport.ts
shared/prisma-charts/prismaChartContracts.ts
shared/prisma-charts/prismaChartAdapters.ts
shared/prisma-charts/prismaChartMocks.ts
shared/prisma-charts/prismaChartOptions.ts
products/<surface>/app/app/<route>/charts/<ComponentName>.tsx
```

Si la familia visual es nueva:

```txt
shared/prisma-charts/recipes/<family>Recipe.ts
shared/prisma-charts/state-gallery/<family>States.ts
```

También debe actualizar:

```txt
shared/prisma-charts/prismaChartAtlas.ts
shared/prisma-charts/prismaChartRegistry.ts
shared/prisma-charts/prismaChartIntentDictionary.ts
docs/prisma/PRISMA_CHART_ATLAS.md
tools/verify_prisma_chart_atlas_01.mjs
```

---

## 9.8 Criterio de aceptación de una gráfica nueva

Una gráfica nueva solo se considera aceptada si cumple:

```txt
- tiene chartId único
- tiene pasaporte
- está en atlas
- tiene contrato tipado
- tiene mock determinístico
- tiene adapter real o placeholder honesto
- tiene option builder separado
- usa receta visual o declara una nueva
- soporta empty/partial/stale/offline/unknown donde aplique
- aparece en Chart Lab
- no importa ECharts fuera de shared/prisma-charts
- no inventa datos
- no toca React runtime aliases
- pasa verificador
```

---

## 9.9 Semáforo de sencillez

```txt
Fácil
- nueva gráfica dentro de familia existente
- datos ya existen en API/adapter
- solo requiere option builder + componente + passport

Medio
- nueva combinación visual
- datos existen pero requieren transformación
- necesita recipe override o surface profile nuevo

Difícil
- nueva familia visual no existente
- datos no existen o requieren backend nuevo
- requiere drill-down/evidencia nueva

No permitido sin diseño previo
- requiere client-side DB
- requiere secretos
- inventa datos
- rompe regla Mobile supervisa / Tablet opera / PC gobierna
```

---

## 9.10 Regla de oro para nuevas gráficas

No se agrega una gráfica porque “se ve bonita”.

Se agrega porque responde una pregunta operativa mejor que tabla, card o texto.

Formato obligatorio:

```txt
Esta gráfica existe para responder: ________
Si no responde eso en 5 segundos, no está lista.
```

---

# 10. Regla final

No queremos solo gráficas bonitas.

Queremos un sistema donde cada gráfica sea una pieza gobernada del Knowledge OS:

```txt
Dato real -> Adapter -> Contract -> Option Builder -> Visual Recipe -> Chart Component -> Surface Profile -> Atlas -> Passport -> Inspector
```

Para gráficas nuevas:

```txt
Pregunta operativa -> Familia visual -> Scaffold -> Passport -> Atlas -> Lab -> Verifier
```

Ese es el camino para que PRISMA se vea premium, siga siendo mantenible y pueda crecer sin convertirse en una vecindad de componentes peleándose por el gas.

