# 📘 Dossier Maestro de Mapeo
## `apps/external_interaction_template`
### Consolidado profesional de frentes, ownership, riesgos, validación y señales de stop

> **Propósito**
>
> Unificar en un solo documento los reportes de mapeo ya generados para el template, con una presentación más limpia, profesional y fácil de navegar.
> Este dossier **no propone implementación final todavía**. Su función es dejar clara la cancha antes de tocar código.

---

## ✨ Qué incluye este dossier

Este consolidado integra estos 5 frentes principales:

1. 🧭 Shell global, top area, backdrop y layout global  
2. 🌐 Arquitectura i18n, shared UI y formatting layer  
3. 🏠 Launcher e Inbox  
4. 🧪 Flow runner, schema text y coupling con validation/state  
5. 🛰️ Record detail, timeline y sync center  

---

## 🧩 Cómo usar este documento

### Recomendación de lectura
- Empieza por **shell + i18n/shared** para entender la base transversal.
- Luego revisa **launcher/inbox** para quick wins de superficie.
- Después entra a **flow** y **detail/timeline/sync** con casco, porque ahí vive la semántica sensible.

### Regla madre
**Primero mapa, luego ownership, luego riesgo, luego validación, y solo después ejecución.**

### Leyenda rápida
- **✅ Confirmado**: sale directo del código inspeccionado.
- **🧠 Inferido**: deducción razonable por composición o contratos visibles.
- **⚠️ Dudoso**: no conviene tocarlo sin cerrar ownership o semántica.
- **🛑 Lista roja**: debe quedarse fuera de la primera ola.

---

## 🗂️ Índice

- [🧭 Shell global, top area, backdrop y layout global](#-shell-global-top-area-backdrop-y-layout-global)
- [🌐 Arquitectura i18n, shared UI y formatting layer](#-arquitectura-i18n-shared-ui-y-formatting-layer)
- [🏠 Launcher e Inbox](#-launcher-e-inbox)
- [🧪 Flow runner, schema text y coupling con validationstate](#-flow-runner-schema-text-y-coupling-con-validationstate)
- [🛰️ Record detail, timeline y sync center](#️-record-detail-timeline-y-sync-center)

---

## 🎯 Resumen ejecutivo consolidado

### Lo que ya quedó muy claro
- El template tiene una base visual potente, pero varias superficies mezclan **copy local**, **shared UI**, **runtime labels**, **schema-driven text** y **evidencia operativa**.
- El shell, el sistema de formato y los helpers de estado son frentes transversales. Si se tocan mal, se riegan como tinta en agua.
- `flow`, `record detail`, `timeline` y `sync` son las superficies más delicadas porque el texto visible ya roza contratos reales de estado, validación, retry, error y evidencia.

### Lo que sí parece seguro para primeras olas
- shell copy visible y chrome superior
- shared UI con strings claramente reutilizables
- loading / empty states / wrappers visuales seguros
- launcher
- porciones acotadas del inbox
- copy segura de sync, pero no su semántica operativa

### Lo que debe mantenerse bajo llave hasta aclarar ownership
- labels de estado y descripciones de estado
- schema titles, summaries, field labels, step labels, action labels
- summaries operativos
- errors crudos del backend o adapters
- timeline narrative ensamblada desde evidence
- cualquier string que deje de ser copy y pase a ser persistencia o contrato

---

## 📦 Documentos fuente consolidados

- `reporte_shell_global_external_interaction_template(1).md`
- `eit_i18n_shared_ui_architecture_report(1).md`
- `launcher_inbox_intervention_map(1).md`
- `flow_runner_controlled_intervention_report(1).md`
- `external_interaction_template_detail_timeline_sync_intervention_report(1).md`

---

## 🧭 Shell global, top area, backdrop y layout global

**Archivo fuente consolidado:** `reporte_shell_global_external_interaction_template(1).md`

### Reporte 1. Mapa y alcance

#### Identidad de la intervención
- **Nombre corto:** shell-global-top-area-preintervencion
- **Proyecto base:** `apps/external_interaction_template`
- **Fecha de apertura:** 2026-04-10
- **Estado actual:** investigando
- **Tipo principal:** `shared visual` + `runtime visual` + `language-sensitive`
- **Superficie principal afectada:** shell global, top area, header, navegación, backdrop y ritmo vertical superior
- **Objetivo en una línea:** mapear el shell global y su chrome superior antes de tocar idioma, layout o atmósfera visual

#### Resumen ejecutivo
Este mapeo usa como base obligatoria el **zip del proyecto** como fuente principal de verdad del código real y el **Formato Universal de Pre-Intervención y Rastreabilidad** como estructura de control.

##### Qué cubre este mapeo
- shell global
- top area / header / navegación / chrome superior
- backdrop / atmósfera fija
- layout global y reglas base de `globals.css`
- riesgos de longitud, sticky, spacing, truncado y saturación visual en la zona superior
- ubicación probable para un selector global de idioma sin proponer implementación final todavía

##### Qué deja resuelto
- mapa de superficies y archivos que realmente controlan el shell
- separación preliminar entre lo visual, lo shared y lo runtime-semantics
- lista de zonas sensibles y zonas que no conviene tocar todavía
- validación mínima a correr antes de cualquier modificación

##### Qué valor aporta para cambios futuros
- baja el riesgo de meter idioma o controles extra en un header ya cargado
- evita mezclar visual shell con runtime, schema o backend por accidente
- deja una base reusable para futuras intervenciones de idioma, tema, densidad y chrome superior

#### Alcance y no alcance

##### Entra en esta intervención
- `app/layout.tsx`
- `components/layout/app-frame.tsx`
- `components/layout/app-shell.tsx`
- `components/layout/ambient-backdrop.tsx`
- `app/globals.css`
- shared relacionados que afectan directo al shell/top area:
  - `components/ui/page-header.tsx`
  - `components/ui/surface.tsx`
  - `components/ui/section-header.tsx`
  - `components/ui/page-loading.tsx`
  - `components/ui/live-region.tsx`
- dependencias inmediatas del shell que mezclan semántica de runtime:
  - `src/lib/ui/runtime.ts`
  - `src/lib/ui/use-accessibility-signals.ts`
- superficies consumidoras para medir top-heaviness real:
  - `app/page.tsx`
  - `components/records/record-inbox.tsx`
  - `components/sync/sync-center.tsx`
  - `components/records/record-detail.tsx`
  - `app/flow/[schemaId]/page.tsx`

##### No entra en esta intervención
- implementación final de i18n
- provider, wiring o persistencia del selector de idioma
- refactor completo de copy por dominio
- cambios de semántica de estados o acciones
- cambios a APIs, schema registry o backend
- cambios a comportamiento de flujo o reglas de negocio

##### Qué partes claramente NO deben tocarse todavía
- `schema.title`, `schema.summary`, `field.label`, `field.helpText`
- mensajes devueltos por backend o API
- semántica de transición de estados
- copy derivado automáticamente desde helpers si no se resuelve ownership primero
- cualquier cambio que exija persistir preferencias de usuario sin definir dueño de esa persistencia

#### Mapa de superficies

#### Superficie principal
- **Shell global sticky:** `components/layout/app-shell.tsx`
- **Por qué es la principal:** concentra navegación, branding textual, descripción de área, CTAs, chips runtime y resumen de superficie actual
- **Qué controla:** el chrome superior completo y el contenedor global de todas las rutas

#### Archivos principales y qué controla cada uno

| Archivo | Confirmado / inferido | Qué controla | Sensibilidad | Nota de control |
|---|---|---|---|---|
| `app/layout.tsx` | **Confirmado** | metadata global, `<html lang="en">`, backdrop fijo, grid overlay fijo, montaje de `AppFrame` | alta | punto de entrada del shell global |
| `components/layout/app-frame.tsx` | **Confirmado** | puente client-side entre routing y shell; inyecta `pathname` y señales de accesibilidad | media-alta | mezcla navegación actual con contexto runtime |
| `components/layout/app-shell.tsx` | **Confirmado** | header sticky, nav principal, CTAs, copy shared del shell, chips runtime, current surface card, contenedor max-width | **muy alta** | hotspot principal |
| `components/layout/ambient-backdrop.tsx` | **Confirmado** | atmósfera visual fija: gradientes, blobs animados, capa de profundidad | media | puramente visual, pero global |
| `app/globals.css` | **Confirmado** | tokens visuales, fondos globales, page gap, estilos de superficies, chips, queue headers, motion/contrast overrides | **muy alta** | cualquier cambio pega transversalmente |
| `src/lib/ui/runtime.ts` | **Confirmado** | áreas UI, presets, densidades, roles, contrastes, brands, defaults por área y data attributes | **muy alta** | no es solo visual; mezcla runtime semantics |
| `src/lib/ui/use-accessibility-signals.ts` | **Confirmado** | lectura de motion/contrast desde media queries | media-alta | define parte del runtime del shell |

#### Superficies secundarias directamente relacionadas

| Superficie | Archivo(s) | Relación con el shell/top area | Riesgo |
|---|---|---|---|
| Encabezados de página | `components/ui/page-header.tsx` | segunda capa de header por ruta | alto |
| Superficies con títulos | `components/ui/surface.tsx`, `components/ui/section-header.tsx` | crean subsecciones visibles inmediatamente debajo del shell | medio-alto |
| Loading global y por ruta | `app/loading.tsx`, `components/ui/page-loading.tsx` | muestran copy y estructura antes del contenido útil | medio |
| Inbox | `components/records/record-inbox.tsx` | apila PageHeader + stats + controls + lanes debajo del shell | alto |
| Sync | `components/sync/sync-center.tsx` | apila PageHeader + stats + dos superficies grandes | alto |
| Record detail | `components/records/record-detail.tsx` | apila PageHeader + stats + columna sticky lateral | **muy alto** |
| Flow | `app/flow/[schemaId]/page.tsx`, `components/flow/flow-runner.tsx` | apila PageHeader + resume surface + panel sticky lateral | alto |
| Launcher | `app/page.tsx` | apila PageHeader + 4 stats + surface principal | alto |

#### Mapa funcional del shell global y su chrome

##### 1) Montaje raíz
**Confirmado**
- `app/layout.tsx` fija `lang="en"`
- monta `AmbientBackdrop`
- monta un overlay fijo `.grid-fade`
- envuelve todo en `AppFrame`

##### 2) Capa puente
**Confirmado**
- `AppFrame` obtiene `pathname`
- lee accesibilidad vía `useAccessibilitySignals()`
- pasa ambos a `AppShell`

##### 3) Shell sticky
**Confirmado**
- contenedor principal: `max-w-[1440px]`, `px-3 sm:px-5 lg:px-8`, `pt-4`, `pb-10`
- header sticky: `sticky top-4 z-30 mb-6`
- shell visual: `surface-shell` + clases de brand/glow runtime

##### 4) Chrome superior dentro del shell
**Confirmado**
- bloque superior izquierdo:
  - icono Orbit
  - eyebrow `External Interaction Template`
  - título truncado `Schema-driven workflow control surface`
  - descripción dinámica por área
  - chips `Area`, `Brand`, `Preset`
- bloque superior derecho:
  - nav principal con 4 links: `Launcher`, `Inbox`, `Sync`, `Schemas`
  - CTAs: `Schema Playground`, `Start Flow`
- bloque inferior del shell:
  - tarjeta `Current surface`
  - texto descriptivo dependiente de role/density/preset
  - grid de chips runtime: `Role`, `Density`, `Preset`, `Motion`, `Contrast`

#### Textos visibles, labels o controles que viven ahí

##### Shell global
**Confirmado**
- metadata visible / strings:
  - `External Interaction Template`
  - `Schema-driven workflow control surface`
  - descripciones por área para `launcher`, `inbox`, `record`, `flow`, `sync`, `system`
  - `Area`, `Brand`, `Preset`
  - `Current surface`
  - `Role`, `Density`, `Preset`, `Motion`, `Contrast`
  - nav labels `Launcher`, `Inbox`, `Sync`, `Schemas`
  - CTA labels `Schema Playground`, `Start Flow`

##### Layout root / loading / fallback
**Confirmado**
- metadata de `app/layout.tsx`:
  - title: `External Interaction Template`
  - description: `Domain-neutral external interaction template for collect, review, update, approve, dispatch and sync flows.`
- loading global:
  - `Loading workspace`
  - `Bootstrapping shell surfaces, summaries and route chrome.`
- defaults de `PageLoading`:
  - `Loading`
  - `Preparing the next view.`
  - `Route shell`
- fallbacks globales:
  - `Runtime interruption`
  - `Something drifted off the happy path`
  - `Retry route`
  - `Go to launcher`
  - `Not found`
  - `This route is missing from the constellation`
  - `Return to launcher`
  - `Open inbox`

#### Qué parte del shell es puramente visual y qué parte mezcla semántica de runtime

##### Puramente visual
**Confirmado**
- `AmbientBackdrop`
- `.grid-fade`
- tokens de color y superficie en `globals.css`
- radios, sombras, blur, glow, spacing base
- `surface-shell`, `surface-panel`, `surface-muted`, `shell-chip`

##### Mezcla visual + runtime semantics
**Confirmado**
- `resolveArea(currentPath)` en `app-shell.tsx`
- `areaDescription(area)`
- `createRuntimeUiContext(...)`
- defaults por área en `runtime.ts`
- `data-ui-area`, `data-ui-density`, `data-ui-preset`, `data-ui-role`, `data-ui-motion`, `data-ui-contrast`, `data-ui-brand`
- lectura automática de motion/contrast en `useAccessibilitySignals.ts`

##### Zona explícitamente dudosa
**Dudoso**
- si `Role`, `Density`, `Preset`, `Motion`, `Contrast` son solo visualización de runtime o eventualmente controles editables
- si `Brand` es puramente tema o representa una semántica real de modo/surface
- si el área actual debe seguir resolviéndose desde path o desde una capa más explícita de layout context

#### Riesgos de top-heavy layout

##### Confirmado
- `AppShell` es sticky completo y contiene dos niveles de información
- múltiples páginas agregan inmediatamente debajo un `PageHeader`
- varias páginas agregan además 4 `StatCard` arriba del contenido principal
- Inbox, Sync, Flow, Record y Launcher introducen una segunda superficie de control o resumen antes del contenido operativo principal

##### Inferido
- en móvil y tablet el shell sticky puede crecer mucho porque el header solo cambia a composición horizontal en `xl`
- un incremento de copy, traducción o nuevos controles puede disparar wrapping y ocupar demasiado viewport antes de llegar al contenido útil

#### Riesgos de truncado o longitud de texto

##### Confirmado
- el título principal del shell usa `truncate`
- la descripción del shell **no** usa clamp ni truncado
- el nav usa `flex-wrap`, no scroll horizontal controlado
- los chips del shell usan `flex-wrap`
- `PageHeader` usa `text-balance` para el título, pero no clamp
- `Current surface` y la descripción inferior del shell tampoco tienen clamp

##### Implicación
- idioma más largo o copy más verboso puede:
  - aumentar altura del sticky header
  - empujar el nav/CTAs a más líneas
  - saturar el bloque izquierdo
  - volver más frágil el primer viewport

#### Hotspots de spacing, sticky, navegación y header

| Hotspot | Confirmado / inferido | Riesgo | Nota |
|---|---|---|---|
| `header.sticky top-4 z-30 mb-6` en `app-shell.tsx` | **Confirmado** | alto | si crece el header, el sticky se vuelve muy dominante |
| `xl:flex-row` del shell | **Confirmado** | alto | antes de `xl`, el shell vive apilado verticalmente |
| `mt-4` bloque inferior del shell | **Confirmado** | medio-alto | suma una segunda banda debajo de nav/CTA |
| `page-stack` + stats + Surface debajo del shell | **Confirmado** | alto | patrón repetido en rutas grandes |
| `xl:sticky xl:top-24` en detail/flow side panels | **Confirmado** | medio-alto | posible interacción visual con shell sticky |
| `--page-gap` dependiente de density | **Confirmado** | medio | ritmo vertical cambia transversalmente |
| nav con `flex-wrap` | **Confirmado** | medio-alto | robusto, pero puede crecer demasiado con labels largos |
| chips runtime como bloques extra | **Confirmado** | medio-alto | útiles, pero contribuyen a top heaviness |

#### Dónde podría vivir el selector de idioma sin saturar

##### Opción A. Dentro del bloque inferior derecho del shell, junto al resumen runtime
**Inferido, recomendado como ubicación conceptual más sana**
- Pros:
  - semánticamente cercano a otras preferencias de experiencia (`Motion`, `Contrast`, `Density`, `Preset`)
  - evita contaminar la navegación primaria
  - evita competir con los CTAs `Schema Playground` y `Start Flow`
- Riesgo:
  - hoy esa zona parece resumen, no control interactivo; habría que cuidar que no se sienta como “falso chip”

##### Opción B. En la franja superior derecha, debajo de nav y arriba o junto a CTAs
**Inferido, viable pero más saturable**
- Pros:
  - visibilidad alta
  - fácil de descubrir
- Riesgo:
  - la zona ya trae nav + dos CTAs
  - en pantallas estrechas puede reventar wrapping más rápido

##### Opción C. Dentro de una futura barra de preferencias del shell, separada de navegación
**Inferido, más mantenible a mediano plazo**
- Pros:
  - separa navegación, acciones y preferencias
  - deja crecer idioma sin ensuciar el header principal
- Riesgo:
  - ya implica decisión estructural, no quick win

##### Dónde NO conviene ponerlo de entrada
- como quinto link del nav principal
- mezclado dentro de los chips `Area/Brand/Preset`
- dentro de `PageHeader` por ruta
- en `AmbientBackdrop` o cualquier zona puramente decorativa

#### Partes más sensibles
- `components/layout/app-shell.tsx`
- `app/globals.css`
- `src/lib/ui/runtime.ts`
- patrón combinado `AppShell sticky` + `PageHeader` + stats de cada ruta

#### Partes claramente fuera o demasiado sensibles para tocar ahora
- persistencia de preferencias
- semántica de `role` y `preset`
- resolución de área por path si no hay motivo sistémico
- copy schema-driven dentro de `record-detail`, `flow` o listas de campos
- formatters de dominio si aún no se decide ownership

---

### Reporte 2. Ownership, lista roja y riesgos

#### Matriz de ownership por elemento

| Elemento | Frontend-owned | Shared-owned | Runtime-owned | Schema-owned | Backend-owned | Dudoso | Nota |
|---|---|---|---|---|---|---|---|
| `AmbientBackdrop` visual puro |  | **Sí** |  |  |  |  | global decorativo |
| `.grid-fade` overlay fijo |  | **Sí** |  |  |  |  | global decorativo |
| tokens y clases base en `globals.css` |  | **Sí** |  |  |  |  | afectan toda la app |
| contenedor `AppFrame` |  | **Sí** | **Sí** |  |  |  | puente entre shell y accesibilidad |
| nav links y labels del shell |  | **Sí** |  |  |  |  | navegación shared |
| CTAs del shell |  | **Sí** |  |  |  |  | acciones globales del shell |
| title/tagline del shell |  | **Sí** |  |  |  |  | copy shared del producto demo |
| `areaDescription(area)` |  | **Sí** | **Sí** |  |  |  | depende de área runtime |
| chips `Area / Brand / Preset` |  | **Sí** | **Sí** |  |  |  | resumen runtime visible |
| tarjeta `Current surface` |  | **Sí** | **Sí** |  |  |  | texto visible construido desde runtime |
| chips `Role / Density / Preset / Motion / Contrast` |  | **Sí** | **Sí** |  |  | **Sí** | resumen visible hoy, posible control mañana |
| `html lang="en"` | **Sí** |  |  |  |  | **Sí** | frontend lo define, pero futura fuente de verdad puede cambiar |
| metadata global `title/description` | **Sí** | **Sí** |  |  |  |  | shared app metadata |
| `PageHeader` estructura |  | **Sí** |  |  |  |  | componente shared |
| copy pasado a `PageHeader` por ruta | **Sí** |  |  | **A veces** |  | **Sí** | depende del caller |
| `PageLoading` defaults |  | **Sí** |  |  |  |  | copy shared |
| `StatusPanel` copy en error/not-found | **Sí** | **Sí** |  |  |  |  | global fallbacks del frontend |
| `createRuntimeUiContext` y defaults por área |  |  | **Sí** |  |  |  | runtime semántico |
| señales motion/contrast |  |  | **Sí** |  |  |  | accesibilidad/runtime |
| `schema.title`, `schema.summary` |  |  |  | **Sí** |  |  | no tocar desde shell |
| mensajes de API o `error.digest` |  |  |  |  | **Sí** |  | backend/runtime técnico |
| `formatDateTime("en")`, `formatValue`, `formatHumanLabel` | **Sí** |  | **Sí** |  |  | **Sí** | helper infra con fuga de idioma |

#### Lista roja de ownership dudoso

| Elemento | Dónde aparece | Por qué es dudoso | Qué falta investigar |
|---|---|---|---|
| `html lang="en"` | `app/layout.tsx` | hoy está hardcodeado, pero puede terminar gobernado por selector global, routing o middleware | decidir fuente canónica de locale |
| `Role / Density / Preset / Motion / Contrast` | `components/layout/app-shell.tsx` | hoy se muestran como lectura; mañana podrían ser controles | decidir si son solo runtime diagnostics o settings reales |
| `Brand` | `app-shell.tsx` + `runtime.ts` | no está claro si es tema visual, tenant demo o modo sistémico | definir si es puramente visual |
| `areaDescription(area)` | `app-shell.tsx` | copy shared pero derivado de ruta/runtime | decidir si vive en shell, dominio o i18n por área |
| `formatHumanLabel(runtime.*)` | `app-shell.tsx`, `record-view.ts`, otros | genera labels visibles desde enums | decidir si esos labels deben ser canónicos vía diccionario |
| `formatDateTime("en")`, `RelativeTimeFormat("en")` | `src/lib/utils.ts` | idioma infra colado fuera de i18n | definir estrategia de locale formatting |
| copy de `PageHeader` en record/detail/flow | consumidores múltiples | parte es frontend-owned, parte podría venir de schema | revisar caso por caso |
| labels derivados de estado | `record-view.ts`, `StateBadge`, inbox, record, sync | frontera entre core state semantics y copy visible | definir dueño canónico de estados |

#### Riesgos identificados

| Riesgo | Tipo | Probabilidad | Impacto | Señal temprana | Mitigación | Owner sugerido |
|---|---|---|---|---|---|---|
| shell sticky demasiado alto | visual/layout | alta | alta | primer viewport dominado por header | medir alturas en móvil/tablet y definir budget de top area | frontend |
| agregar idioma en zona saturada | UX/layout | alta | alta | nav/CTA/chips empiezan a wrapear feo | separar navegación de preferencias | frontend/shared |
| mezclar shell visual con runtime semantics | ownership | alta | alta | cambios visuales exigen tocar `runtime.ts` | aislar elementos puramente visuales vs runtime-owned | frontend/runtime |
| traducción más larga rompe truncado | language/layout | alta | alta | title shell o CTAs saltan a demasiadas líneas | revisar clamp/wrap budgets antes de traducir | frontend |
| duplicar labels de runtime | language/consistency | media-alta | alta | `Motion`, `Contrast`, `Preset` aparecen con nombres distintos | catálogo canónico por dominio | frontend/shared |
| tocar `globals.css` y romper surfaces | transversal visual | media | alta | variaciones raras en cards/panels/chips | validar por rutas y variantes | frontend/shared |
| depender de `formatHumanLabel` para copy visible | content/system | alta | media-alta | labels “aceptables” pero inconsistentes | decidir dónde se reemplaza por claves canónicas | frontend |
| cambio local exige persistencia global | scope creep | media | alta | selector necesita storage, SSR o hydrations | congelar alcance antes de implementar | frontend/platform |
| interacción sticky shell + sticky side panel | layout | media | media-alta | side panels pegan visualmente con header en xl | validar record/flow con scroll real | frontend |
| fallbacks globales quedan fuera del sistema de idioma | language | media | media | loading/error/not-found permanecen hardcodeados | incluirlos en primera ola del shell | frontend/shared |

#### Señales tempranas
- el nav o los CTAs empiezan a usar dos o tres renglones en widths intermedios
- el shell sticky ocupa más alto que un `PageHeader`
- la vista requiere demasiado scroll para llegar al primer contenido accionable
- aparecen labels runtime duplicados o auto-humanizados distintos
- el layout cambia entre áreas por razones de copy y no de función
- cualquier intento de mover idioma obliga a tocar `runtime.ts` sin una razón fuerte

#### Mitigaciones
- fijar un **budget de altura** del shell por breakpoint antes de implementar nada
- separar conceptualmente **navegación**, **acciones** y **preferencias**
- no tocar `runtime.ts` si el objetivo real es solo copy o layout visual
- introducir validación explícita de longitudes para inglés y un idioma más largo
- documentar y congelar ownership de labels runtime antes de internacionalizarlos
- incluir `loading`, `error`, `not-found` dentro de la misma estrategia del shell

#### Señales de stop
- cualquier cambio menor al shell obliga a redefinir roles, preset o area resolution
- el selector de idioma exige persistencia no acordada
- una modificación en `globals.css` rompe múltiples superficies críticas
- el header sticky supera el budget de viewport aceptable en móvil/tablet
- no está claro si un label viene de runtime, schema o shared
- aparecen mezclas de copy canónico e inferido por helper automático

---

### Reporte 3. Validación y criterios de aceptación

#### Validación funcional

| Caso | Qué validar | Superficie | Resultado esperado | Estado |
|---|---|---|---|---|
| root layout monta shell | backdrop, grid overlay, frame y shell cargan | global | todas las rutas entran por el mismo shell | pendiente |
| sticky shell funciona sin tapar contenido | scroll vertical | global | el shell permanece visible sin ocultar el contenido inicial de forma excesiva | pendiente |
| nav principal resuelve área correcta | `/`, `/inbox`, `/sync`, `/playground`, `/flow/*`, `/record/*` | shell | link activo y descripción de área coherentes | pendiente |
| runtime ui context se aplica | todas las áreas | shell/runtime | `data-ui-*` correctos según área y accesibilidad | pendiente |
| motion/contrast reaccionan | navegador con prefers-reduced-motion y prefers-contrast | shell/runtime | clases y comportamiento cambian sin romper layout | pendiente |
| loading global respeta shell visual | `app/loading.tsx` | global | no se siente una ruta “fuera del sistema” | pendiente |
| fallbacks globales se ven consistentes | `error.tsx`, `not-found.tsx` | global | siguen coherentes dentro del shell | pendiente |

#### Validación visual por ruta

| Vista | Qué revisar | Riesgo | Estado |
|---|---|---|---|
| `/` | shell sticky + PageHeader + 4 stats + surface principal | alto | pendiente |
| `/inbox` | shell + PageHeader + queue controls + lanes | **muy alto** | pendiente |
| `/flow/[schemaId]` | shell + PageHeader + resume surface + sticky lateral | alto | pendiente |
| `/record/[recordId]` | shell + PageHeader + stats + sticky sidebar | **muy alto** | pendiente |
| `/sync` | shell + PageHeader + stats + two-column surfaces | alto | pendiente |
| `/playground` | shell + PageHeader + cards | medio-alto | pendiente |
| `loading` | copy, skeletons y proporción del top area | medio | pendiente |
| `error` / `not-found` | fallback centrado dentro del sistema | medio | pendiente |

#### Validación transversal
- [ ] responsive básico
- [ ] scroll
- [ ] top area
- [ ] navegación principal
- [ ] acciones del shell
- [ ] truncado y wrapping
- [ ] layout sensible a longitud
- [ ] motion reducido
- [ ] contraste aumentado
- [ ] consistencia de spacing entre shell y contenido
- [ ] ausencia de mezcla rara de ownership
- [ ] ausencia de mezcla rara de idioma

#### Responsive básico a revisar

| Breakpoint | Qué mirar primero | Riesgo |
|---|---|---|
| móvil | header sticky demasiado alto, CTAs apilados, nav con wraps excesivos | muy alto |
| `sm` / `md` | chips y nav compitiendo por altura | alto |
| `lg` | shell todavía vertical en parte superior | medio-alto |
| `xl` | transición a layout horizontal, interacción con sidebars sticky | alto |

#### Top area

##### Checklist de top area
- [ ] el shell superior entra visualmente antes que el contenido sin tragarse la pantalla
- [ ] la zona superior no parece dos headers peleándose entre sí
- [ ] nav, CTAs y cualquier control extra conservan jerarquía clara
- [ ] el `PageHeader` de ruta no se vuelve redundante con el shell
- [ ] la segunda banda `Current surface + runtime chips` no sobrecarga la primera impresión

#### Scroll
- [ ] el sticky del shell no produce saltos incómodos al hacer scroll
- [ ] en vistas con panel lateral sticky no hay colisión visual con el shell
- [ ] el contenido principal arranca suficientemente arriba como para ser útil sin scroll excesivo

#### Truncado y longitud

##### Qué validar explícitamente
- [ ] título largo del shell
- [ ] descripciones de área más largas que las actuales
- [ ] labels de nav más largos que `Schemas`
- [ ] CTAs más largos que `Schema Playground`
- [ ] `Current surface` con valores más extensos
- [ ] labels runtime más largos o traducidos
- [ ] `PageHeader` con copy más largo en launcher/inbox/sync/flow/record

##### Casos sensibles confirmados
- shell title hoy usa `truncate`
- descripciones del shell no usan clamp
- `PageHeader` title usa `text-balance`, no clamp
- `PageHeader` description tampoco usa clamp
- nav y chips hacen wrap

#### Layout sensible a longitud

| Zona | Sensibilidad | Qué observar |
|---|---|---|
| shell title row | alta | si el truncado es suficiente o demasiado agresivo |
| shell description | alta | crecimiento de altura del sticky |
| nav principal | alta | wraps múltiples o links partidos |
| CTA row | alta | botones demasiado anchos |
| chips `Area/Brand/Preset` | media-alta | exceso de líneas en móvil |
| `Current surface` card | media | copy descriptivo demasiado alto |
| runtime chip grid | media-alta | demasiadas tarjetas compactas arriba del fold |
| route `PageHeader` | alta | redundancia con shell + crecimiento vertical |

#### Criterios de aceptación

##### Lista para ejecutar una intervención sobre shell/top area cuando
- [ ] el mapa de superficies ya está cerrado
- [ ] ownership del shell y runtime está suficientemente clasificado
- [ ] existe lista roja de dudas abiertas
- [ ] ya se definió dónde **no** va el selector de idioma
- [ ] existe budget de altura del shell por breakpoint
- [ ] se acordó si idioma es preferencia global dentro de runtime o preferencia separada
- [ ] loading/error/not-found están incluidos dentro del perímetro de validación

##### Se considera aceptable una ejecución posterior si
- [ ] no aumenta de forma descontrolada la altura del shell sticky
- [ ] no se rompe la jerarquía navegación vs acciones vs preferencias
- [ ] no aparecen ownerships nuevos sin resolver
- [ ] no se mezclan labels canónicos con labels auto-humanizados en la misma zona
- [ ] el primer contenido útil sigue siendo alcanzable con rapidez
- [ ] la app sigue coherente en móvil, tablet y desktop

#### Gates para pasar a ejecución

##### Gate 1. Mapa
- [ ] archivos principales y secundarios confirmados
- [ ] hotspots identificados
- [ ] partes fuera de alcance explicitadas

##### Gate 2. Ownership
- [ ] shell visual vs runtime semántico separados
- [ ] lista roja de dudosos vigente
- [ ] sin necesidad de tocar schema/backend

##### Gate 3. Layout
- [ ] budget de altura definido
- [ ] plan de validación de longitudes definido
- [ ] decisión preliminar sobre ubicación conceptual del selector tomada

##### Gate 4. Validación
- [ ] rutas críticas seleccionadas
- [ ] responsive mínimo definido
- [ ] scroll/sticky/truncado incluidos en checklist

---

### Reporte 4. Hallazgos extra y qué nos deja resuelto

#### Quick wins reales

##### 1) Tratar `app-shell.tsx` como hotspot de idioma y chrome, no solo como layout
**Confirmado**
Es el archivo con más concentración de labels visibles shared dentro del shell.

##### 2) Incluir `loading`, `error` y `not-found` en la misma primera ola del shell
**Confirmado**
Hoy ya cargan copy hardcodeado y forman parte de la experiencia global.

##### 3) Congelar un budget de top area antes de meter un selector global
**Inferido, muy recomendable**
El shell ya está cargado. Sin ese budget, cualquier control nuevo puede volverlo pesado.

##### 4) No meter el selector de idioma en el nav primario
**Inferido, recomendable**
Ese nav ya funciona como navegación de superficies. Mezclar preferencia global ahí contamina jerarquía.

##### 5) Considerar el bloque runtime como el lugar semánticamente más cercano para preferencias globales
**Inferido**
Idioma conversa mejor con `Motion` y `Contrast` que con `Launcher` o `Start Flow`.

#### Simplificaciones posibles
- separar el shell en subzonas conceptuales documentadas:
  - navegación
  - acciones
  - resumen/contexto
  - preferencias
- congelar una taxonomía para labels runtime del shell
- tratar `areaDescription` como copy por dominio/área, no como texto suelto incrustado
- mantener `AmbientBackdrop` como capa visual independiente para que no cargue lógica ni copy

#### Artefactos sugeridos
- ficha oficial del shell global con ownership
- matriz de budget de altura por breakpoint
- catálogo de labels del shell y top area
- lista priorizada de strings hardcodeados del chrome superior
- matriz de casos de longitud por idioma
- checklist de validación sticky + top-heavy por ruta

#### Decisiones que convendría congelar antes de cualquier implementación
- si idioma será una preferencia global del usuario o una preferencia de sesión
- si el selector de idioma pertenece al mismo grupo conceptual que `Motion/Contrast` o a una capa aparte
- si `Brand` es visual puro o parte de una semántica más fuerte del shell
- si los labels runtime visibles seguirán usando `formatHumanLabel` o migrarán a claves explícitas
- si `html lang` se resuelve localmente en layout o desde una futura capa de locale

#### Deudas que convendría evitar
- meter más copy en el shell sin plan de longitudes
- dejar `formatDateTime("en")` y `RelativeTimeFormat("en")` fuera de conversación de idioma
- mezclar selector de idioma con CTAs primarios
- tocar `runtime.ts` para resolver un problema que en realidad es de copy/layout
- traducir estados o labels derivados sin definir dueño canónico

#### Preguntas abiertas reales
1. ¿Idioma debe vivir como preferencia global del producto o solo del shell/UI?  
2. ¿El bloque runtime inferior del shell será solo diagnóstico o terminará siendo un panel de preferencias?  
3. ¿`Brand` representa tema, tenant demo o una capa de identidad funcional?  
4. ¿Se quiere conservar el patrón actual de `AppShell sticky` + `PageHeader` por ruta, o ese doble encabezado se considera deuda visual futura?  
5. ¿Se aceptará truncado agresivo en el shell o se prioriza expansión controlada en más líneas?  
6. ¿Las descripciones de área son parte del producto final o solo copy temporal del template?  

#### Qué nos deja resuelto este chat
Este chat deja resuelto el **mapa de control previo** para intervenir el shell global sin pisar minas.

##### Queda pavimentado
- qué archivos sí gobiernan el shell y el top area
- qué partes son visuales puras y cuáles mezclan runtime semantics
- dónde están los textos visibles y labels del chrome superior
- por qué el sistema ya es top-heavy antes de meter idioma
- dónde hay espacio conceptual para un selector de idioma y dónde no conviene meterlo
- cuáles son los hotspots reales de sticky, spacing, longitud y navegación
- qué ownerships están razonablemente claros y cuáles deben permanecer en lista roja
- qué validación mínima debemos correr antes de tocar cualquier cosa

##### En una línea
Si se sigue este mapa, la próxima intervención ya no arranca “a ojo”: arranca con superficie, ownership, riesgos, gates y validación del shell global suficientemente aterrizados como para modificar después con mucho menos blast radius.
## 🌐 Arquitectura i18n, shared UI y formatting layer

**Archivo fuente consolidado:** `eit_i18n_shared_ui_architecture_report(1).md`

### Reporte 1. Mapa y alcance

#### Resumen ejecutivo

Este reporte usa como base obligatoria:
- el **zip del proyecto** como fuente principal de verdad del código real [C]
- el **Formato Universal de Pre-Intervención y Rastreabilidad** como estructura de análisis, control, riesgo y validación 

##### Qué cubre este análisis
- sistema central de idioma / i18n a nivel arquitectura conceptual
- shared UI con textos reutilizables y sus verdaderos puntos emisores
- formatting layer y humanización distribuida
- riesgos de centralización, hardcodes residuales y convención de claves

##### Qué deja resuelto
- una arquitectura central recomendada para `src/lib/i18n/*` sin proponer implementación final todavía
- separación clara entre texto **caller-owned**, texto **shared-owned**, texto **runtime-owned**, texto **schema-owned** y texto **backend/data-owned**
- inventario de strings shared y formatting leaks relevantes
- criterios de qué conviene centralizar primero y qué conviene aplazar

##### Hallazgo central
Hoy **no existe** `src/lib/i18n/*` en el zip revisado [C]. El idioma/humanización está repartido entre:
- `app/layout.tsx` con `<html lang="en">` [C]
- `src/lib/utils.ts` [C]
- `src/lib/ui/contracts.ts` [C]
- `src/lib/core/record-view.ts` [C]
- `src/lib/ui/runtime.ts` por labels de brand profile [C]
- `components/layout/app-shell.tsx` [C]
- `components/ui/page-loading.tsx` [C]
- defaults de `components/ui/filter-pills.tsx` [C]
- callers de `PageHeader`, `StatusPanel`, `EmptyState`, `StatCard`, `SectionHeader`, `Surface` [C]

##### Leyenda de certeza
- **[C] Confirmado** por código del zip
- **[I] Inferido** por composición o por patrón de uso
- **[D] Dudoso** porque mezcla ownership o semántica

#### Alcance y no alcance

##### Entra en este análisis

###### Arquitectura central de idioma
- propuesta conceptual para `src/lib/i18n/*` [I]
- relación de i18n con layout, provider, helper layer, formatting y callers [C][I]

###### Shared UI prioritaria revisada
- `components/ui/page-header.tsx` [C]
- `components/ui/button.tsx` [C]
- `components/ui/filter-pills.tsx` [C]
- `components/ui/status-panel.tsx` [C]
- `components/ui/empty-state.tsx` [C]
- `components/ui/state-badge.tsx` [C]
- `components/ui/stat-card.tsx` [C]
- `components/ui/detail-list.tsx` [C]
- `components/ui/section-header.tsx` [C]
- `components/ui/page-loading.tsx` [C]

###### Formatting / humanization layer revisada
- `src/lib/utils.ts` [C]
- `src/lib/core/record-view.ts` [C]
- `src/lib/ui/contracts.ts` [C]
- `src/lib/ui/record-contracts.ts` [C]
- `src/lib/ui/runtime.ts` [C]
- `components/layout/app-shell.tsx` [C]
- consumers clave para validación transversal: `app/loading.tsx`, `app/not-found.tsx`, `app/error.tsx`, `components/records/record-detail.tsx`, `components/flow/flow-runner.tsx`, `components/sync/sync-center.tsx` [C]

##### No entra por ahora
- implementación final de provider, hooks o loaders [I]
- refactor técnico real de componentes [I]
- traducción efectiva de schemas [I]
- centralización de copy de negocio atada a backend [I]
- rollout por commits o patches [I]

##### Condiciones de corte heredadas del formato universal
- ownership incierto [C][I]
- semántica real mezclada con copy [C][I]
- necesidad de mover texto de schema o backend sin resolver source of truth [C][I]
- blast radius transversal en shared UI [I]

#### Mapa de arquitectura central recomendada

> Objetivo: separar **idioma**, **formatting**, **runtime visual** y **semántica de negocio** para que no se mezclen como sopa con tornillos.

##### Estado actual
| Pieza | Estado actual | Observación |
|---|---|---|
| `src/lib/i18n/*` | no existe [C] | no hay catálogo ni lookup central |
| locale raíz | `app/layout.tsx` fija `lang="en"` [C] | idioma actual está clavado en layout |
| traducción de labels genéricos | `formatHumanLabel()` en `src/lib/utils.ts` [C] | humaniza ids, no traduce de forma curada |
| fechas relativas y absolutas | `Intl.*("en")` en `src/lib/utils.ts` [C] | locale fijo |
| yes/no, counts, items | `utils.ts` y `ui/contracts.ts` [C] | duplicación de formato |
| labels de estado | `record-view.ts` [C] | shared, no inbox-only |
| labels visibles de shell/runtime | `app-shell.tsx` y `runtime.ts` [C] | mezcla entre ids visuales y copy visible |

##### Arquitectura recomendada para `src/lib/i18n/*`

###### 1) Núcleo de definiciones
**Sí debería vivir en `src/lib/i18n/*`:**
- `src/lib/i18n/types.ts` [I]
  - `Locale`
  - tipos de dominio de clave
  - metadata de fallback
- `src/lib/i18n/domains.ts` [I]
  - dominios oficiales de claves
  - convención de namespaces
- `src/lib/i18n/catalogs/<locale>/*.ts` o equivalente [I]
  - catálogos por dominio y por locale
- `src/lib/i18n/resolve.ts` [I]
  - lookup por key
  - fallback de locale
  - fallback por missing key
- `src/lib/i18n/provider.tsx` y/o `src/lib/i18n/context.ts` [I]
  - acceso conceptual al locale actual
  - no lógica visual de runtime
- `src/lib/i18n/format.ts` [I]
  - wrappers de fecha, relative time, booleanos, pluralización, humanización con locale
- `src/lib/i18n/registry.ts` o `keys.ts` [I]
  - mapa de claves curadas si el proyecto quiere tipado/orden estricto

###### 2) Dominios recomendados
- `app_shell.*` [I]
- `loading.*` [I]
- `status.*` [I]
- `empty_state.*` [I]
- `common.record_state.*` [I]
- `common.filters.*` [I]
- `common.format.*` [I]
- `common.a11y.*` [I]
- `runtime_labels.*` solo si se decide mostrar labels humanos de runtime [D]
- `schema.{schemaId}.*` solo cuando se cierre ownership de schemas [D]

###### 3) Separación recomendada de capas
| Capa | Qué debe resolver | Qué no debe resolver |
|---|---|---|
| `i18n` | claves, catálogo, locale, fallback, format wrappers [I] | densidad, preset, contraste, brand styling [I] |
| `runtime` | área, densidad, preset, contraste, motion, brand ids [C][I] | copy visible, labels traducidos, pluralización, locale [I] |
| `shared UI` | composición visual y props [C] | inventar textos globales salvo defaults mínimos [C][I] |
| `schema registry` | titles, summaries, field labels de schema [C] | copy shared de shell o formatos comunes [I] |
| `backend/data` | valores de record, ids, timestamps, payloads [C] | copy UI traducida [I] |

#### Mapa de shared UI con textos reutilizables

##### Clasificación general
| Componente | Emite texto propio | Recibe texto del caller | Riesgo de centralización | Prioridad |
|---|---:|---:|---|---|
| `PageHeader` | no [C] | sí [C] | bajo si se centraliza por caller, alto si se le meten defaults globales | media |
| `Button` | no [C] | sí [C] | bajo | baja |
| `FilterPills` | sí, `ariaLabel="Filter options"` [C] | sí [C] | medio por a11y shared | alta |
| `StatusPanel` | no visible por default [C] | sí [C] | bajo | media |
| `EmptyState` | no visible por default [C] | sí [C] | bajo | media |
| `StateBadge` | sí, `stateLabel()` [C] | parcialmente [C] | alto, shared transversal | alta |
| `StatCard` | no [C] | sí [C] | medio por `toDisplayText()` [C] | alta |
| `DetailList` | no [C] | sí [C] | medio por labels de items caller/schema-owned | baja |
| `SectionHeader` | no [C] | sí [C] | bajo | media |
| `PageLoading` | sí, `title="Loading"`, `subtitle="Preparing the next view."` [C] | sí [C] | alto porque se usa en rutas y LiveRegion | alta |
| `Surface` | no propio salvo títulos caller [C] | sí [C] | bajo | baja |
| `LiveRegion` | no default copy [C] | sí [C] | medio por accesibilidad | media |

##### Inventario de strings shared confirmados
| Archivo | Texto / tipo de texto | Tipo | Ownership actual | Nota |
|---|---|---|---|---|
| `components/ui/filter-pills.tsx` | `Filter options` | a11y default | shared-owned [C] | buen candidato para `common.a11y.filter_options` |
| `components/ui/page-loading.tsx` | `Loading` | visible + live region | shared-owned [C] | default global |
| `components/ui/page-loading.tsx` | `Preparing the next view.` | visible + live region | shared-owned [C] | default global |
| `components/ui/state-badge.tsx` | `stateLabel(safeState)` | derived shared label | record-view-owned [C] | high priority |
| `src/lib/core/record-view.ts` | `stateDescription(state)` | derived shared description | record-view-owned [C] | high priority |
| `src/lib/utils.ts` | `Yes / No` | formatter boolean | shared-owned [C] | formatting leak |
| `src/lib/utils.ts` | `item / items` | formatter plural | shared-owned [C] | formatting leak |
| `src/lib/ui/contracts.ts` | `Yes / No` | formatter boolean | shared-owned [C] | duplicado |
| `src/lib/ui/contracts.ts` | `{n} items` | formatter plural | shared-owned [C] | duplicado |
| `src/lib/ui/runtime.ts` | `Aurora / Neutral / Signal / Graphite` | runtime display label | runtime-owned hoy, pero dudoso para i18n [C][D] | no debería quedar ahí si será visible traducible |
| `components/layout/app-shell.tsx` | `Role / Density / Preset / Motion / Contrast` | shell labels | frontend/shared caller-owned [C] | gran candidato temprano |
| `components/layout/app-shell.tsx` | `Area {x}`, `Brand {x}`, `Preset {x}` | shell chips | frontend/shared caller-owned [C] | mezcla copy + humanización |
| `components/layout/app-shell.tsx` | `areaDescription(area)` switch | shell description | frontend/shared caller-owned [C] | gran candidato temprano |

#### Mapa de formatting layer

##### Emisores confirmados
| Archivo | Función | Qué humaniza | Riesgo |
|---|---|---|---|
| `src/lib/utils.ts` | `formatDateTime()` | fecha/hora con `Intl.DateTimeFormat("en")` [C] | locale fijo |
| `src/lib/utils.ts` | `formatRelativeTime()` | relativo con `Intl.RelativeTimeFormat("en")` [C] | locale fijo |
| `src/lib/utils.ts` | `formatHumanLabel()` | `snake_case -> Title Case` [C] | útil como fallback, mala base final de idioma |
| `src/lib/utils.ts` | `formatValue()` | booleanos, arrays, fechas, objetos [C] | mezcla display de tipos con idioma |
| `src/lib/ui/contracts.ts` | `toDisplayText()` | booleanos, arrays, fechas ISO, objetos [C] | duplicación y leak fuerte |
| `src/lib/core/record-view.ts` | `stateLabel()` | delega a `formatHumanLabel` [C] | estado humanizado, no traducido curado |
| `src/lib/core/record-view.ts` | `stateDescription()` | copy literal por estado [C] | shared de negocio/UI |
| `src/lib/ui/record-contracts.ts` | `summarizeRecordFieldValue()` | delega a `toDisplayText` [C] | hereda leaks |

##### Formatting leaks confirmados
| Leak | Dónde | Estado |
|---|---|---|
| locale fijo `en` | `utils.formatDateTime`, `utils.formatRelativeTime` [C] | alto |
| html root fijo `lang="en"` | `app/layout.tsx` [C] | alto |
| booleanos `Yes/No` en dos capas | `utils.ts`, `ui/contracts.ts` [C] | alto |
| pluralización `item/items` en dos capas | `utils.ts`, `ui/contracts.ts` [C] | alto |
| fallback de fechas a `-` | `utils.ts` [C] | medio |
| fechas serializadas como ISO | `ui/contracts.ts` [C] | medio |
| humanización por capitalización de ids | `formatHumanLabel()` [C] | alto |
| labels de estado basadas en `formatHumanLabel()` | `record-view.ts` [C] | alto |
| labels runtime humanizados fuera de i18n | `app-shell.tsx` [C] | medio |

#### Qué piezas deben centralizarse sí o sí

##### Prioridad alta
1. **Formatting wrappers de locale** [C][I]
   - fecha absoluta
   - fecha relativa
   - booleanos
   - conteos/pluralización mínima
   - humanización curada de enums frecuentes

2. **Record state labels + descriptions** [C][I]
   - hoy viven en `record-view.ts`
   - pegan en inbox, record detail y cualquier `StateBadge`

3. **App shell visible copy** [C][I]
   - descripciones de área
   - labels `Role`, `Density`, `Preset`, `Motion`, `Contrast`
   - chips `Area`, `Brand`, `Preset`

4. **Route loading copy** [C][I]
   - `PageLoading` defaults
   - `app/loading.tsx`, `app/inbox/loading.tsx`, `app/flow/[schemaId]/loading.tsx`, `app/record/[recordId]/loading.tsx`, `app/sync/loading.tsx`

5. **Shared a11y minima** [C][I]
   - `FilterPills` aria label
   - cualquier default de `LiveRegion` si apareciera luego

##### Prioridad media
- copy caller-owned que se repite en `StatusPanel`, `EmptyState`, `PageHeader`, `SectionHeader`, `StatCard` [C][I]
- fallbacks shared como `Record` y similares [C][I]

#### Qué piezas no conviene centralizar todavía

1. **Textos de schema** [C][D]
- `schema.title`
- `schema.summary`
- `field.label`
- `flow.title`
- `step.title`
- `action.label`

2. **Valores reales de datos** [C]
- títulos escritos por usuarios
- payloads
- ids
- adapter ids
- timestamps crudos como datos

3. **Semántica runtime mezclada con copy visible** [C][D]
- `BrandProfile.label` no debería quedarse en `runtime.ts` si será traducible
- el id de brand sí puede quedarse; el label visible no conviene congelarlo ahí

4. **Humanización automática como única estrategia** [C][I]
- `formatHumanLabel()` sirve como fallback técnico
- no debería convertirse en solución definitiva para idioma

5. **Cualquier string cuya verdad dependa de backend/state machine** [I][D]
- textos que parezcan UI pero realmente expresen semántica operativa o contractual

---

### Reporte 2. Ownership, lista roja y riesgos

#### Matriz de ownership por categoría de texto

| Categoría | Ejemplos | Ownership | Confirmación | Nota |
|---|---|---|---|---|
| caller copy de `PageHeader`, `StatusPanel`, `EmptyState`, `StatCard`, `SectionHeader`, `Surface` | titles, descriptions, meta, eyebrow, CTA labels | frontend-owned [C] | [C] | el componente shared no es el dueño del texto |
| defaults de `PageLoading` y `FilterPills` | `Loading`, `Preparing the next view.`, `Filter options` | shared-owned [C] | [C] | deben inventariarse como shared |
| labels de estado y descriptions de estado | `stateLabel`, `stateDescription` | record-view-owned [C] | [C] | shared de negocio/UI, no de un caller aislado |
| ids runtime y enums visuales | `area`, `density`, `preset`, `motion`, `contrast`, `brandProfile.id` | runtime-owned [C] | [C] | ids sí, copy visible no necesariamente |
| `BrandProfile.label` | `Aurora`, `Neutral`, `Signal`, `Graphite` | runtime-owned hoy, pero dudoso para idioma [C][D] | [C] | mejor mover label humano fuera de runtime si será traducible |
| `schema.title`, `summary`, `field.label`, `action.label`, `step.title` | schema registry | schema-owned [C] | [C] | no centralizar como shared genérico todavía |
| record values y backend payloads | `record.title`, ids, field values, digest, adapter ids | backend/data-owned [C] | [C] | no son copy de UI traducible |
| formatters de fecha/boolean/plural/human label | `formatDateTime`, `formatRelativeTime`, `formatValue`, `toDisplayText` | shared-owned [C] | [C] | hoy dispersos, candidato claro a i18n/format layer |
| labels shell construidas desde runtime | `Role`, `Density`, `Preset`, etc. + `formatHumanLabel(runtime.role)` | frontend/shared mix [C][D] | [C] | copy caller-owned con datos runtime |

#### Matrices por ownership solicitado

##### Frontend-owned
| Elemento | Dónde | Riesgo | Acción conceptual |
|---|---|---|---|
| copy de route loading callers | `app/*/loading.tsx` [C] | medio | mover a dominios por ruta o `loading.*` |
| copy de `app/error.tsx` y `app/not-found.tsx` | callers de `StatusPanel` [C] | medio | centralizar por dominio de estado del shell |
| labels y descripciones de launcher/sync/record/inbox/flow callers | `app/*`, `components/*` [C] | medio/alto | centralizar por superficie, no por componente base |
| app shell descriptive copy | `components/layout/app-shell.tsx` [C] | alto | candidato temprano |

##### Shared-owned
| Elemento | Dónde | Riesgo | Acción conceptual |
|---|---|---|---|
| `Filter options` | `components/ui/filter-pills.tsx` [C] | medio | `common.a11y.filter_options` |
| `Loading`, `Preparing the next view.` | `components/ui/page-loading.tsx` [C] | alto | `loading.defaults.*` |
| date / relative / boolean / items formatters | `utils.ts`, `ui/contracts.ts` [C] | alto | mover a formatting layer común |
| fallbacks shared tipo `Record` y derivados | `record-view.ts`, `record-contracts.ts` [C] | medio | inventario separado de fallbacks |

##### Runtime-owned
| Elemento | Dónde | Riesgo | Acción conceptual |
|---|---|---|---|
| `area`, `density`, `preset`, `role`, `motion`, `contrast` ids | `src/lib/ui/runtime.ts` [C] | bajo | mantener ids ahí |
| `BrandProfile.id` | `src/lib/ui/runtime.ts` [C] | bajo | mantener id ahí |
| `BrandProfile.label` | `src/lib/ui/runtime.ts` [C] | medio/alto | sacar label visible de runtime si habrá i18n |
| defaults por área (`balanced`, `operational`, etc.) | `src/lib/ui/runtime.ts` [C] | bajo | mantener como config técnica, no copy |

##### Schema-owned
| Elemento | Dónde | Riesgo | Acción conceptual |
|---|---|---|---|
| schema titles/summaries | `src/lib/core/schema-registry.ts` [C] | alto | aplazar centralización shared |
| step titles/descriptions | `src/lib/core/schema-registry.ts` [C] | alto | revisar si demo-only o negocio real |
| field labels/placeholders/help texts | `src/lib/core/schema-registry.ts` [C] | muy alto | no meter a shared i18n sin cerrar ownership |
| action labels | `src/lib/core/schema-registry.ts` [C] | alto | separar de shell/shared |

##### Backend-owned
| Elemento | Dónde | Riesgo | Acción conceptual |
|---|---|---|---|
| record values | records/services [C] | alto | nunca tratarlos como copy shared |
| timestamps como data | store/services/API [C] | medio | formatearlos solo al borde de UI |
| ids/digests/adapter ids | rutas y servicios [C] | medio | no traducir |

##### Dudoso
| Elemento | Dónde | Por qué es dudoso | Acción conceptual |
|---|---|---|---|
| `BrandProfile.label` | `runtime.ts` [C] | es copy visible dentro de config técnica | no congelarlo en runtime |
| humanización por `formatHumanLabel()` | `utils.ts` y usos [C] | sirve como fallback, no como traducción final | usarlo solo como red de seguridad |
| shell labels construidas con ids runtime | `app-shell.tsx` [C] | mezcla dato técnico + copy visible | mover copy a i18n; dejar ids en runtime |
| descripciones de estado | `record-view.ts` [C] | son UI, pero con semántica operativa | validarlas antes de centralizar |
| fallback `Record` | `record-view.ts` / `record-contracts.ts` [C] | shared, pero también semántico | centralizar solo como fallback global |

#### Lista roja global de textos dudosos

No deberían centralizarse todavía sin investigación adicional:

1. **Todo el contenido de `schema-registry` que describa negocio** [C][D]
   - `title`
   - `summary`
   - `step.title`
   - `step.description`
   - `field.label`
   - `placeholder`
   - `helpText`
   - `action.label`

2. **Copy basada en ids humanizados como solución final** [C][D]
   - `formatHumanLabel(state)`
   - `formatHumanLabel(runtime.role)`
   - `formatHumanLabel(runtime.preset)`
   - etc.

3. **Labels visibles que hoy viven en runtime config** [C][D]
   - `BrandProfile.label`

4. **Datos de usuario/record/backend** [C]
   - títulos de records
   - ids
   - payloads serializados
   - adapter ids
   - digests

5. **Cualquier copy que aparente ser UI pero exprese semántica real de estado** [C][D]
   - descriptions de estados
   - outcomes operativos
   - mensajes que deban cuadrar con lógica real

#### Strings peligrosos del formatting layer

| String o patrón | Origen | Peligro |
|---|---|---|
| `Yes` / `No` | `utils.ts`, `ui/contracts.ts` [C] | duplicación y mezcla de capas |
| `item/items` | `utils.ts`, `ui/contracts.ts` [C] | pluralización pobre y duplicada |
| `-` como fallback universal | `utils.ts`, `ui/contracts.ts` [C] | puede quedar raro según contexto/idioma |
| fecha absoluta con locale fijo | `utils.ts` [C] | inconsistencia global |
| fecha relativa con locale fijo | `utils.ts` [C] | inconsistencia global |
| ISO string como display de fecha | `ui/contracts.ts` [C] | salida técnica, no humana |
| `attachment(s)` | `flow-runner.tsx` [C] | hardcode residual fuera de formatting layer |

#### Riesgos de hardcodes residuales

| Riesgo | Evidencia | Severidad | Nota |
|---|---|---:|---|
| locale fijo `en` conviviendo con futuro i18n | `app/layout.tsx`, `utils.ts` [C] | alta | genera UI híbrida |
| formatters duplicados | `utils.ts` + `ui/contracts.ts` [C] | alta | resultados distintos para cosas parecidas |
| callers shared con mucho copy suelto | `app/*`, `components/*` [C] | alta | dispersa inventario |
| brand labels en config técnica | `runtime.ts` [C] | media/alta | mezcla runtime con copy |
| route loading copy diseminada | `app/*/loading.tsx` [C] | media | fácil dejar rezagos |
| fallback humanizado desde ids | `formatHumanLabel` [C] | alta | parece bonito, pero no resuelve idioma real |

#### Riesgos de claves caóticas

| Riesgo | Cómo se ve | Mitigación conceptual |
|---|---|---|
| claves por componente en lugar de dominio semántico | `page-header.title`, `status-panel.title` por todos lados | separar dominio de negocio/caller de shell visual |
| duplicar la misma semántica en varios namespaces | `submitted.label`, `badge.submitted`, `pill.submitted` | usar `common.record_state.submitted.label` |
| mezclar fallback técnicos con copy curada | `humanLabel.*` junto a copy de negocio | separar `common.format.*` de `app_*.*` |
| meter schema copy en `common.*` | `common.field.requester_name.label` | reservar `schema.{schemaId}.*` |
| meter runtime ids y labels en el mismo saco | `runtime.preset.operational` tanto id como texto visible | mantener ids en runtime, labels en i18n |

#### Riesgos de mezclar idioma con semántica real

| Caso | Riesgo | Ejemplo |
|---|---|---|
| descriptions de estado | que el texto traducido no refleje workflow real | `Approved and ready for dispatch.` [C][D] |
| action labels de schema | que parezcan shared pero estén atadas al negocio real | `Approve Packet`, `Dispatch`, etc. [C][D] |
| field labels y help text de schema | que el equipo los quiera “shared” cuando son contrato de flujo | `Requester name`, `Needs attachment` [C][D] |
| humanización de enums | que un id técnico parezca copy de producto final | `in_review -> In Review` [C][D] |

---

### Reporte 3. Validación y criterios de aceptación

#### Validación de provider / helper conceptual

> No se propone implementación final. Se define qué debe poder validarse cuando exista la capa.

| Frente | Qué validar | Resultado esperado |
|---|---|---|
| locale source of truth | el árbol de UI tiene una fuente única del locale actual [I] | no hay `lang="en"` duro conviviendo con otro locale |
| lookup de claves | una key shared resuelve el mismo texto en todos sus consumidores [I] | `common.record_state.*` consistente |
| fallback | si falta una key, el fallback es explícito y auditable [I] | no aparece basura silenciosa |
| wrapper de formato | fecha/relative/boolean/plural usan la misma capa [I] | no hay `Yes/No` repartido |
| separación de capas | runtime no resuelve copy visible [I] | ids técnicos y labels visibles no se mezclan |

#### Validación de shared UI

| Componente | Validación requerida | Señal de éxito |
|---|---|---|
| `PageHeader` | acepta copy externa sin layout roto [C][I] | eyebrow/title/description soportan expansión |
| `FilterPills` | `ariaLabel` traducible y pills estables [C][I] | a11y y ancho controlados |
| `StatusPanel` | titles/descriptions/actions caben y no rompen densidad [C][I] | panel sigue equilibrado |
| `EmptyState` | title/description/footer/action soportan expansión [C][I] | jerarquía visual intacta |
| `StateBadge` | labels de estado consistentes en todas las superficies [C][I] | badge compacto y coherente |
| `StatCard` | label/meta/value formateado igual en todas las rutas [C][I] | no hay Yes/No mixto ni fechas raras |
| `DetailList` | labels/value pairs soportan longitud variable [C][I] | grid no se deforma feo |
| `SectionHeader` | title/description/badge/actions siguen respirando [C][I] | sin truncado accidental crítico |
| `PageLoading` | title/subtitle/live region usan misma fuente de copy [C][I] | loading consistente y accesible |

#### Validación de consistencia de labels

##### Casos mínimos
- [ ] un mismo estado usa el mismo label en badge, stat, lane, filter y detail [I]
- [ ] `Yes/No` no aparece en una ruta mientras otra ya usa otro idioma [I]
- [ ] `item/items` no convive con otro pluralizador [I]
- [ ] `Area`, `Role`, `Density`, `Preset`, `Motion`, `Contrast` salen del mismo dominio [I]
- [ ] `Loading` y route loading titles siguen una convención única [I]

#### Validación de fallback

| Caso | Qué revisar | Resultado esperado |
|---|---|---|
| key faltante | fallback controlado [I] | visible pero trazable |
| fecha inválida | fallback consistente [C][I] | no explota layout |
| valor vacío | placeholder/fallback consistente [C][I] | no hay mezcla de `-`, vacío y `undefined` según componente |
| state desconocido | label/description segura [C][I] | no rompe badge ni panel |

#### Validación de formatting

| Frente | Qué revisar | Resultado esperado |
|---|---|---|
| fecha absoluta | mismo locale y estilo en inbox/detail/sync [I] | coherencia global |
| fecha relativa | mismo locale y misma regla [I] | coherencia global |
| booleanos | una sola convención [I] | sin `Yes/No` duplicado fuera de capa |
| pluralización | conteos mínimos correctos [I] | sin strings improvisados |
| humanización de enums | fallback solo donde corresponda [I] | no sustituye copy curada |

#### Validación transversal en rutas principales

| Ruta / superficie | Qué revisar | Por qué entra |
|---|---|---|
| `/` launcher | `PageHeader`, `StatCard`, `Surface`, app shell [C] | alta densidad de copy general |
| `/inbox` | `PageHeader`, `StatCard`, `FilterPills`, `StateBadge`, `EmptyState` [C] | máxima mezcla entre shared + record-state |
| `/record/[recordId]` | `PageHeader`, `StateBadge`, `StatCard`, dates, relative time, values [C] | máxima presión del formatting layer |
| `/flow/[schemaId]` | `PageLoading`, progress labels, notices, relative time [C] | mezcla caller + schema + formatting |
| `/sync` | `StatCard`, `FilterPills`, `EmptyState`, date formatting [C] | copy operational shared |
| shell global / `AppShell` | labels runtime humanizadas + descripciones de área [C] | lugar más obvio donde runtime y copy se rozan |
| `app/error.tsx` y `app/not-found.tsx` | `StatusPanel` + buttons [C] | estados sistémicos reutilizables |
| `app/*/loading.tsx` | `PageLoading` [C] | default shared + caller copy |

#### Criterios de aceptación

Se considera esta intervención conceptualmente lista para ejecutar cuando:
- [ ] existe una frontera clara entre `i18n`, `runtime`, `schema` y `data`
- [ ] existe inventario de strings shared y formatting leaks
- [ ] existe convención de dominios de claves
- [ ] existe lista roja de lo que no se centraliza todavía
- [ ] están definidos los componentes shared prioritarios
- [ ] quedó definida la validación transversal mínima
- [ ] quedó explícito qué no debe vivir en `runtime.ts`

#### Señales de stop

Detener y revaluar si ocurre cualquiera de estas:
- [ ] se intenta meter `schema.title` o `field.label` dentro de `common.*`
- [ ] se propone que `runtime.ts` resuelva traducción o fallback de idioma
- [ ] se deja `formatHumanLabel()` como estrategia principal de i18n
- [ ] se mantienen dos capas distintas para booleanos/pluralización sin razón
- [ ] aparece UI mezclada: copy traducida pero fechas/Yes-No en inglés
- [ ] los mismos estados generan claves distintas por componente
- [ ] brand ids y brand labels quedan acoplados dentro de runtime

---

### Reporte 4. Hallazgos extra y qué nos deja resuelto

#### Quick wins

1. **Crear el inventario maestro de shared strings antes que cualquier provider real** [I]
   - `PageLoading`
   - `FilterPills`
   - `record-view` state labels/descriptions
   - app shell labels/descriptions
   - wrappers de format

2. **Separar “runtime ids” de “runtime labels visibles”** [C][I]
   - mantener ids en `runtime.ts`
   - sacar labels humanos a i18n o caller domains

3. **Consolidar formatting layer** [C][I]
   - una sola capa para fecha/relative/boolean/plural
   - desactivar la duplicación entre `utils.ts` y `ui/contracts.ts`

4. **Tratar `PageHeader`, `StatusPanel`, `EmptyState`, `SectionHeader`, `StatCard` como shells** [C]
   - centralizar la copy en dominios de caller, no dentro del componente

5. **Usar `stateLabel/stateDescription` como primer dominio shared real** [C][I]
   - es el caso más claro de texto transversal

#### Catálogo de componentes shared prioritarios

| Prioridad | Pieza | Motivo |
|---|---|---|
| 1 | `src/lib/utils.ts` / `src/lib/ui/contracts.ts` | concentran formatting leaks [C] |
| 1 | `src/lib/core/record-view.ts` | labels/descriptions de estado shared [C] |
| 1 | `components/layout/app-shell.tsx` | gran volumen de shell copy + humanización runtime [C] |
| 1 | `components/ui/page-loading.tsx` + `app/*/loading.tsx` | defaults + reuse transversal [C] |
| 1 | `components/ui/filter-pills.tsx` | a11y default shared [C] |
| 2 | `components/ui/state-badge.tsx` | consumidor crítico de state labels [C] |
| 2 | `app/error.tsx` / `app/not-found.tsx` | reusable status patterns [C] |
| 3 | `PageHeader`, `StatusPanel`, `EmptyState`, `SectionHeader`, `StatCard`, `DetailList` | shells que deben obedecer dominios, no emitir defaults fuertes [C] |

#### Propuesta de dominios de claves

##### Dominios raíz recomendados
| Dominio | Uso |
|---|---|
| `common.format.*` | fecha, relative time, booleanos, conteos, placeholders |
| `common.record_state.*` | label y description de estados |
| `common.a11y.*` | `Filter options` y futuros strings accesibles |
| `app_shell.*` | shell global, chips, métricas runtime, descripciones de área |
| `loading.*` | defaults y route loading copy |
| `status.system.*` | error/not-found/global system panels |
| `inbox.*`, `record.*`, `flow.*`, `sync.*`, `launcher.*` | caller copy por superficie |
| `schema.{schemaId}.*` | solo cuando se cierre ownership de schemas |

##### Ejemplos de clave sugerida
- `common.format.boolean.true`
- `common.format.boolean.false`
- `common.format.empty_value`
- `common.format.item_count`
- `common.record_state.submitted.label`
- `common.record_state.submitted.description`
- `common.a11y.filter_options`
- `app_shell.metric.role`
- `app_shell.metric.density`
- `app_shell.chip.area`
- `app_shell.area_description.inbox`
- `loading.defaults.title`
- `loading.defaults.subtitle`
- `loading.route.inbox.title`
- `loading.route.inbox.subtitle`
- `status.system.not_found.eyebrow`
- `status.system.error.retry`

#### Artefactos sugeridos

1. `docs/i18n/shared-text-inventory.md` [I]
2. `docs/i18n/key-domain-map.md` [I]
3. `docs/i18n/formatting-leaks.md` [I]
4. `docs/i18n/lista-roja-centralizacion.md` [I]
5. `docs/i18n/validation-shared-ui-checklist.md` [I]
6. `src/lib/i18n/` como frontera técnica futura, no implementada todavía [I]

#### Decisiones que conviene congelar

Congelar ahora para no patinar después:
- `runtime.ts` **no** será dueño del idioma ni de labels visibles traducibles [I]
- `formatHumanLabel()` será fallback técnico, **no** estrategia final de copy [I]
- `schema-registry` no se mezcla de inicio con `common.*` [I]
- el formatting layer será único, no doble [I]
- las claves se agrupan por **dominio semántico**, no por nombre del componente base [I]
- `PageHeader` / `EmptyState` / `StatusPanel` / `StatCard` se tratan como shells visuales [C][I]

#### Qué nos deja resuelto este chat

Este chat deja muy avanzada la base del frente global de idioma porque ya resuelve:

1. **Dónde sí están los verdaderos emisores de texto shared** [C]
   - no son todos los componentes base
   - muchos shared son solo marcos que reciben copy externa

2. **Qué debe vivir en `src/lib/i18n/*`** [I]
   - catálogo, lookup, fallback, wrappers de formato, dominios y tipado conceptual

3. **Qué no debe vivir en `runtime.ts`** [C][I]
   - traducción
   - locale
   - labels visibles traducibles
   - pluralización y formateo humano

4. **Cuál es la primera ola segura de centralización** [C][I]
   - formatting layer
   - record states
   - app shell
   - loading copy
   - a11y defaults shared

5. **Qué no debe centralizarse todavía** [C][D]
   - schemas
   - data values
   - copy que codifique semántica real no validada

6. **Cómo evitar claves caóticas desde el día 1** [I]
   - dominios semánticos
   - separar emisor visual de significado compartido

En resumen: este chat deja listo el mapa de intervención controlada para shared UI e idioma. Ya no se arranca desde intuición ni desde “vamos metiendo strings a un diccionario a ver qué pasa”. Se arranca con frontera de capas, ownership, lista roja, prioridades y validación transversal.

#### Preguntas abiertas reales

1. **¿El locale será global del workspace, por usuario, por tenant o por ruta?** [D]
2. **¿Los schemas son demo data editable o contrato de negocio real?** [D]
3. **¿`BrandProfile.label` debe existir como copy visible o solo como etiqueta de debug/internal shell?** [D]
4. **¿Los labels de estado deben ser curados por producto o basta fallback técnico al inicio?** [D]
5. **¿El formatting debe obedecer timezone del usuario, del sistema o del record?** [D]
6. **¿La fase 1 incluye accesibilidad textual formal o solo visible UI?** [D]
7. **¿Se aceptará un fallback temporal en inglés para schemas mientras shared UI ya sea multi-locale?** [D]

#### Qué nos deja resuelto este chat

Nos deja resuelto el esqueleto crítico del frente de idioma compartido:
- mapa de arquitectura central recomendada
- frontera clara entre i18n, runtime, schema y data
- inventario de shared strings y formatting leaks
- lista roja de centralización
- catálogo de quick wins reales
- validación transversal para shared UI
- base reusable para seguir con el inventario global sin mezclar componentes shell con copy semántica
## 🏠 Launcher e Inbox

**Archivo fuente consolidado:** `launcher_inbox_intervention_map(1).md`

### Reporte 1. Mapa y alcance

**Base obligatoria usada**
- **Fuente principal de verdad:** ZIP del proyecto `apps/external_interaction_template`
- **Marco de control aplicado:** “Formato Universal de Pre-Intervención y Rastreabilidad”

**Leyenda de evidencia**
- **Confirmado:** visible directamente en el código del ZIP
- **Inferido:** deducción fuerte basada en clases, composición, imports y contratos
- **Dudoso:** no conviene traducir, renombrar o centralizar todavía sin resolver ownership

#### 1.1 Resumen ejecutivo

##### Qué cubre este mapeo
Este mapeo cubre dos superficies primarias del frente de idioma y control visual dentro de `apps/external_interaction_template`:
- **Launcher / home** desde `app/page.tsx`
- **Inbox** desde `app/inbox/page.tsx` y `components/records/record-inbox.tsx`

Además cubre los shared components y helpers que alteran copy visible, densidad de lectura o riesgo de ruptura:
- `components/records/inbox-record-card.tsx`
- `components/layout/app-shell.tsx`
- `components/layout/app-frame.tsx`
- `components/ui/page-header.tsx`
- `components/ui/stat-card.tsx`
- `components/ui/surface.tsx`
- `components/ui/section-header.tsx`
- `components/ui/button.tsx`
- `components/ui/badge.tsx`
- `components/ui/empty-state.tsx`
- `components/ui/filter-pills.tsx`
- `components/ui/input.tsx`
- `components/ui/select.tsx`
- `components/ui/state-badge.tsx`
- `components/ui/detail-list.tsx`
- `src/lib/core/record-view.ts`
- `src/lib/core/schema-registry.ts`
- `src/lib/ui/record-contracts.ts`
- `src/lib/utils.ts`
- `src/lib/ui/runtime.ts`
- `app/layout.tsx`
- `app/globals.css`

##### Qué deja listo
- Un **mapa funcional y visual** de launcher e inbox
- Un **inventario reusable por archivo** usando estas dos superficies como caso de prueba
- Un corte claro entre:
  - copy local de pantalla
  - copy shared
  - copy runtime-humanized
  - copy schema/data/state-driven
- Un mapa de **riesgos de longitud** y de **scan speed**
- Una **lista roja** de ownership dudoso para no traducir a ciegas
- Una base lista para pasar luego a extracción de claves, rollout o validación, sin proponer implementación final todavía

##### Riesgos principales
1. **Launcher e inbox heredan shell global visible** desde `AppShell`, así que no existe análisis limpio del home/inbox sin incluir shell.
2. **El inbox mezcla copy local con labels provenientes de schema, estados y helpers humanizadores**, especialmente en `record-view`, `schema-registry`, `formatHumanLabel` y `formatDateTime`.
3. **Hay hotspots de longitud en zonas compactas**: badges, state pills, CTAs sm, metric labels, select options, rows compactas, cards y shell sticky header.
4. **Hay hotspots de scan speed**: si se alargan labels o desalinean pills/cards, el inbox pierde velocidad de triage aun cuando no “rompa” visualmente.
5. **`app/layout.tsx` mantiene `lang="en"` y metadata en inglés**, así que una traducción parcial de launcher o inbox dejaría el frente idioma a medias.

#### 1.2 Alcance y no alcance

##### Entra en esta intervención
- Mapeo del launcher desde `app/page.tsx`
- Mapeo del inbox desde `app/inbox/page.tsx` y `components/records/record-inbox.tsx`
- `components/records/inbox-record-card.tsx`
- Shell visible compartido que impacta ambas pantallas
- Helpers y dependencias que afectan copy visible, labels, estados, fechas, summaries, field labels o enum display
- Riesgos de layout por longitud
- Riesgos de scan speed
- Inventario reusable por archivo

##### No entra todavía
- Implementación final de i18n
- Refactor final de ownership
- Cambio de contratos de schema o backend
- Renombre definitivo de estados, adapters o access modes
- Intervención de otras superficies completas como `/record/[recordId]`, `/flow/[schemaId]`, `/sync` o `/playground`
- Cierre final de glosario ni naming definitivo de producto

##### Señales de corte según el formato universal
Si durante una futura intervención real aparece cualquiera de estas señales, conviene pausar:
- ownership incierto entre launcher/inbox y schema/runtime
- traducción de enums o IDs expuestos como si fueran copy local
- cambio local que obliga a tocar runtime helpers o schema definitions sin estar en alcance
- degradación de scan speed en inbox aunque no exista overflow
- inconsistencia entre shell y page content

#### 1.3 Mapa del launcher

##### Superficie principal
- **Archivo principal:** `app/page.tsx`
- **Envolvente visible:** `app/layout.tsx` → `components/layout/app-frame.tsx` → `components/layout/app-shell.tsx`

##### Zonas de UI del launcher

| Zona | Archivo/componente dominante | Qué hace | Copy visible principal | Evidencia | Sensibilidad |
|---|---|---|---|---|---|
| Shell sticky top area | `components/layout/app-shell.tsx` | marco global, navegación, CTAs globales, chips y contexto actual | `External Interaction Template`, `Schema-driven workflow control surface`, labels nav, chips, CTA globales | Confirmado | Alta |
| Hero del launcher | `app/page.tsx` + `components/ui/page-header.tsx` | aterrizaje principal del home | `Launcher`, título, descripción, `Open schemas`, `Review inbox` | Confirmado | Alta |
| Strip de stats | `app/page.tsx` + `components/ui/stat-card.tsx` | resumen de estado general | `Records`, `Pending sync`, `Retryable`, `Schemas` + metas | Confirmado | Media |
| Bloque de flows | `app/page.tsx` + `components/ui/surface.tsx` | contenedor del catálogo de schemas | `Available flows`, subtítulo explicativo | Confirmado | Media |
| Schema cards | `app/page.tsx` + `Surface`, `Badge`, `Button` | entrada por flujo/schema | title, summary, badges, métricas, CTAs por schema | Confirmado | Muy alta |

##### Componentes implicados en launcher
- `PageHeader`
- `StatCard`
- `Surface`
- `SectionHeader`
- `Badge`
- `Button`
- `AppShell`

##### Copy local visible del launcher

**Claramente local de pantalla (`app/page.tsx`)**
- `Launcher`
- `Premium control surface for external interaction flows`
- `Launch schema-driven intake flows, review active records, and monitor sync outcomes from one calmer, more deliberate workspace.`
- `Open schemas`
- `Review inbox`
- `Records`
- `Across all schema-driven flows.`
- `Pending sync`
- `Waiting for the next sync pass.`
- `Retryable`
- `Need an operator retry.`
- `Schemas`
- `Neutral examples across use cases.`
- `Available flows`
- `Each schema inherits the same visual system but adapts to a different workflow shape.`
- `Steps`
- `Fields`
- `Outbound adapter`
- `Start flow`
- `Resume / token`

**Visible pero no locales del launcher**
- `schema.title`
- `schema.summary`
- `schema.category`
- `schema.flow.accessMode`
- `schema.tags`
- `schema.adapterBindings.outbound`
- conteos de `records` y `syncData`
- shell labels globales

##### Dependencias relevantes del launcher

| Dependencia | Rol visible | Qué inyecta a UI | Tipo |
|---|---|---|---|
| `src/lib/core/schema-registry.ts` | catálogo de schemas | titles, summaries, categories, tags, accessMode, adapter bindings | Schema-owned |
| `src/lib/services/records.ts` | records | conteo visible en stats | Data/service-owned |
| `src/lib/services/actions.ts` | sync data | conteos `pending` y `retryable` | Data/service-owned |
| `components/layout/app-shell.tsx` | shell global | nav, top area, CTAs, chips, labels runtime | Shared + runtime |
| `src/lib/utils.ts` | humanización y formato | `formatHumanLabel` indirecto vía shell | Runtime/helper-owned |

##### Superficies más sensibles del launcher
- Hero title y CTA row
- Shell sticky title con `truncate`
- Schema badges
- Fila compacta `Outbound adapter`
- CTAs sm por card
- Summaries de schema
- Uppercase labels de stat cards y badges

#### 1.4 Mapa del inbox

##### Superficie principal
- **Entry point:** `app/inbox/page.tsx`
- **Contenedor real de UI:** `components/records/record-inbox.tsx`
- **Card principal de resultados:** `components/records/inbox-record-card.tsx`
- **Envolvente visible:** `AppShell`

##### Zonas de UI del inbox

| Zona | Archivo/componente dominante | Qué hace | Copy visible principal | Evidencia | Sensibilidad |
|---|---|---|---|---|---|
| Shell sticky top area | `components/layout/app-shell.tsx` | marco global visible también en inbox | descripción del área inbox, nav, chips, CTAs | Confirmado | Alta |
| Hero / queue overview | `components/records/record-inbox.tsx` + `PageHeader` | contexto del inbox + stats + toggle de vista | `Inbox`, título, descripción, stats, `Clear filters` | Confirmado | Alta |
| Queue controls | `record-inbox.tsx` + `Surface`, `Input`, `Select`, `FilterPills` | búsqueda y filtros | `Queue controls`, placeholder search, `Schema`, `State`, `All schema types`, `All states`, `State lanes` | Confirmado | Muy alta |
| Queue summary row | `record-inbox.tsx` + `.queue-header` | feedback de resultados y modo de vista | `Showing... results`, `Filtered view active`, `Default queue order...` | Confirmado | Alta |
| Empty state | `record-inbox.tsx` + `EmptyState` | fallback sin resultados | `Queue empty`, `No records match...`, `Go to launcher` | Confirmado | Media |
| Lane headers en list view | `record-inbox.tsx` + `StateBadge` | agrupación por estado | state badge, `stateDescription(...)`, conteo por lane | Confirmado | Alta |
| Record cards | `components/records/inbox-record-card.tsx` | resumen navegable por record | schema title, record title, summary, preview fields, state badge, updated time, record id | Confirmado | Muy alta |

##### Componentes implicados en inbox
- `RecordInbox`
- `InboxRecordCard`
- `PageHeader`
- `StatCard`
- `Surface`
- `Button`
- `EmptyState`
- `FilterPills`
- `Input`
- `Select`
- `StateBadge`
- `DetailList`
- `Badge`
- `AppShell`

##### Copy local visible del inbox

**Claramente local de pantalla o componente local**
- `Inbox`
- `Review queue tuned for quick triage`
- `Scan current records, isolate the states that matter, and move from queue to decision without fighting the UI.`
- `Visible records`
- `Current results after filters.`
- `Needs attention`
- `Awaiting update or failed states.`
- `Submitted`
- `Ready for first review pass.`
- `In review`
- `Already under active operator handling.`
- `Clear filters`
- `Queue controls`
- `Filter by schema, status, or keywords without losing scan rhythm.`
- `Search title, fields, record id, requester...`
- `Schema`
- `State`
- `All schema types`
- `All states`
- `State lanes`
- `Showing {n} result(s) across {m} active state lane(s).`
- `List mode preserves queue lanes for scan speed, while grid mode flattens cards for broader browsing.`
- `Filtered view active`
- `Default queue order prioritizes attention states first`
- `Queue empty`
- `No records match the current queue view`
- `Clear a filter, switch schema scope, or launch a new flow to create another record.`
- `Go to launcher`
- `Updated {formatDateTime(...)}`
- fallback `Schema-neutral record surface ready for downstream integration.`

**Visible pero no puramente locales**
- labels y descripciones de estado desde `record-view.ts`
- schema titles y summaries
- field labels de preview desde `schema-registry.ts`
- record title, record id, field values y fechas
- `Filter options` como aria default de `FilterPills`
- shell labels globales

##### Dependencias relevantes del inbox

| Dependencia | Rol visible | Qué inyecta a UI | Tipo |
|---|---|---|---|
| `src/lib/core/record-view.ts` | helper de inbox | orden de estados, labels, descriptions, tone, preview field logic | Runtime/domain helper |
| `src/lib/core/schema-registry.ts` | schema display data | titles, summaries, field labels usados en cards y selects | Schema-owned |
| `src/lib/ui/record-contracts.ts` | fallback y normalización | título fallback `Record {id}`, preview clamp, ensure state | Helper/domain-owned |
| `src/lib/utils.ts` | formato visible | `formatHumanLabel`, `formatDateTime`, `formatValue` | Helper/runtime-owned |
| `src/lib/services/records.ts` | records listados | títulos, ids, states, fields, dates | Data/service-owned |
| `components/layout/app-shell.tsx` | shell global | copy visible persistente | Shared + runtime |
| `app/layout.tsx` | metadata/lang | idioma del documento, metadata | Root/shared |

##### Superficies más sensibles del inbox
- Search placeholder y fila de controles
- Select labels y option labels largas
- Filter pills de estados
- Queue summary line
- StateBadge
- `stateDescription(...)`
- Schema title row dentro de card
- Record title truncado
- Summary de schema en card
- DetailList labels/values
- Footer `Updated...` + `record.id`
- Grid mode y list mode bajo traducción larga

#### 1.5 Componentes implicados y acoplamientos visibles

| Archivo | Rol | Acoplamientos visibles | Estado de análisis |
|---|---|---|---|
| `app/page.tsx` | launcher page | usa records, sync data, schema registry, shared UI | Confirmado |
| `app/inbox/page.tsx` | inbox route loader | pasa `records` y `schemas` a `RecordInbox` | Confirmado |
| `components/records/record-inbox.tsx` | inbox controller UI | controla filtros, vista, lanes y empty state | Confirmado |
| `components/records/inbox-record-card.tsx` | card reusable | depende de `StateBadge`, `DetailList`, `normalizeRecordTitle`, `formatDateTime` | Confirmado |
| `components/layout/app-shell.tsx` | shell global | copy visible persistente + runtime chips | Confirmado |
| `src/lib/core/record-view.ts` | helper de semántica de inbox | labels/descriptions de estados, preview fields | Confirmado |
| `src/lib/core/schema-registry.ts` | fuente de schema display | titles, summaries, field labels, categories, tags | Confirmado |
| `src/lib/utils.ts` | helper visible | human labels, dates, generic values | Confirmado |
| `app/layout.tsx` | root shell document | metadata y `lang="en"` | Confirmado |
| `app/globals.css` | clases densidad/scan | `queue-header`, `shell-chip`, `metric-label`, `eyebrow` | Confirmado |

---

### Reporte 2. Ownership, lista roja y riesgos

#### 2.1 Matriz de ownership

| Elemento visible | Archivo/zona | Frontend-owned | Shared-owned | Runtime-owned | Schema-owned | Backend-owned / data-owned | Dudoso | Evidencia | Nota |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Hero eyebrow `Launcher` | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Hero title/description | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `Open schemas`, `Review inbox` | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Stat labels/meta del launcher | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Counts `records.length`, pending/retryable | `app/page.tsx` |  |  |  |  | Sí |  | Confirmado | Data visible, no copy |
| `Available flows` y subtítulo | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `Steps`, `Fields`, `Outbound adapter` | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `Start flow`, `Resume / token` | `app/page.tsx` | Sí |  |  |  |  |  | Confirmado | Copy local pero sensible |
| `schema.title` | schema card / record card |  |  |  | Sí |  |  | Confirmado | No es copy local |
| `schema.summary` | schema card / record card |  |  |  | Sí |  |  | Confirmado | No es copy local |
| `schema.category` | launcher badge |  |  |  | Sí |  | **Sí** | Confirmado | Hoy parece ID expuesto |
| `schema.flow.accessMode` | launcher badge |  |  | **Sí** | Sí |  | **Sí** | Confirmado | Enum visible |
| `schema.tags` | launcher badges |  |  |  | Sí |  | **Sí** | Confirmado | Taxonomía compartida |
| `schema.adapterBindings.outbound` | launcher metric row |  |  |  | Sí |  | **Sí** | Confirmado | Parece ID técnico |
| Shell nav labels | `AppShell` |  | Sí |  |  |  |  | Confirmado | Shared shell |
| Shell title/description | `AppShell` |  | Sí | Sí |  |  |  | Confirmado | área resuelta por runtime helper |
| Shell chips `Area/Brand/Preset` | `AppShell` |  | Sí | Sí |  |  |  | Confirmado | Mezcla shared + runtime |
| Shell metric labels `Role/Density/...` | `AppShell` |  | Sí | Sí |  |  |  | Confirmado | Shared + runtime |
| Inbox title/description | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Inbox stat labels/meta | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `Clear filters` | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `Queue controls` y subtítulo | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Search placeholder | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Filter labels `Schema`, `State` | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `All schema types`, `All states` | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| `State lanes` | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Queue summary sentences | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| Empty state copy | `record-inbox.tsx` | Sí |  |  |  |  |  | Confirmado | Local limpio |
| State labels `Submitted`, etc. | `record-view.ts` + `StateBadge` |  |  | Sí |  |  | **Sí** | Confirmado | Humanizados vía helper, no locales del inbox |
| State descriptions | `record-view.ts` |  |  | Sí |  |  |  | Confirmado | Domain/runtime helper |
| Record title | records/cards |  |  |  |  | Sí |  | Confirmado | Data-owned |
| Record ID | cards |  |  |  |  | Sí |  | Confirmado | Data-owned |
| Preview field labels | `recordPreviewFields` + `schema-registry` |  |  |  | Sí |  | **Sí** | Confirmado | Provienen de schema |
| Preview field values | records/cards |  |  |  |  | Sí |  | Confirmado | Data-owned |
| `Updated {date}` | record card footer | Sí |  | **Sí** |  | Sí | **Sí** | Confirmado | prefijo local + fecha helper localizable |
| `Schema-neutral record surface ready for downstream integration.` | card fallback | Sí |  |  |  |  |  | Confirmado | local del componente |
| `Record {id}` fallback | `record-contracts.ts` |  |  | Sí |  | Sí | **Sí** | Confirmado | helper/domain fallback |
| Root metadata title/description | `app/layout.tsx` |  | Sí |  |  |  |  | Confirmado | root shared |
| `html lang="en"` | `app/layout.tsx` |  | Sí |  |  |  |  | Confirmado | documento raíz |

#### 2.2 Lista roja del launcher

No conviene traducir o centralizar esto como si fuera copy local del launcher:

| Elemento | Dónde aparece | Motivo | Estado |
|---|---|---|---|
| `schema.title` | cards de flows | pertenece al dominio schema | Confirmado |
| `schema.summary` | cards de flows | pertenece al dominio schema | Confirmado |
| `schema.category` | badge | parece taxonomy/ID expuesto, no label de marketing | Confirmado + Dudoso |
| `schema.flow.accessMode` | badge | enum del sistema expuesto directo | Confirmado + Dudoso |
| `schema.tags` | badges | taxonomía compartida, posiblemente reusable en otras superficies | Confirmado + Dudoso |
| `schema.adapterBindings.outbound` | metric row | parece adapter ID o label técnica | Confirmado + Dudoso |
| pending/retryable counts | stat values | data/service-owned | Confirmado |
| shell labels visibles | arriba del launcher | no son del archivo `app/page.tsx` | Confirmado |
| `Schema Playground` vs `Open schemas` vs `Schemas` | shell + launcher | duplicación semántica sin congelar glosario | Confirmado + Dudoso |

#### 2.3 Lista roja del inbox

| Elemento | Dónde aparece | Motivo | Estado |
|---|---|---|---|
| `stateLabel(state)` | pills, select, badges, lane headers | proviene de helper y enum, no de pantalla | Confirmado + Dudoso |
| `stateDescription(state)` | lane header | semántica de dominio, no local de pantalla | Confirmado |
| `schema.title` | select y card eyebrow | schema-owned | Confirmado |
| `schema.summary` | record card summary | schema-owned | Confirmado |
| preview field labels | `DetailList` | salen de `schema-registry` | Confirmado |
| preview field values | `DetailList` | data-owned | Confirmado |
| `record.title` | cards | data-owned | Confirmado |
| `record.id` | cards | data-owned | Confirmado |
| `formatDateTime(...)` | footer `Updated...` | helper visible con locale fijo `en` | Confirmado + Dudoso |
| fallback `Record {id}` | helper | no es copy de inbox sino fallback cross-surface | Confirmado + Dudoso |
| `Filter options` aria default | `FilterPills` | shared component text, no inbox local | Confirmado |
| shell labels visibles | top area del inbox | shared + runtime | Confirmado |

#### 2.4 Matriz de riesgos general

| Riesgo | Tipo | Probabilidad | Impacto | Dónde pega | Señal temprana | Evidencia |
|---|---|---:|---:|---|---|---|
| Títulos demasiado largos | Longitud | Alta | Alta | launcher hero, shell, record card | wraps agresivos, truncado o cards desparejas | Confirmado |
| CTAs truncados o inflados | Longitud | Alta | Alta | hero CTAs, schema CTAs, clear filters, shell CTA | wrap torcido, altura extra, botones enormes | Confirmado |
| State badges demasiado largos | Longitud + scan speed | Alta | Alta | inbox lanes, cards, pills, selects | badges dominan la fila, baja legibilidad | Confirmado |
| Cards desalineadas | Layout | Alta | Media/Alta | launcher schema grid, inbox grid | mosaico irregular, acción baja demasiado | Confirmado |
| Pérdida de scan speed | Usabilidad | Alta | Alta | inbox list mode, controls, pills, card detail list | cuesta escanear estados/filas rápido | Confirmado + Inferido |
| Mezcla local + semántica real | Ownership | Alta | Alta | inbox y launcher | traducción inconsistente o parcial | Confirmado |
| IDs técnicos visibles | Semántica | Alta | Media/Alta | category, accessMode, adapter, tags | UI más técnica de lo previsto | Confirmado |
| Traducción parcial del frente | Consistencia | Alta | Media | page vs shell vs layout | home/inbox en ES pero shell/root en EN | Confirmado |
| Humanización confundida con localización | Ownership | Alta | Alta | `formatHumanLabel`, `stateLabel` | etiquetas “bonitas” pero no localizadas | Confirmado |
| Locale fijo en fecha/hora | Longitud + consistencia | Media | Media | footer cards | mezcla de idioma en fechas | Confirmado |

#### 2.5 Riesgos de longitud

| Superficie / componente | Por qué es sensible | Severidad | Caso que podría romper | Señal de ruptura | Evidencia |
|---|---|---|---|---|---|
| Shell title | usa `truncate` directo | Muy alta | título más largo en ES | elipsis destructiva | Confirmado |
| Shell nav | botones de nav con icono + texto | Alta | `Sync` o `Schemas` en versión larga | wrap prematuro del nav | Confirmado |
| Shell chips | pills compactas `min-h-8` | Media/Alta | labels runtime/localizadas | fila más alta y más densa | Confirmado |
| Launcher hero title | comparte región con acciones | Alta | ES con frase más larga | 3+ líneas o choque con acciones | Confirmado |
| Launcher hero CTAs | botones md en flex-wrap | Alta | traducciones largas | fila fea, wrap incómodo | Confirmado |
| Launcher stat labels/meta | uppercase + meta pequeña | Media | labels más largas | cards con alturas disparejas | Confirmado |
| Schema card badges | uppercase compacta + tags variables | Muy alta | `authenticated`, tags largas, ES | pills gigantes, ruido visual | Confirmado |
| Launcher metric row `Outbound adapter` | row compacta justify-between | Muy alta | label o adapter largos | empuje lateral, salto raro | Confirmado |
| Schema card summary | altura libre | Alta | summaries más largas | cards muy desparejas | Confirmado |
| Schema card CTA row | botones sm compactos | Muy alta | `Resume / token` en ES | wrap torcido, alturas distintas | Confirmado |
| Inbox search placeholder | input único muy largo | Media | placeholder en ES | placeholder recortado / ruido | Confirmado |
| Schema select option labels | width acotada 220px | Alta | schema titles más largas | dropdown o control se ve apretado | Confirmado |
| State select labels | width acotada | Alta | estados traducidos largos | select muy apretado | Confirmado |
| FilterPills | botón con label + count | Muy alta | estados largos | múltiples wraps, pérdida de ritmo | Confirmado |
| Queue summary sentence | línea compuesta con pluralización | Alta | ES más larga | bloque más alto o duro de escanear | Confirmado |
| StateBadge | `Badge` fijo de alto 6 con uppercase | Muy alta | `Awaiting update` en ES | badge ancho y dominante | Confirmado |
| Lane descriptions | oración secundaria por estado | Media/Alta | descriptions más largas | headers más altos, menos densidad | Confirmado |
| Card eyebrow schema title | no hay truncate visible en esa línea | Alta | schema title larga | empuja state badge o arrow | Confirmado |
| Record title | `truncate` | Alta | títulos largos | pérdida de información crítica | Confirmado |
| Card summary | `max-w-[54ch]` pero sin clamp | Alta | summaries largas | card crece demasiado | Confirmado |
| DetailList labels | uppercase pequeñas | Alta | field labels largas | wraps y ruido visual | Confirmado |
| Footer `Updated...` + `record.id` | dos bloques en flex-wrap | Media/Alta | fecha local larga o ids largos | footer más alto o partido | Confirmado |

#### 2.6 Riesgos de scan speed

| Riesgo | Dónde | Por qué afecta scan speed | Severidad | Evidencia |
|---|---|---|---|---|
| Filter pills demasiado verbosos | inbox controls | el usuario tarda más en identificar lanes | Muy alta | Confirmado + Inferido |
| Queue header demasiado narrativo | inbox summary row | roba atención y ocupa alto de lectura | Alta | Confirmado + Inferido |
| DetailList labels largas | record cards | rompe el patrón rápido label/value | Alta | Confirmado |
| State badges largos | lanes y cards | visualmente pesan demasiado frente a record title | Muy alta | Confirmado |
| Cards desparejas en grid | launcher e inbox grid | el ojo pierde ritmo entre bloques | Alta | Confirmado + Inferido |
| Summary de schema muy dominante | record cards | desplaza señales operativas más importantes | Alta | Confirmado + Inferido |
| Demasiados términos operativos distintos | launcher + inbox + shell | aumenta carga cognitiva | Media/Alta | Confirmado |
| Uppercase + tracking en exceso | badges, metric labels, eyebrows | empeora densidad con idiomas largos | Media/Alta | Confirmado |

#### 2.7 Riesgos de mezcla entre UI local y semántica real

| Mezcla problemática | Dónde | Riesgo | Estado |
|---|---|---|---|
| copy local + enums humanizados | inbox states y shell runtime labels | traducir solo un lado deja mezcla rara | Confirmado |
| screen copy + schema copy | launcher cards e inbox cards | un bloque queda ES y otro sigue siendo schema/raw | Confirmado |
| UI friendly label + ID técnico | category/accessMode/adapter | falsa sensación de copy local | Confirmado |
| queue copy local + state semantics reales | lane headers y counts | se puede traducir el texto de contexto pero no el valor semántico sin mapa | Confirmado |
| shell global + page local | launcher e inbox | inconsistencia transversal | Confirmado |
| locale textual + locale de fecha | record cards | UI ES con fecha EN | Confirmado |

---

### Reporte 3. Validación y criterios de aceptación

#### 3.1 Validación visual del launcher

| Caso | Qué validar | Resultado esperado | Severidad |
|---|---|---|---|
| Hero desktop | eyebrow, title, description, 2 CTAs | sin colisión entre bloque textual y acciones | Alta |
| Hero tablet | wrap de texto y CTAs | jerarquía intacta, CTAs legibles | Alta |
| Hero mobile | stack vertical | sin truncado raro ni botones excesivos | Alta |
| Stats row `md/xl` | labels/meta | cards con alturas razonables y comparables | Media |
| Section `Available flows` | title/subtitle | encabezado estable sin empujar el grid | Media |
| Schema grid `md` | badges, metrics y CTAs | cards visualmente coherentes | Alta |
| Schema grid `xl` | summaries y badges largas | sin mosaico caótico | Alta |
| Shell sticky header | nav, shell title, chips, CTA globales | no truncado destructivo ni altura excesiva | Muy alta |

#### 3.2 Validación visual del inbox

| Caso | Qué validar | Resultado esperado | Severidad |
|---|---|---|---|
| Hero inbox desktop | title, description, stats, actions | lectura rápida y sin ruido | Alta |
| Hero inbox mobile | stats + toggle view + clear filters | sin overflow ni apilado raro | Alta |
| Queue controls desktop | search + 2 selects | tres columnas funcionales y legibles | Muy alta |
| Queue controls tablet/mobile | wrap de controles | sin degradación severa de uso | Muy alta |
| State lanes pills | label + count + wrap | legibles, distinguibles, sin fila caótica | Muy alta |
| Queue summary row | sentence + status note | clara y escaneable | Alta |
| List view lane headers | StateBadge + description + count | lectura rápida por lane | Muy alta |
| Grid view cards | igualdad visual relativa | grid legible y sin drift grave | Alta |
| Record card footer | updated + id | wrap tolerable, sin ruido | Media/Alta |
| Shell sticky header en inbox | integración con queue UI | no competir visualmente con filtros | Alta |

#### 3.3 Validación funcional del inbox

| Caso | Qué validar | Resultado esperado | Nota |
|---|---|---|---|
| filtro por schema | select `Schema` | cambia el conjunto visible correctamente | Confirmado por código |
| filtro por state | select `State` y pills | ambos afectan el mismo `stateFilter` | Confirmado por código |
| clear filters | botón ghost | resetea query + schema + state | Confirmado por código |
| búsqueda libre | input search | busca en `title`, `id` y `fields` serializados | Confirmado por código |
| toggle list/grid | botones icon-only | alterna `view` sin perder filtros | Confirmado por código |
| lane grouping | list mode | ordena y agrupa por `INBOX_STATE_ORDER` | Confirmado por código |
| navegación card → record | `InboxRecordCard` | link a `/record/{id}` | Confirmado por código |
| empty state CTA | `Go to launcher` | navega a `/` | Confirmado por código |

#### 3.4 Validación de empty states

| Caso | Qué validar | Resultado esperado | Severidad |
|---|---|---|---|
| sin resultados por filtros | empty state visible | mensaje claro, CTA legible | Alta |
| empty state con idioma alterno | eyebrow, title, description, CTA | sin crecimiento desproporcionado del bloque | Media |
| empty state dentro del shell | convivencia con top area | no sensación de pantalla saturada | Media |

#### 3.5 Validación de filtros

| Caso | Qué validar | Resultado esperado | Severidad |
|---|---|---|---|
| labels cortas y largas | `Schema`, `State`, `All schema types`, `All states` | select sigue usable | Alta |
| labels de schema | options con `schema.title` | títulos largos no vuelven torpe el control | Alta |
| labels de estado | options con `stateLabel` | se distinguen rápido | Muy alta |
| state pills | wrap y counts | no se vuelven pared de chips | Muy alta |
| query + filters activos | `Filtered view active` | feedback claro y breve | Media |

#### 3.6 Validación de cards

| Caso | Qué validar | Resultado esperado | Severidad |
|---|---|---|---|
| launcher schema cards | badges + summary + metrics + CTAs | jerarquía estable | Muy alta |
| inbox cards list | state badge, title, summary, detail list | escaneo rápido | Muy alta |
| inbox cards grid | equilibrio entre cards | grid útil, no ruidoso | Alta |
| record title largo | `truncate` | no pierde la esencia del registro | Alta |
| preview labels largas | `DetailList` | wraps tolerables sin colapso | Alta |
| summary larga | `schema.summary` | no desplaza señales clave | Alta |
| footer con fecha local | `Updated...` | mantiene densidad razonable | Media/Alta |

#### 3.7 Validación de consistencia de labels

| Caso | Qué revisar | Resultado esperado |
|---|---|---|
| launcher vs shell | `Schemas` / `Open schemas` / `Schema Playground` | criterio consistente o explicitado |
| inbox local vs states | `Submitted`, `In review`, `Needs attention` | no coexistencia confusa entre resumen y estado real |
| humanized enums | `Area`, `Preset`, `Density`, `Motion`, `Contrast` | coherencia terminológica |
| schema labels | title/summary/field labels | no mezcla de schema raw con copy UI ya localizado |
| fechas | `Updated...` | idioma consistente con el resto de la pantalla |

#### 3.8 Criterios de aceptación

Se puede considerar resuelta la fase de descubrimiento/control para launcher e inbox cuando:
- existe mapa claro de superficies, ownership y dependencias
- está separada la copy local de la copy shared/runtime/schema/data
- existe lista roja para no traducir a ciegas
- están marcados hotspots de longitud y scan speed
- existe inventario reusable por archivo
- existe una matriz de validación mínima por superficie
- están registradas señales de stop

Se puede considerar lista una futura intervención de implementación solo si además:
- no quedan ownerships dudosos sin clasificar dentro del cambio específico
- se define si shell entra o se congela explícitamente fuera
- se define si estados/runtime labels entran o se congelan fuera
- se prueba launcher e inbox en al menos `sm`, `md`, `lg` y `xl`

#### 3.9 Señales de stop

Si aparece cualquiera de estas señales durante una siguiente fase, conviene detener la ejecución y reabrir análisis:
- se intenta traducir `schema.title`, `schema.summary`, `field.label` o `stateLabel(...)` como si fueran copy local
- se quiere resolver inbox sin tocar shell pero el resultado visible sigue mezclado
- aparecen labels técnicas (`adapterId`, `category`, `accessMode`) tratadas como copy definitiva
- una traducción mejora idioma pero empeora scan speed de lanes/cards
- el sticky shell crece tanto que compite con el contenido principal
- fechas siguen en EN mientras el resto cambia a ES
- se descubre que otras superficies consumen los mismos helpers y quedan fuera del rollout

---

### Reporte 4. Hallazgos extra y qué nos deja resuelto

#### 4.1 Quick wins reales

| Quick win | Por qué sí conviene | Estado |
|---|---|---|
| Separar todo el copy local de `app/page.tsx` | es el bloque más limpio del launcher | Confirmado |
| Separar todo el copy local de `components/records/record-inbox.tsx` | concentra casi toda la narrativa del inbox | Confirmado |
| Tratar `AppShell` como dominio aparte | aparece en launcher e inbox y tiene copy persistente | Confirmado |
| Tratar `record-view.ts` como capa semántica propia | concentra states, labels y descriptions visibles | Confirmado |
| Marcar `schema-registry.ts` como fuente display de schema | evita confundirlo con copy local | Confirmado |
| Congelar por ahora `category`, `accessMode`, `adapterBindings` | hoy son los más dudosos del launcher | Confirmado |
| Congelar por ahora `formatDateTime` y `formatHumanLabel` como helpers visibles | son foco claro de mezcla localización vs humanización | Confirmado |
| Identificar `Resume / token` y `Retryable` como copy candidata a simplificación futura | semánticamente tensas y tipográficamente incómodas | Inferido fuerte |

#### 4.2 Inventario reusable por archivo

##### Matriz reusable por archivo

| Archivo | Superficie | Rol | Copy local visible | Copy no local visible | Hotspots de longitud | Hotspots de scan speed | Ownership dominante | Estado |
|---|---|---|---|---|---|---|---|---|
| `app/page.tsx` | Launcher | composición principal del home | hero, stats, section title, metric labels, CTAs | schema titles/summaries/badges, counts | hero, stat labels, schema cards, CTAs | cards y badges | Frontend + schema/data | Confirmado |
| `app/inbox/page.tsx` | Inbox | loader de ruta | none relevante | schemas + records pasan a UI | baja | baja | Data pass-through | Confirmado |
| `components/records/record-inbox.tsx` | Inbox | controller visual de queue | hero, stats, filters, summary, empty state | states humanizados, schema titles | controls, pills, summary line | muy alta por triage | Frontend + runtime/schema/data | Confirmado |
| `components/records/inbox-record-card.tsx` | Inbox | card reusable | fallback summary, prefix `Updated` | schema title/summary, state, title, fields, id, date | badge/title/summary/detail/footer | muy alta en card scanning | Mixed | Confirmado |
| `components/layout/app-shell.tsx` | Shared shell | marco global visible | nav labels, CTA labels, shell text | runtime labels y brand label | sticky title, nav, chips | alta por competencia visual | Shared + runtime | Confirmado |
| `components/ui/page-header.tsx` | Shared UI | contenedor textual | none hardcoded | recibe title/description/actions/stats | title + action row | media | Shared presentational | Confirmado |
| `components/ui/stat-card.tsx` | Shared UI | stat shell | none hardcoded | recibe label/meta/value | uppercase label + meta | media | Shared presentational | Confirmado |
| `components/ui/surface.tsx` | Shared UI | panel/section wrapper | none hardcoded | recibe title/subtitle/eyebrow/actions | depende del contenido | baja/media | Shared presentational | Confirmado |
| `components/ui/section-header.tsx` | Shared UI | encabezado de sección | none hardcoded | recibe title/description | title + action row | media | Shared presentational | Confirmado |
| `components/ui/button.tsx` | Shared UI | CTA wrapper | none hardcoded | recibe children | labels largas en sizes sm/md | alta si hay muchas acciones | Shared presentational | Confirmado |
| `components/ui/badge.tsx` | Shared UI | badge compacta | none hardcoded | recibe children | muy alta por uppercase y alto fijo | alta | Shared presentational | Confirmado |
| `components/ui/filter-pills.tsx` | Shared UI | filtros tipo tabs | aria default `Filter options` | labels y counts recibidos | muy alta | muy alta | Shared presentational | Confirmado |
| `components/ui/select.tsx` | Shared UI | dropdown | none hardcoded | options recibidas | alta con labels largas | media | Shared presentational | Confirmado |
| `components/ui/input.tsx` | Shared UI | text input | none hardcoded | placeholder recibido | media | baja/media | Shared presentational | Confirmado |
| `components/ui/state-badge.tsx` | Shared UI/domain bridge | badge de estado | none hardcoded | `stateLabel` y tono | muy alta | muy alta | Runtime/domain bridge | Confirmado |
| `components/ui/detail-list.tsx` | Shared UI | lista label/value | none hardcoded | labels/values recibidos | alta | alta | Shared presentational | Confirmado |
| `components/ui/empty-state.tsx` | Shared UI | empty block | default icons only | title/description/action recibidos | media | baja | Shared presentational | Confirmado |
| `src/lib/core/record-view.ts` | Domain helper | semántica visible del inbox | state descriptions, fallback preview `Record` | schema field labels y values procesados | alta | muy alta | Runtime/domain | Confirmado |
| `src/lib/core/schema-registry.ts` | Domain source | display source de schemas | schema titles, summaries, field labels, step/action labels | n/a | alta | media/alta | Schema-owned | Confirmado |
| `src/lib/ui/record-contracts.ts` | Helper | normalización visible | `Record {id}`, `Submission captured`, `Sync signal` | values normalizados | media | baja | Helper/domain | Confirmado |
| `src/lib/utils.ts` | Helper | formato visible | `Yes/No`, locale `en`, humanized labels | n/a | media/alta | media | Runtime/helper | Confirmado |
| `src/lib/ui/runtime.ts` | Runtime | define labels base por area/preset/density | brand labels | runtime values humanizados luego | media | media | Runtime | Confirmado |
| `app/layout.tsx` | Root | metadata/lang | title, description, `lang=en` | n/a | baja | baja | Shared root | Confirmado |
| `app/globals.css` | Shared style | densidad/clases de lectura | none textual | estilos que amplifican riesgos | muy alta en compact UI | muy alta | Shared styling | Confirmado |

#### 4.3 Matriz maestra sugerida para seguir inventariando

Usar esta matriz como plantilla para continuar con otras superficies:

| Archivo | Ruta/superficie | Rol en la UI | Textos locales visibles | Textos recibidos de otra capa | Dependencias visibles | Ownership preliminar | Riesgo de longitud | Riesgo de scan speed | Riesgo semántico | Confirmado / Inferido / Dudoso | Nota de validación |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | bajo/medio/alto | bajo/medio/alto | bajo/medio/alto |  |  |

#### 4.4 Artefactos sugeridos

Sin proponer implementación final todavía, este chat deja sugeridos estos artefactos de trabajo siguientes:
- inventario de copy local `launcher.*`
- inventario de copy local `inbox.*`
- mapa separado de `shell.*`
- inventario de `record-state.*` o dominio equivalente para estados/descripciones
- inventario de `schemas.<id>.*` o estrategia equivalente para schema display strings
- mapa de helpers visibles (`formatDateTime`, `formatHumanLabel`, `formatValue`)
- checklist visual mínimo por viewport
- checklist de scan speed para inbox list/grid

#### 4.5 Decisiones que conviene congelar

Estas decisiones conviene congelarlas antes de una siguiente fase, porque destraban mucho y evitan pasos falsos:

1. **Si shell entra en el mismo rollout o se congela aparte**
2. **Si estados del inbox se tratarán como dominio propio y no como copy local**
3. **Si `schema-registry.ts` se considera fuente display temporal o definitiva**
4. **Si `formatHumanLabel` seguirá existiendo como fallback visible o se reemplazará por labels controladas**
5. **Si `formatDateTime("en")` entra en alcance inmediato o se congela aparte**
6. **Qué hacer con labels tensas como `Retryable`, `Resume / token`, `Outbound adapter`**
7. **Si `category`, `accessMode` y `adapterBindings.outbound` se ocultan, mapean o se dejan sin tocar por ahora**

#### 4.6 Preguntas abiertas reales

| Pregunta | Por qué importa | Estado |
|---|---|---|
| ¿Shell se interviene junto con launcher/inbox o se trata como frente aparte? | ambos screens ya lo muestran | Abierta |
| ¿Los estados del inbox deben vivir en un dominio propio o seguir en helper humanizado? | define ownership y riesgo de mezcla | Abierta |
| ¿`schema-registry.ts` es solo ejemplo semilla o es fuente de display real del template? | cambia el tratamiento de titles/summaries/field labels | Abierta |
| ¿`formatHumanLabel` debe seguir mostrándose en UI final? | hoy humaniza pero no localiza | Abierta |
| ¿`formatDateTime` con locale fijo `en` entra ya en frente idioma? | si no, habrá mezcla visible | Abierta |
| ¿Qué terminología se congela para `Schemas / Playground / Flows`? | hoy hay duplicidad conceptual | Abierta |
| ¿Quick triage privilegia densidad operativa sobre literalidad? | afecta decisiones de copy futura | Inferida como importante |

#### 4.7 Qué nos deja resuelto este chat

Este chat deja resuelta la fase de **mapeo, clasificación y control previo** para **launcher/home** e **inbox** usando el ZIP como fuente principal de verdad y el formato universal como puerta de análisis.

Queda despejado:
- qué archivos realmente gobiernan launcher e inbox
- qué copy visible sí es local y cuál no
- qué piezas visibles dependen de schema, runtime, helpers o data
- dónde están los hotspots de longitud
- dónde están los hotspots de scan speed
- qué no se debe traducir a ciegas
- qué validaciones mínimas necesita cualquier intervención futura
- cómo seguir inventariando otras superficies con la misma matriz

En términos prácticos, después de este chat ya no estás entrando a launcher e inbox con radar apagado. Ya quedó separado el copy limpio del cableado semántico y del material inflamable. Eso no implementa i18n todavía, pero sí quita la parte más cara de la niebla.

**Qué nos deja resuelto este chat**
- launcher e inbox quedan **mapeados y acotados**
- el shell visible queda **identificado como dependencia transversal real**
- el ownership queda **separado entre local, shared, runtime, schema y data**
- la lista roja queda **lista para evitar traducción ciega**
- el inventario reusable por archivo queda **establecido como patrón para continuar**
- la siguiente fase puede enfocarse en **extracción, estrategia de claves o rollout**, ya con menos riesgo de mezclar capas o romper scan speed
## 🧪 Flow runner, schema text y coupling con validation/state

**Archivo fuente consolidado:** `flow_runner_controlled_intervention_report(1).md`

### Reporte 1. Mapa y alcance

**Base obligatoria usada**
- **Fuente principal de verdad:** el zip real del proyecto, inspeccionado directamente en `app/flow/[schemaId]/page.tsx`, `components/flow/flow-runner.tsx`, `src/lib/core/schema-registry.ts`, `src/lib/core/validation.ts`, `src/lib/core/state.ts`, `src/lib/core/record-view.ts`, `src/lib/services/records.ts`, `src/lib/request-context.ts`, `src/lib/utils.ts`, `components/ui/state-badge.tsx` y rutas API relacionadas.
- **Marco de control:** el Formato Universal de Pre-Intervención y Rastreabilidad, aplicado aquí como ficha de pre-intervención: resumen ejecutivo, alcance, ownership, lista roja, riesgos, validación, señales de stop y artefactos.

**Leyenda de certeza**
- **[Confirmado]** leído directo del código.
- **[Inferido]** deducción razonable por acoplamiento visible.
- **[Dudoso]** no debe tocarse sin resolver ownership o contrato.

#### Resumen ejecutivo

##### Qué cubre este mapeo
- La superficie visible del flow en `app/flow/[schemaId]/page.tsx:35-81` y `components/flow/flow-runner.tsx:107-554`.
- El texto schema-driven que entra al flow desde `src/lib/core/schema-registry.ts:20-321`.
- El coupling de copy visible con `validation`, `state`, `record-view`, `records service`, `request-context`, `utils` y rutas API.
- Las fugas semánticas donde un string deja de ser solo UI y se vuelve dato persistido, estado, error operativo o señal de runtime.

##### Riesgos principales detectados
1. **El flow mezcla copy local con semántica real**: schema, validation, state y backend conviven en la misma superficie.
2. **Attachments ya no son solo UI**: el runner convierte `FileList` a texto (`"n attachment(s)"`) y lo manda a persistencia como `fields` del record. [Confirmado] `components/flow/flow-runner.tsx:75-83`, `181-186`, `165`; `src/lib/services/records.ts:52-91`, `107-145`; `src/lib/store/memory-store.ts:37-52`, `89-101`; `src/lib/store/prisma-store.ts:176-195`.
3. **Access mode y allowDrafts hoy son display-only**: se muestran, pero no se aplican como control real en el flow. [Confirmado] `app/flow/[schemaId]/page.tsx:41-43`; referencias totales en búsqueda: `accessMode` solo se renderiza en UI y no se usa para enforcement, `allowDrafts` solo aparece en schema/types/UI.
4. **Resume token sirve para lookup inicial, no para persistencia posterior**: el flow reanuda con token server-side, pero luego guarda por `recordId` vía `/api/records/[recordId]`, no por token. [Confirmado] `app/flow/[schemaId]/page.tsx:31`; `components/flow/flow-runner.tsx:190-218`; `app/api/records/token/[token]/route.ts:20-63` existe pero el runner no la usa.
5. **Cliente y servidor no validan con el mismo rol**: el cliente valida como `external_user`, el servidor toma el actor desde headers y sin headers cae a `public`. [Confirmado] `components/flow/flow-runner.tsx:173`; `src/lib/request-context.ts:5-19`; no hay envío de `x-actor-role` en el flow runner.
6. **Save/submit + upload no son transaccionales**: el record puede crearse o actualizarse antes de que fallen attachments. [Confirmado] `components/flow/flow-runner.tsx:189-236`.

##### Qué deja resuelto este mapeo
- Separa qué copy sí es local del runner/page y qué ya pertenece a schema, validation, state o backend.
- Deja una lista roja seria para no traducir donde todavía no hay ownership confirmado.
- Hace visible dónde un string deja de ser solo copy y contamina persistencia, timeline o errores operativos.
- Despeja una **primera ola segura** de cambios y deja bloqueadas las zonas que necesitan contrato previo.

#### Alcance y no alcance

##### Entra en esta intervención
- Shell de `app/flow/[schemaId]/page.tsx`.
- Flow runner completo: progreso, steps, CTAs, fields, hints, notices, sidebar, safety panel.
- Texto schema-driven visible al usuario desde `schema-registry`.
- Coupling con `validation`, `state`, `record-view`, `records service`, `request-context`, `utils` y API routes.
- Riesgos de attachments, transitions, save/submit y resume token.

##### No entra todavía
- Implementación final de i18n.
- Refactor final de contracts o persistencia.
- Normalización definitiva de errores backend.
- Estrategia completa de localización de schema.
- Estrategia completa de localización de state semantics.
- Refactor general de inbox/detail/sync fuera de lo estrictamente necesario para evidenciar coupling.

##### Condiciones de corte
- Si un string aparentemente de UI resulta venir de `schema`, `validation`, `record-view`, `records service`, `store` o API.
- Si una intervención toca persistencia (`fields`, `submission.payload`, `sync summary`, `attachment metadata`) sin contrato explícito.
- Si aparece una dependencia de `accessMode`, `allowDrafts`, `recordState` o token como semántica real.

#### Mapa del flow

#### 1) Ruta y dependencias visibles

| Superficie | Responsabilidad visible | Dependencias directas | Evidencia |
|---|---|---|---|
| `app/flow/[schemaId]/page.tsx` | Shell del flow, header, resumen de access/steps/drafts, panel de resume token | `getSchema`, `getRecordByToken`, `PageHeader`, `Surface`, `Input`, `Button`, `FlowRunner` | `page.tsx:10-11`, `20-31`, `35-81` |
| `components/flow/flow-runner.tsx` | Runner principal, progreso, steps, render de fields, save/submit, resumen lateral y panel de seguridad | `getFieldById`, `stateDescription`, `validateStepPayload`, `isFieldVisible`, `formatRelativeTime`, `StateBadge` | `flow-runner.tsx:19-31`, `86-554` |
| `src/lib/core/schema-registry.ts` | Define títulos, descripciones, labels, placeholders, options, helpText, accessMode, allowDrafts, steps y detailSections | `RecordTypeSchema`, `FieldDefinition`, `StepDefinition` | `schema-registry.ts:20-321` |
| `src/lib/core/validation.ts` | Produce errores visibles y shape de validación por step | `getFieldById`, `isFieldVisible`, zod | `validation.ts:7-90` |
| `src/lib/core/record-view.ts` | Produce label y descripción del estado visibles en flow/detail/inbox | `formatHumanLabel`, schema preview helpers | `record-view.ts:19-64` |
| `src/lib/core/state.ts` | Define transiciones válidas y disponibilidad de acciones | `RecordState`, `ActionDefinition`, `ActorContext` | `state.ts:8-46` |
| `src/lib/services/records.ts` | create/update/get por token/id, validación server-side, título fallback, secure token, sync summaries | `getSchema`, `canTransition`, `validateStepPayload`, `randomToken`, store | `records.ts:18-169` |
| API routes | Propagan errores visibles y conectan runner con services | `POST /api/records`, `PATCH /api/records/[recordId]`, `POST /attachments`, `GET/PATCH /token/[token]` | rutas API inspeccionadas |
| `src/lib/utils.ts` | Formateo visible de tiempo relativo y etiquetas humanas | `Intl.RelativeTimeFormat("en")`, `formatDateTime("en")` | `utils.ts:8-48` |

#### 2) Zonas de UI del page shell

| Zona | Texto / señal visible | Source real | Estado |
|---|---|---|---|
| Eyebrow | `Flow runner` | literal local | [Confirmado] frontend local. `page.tsx:35-38` |
| Title | ``${schema.title} intake flow`` | `schema.title` + sufijo local | [Confirmado] mezcla UI local + schema. `page.tsx:37` |
| Description | `A guided, lower-friction runner...` | literal local | [Confirmado]. `page.tsx:38` |
| Header chip | `Access: {schema.flow.accessMode}` | enum de schema | [Confirmado] texto UI local + valor semántico. `page.tsx:41` |
| Header chip | `Steps: {schema.flow.steps.length}` | conteo de schema | [Confirmado]. `page.tsx:42` |
| Header chip | `Drafts: enabled/disabled` | `schema.flow.allowDrafts` + copy local | [Confirmado]. `page.tsx:43` |
| CTA | `New session` | literal local | [Confirmado]. `page.tsx:48-52` |
| CTA | `Open inbox` | literal local | [Confirmado]. `page.tsx:54-58` |
| Surface title | `Resume an existing session` | literal local | [Confirmado]. `page.tsx:64` |
| Surface subtitle | `Paste a secure token...` | literal local | [Confirmado]. `page.tsx:64` |
| Field label | `Resume token` | literal local | [Confirmado]. `page.tsx:66-68` |
| Placeholder | `ext_xxx` | convención técnica visible | [Confirmado] técnico/dudoso. `page.tsx:68` |
| CTA | `Resume with token` | literal local | [Confirmado]. `page.tsx:71-73` |
| CTA | `Clear` | literal local | [Confirmado]. `page.tsx:74-76` |

#### 3) Zonas de UI del flow runner

##### 3.1 Fallback / config issue
| Zona | Texto | Source | Estado |
|---|---|---|---|
| Fatal surface | `Flow configuration issue` | literal local | [Confirmado]. `flow-runner.tsx:107-112` |
| Fatal message | `No steps configured for this schema.` | literal local | [Confirmado]. `flow-runner.tsx:109-110` |

##### 3.2 Progreso y header del step
| Zona | Texto / señal visible | Source | Estado |
|---|---|---|---|
| Step eyebrow | `Step X of Y` | local + schema length | [Confirmado]. `flow-runner.tsx:260` |
| Step title | `activeStep.title` | schema step | [Confirmado]. `flow-runner.tsx:261`; `schema-registry.ts:32-45`, `144-155`, `237-249` |
| Step description | `activeStep.description` | schema step | [Confirmado]. `flow-runner.tsx:262` |
| State badge | `StateBadge(state)` | `stateLabel()` / `stateTone()` | [Confirmado]. `flow-runner.tsx:266`; `state-badge.tsx:27-34`; `record-view.ts:19-40` |
| Percent complete | `N% complete` | cálculo local | [Confirmado]. `flow-runner.tsx:267-269` |
| Progress bar | ancho animado | cálculo local | [Confirmado]. `flow-runner.tsx:321-326` |

##### 3.3 Steps / step pills
| Zona | Texto / señal visible | Source | Estado |
|---|---|---|---|
| Step pill title | `entry.step.title` | schema | [Confirmado]. `flow-runner.tsx:312` |
| Step pill status | `Ready` | local | [Confirmado]. `flow-runner.tsx:278-281` |
| Step pill status | `Not started` | local | [Confirmado]. `flow-runner.tsx:279-281` |
| Step pill status | `x/y required` | local + required summary | [Confirmado]. `flow-runner.tsx:282` |
| Step navigation | click en pill cambia `stepIndex` | local | [Confirmado]. `flow-runner.tsx:285-289` |

##### 3.4 Errores y notices visibles
| Zona | Texto / patrón | Source | Estado |
|---|---|---|---|
| Notice danger | `Check the highlighted fields before continuing.` | runner local | [Confirmado]. `flow-runner.tsx:173-178` |
| Notice success | `Draft saved successfully.` | runner local | [Confirmado]. `flow-runner.tsx:223-226` |
| Notice success | `Submission sent successfully.` | runner local | [Confirmado]. `flow-runner.tsx:223-226` |
| Notice danger fallback | `Unexpected error while saving.` | runner local | [Confirmado]. `flow-runner.tsx:228-232` |
| Notice danger propagated | `error.message` | backend/service/validation propagated | [Confirmado]. `flow-runner.tsx:228-232` |
| Global count warning | `N field(s) need attention before this step can continue.` | runner local | [Confirmado]. `flow-runner.tsx:343-346` |
| Inline field error | `errors[field.id]` | validation | [Confirmado]. `flow-runner.tsx:455`; `validation.ts:70-80` |

##### 3.5 Fields y agrupación
| Zona | Texto / señal visible | Source | Estado |
|---|---|---|---|
| Field label | `field.label` | schema | [Confirmado]. `flow-runner.tsx:369` |
| Required badge | `Required` | local, activado por `field.required` | [Confirmado]. `flow-runner.tsx:370` |
| Help text | `field.helpText` | schema | [Confirmado]. `flow-runner.tsx:372` |
| Placeholder | `field.placeholder` | schema | [Confirmado]. `flow-runner.tsx:379`, `439`, `451` |
| Select prompt | `Select...` | local | [Confirmado]. `flow-runner.tsx:383` |
| Select option | `option` | schema | [Confirmado]. `flow-runner.tsx:384-387` |
| Checkbox state title | `Enabled` / `Disabled` | local | [Confirmado]. `flow-runner.tsx:402-403` |
| Checkbox help | `Use this toggle only when the step requires it.` | local | [Confirmado]. `flow-runner.tsx:403` |
| File prompt | `Add supporting files when needed.` | local | [Confirmado]. `flow-runner.tsx:416-419` |
| File selected count | `N file(s) selected` | local calculado | [Confirmado]. `flow-runner.tsx:421-429` |
| Persisted file summary | string mostrado cuando `value` ya es string | valor persistido | [Confirmado]. `flow-runner.tsx:430-431` |

##### 3.6 CTAs / footer operativo
| Zona | Texto | Source | Estado |
|---|---|---|---|
| Footer title | `One clear next move` | local | [Confirmado]. `flow-runner.tsx:463-468` |
| Footer helper | `Save progress as a draft...` | local + `nextStepTitle` schema | [Confirmado]. `flow-runner.tsx:467-469` |
| CTA | `Back` | local | [Confirmado]. `flow-runner.tsx:473-480` |
| CTA | `Save Draft` | local | [Confirmado]. `flow-runner.tsx:481-484` |
| CTA | `Save and Continue` | local | [Confirmado]. `flow-runner.tsx:485-489` |
| CTA | `Submit for Review` | local | [Confirmado]. `flow-runner.tsx:490-494` |

##### 3.7 Sidebar / summary / safety
| Zona | Texto / señal visible | Source | Estado |
|---|---|---|---|
| Surface title | `Session summary` | local | [Confirmado]. `flow-runner.tsx:501-502` |
| Surface subtitle | `Keep the essentials visible...` | local | [Confirmado]. `flow-runner.tsx:502` |
| Stat label | `Progress` | local | [Confirmado]. `flow-runner.tsx:504` |
| Stat meta | `Step X of Y` | local + schema length | [Confirmado]. `flow-runner.tsx:504` |
| Stat label | `Required remaining` | local | [Confirmado]. `flow-runner.tsx:505` |
| Stat meta | `Open required inputs still missing across the flow.` | local | [Confirmado]. `flow-runner.tsx:505` |
| Panel label | `Current state` | local | [Confirmado]. `flow-runner.tsx:507` |
| Value | `StateBadge(state)` | state semantics | [Confirmado]. `flow-runner.tsx:508` |
| Description | `stateDescription(recordState)` | state semantics | [Confirmado]. `flow-runner.tsx:509`; `record-view.ts:42-64` |
| Panel label | `Record id` | local | [Confirmado]. `flow-runner.tsx:512` |
| Placeholder text | `Created after the first save.` | local | [Confirmado]. `flow-runner.tsx:513` |
| Panel label | `Resume token` | local | [Confirmado]. `flow-runner.tsx:516` |
| Placeholder text | `Generated once the record is first saved.` | local | [Confirmado]. `flow-runner.tsx:517` |
| Panel label | `Last save` | local | [Confirmado]. `flow-runner.tsx:520` |
| Value | `formatRelativeTime(lastSavedAt)` | shared formatter | [Confirmado]. `flow-runner.tsx:521`; `utils.ts:18-42` |
| Placeholder text | `Not saved yet.` | local | [Confirmado]. `flow-runner.tsx:521` |
| Surface title | `Why this feels safe` | local | [Confirmado]. `flow-runner.tsx:526` |
| Surface subtitle | `A few cues...` | local | [Confirmado]. `flow-runner.tsx:526` |
| Card title | `Inline validation` | local | [Confirmado]. `flow-runner.tsx:531` |
| Card body | `Required fields are checked...` | local, pero describe validation real | [Confirmado]. `flow-runner.tsx:532` |
| Card title | `Resume token` | local | [Confirmado]. `flow-runner.tsx:538` |
| Card body | `A secure token appears...` | local, pero describe token real | [Confirmado]. `flow-runner.tsx:539` |
| Card title | `Clear next action` | local | [Confirmado]. `flow-runner.tsx:545` |
| Card body | `The footer keeps draft save...` | local | [Confirmado]. `flow-runner.tsx:546` |

#### 4) Progreso: cómo se calcula de verdad

| Elemento | Source real | Observación |
|---|---|---|
| `visibleFieldIds` | `isFieldVisible(field, values, "external_user")` | [Confirmado] el progreso depende de visibilidad calculada, no solo de fieldIds. `flow-runner.tsx:48-53` |
| required total por step | `field.required` del schema | [Confirmado]. `flow-runner.tsx:55-67` |
| complete por step | required completos o, si no hay required, todos los visibles con valor | [Confirmado]. `flow-runner.tsx:57-65` |
| step inicial | primer step incompleto | [Confirmado]. `flow-runner.tsx:69-72` |
| progress global | suma ponderada por required | [Confirmado]. `flow-runner.tsx:118-128` |
| required remaining | suma global de faltantes | [Confirmado]. `flow-runner.tsx:118`, `505` |

**Implicación:** el progreso es **UI-local calculado**, pero depende de semántica de schema/visibility/required, así que no conviene traducir o reescribir copy de progreso sin respetar esa semántica.

#### 5) Attachments

| Punto | Qué pasa | Evidencia |
|---|---|---|
| Visibilidad del file field | depende de `visibleWhen` en schema | `schema-registry.ts:69-75`, `265-270`; `visibility.ts:21-33` |
| Selección en cliente | el value se guarda como `FileList` | `flow-runner.tsx:420` |
| Serialización previa al save | `FileList` se convierte a `"n attachment(s)"` | `flow-runner.tsx:75-83` |
| Payload de create/update | se manda `fields: persistableValues` | `flow-runner.tsx:181-186`, `208-212` |
| Upload real | ocurre **después** de crear/actualizar record | `flow-runner.tsx:189-218` |
| Tras upload | el estado local del field también se reemplaza por `"n attachment(s)"` | `flow-runner.tsx:165` |
| Persistencia del record | `fields` se guardan tal cual | `memory-store.ts:45`, `92-95`; `prisma-store.ts:182`, `30-32` |
| Metadata de attachments | va a tabla/lista separada | `records.ts:147-168`; `attachments route:34-41`; `memory-store.ts:141-160` |

**Conclusión de attachments:**
- [Confirmado] hay **doble representación**: un string resumido en `record.fields[fieldId]` y una lista estructurada en attachments.
- [Confirmado] el string `"n attachment(s)"` ya no es copy inocente. Es persistencia.
- [Confirmado] si upload falla después del create/update, el record puede quedar creado/actualizado y aun así mostrar error al usuario.

#### 6) Resume token

| Punto | Qué pasa | Evidencia |
|---|---|---|
| Lookup inicial | `page.tsx` usa `getRecordByToken(query.token)` server-side | `page.tsx:31` |
| Token inválido en page | no se muestra error; solo `initialRecord = null` | [Confirmado] no hay rama de error visible en `page.tsx:20-81` |
| API token route existe | `GET/PATCH /api/records/token/[token]` | `app/api/records/token/[token]/route.ts:10-63` |
| El runner no usa token route para guardar | usa `/api/records` y `/api/records/[recordId]` | `flow-runner.tsx:191-218` |
| Secure token se genera al crear record | `randomToken("ext")` | `records.ts:71`; `utils.ts:79-82` |

**Conclusión de resume token:**
- [Confirmado] el token está integrado como **lookup inicial** y como dato visible en sidebar/page.
- [Confirmado] el token **no es** el canal de persistencia posterior del flow runner actual.
- [Inferido] si el objetivo era un flujo realmente token-driven de extremo a extremo, hoy el contrato está incompleto.

#### 7) CTAs y transitions

| CTA / operación | Semántica real | Evidencia |
|---|---|---|
| `Save Draft` | `persist(false)`; crea o actualiza record sin submit | `flow-runner.tsx:169-236`, `481-484` |
| `Save and Continue` | `persist(false)` y luego incrementa `stepIndex` | `flow-runner.tsx:239-245`, `486-489` |
| `Submit for Review` | `persist(true)` y luego `setRecordState("submitted")` | `flow-runner.tsx:247-252`, `491-494` |
| En server create | `submit ? "submitted": "draft"` | `records.ts:67-74` |
| En server update | valida `canTransition(existing.state, request.state)` | `records.ts:118-120`; `state.ts:10-29` |
| `Back` | solo UI local, no persiste | `flow-runner.tsx:473-480` |

**Hallazgo crítico:**
- [Confirmado] `schema.flow.allowDrafts` se muestra en header (`page.tsx:43`) pero **no** controla la aparición o disponibilidad de `Save Draft` en el runner (`flow-runner.tsx:481-484`).

#### 8) Errores visibles y de dónde vienen

| Mensaje visible | Source real | Capa |
|---|---|---|
| `Required` | `validation.ts:78-80` | validation |
| `Must be a number` | `validation.ts:10-13` | validation |
| `Invalid value` | `validation.ts:73` fallback | validation |
| `Unknown step 'x'` | `validation.ts:51-58` | validation/schema |
| `Validation failed: {...}` | `records.ts:53-55`, `114-116` | service -> API -> UI propagated |
| `Record creation failed` | `flow-runner.tsx:197`, `api/records/route.ts:47-53` | backend/service propagation |
| `Record update failed` | `flow-runner.tsx:215`, `api/records/[recordId]/route.ts:53-59` | backend/service propagation |
| `Attachment upload failed` | `flow-runner.tsx:160-161`, `attachments route.ts:42-48` | backend/service propagation |
| `Token not found` | `api/records/token/[token]/route.ts:12-25` | backend/API |
| `Record not found` | `api/records/[recordId]/route.ts:13-15` | backend/API |
| `Missing file` | `attachments route.ts:21-24` | backend/API |
| `Invalid transition from...` | `records.ts:118-120` | state/service |

#### 9) Dependencias visibles que afectan el flow

| Dependencia | Impacto en texto / comportamiento visible | Evidencia |
|---|---|---|
| `schema-registry` | define títulos, descripciones, labels, placeholders, options, helpText, accessMode, allowDrafts | `schema-registry.ts:20-321` |
| `validation` | define mensajes de required, number, invalid, unknown step | `validation.ts:7-90` |
| `record-view` | define label y descripción de state visibles en flow/detail/inbox | `record-view.ts:19-64` |
| `state.ts` | define transiciones válidas y errores por transición inválida | `state.ts:10-29` |
| `records service` | define secure token, title fallback, create/update semantics, sync summaries | `records.ts:18-169` |
| `request-context` | define rol server-side desde headers; default `public` | `request-context.ts:5-29` |
| `utils` | hardcodea locale `en` para tiempo relativo y datetime | `utils.ts:8-42` |
| `state-badge` | shared wrapper para `stateLabel` y `stateTone` | `state-badge.tsx:27-34` |

#### 10) Fuentes de texto

##### A. Texto local del page / runner
- Confirmado en `page.tsx:35-79` y `flow-runner.tsx:107-554`.
- Incluye shell copy, CTAs, helper copy, notices locales, labels del summary y safety panel.

##### B. Texto schema-driven visible en el flow

###### `service_request`
- **Schema / flow titles:** `Service Request`, `Service Request Flow`.
- **Step titles/descriptions:** `Requester`, `Who is submitting and what is needed?`, `Context`, `Add timing and optional supporting files.`
- **Field labels/placeholders/help/options:** `Title`, `Request title`, `Description`, `Describe the request, context and expected outcome`, `Priority`, options `low/medium/high/urgent`, `Requester name`, `Requester email`, `Required by`, `Region`, options `north/south/east/west/global`, `Needs attachment`, `Attachments`, `Optional files for additional context.`
- **Detail section titles:** `Summary`, `Requester`, `Delivery`.
- Evidencia: `schema-registry.ts:20-129`.

###### `approval_packet`
- **Schema / flow titles:** `Approval Packet`, `Approval Packet Flow`.
- **Step titles/descriptions:** `Packet`, `Provide packet context.`, `Decision Inputs`, `Complete mandatory checklist before decision.`
- **Field labels/options:** `Packet title`, `Owner`, `Scope`, `Due date`, `Risk level`, options `low/moderate/high`, `Compliance reviewed`, `Decision notes`.
- **Detail section titles:** `Packet`, `Decision Inputs`.
- Evidencia: `schema-registry.ts:132-223`.

###### `inspection_checklist`
- **Schema / flow titles:** `Field Inspection Checklist`, `Inspection Checklist Flow`.
- **Step titles/descriptions:** `Inspection Meta`, `Where and when was this inspection made?`, `Checks`, `Capture condition and findings.`
- **Field labels/options:** `Site name`, `Inspector`, `Inspection date`, `Inspection type`, options `routine/incident/commissioning/closure`, `Condition score`, `Requires follow-up`, `Findings`, `Photo attachments`.
- **Detail section titles:** `Inspection Meta`, `Checks & Findings`.
- Evidencia: `schema-registry.ts:225-319`.

##### C. Texto de validation
- `Must be a number`, `Invalid value`, `Required`, `Unknown step 'x'`.
- Evidencia: `validation.ts:10-13`, `73`, `79`, `56`.

##### D. Texto de state / record-view
- Labels: derivados por `formatHumanLabel(state)` como `Draft`, `In Review`, `Awaiting Update`, etc.
- Descriptions: `Collecting inputs before submission.`, `Waiting for reviewer triage.`, `Needs another external update.`, etc.
- Evidencia: `record-view.ts:38-64`; `utils.ts:44-48`.

##### E. Texto propagado desde service / API
- `Validation failed:...`, `Record creation failed`, `Record update failed`, `Attachment upload failed`, `Record not found`, `Token not found`, `Missing file`, `Invalid transition from...`.
- Evidencia: `records.ts:52-55`, `113-120`; rutas API inspeccionadas.

---

### Reporte 2. Ownership, lista roja y riesgos

#### Matriz 1. Frontend-owned

| Elemento | Estado | Evidencia | Nota |
|---|---|---|---|
| `Flow runner` | [Confirmado] | `page.tsx:35-38` | Copy local puro |
| Header description del page | [Confirmado] | `page.tsx:38` | Copy local puro |
| `New session`, `Open inbox` | [Confirmado] | `page.tsx:48-58` | Copy local puro |
| `Resume an existing session`, `Paste a secure token...`, `Resume token`, `Resume with token`, `Clear` | [Confirmado] | `page.tsx:64-76` | Copy local puro, aunque describa token real |
| `Flow configuration issue`, `No steps configured for this schema.` | [Confirmado] | `flow-runner.tsx:107-112` | Local |
| `Check the highlighted fields before continuing.` | [Confirmado] | `flow-runner.tsx:173-178` | Local |
| `Draft saved successfully.`, `Submission sent successfully.` | [Confirmado] | `flow-runner.tsx:223-226` | Local |
| `Unexpected error while saving.` | [Confirmado] | `flow-runner.tsx:228-232` | Local fallback |
| `Ready`, `Not started`, `Select...` | [Confirmado] | `flow-runner.tsx:278-283`, `383` | Local |
| `Enabled`, `Disabled`, `Use this toggle only when the step requires it.` | [Confirmado] | `flow-runner.tsx:402-403` | Local |
| `Add supporting files when needed.` | [Confirmado] | `flow-runner.tsx:416-419` | Local |
| `One clear next move` + helper text base | [Confirmado] | `flow-runner.tsx:466-469` | Local, pero el helper incrusta `nextStepTitle` del schema |
| `Back`, `Save Draft`, `Save and Continue`, `Submit for Review` | [Confirmado] | `flow-runner.tsx:473-494` | Copy local |
| `Session summary`, `Why this feels safe` y copy interno de ambos paneles | [Confirmado] | `flow-runner.tsx:501-549` | Local |
| `Created after the first save.`, `Generated once the record is first saved.`, `Not saved yet.` | [Confirmado] | `flow-runner.tsx:513`, `517`, `521` | Local |

#### Matriz 2. Shared-owned

| Elemento | Estado | Evidencia | Nota |
|---|---|---|---|
| `formatRelativeTime(lastSavedAt)` | [Confirmado] | `flow-runner.tsx:521`; `utils.ts:18-42` | El string final visible depende de helper compartido y locale hardcodeado `en` |
| `StateBadge` como wrapper UI | [Confirmado] | `state-badge.tsx:27-34` | El wrapper es shared, pero el label real no es suyo; viene de `record-view` |
| `formatHumanLabel(state)` | [Confirmado] | `record-view.ts:38-40`; `utils.ts:44-48` | Shared helper usado para labels de estado |

#### Matriz 3. Runtime-owned

| Elemento | Estado | Evidencia | Nota |
|---|---|---|---|
| Ningún string visible del flow quedó confirmado como **puramente** runtime-owned | [Confirmado] | revisión de `page.tsx`, `flow-runner.tsx`, `PageHeader`, `Surface`, `StatCard` | Hay componentes runtime/shared, pero los strings del flow que muestran hoy se originan como local, schema, validation, state o backend |

#### Matriz 4. Schema-owned

| Elemento | Estado | Evidencia | Nota |
|---|---|---|---|
| `schema.title` | [Confirmado] | `page.tsx:37`; `schema-registry.ts:22`, `134`, `227` | Visible en title del page |
| `activeStep.title`, `entry.step.title` | [Confirmado] | `flow-runner.tsx:261`, `312`; `schema-registry.ts:32-45`, `144-155`, `237-249` | Visible directamente |
| `activeStep.description` | [Confirmado] | `flow-runner.tsx:262` | Visible directamente |
| `field.label` | [Confirmado] | `flow-runner.tsx:369` | Visible directamente |
| `field.helpText` | [Confirmado] | `flow-runner.tsx:372`; `schema-registry.ts:73` | Visible directamente |
| `field.placeholder` | [Confirmado] | `flow-runner.tsx:379`, `439`, `451`; `schema-registry.ts:48-55` | Visible directamente |
| `field.options[]` | [Confirmado] | `flow-runner.tsx:384-387`; `schema-registry.ts:57-67`, `163-167`, `255-260` | Visible directamente |
| `field.required`, `visibleWhen` | [Confirmado] | `flow-runner.tsx:55-65`, `370`; `visibility.ts:21-33` | No son copy, pero mandan progreso, required y render |
| `schema.flow.accessMode`, `schema.flow.allowDrafts`, `schema.flow.steps.length` | [Confirmado] | `page.tsx:41-43` | Se muestran en UI y expresan semántica real |

#### Matriz 5. Backend-owned

| Elemento | Estado | Evidencia | Nota |
|---|---|---|---|
| `error.message` propagado a notice | [Confirmado] | `flow-runner.tsx:228-232` | La UI final puede mostrar texto de services/API tal cual |
| `Validation failed:...` | [Confirmado] | `records.ts:52-55`, `113-116` | Service -> API -> UI |
| `Record creation failed`, `Record update failed` | [Confirmado] | `flow-runner.tsx:197`, `215`; rutas API | Fallback/back-propagation |
| `Attachment upload failed`, `Missing file` | [Confirmado] | `flow-runner.tsx:160-161`; `attachments route.ts:21-24`, `42-46` | Backend/API |
| `Record not found`, `Token not found` | [Confirmado] | rutas API correspondientes | Backend/API |
| `secureToken` visible y generado server-side | [Confirmado] | `records.ts:71`; `utils.ts:79-82` | No es copy, es dato operativo |
| title fallback `${schema.title} YYYY-MM-DD` | [Confirmado] | `records.ts:59-66` | String visible potencial, generado server-side |
| sync summaries: `Record submitted from external flow`, `Draft created`, `Record updated from external flow`, `Attachment metadata added` | [Confirmado] | `records.ts:84-90`, `138-144`, `159-166` | No se muestran en el runner, pero sí en superficies conectadas |

#### Matriz 6. Dudoso

| Elemento | Estado | Evidencia | Por qué queda dudoso |
|---|---|---|---|
| `Access: {accessMode}` | [Confirmado] | `page.tsx:41` | El copy `Access:` es local, pero el valor mostrado es semántica real; no traducir a ciegas |
| `Drafts: enabled/disabled` | [Confirmado] | `page.tsx:43` | Describe capacidad real, no solo copy |
| `ext_xxx` | [Confirmado] | `page.tsx:68` | Placeholder técnico/branding de token |
| `N% complete`, `Step X of Y`, `Required remaining`, `x/y required` | [Confirmado] | `flow-runner.tsx:260`, `267-269`, `282`, `504-505` | Copy local, pero dependiente de semántica schema/visibility/required |
| `Current state` + `stateDescription()` | [Confirmado] | `flow-runner.tsx:507-509` | Mezcla label local con catálogo de estado |
| `Resume token` como concepto visible repetido | [Confirmado] | `page.tsx:67`; `flow-runner.tsx:516`; `flow-runner.tsx:538` | Parece copy local, pero también expresa contrato técnico real |
| `N attachment(s)` y `N file(s) selected` | [Confirmado] | `flow-runner.tsx:79`, `165`, `423`, `430-431` | Una parte es UI, otra ya es persistencia |
| `allowDrafts` y `accessMode` como display-only | [Confirmado] | búsquedas globales | Si se traduce o remapea sin contrato, maquilla semántica no aplicada |

#### Capas semánticas transversales que no conviene falsear

| Capa | Elementos | Evidencia |
|---|---|---|
| Validation-owned | `Required`, `Must be a number`, `Invalid value`, `Unknown step 'x'` | `validation.ts:10-13`, `56`, `73`, `79` |
| State-owned | label y descripción del estado | `record-view.ts:19-64`; `state-badge.tsx:31-33` |
| Service-owned | title fallback, secure token, sync summaries, invalid transition | `records.ts:59-66`, `71`, `84-90`, `118-120`, `138-166` |

#### Lista roja agresiva

##### No traducir todavía sin comprobar ownership
1. **Todo lo que venga del schema**
   - `schema.title`
   - `step.title`
   - `step.description`
   - `field.label`
   - `field.helpText`
   - `field.placeholder`
   - `field.options`
   - `detailSections.title`

2. **Todo lo que venga de validation**
   - `Required`
   - `Must be a number`
   - `Invalid value`
   - `Unknown step 'x'`

3. **Todo lo que venga de state semantics**
   - `stateLabel()`
   - `stateDescription()`
   - cualquier etiqueta derivada de `RecordState`

4. **Todo lo propagado por backend/service/API**
   - `Validation failed:...`
   - `Record creation failed`
   - `Record update failed`
   - `Attachment upload failed`
   - `Record not found`
   - `Token not found`
   - `Missing file`
   - `Invalid transition from...`

5. **Todo string que ya se persiste o que deja traza operativa**
   - `"n attachment(s)"`
   - title fallback `${schema.title} YYYY-MM-DD`
   - sync summaries del service

6. **Todo valor técnico visible que aparenta ser solo copy**
   - `public / authenticated / token`
   - `enabled / disabled` para drafts
   - `ext_xxx`
   - `submitted` y cualquier display crudo de enum/estado si luego se humaniza en otra capa

#### Fugas semánticas detectadas

| Fuga | Estado | Evidencia | Riesgo |
|---|---|---|---|
| `FileList` -> `"n attachment(s)"` -> `fields` persistidos | [Confirmado] | `flow-runner.tsx:75-83`, `181-186`; stores | UI string contaminando data |
| Upload falla después de create/update | [Confirmado] | `flow-runner.tsx:189-236` | Error visible con persistencia parcial |
| `allowDrafts` se muestra pero no gobierna CTA | [Confirmado] | `page.tsx:43`; `flow-runner.tsx:481-484` | Semántica maquillada en UI |
| `accessMode` se muestra pero no gobierna acceso | [Confirmado] | refs globales de `accessMode` | Semántica maquillada en UI |
| Resume token lookup inicial, pero no persistencia posterior | [Confirmado] | `page.tsx:31`; `flow-runner.tsx:205-212` | Token UX incompleto |
| Cliente valida como `external_user`, servidor procesa como `public` sin headers | [Confirmado] | `flow-runner.tsx:173`; `request-context.ts:5-19` | Divergencia validation/visibility futura |

#### Strings que dejan de ser solo UI

| String / familia | Dónde nace | Dónde deja de ser UI |
|---|---|---|
| `"n attachment(s)"` | runner | `record.fields`, `submission.payload`, potencial detail/inbox/search |
| `${schema.title} YYYY-MM-DD` | service | `record.title` persistido |
| `Record submitted from external flow`, `Draft created`, `Record updated from external flow`, `Attachment metadata added` | service | `syncEvents` |
| `stateLabel/stateDescription` | record-view | flow/detail/inbox y cualquier otra superficie compartida |
| `Validation failed:...` | service | API response -> flow notice |

#### Riesgos de validation
- **Mezclar copy local con mensajes de validation real.**
- **Traducir `Required` en runner pero dejar `validation.ts` en inglés.**
- **Tocar errores sin definir si la fuente final será client-side, server-side o shared catalog.**
- **Abrir divergencia entre validación del cliente (`external_user`) y validación server-side (`public` por default).**

#### Riesgos de state semantics
- **Traducir `Current state` y dejar `StateBadge` o `stateDescription` en otro idioma.**
- **Cambiar labels de estado en un lado y romper consistencia con inbox/detail.**
- **Asumir que los estados son solo copy cuando gobiernan transiciones reales en `state.ts`.**

#### Riesgos de backend/service propagation
- **El runner puede mostrar texto backend crudo en la notice.**
- **Cambios de copy local no arreglan errores propagados.**
- **Save/submit pueden producir estados parciales con attachments fallidos.**
- **El fallback del título y los sync summaries ya son strings operativos compartidos.**

---

### Reporte 3. Validación y criterios de aceptación

#### Validación del progreso

| Caso | Qué validar | Evidencia / regla | Resultado esperado |
|---|---|---|---|
| Progress global | `% complete` | `flow-runner.tsx:118-128`, `267-269`, `504` | Coincide con fields visibles + required |
| Meta de step | `Step X of Y` en header y stat card | `flow-runner.tsx:260`, `504` | Consistencia entre ambas zonas |
| Required remaining | contador global | `flow-runner.tsx:118`, `505` | Baja/sube correctamente al cambiar valores |
| Step summary | `Ready` / `Not started` / `x/y required` | `flow-runner.tsx:277-283` | Refleja estado real del step |
| Visibilidad condicional | file field visible solo si toggle aplica | `visibility.ts:21-33`; schemas | Conteo y progreso no cuentan fields ocultos |

#### Validación de steps

| Caso | Qué validar | Resultado esperado |
|---|---|---|
| Step inicial vacío | `resolveInitialStepIndex` | arranca en primer step incompleto |
| Record reanudado | `initialRecord.fields` | abre en primer step incompleto del record cargado |
| Navegación por pills | click en step card | solo cambia `stepIndex`, no persiste |
| `Back` | stepIndex - 1 | no cambia record state ni datos persistidos |
| Último step | CTA final cambia a `Submit for Review` | correcto |

#### Validación de CTAs

| CTA | Qué validar | Resultado esperado |
|---|---|---|
| `Save Draft` | create/update sin submit | record en `draft` o estado actual compatible |
| `Save and Continue` | save + avance | persiste y luego avanza step |
| `Submit for Review` | save + submit | record queda `submitted` si transición válida |
| `New session` | navegación | limpia token/query y arranca nuevo flow |
| `Resume with token` | lookup inicial | carga record si token existe |
| `Clear` | navegación | limpia query token |

#### Validación de required / error states

| Caso | Qué validar | Source real | Resultado esperado |
|---|---|---|---|
| Required field vacío | badge + inline error + count banner | runner + validation | UI consistente |
| Number inválido | `Must be a number` | validation | mismo mensaje en lugar correcto |
| Invalid value fallback | `Invalid value` | validation | visible y atribuible |
| Unknown step | `Unknown step 'x'` | validation | no confundir con copy local |
| Error count banner | pluralización `needs/need` | runner local | consistente |

#### Validación de save / submit

| Caso | Qué validar | Resultado esperado |
|---|---|---|
| Create exitoso | recordId, secureToken, state, lastSavedAt | se actualizan sidebar y notices |
| Update exitoso | state y lastSavedAt | se actualizan |
| Submit válido | `submitted` | se refleja en state badge y sidebar |
| Invalid transition | service error visible | aparece error backend/service, no falso success |
| Save parcial con attachment fail | create/update pudo pasar, upload falló | el caso se documenta como parcial, no se asume atomicidad |

#### Validación de resume token

| Caso | Qué validar | Resultado esperado |
|---|---|---|
| Token válido en query | carga initialRecord | valores, state, token e id aparecen |
| Token inválido en query | comportamiento actual real | hoy queda `initialRecord = null` y no hay error visible; documentar como gap |
| Token route API | GET/PATCH por token | funciona vía API, pero el runner actual no la usa |
| Persistencia después de resume | PATCH usa recordId | documentar gap de semántica token-driven |

#### Validación de attachments

| Caso | Qué validar | Resultado esperado |
|---|---|---|
| Toggle que revela file field | visibilidad | file field aparece/desaparece correctamente |
| Selección local | `N file(s) selected` | refleja selección temporal |
| Create/update payload | serialización | hoy manda `"n attachment(s)"`; documentar como fuga, no ocultarla |
| Upload success | metadata creada | attachment aparece en subresource correspondiente |
| Upload fail | error visible | el usuario ve fallo; documentar que puede haber persistencia parcial |
| Record detail/inbox posteriores | field string + attachment metadata | revisar consistencia o duplicidad visual |

#### Criterios de aceptación para una futura primera implementación segura
- El inventario de textos frontend-owned del flow queda separado del texto schema-driven.
- Ningún string de `schema-registry`, `validation`, `record-view`, `records service` o API se toca sin contrato explícito.
- Attachments quedan marcados como zona de riesgo semántico/persistente.
- Resume token queda documentado como lookup inicial, no como canal real de persistencia posterior.
- `accessMode` y `allowDrafts` quedan documentados como display-only hasta que exista enforcement real.
- La validación contempla el desacople cliente `external_user` vs servidor `public`.
- Se evita UX bilingüe a medias entre flow, state badge, validation errors y backend errors.

#### Señales de stop
- Aparece un string cuyo source real es `schema-registry`, `validation`, `record-view`, `records service`, store o API y se pretendía tratar como copy local.
- Se intenta traducir `"n attachment(s)"` sin rediseñar la persistencia de file fields.
- Se intenta traducir estado o validation solo en una superficie.
- Se intenta “arreglar” resume token sin definir si el contrato es lookup-only o token-auth real.
- Se intenta traducir `enabled/disabled`, `accessMode` o `allowDrafts` como si fueran texto decorativo y no señal de capability.
- Se asume atomicidad entre save/update y upload cuando el código actual no la tiene.

---

### Reporte 4. Hallazgos extra y qué nos deja resuelto

#### Quick wins del flow

##### Primera ola segura
- Shell del page:
  - `Flow runner`
  - description del header
  - `New session`
  - `Open inbox`
  - `Resume an existing session`
  - `Paste a secure token...`
  - `Resume token`
  - `Resume with token`
  - `Clear`
- Fallback local:
  - `Flow configuration issue`
  - `No steps configured for this schema.`
- Runner local:
  - `Ready`
  - `Not started`
  - `Check the highlighted fields before continuing.`
  - `Draft saved successfully.`
  - `Submission sent successfully.`
  - `Unexpected error while saving.`
  - `Select...`
  - `Enabled` / `Disabled`
  - `Use this toggle only when the step requires it.`
  - `Add supporting files when needed.`
  - `One clear next move`
  - base helper del footer
  - `Back`
  - `Save Draft`
  - `Save and Continue`
  - `Submit for Review`
  - `Session summary`
  - `Why this feels safe`
  - copy de safety cards
  - `Created after the first save.`
  - `Generated once the record is first saved.`
  - `Not saved yet.`

##### Quick wins con cuidado mínimo extra
- Labels como `Progress`, `Required remaining`, `Current state`, `Record id`, `Resume token`, `Last save`.
- Se pueden mover, pero solo si se acepta que conviven con values de otras capas aún no localizadas.

#### Zonas que deben esperar
- Todo texto schema-driven.
- Todo texto de validation.
- Labels y descripciones de estado.
- Errores propagados por backend/service/API.
- `"n attachment(s)"` y cualquier resumen persistido de file fields.
- `accessMode` y `allowDrafts` hasta definir si son solo display o enforcement real.
- Resume token hasta definir si será lookup-only o credencial operativa real.
- Locale compartido de `formatRelativeTime` y `formatDateTime`.

#### Artefactos sugeridos
- **Inventario seguro de textos UI del flow**: la lista de quick wins anterior.
- **Lista roja del flow**: la sección de Reporte 2 ya sirve como checklist obligatoria.
- **Matriz de ownership del flow**: tablas de Reporte 2.
- **Matriz de validación de flow**: Reporte 3.
- **Lista de preguntas bloqueantes**: ver sección siguiente.

#### Contratos que convendría aclarar antes
1. **Contrato de schema text**
   - ¿El schema seguirá cargando labels finales visibles o solo claves/ids semánticos?
   - ¿`detailSections.title` entra al mismo contrato?

2. **Contrato de validation**
   - ¿Los mensajes finales visibles viven en `validation.ts`, en una capa shared o en el frontend?
   - ¿Cómo se evita divergencia entre validación cliente y servidor?

3. **Contrato de state presentation**
   - ¿`stateLabel` y `stateDescription` son catálogo oficial compartido?
   - ¿Quién es dueño de sus traducciones?

4. **Contrato de attachments**
   - ¿Se seguirá persistiendo una cadena resumen en `record.fields[fieldId]`?
   - Si no, ¿cuál es la representación canónica del valor file en flow/detail/inbox/search?

5. **Contrato de token resume**
   - ¿El token es solo lookup inicial o credencial válida para update?
   - ¿Debe usarse `PATCH /api/records/token/[token]` desde el flow runner?

6. **Contrato de access/capabilities**
   - ¿`accessMode` y `allowDrafts` deben gobernar UI/comportamiento o solo documentar el schema?

#### Simplificaciones posibles
- **Separar display text de data persistida en file fields**. Esto baja el blast radius más que mil traducciones heroicas.
- **Unificar actor role entre cliente y servidor** para que `external_user` no choque con `public`.
- **Decidir una sola ruta de persistencia para resume**: por token o por recordId, pero no una mezcla muda.
- **Crear display maps explícitos** para `accessMode`, `allowDrafts` y estados, en vez de renderizar valores técnicos crudos.
- **Sacar locale hardcodeado `en`** de `utils` hacia una capa shared de idioma cuando toque.
- **Revisar `searchParams.mode`** en `page.tsx:17,22`; hoy no se usa y es ruido.

#### Preguntas abiertas reales
- ¿El flow debe respetar `accessMode` operativamente o hoy es solo meta informativa?
- ¿`allowDrafts` debe ocultar/deshabilitar `Save Draft` cuando sea `false`?
- ¿El actor de flow debe ser `public` o `external_user` en servidor?
- ¿La reanudación por token debe seguir por token durante los updates?
- ¿Los labels/options del schema van a quedarse embebidos o migrarán a un catálogo?
- ¿Se quiere que el sidebar pueda quedar bilingüe temporalmente mientras state/validation siguen en inglés?
- ¿La cadena `"n attachment(s)"` debe existir en absoluto dentro de `fields`?
- ¿El detail/inbox deben leer attachments desde metadata estructurada, desde `fields`, o ambos?

#### Qué nos deja resuelto este chat

Este chat deja resuelto, con base en código real y no en documentación suelta, lo siguiente:

1. **Qué sí es local del flow y qué no.**
   Ya quedó separado el copy del page/runner de todo lo schema-driven, validation-driven, state-driven y backend-propagated.

2. **Dónde están las minas ocultas.**
   La más seria es que attachments ya no son solo UI: se convierten en texto persistido. También quedaron marcados `accessMode`, `allowDrafts`, token resume y role mismatch como zonas semánticas delicadas.

3. **Qué parte del flow queda despejada para una primera implementación.**
   Queda despejada una primera ola enfocada en shell local, CTAs locales, helper copy, notices locales y paneles laterales del runner, sin invadir schema, validation, state ni backend.

4. **Qué paso en falso evita este mapeo.**
   Evita traducir a ciegas strings que en realidad son datos, estados, errores propagados o capacidad real del flujo. Eso te ahorra una UX Frankenstein, persistencia contaminada y contradicciones entre superficies.

5. **Qué debe esperar hasta tener contrato.**
   Schema text, validation text, state text, errores backend/service, attachments persistidos, token resume operativo, locale shared y enforcement real de `accessMode` / `allowDrafts`.

En resumen: este chat deja el flow runner **quirúrgicamente partido** entre copy local seguro y semántica real peligrosa. Con eso ya no caminas a oscuras ni pateas el hormiguero antes de tiempo.
## 🛰️ Record detail, timeline y sync center

**Archivo fuente consolidado:** `external_interaction_template_detail_timeline_sync_intervention_report(1).md`

### Reporte 1. Mapa y alcance

#### 1.1 Base obligatoria usada

**Fuente principal de verdad del código real**
- Zip inspeccionado directamente en `/mnt/data/external_interaction_template(4).zip`
- Archivos revisados de forma prioritaria:
  - `app/record/[recordId]/page.tsx`
  - `components/records/record-detail.tsx`
  - `components/records/activity-timeline.tsx`
  - `app/sync/page.tsx`
  - `components/sync/sync-center.tsx`
  - `src/lib/core/record-view.ts`
  - `src/lib/ui/record-contracts.ts`
  - `src/lib/core/state.ts`
  - `src/lib/services/actions.ts`
  - `src/lib/services/records.ts`
  - `src/lib/core/types.ts`
  - `src/lib/core/schema-registry.ts`
  - `src/lib/store/memory-store.ts`
  - `app/api/records/[recordId]/action/route.ts`
  - `app/api/sync/jobs/[jobId]/retry/route.ts`

**Estructura de control aplicada**
- Se usó el “Formato Universal de Pre-Intervención y Rastreabilidad” como marco para:
  - alcance / no alcance
  - mapa de superficies
  - ownership
  - lista roja
  - matriz de riesgos
  - validación
  - criterios de aceptación
  - señales de stop

#### 1.2 Convenciones de lectura

- **Confirmado:** sale de inspección directa del código real del zip.
- **Inferido:** deducción razonable a partir del código revisado, pero no validada en runtime.
- **Dudoso:** ownership o semántica no suficientemente clara como para tocarla sin contrato previo.

#### 1.3 Resumen ejecutivo

##### Qué cubre este trabajo
- Mapa controlado de tres superficies críticas:
  - **record detail**
  - **activity timeline**
  - **sync center**
- Separación entre:
  - copy segura
  - evidencia visible
  - semántica operativa sensible
- Riesgos reales de:
  - estados
  - actions
  - timeline
  - retries
  - errors
  - metrics
  - summaries
- Validación operativa reusable por superficie, sin proponer implementación final todavía.

##### Qué deja resuelto
- Dónde vive realmente la carga de UI y semántica.
- Qué cosas sí parecen seguras para una primera ola controlada.
- Qué partes no deben tocarse todavía por mezclar frontend con contratos operativos o schema-driven content.
- Qué señales deben detener cualquier intervención antes de que el cambio se vuelva una granada con glitter.

##### Riesgos operativos detectados
- `record-detail`, `activity-timeline` y `sync-center` mezclan copy editorial con evidencia operativa visible.
- El timeline **reinterpreta** estados operativos en estados de record, y esa traducción ya es una capa semántica delicada.
- `sync-center` expone errores crudos, summaries y badges atados a enums reales.
- `record-detail` muestra labels schema-driven, action labels schema-driven y estados shared/runtime, todo en la misma vista.
- La semántica de retry existe en backend/service logic y se proyecta en UI con wording local.

#### 1.4 Alcance y no alcance

##### Entra en esta intervención
- Mapeo estructural y operativo de:
  - `/record/[recordId]`
  - `ActivityTimeline`
  - `/sync`
- Identificación de ownership tentativo por elemento visible.
- Inventario de zonas seguras vs zonas sensibles.
- Validación operativa reusable antes de tocar implementación.

##### No entra todavía
- Implementación final de idioma.
- Refactor de i18n/provider/dictionary.
- Normalización final de errores.
- Rediseño de estados o contratos de retry.
- Traducción definitiva de schema content.
- Redefinición de summary, payload o evidence rendering.

##### Condiciones de corte
Se debe detener cualquier intervención si aparece cualquiera de estas señales:
- ownership incierto de un texto visible
- necesidad de cambiar enums, estados o rutas para “hacer calzar” un label
- necesidad de tocar schema definitions para resolver una decisión de UI no cerrada
- necesidad de reinterpretar errors o summaries del backend
- mezcla no documentada entre copy local y evidencia operativa
- desalineación entre métricas, filtros y estados reales

#### 1.5 Mapa de superficies impactadas

##### Superficie principal
| Superficie | Archivo(s) principal(es) | Por qué es principal | Riesgo |
|---|---|---|---|
| Record detail | `app/record/[recordId]/page.tsx`, `components/records/record-detail.tsx` | concentra UI de detalle, actions, metadata, panel operativo y acceso al timeline | Crítico |
| Activity timeline | `components/records/activity-timeline.tsx`, `src/lib/ui/record-contracts.ts` | reordena y resume evidencia operativa en historia legible | Crítico |
| Sync center | `app/sync/page.tsx`, `components/sync/sync-center.tsx` | superficie operativa más sensible: métricas, filtros, retries, errors, summaries | Crítico |

##### Dependencias visibles relevantes
| Dependencia | Dónde impacta | Qué controla | Riesgo |
|---|---|---|---|
| `src/lib/core/record-view.ts` | detail, badges, inbox/shared semantics | labels y descripciones de `RecordState` | Alto |
| `src/lib/core/state.ts` | detail actions, retry reconciliation | disponibilidad de actions y transiciones | Crítico |
| `src/lib/ui/record-contracts.ts` | timeline | construcción de entradas de timeline, mapeos y detail payload | Crítico |
| `src/lib/services/actions.ts` | detail, sync, timeline | action feedback, dispatch, retry, sync event generation | Crítico |
| `src/lib/services/records.ts` | detail, timeline | fetch de record y subrecursos; eventos inbound | Alto |
| `src/lib/core/schema-registry.ts` | detail | schema title, summary, field labels, section titles, action labels | Alto |
| `src/lib/store/memory-store.ts` | detail, timeline, sync | orden de `dispatchJobs` y `syncEvents` | Medio |
| `app/api/records/[recordId]/action/route.ts` | detail | action execution contract y error shape | Alto |
| `app/api/sync/jobs/[jobId]/retry/route.ts` | sync | retry contract y error shape | Alto |

---

#### 1.6 Mapa del detail

##### 1.6.1 Estructura general confirmada
- `app/record/[recordId]/page.tsx`:
  - resuelve `recordId`
  - carga `record`
  - obtiene `schema`
  - carga subrecursos con `listRecordSubresources(recordId)`
  - renderiza `RecordDetail`
- `components/records/record-detail.tsx` concentra casi toda la superficie visible.

##### 1.6.2 Zonas de UI del detail
| Zona | Qué muestra | Naturaleza | Estado |
|---|---|---|---|
| Header | eyebrow, title, description, badges, shortcuts | mezcla copy local + evidencia + schema | Confirmado |
| Stat cards | current state, activity, attachments, latest sync | mezcla labels locales + semántica operativa | Confirmado |
| Business details | secciones y campos del schema + values del record | schema-driven + evidence | Confirmado |
| Activity timeline block | wrapper local para timeline | copy local | Confirmado |
| Record controls | actor role, note, available actions, feedback | mezcla local + schema + runtime + backend errors | Confirmado |
| Operational summary | ids, token, timestamps | wrappers locales + evidencia cruda | Confirmado |
| Attachments | file evidence | wrappers locales + evidencia | Confirmado |
| Dispatch & sync | jobs y events resumidos + shortcuts | operativa visible sensible | Confirmado |

##### 1.6.3 Headings visibles en detail
| Elemento | Valor visible | Fuente | Ownership tentativo |
|---|---|---|---|
| Eyebrow | `Record detail` | componente local | Frontend-owned |
| Title | `record.title` | record data | Dudoso / evidencia |
| Description | `schema.summary` | schema registry | Schema-owned |
| Panel title | `Business details` | componente local | Frontend-owned |
| Panel subtitle | `Grouped by meaning instead of raw field order so the record reads like a decision-ready document.` | componente local | Frontend-owned |
| Panel title | `Activity timeline` | componente local | Frontend-owned |
| Panel subtitle | `Submissions, state transitions, and operator notes arranged for quick historical reading.` | componente local | Frontend-owned |
| Panel title | `Record controls` | componente local | Frontend-owned |
| Panel subtitle | `Switch execution role, add operator context, and trigger the next state.` | componente local | Frontend-owned |
| Panel title | `Operational summary` | componente local | Frontend-owned |
| Panel subtitle | `Keep the key metadata visible while working through decisions.` | componente local | Frontend-owned |
| Panel title | `Attachments` | componente local | Frontend-owned |
| Panel subtitle | `File evidence attached to the record.` | componente local | Frontend-owned |
| Panel title | `Dispatch & sync` | componente local | Frontend-owned |
| Panel subtitle | `Operational trail for outbound work and external acknowledgements.` | componente local | Frontend-owned |
| Section title | `section.title` | schema views | Schema-owned |

##### 1.6.4 Metadata visible en detail
| Elemento | Valor visible | Riesgo | Estado |
|---|---|---|---|
| Header badge | `StateBadge(record.state)` | shared/runtime semantics | Confirmado |
| Header badge | `schema.title` | schema content | Confirmado |
| Header badge | `Updated {formatRelativeTime(record.updatedAt)}` | wrapper local + temporal formatting | Confirmado |
| Header badge | `{attachments.length} attachment(s)` | wrapper local + count | Confirmado |
| Stat | `Current state` + `stateLabel(record.state)` + `stateDescription(record.state)` | label local + runtime semantics | Confirmado |
| Stat | `Activity` + `submissions.length` | local + count | Confirmado |
| Stat | `Attachments` + `attachments.length` | local + count | Confirmado |
| Stat | `Latest sync` + `latestSync.status` or `none` + `latestSync.summary` | local + semántica operativa + summary | Confirmado |
| Summary item | `Record id` + `record.id` | wrapper local + evidencia | Confirmado |
| Summary item | `Secure token` + `record.secureToken` | wrapper local + evidencia sensible | Confirmado |
| Summary item | `Created` + `record.createdAt` | wrapper local + evidencia | Confirmado |
| Summary item | `Submitted` + `record.submittedAt` | wrapper local + evidencia | Confirmado |
| Summary item | `Last sync` + `record.lastSyncAt` | wrapper local + evidencia | Confirmado |

##### 1.6.5 Actions visibles en detail
| Acción visible | Fuente del label | Comportamiento real | Riesgo |
|---|---|---|---|
| `Inbox` | local | `router.push("/inbox")` | Bajo |
| `Refresh` | local | `router.refresh()` | Bajo |
| `Open Sync Center` | local | `router.push("/sync")` | Bajo |
| selector de `Actor role` | options visibles `external_user`, `reviewer`, `approver`, `operator` | filtra disponibilidad de actions | Alto |
| textarea `Operator note` | placeholder local condicionado por `requiresNote` | alimenta action route | Alto |
| action button `action.label` | schema action label | ejecuta `/api/records/${record.id}/action` | Crítico |
| busy label `Running...` | local | se muestra mientras corre la action | Medio |
| badge `Note required` | local | depende de `action.requiresComment` | Medio |
| `Open Sync Center` en panel operativo | local | navegación | Bajo |
| `Refresh record` | local | `router.refresh()` | Bajo |

##### 1.6.6 States visibles en detail
| Superficie | Representación visible | Fuente | Riesgo |
|---|---|---|---|
| Header badge | `StateBadge(record.state)` | `stateLabel`, `stateTone`, `ensureRecordState` | Alto |
| Stat card | `stateLabel(record.state)` + `stateDescription(record.state)` | `record-view.ts` | Alto |
| Latest sync stat | `latestSync.status` | `SyncStatus` raw | Crítico |
| Dispatch & sync panel | `job.status`, `event.status` | `DispatchStatus`, `SyncStatus` raw | Crítico |
| availableActions | depende de `isActionAvailable(record.state, action, { role })` | runtime/state contract | Crítico |

##### 1.6.7 Retries en detail
- **Confirmado:** el detail no ejecuta retry directo.
- **Confirmado:** el detail solo:
  - expone jobs/events resumidos
  - redirige al `/sync`
  - refresca el record
- **Inferido:** cualquier copy en detail que sugiera retry o reconciliación directa sería engañosa porque el control real vive en sync/service logic.

##### 1.6.8 Errors y feedback en detail
| Elemento | Fuente | Naturaleza | Riesgo |
|---|---|---|---|
| guard-rail de nota requerida | local | copy preventiva | Medio |
| feedback éxito | `${action.label} executed successfully.` | local + schema label | Alto |
| feedback error | `body.error ?? "Action failed"` | backend/service error crudo o fallback local | Crítico |
| dispatch job error | `job.error` | evidencia operativa | Crítico |
| sync event error | `event.error` | evidencia operativa | Crítico |

##### 1.6.9 Summaries / evidence en detail
| Elemento | Fuente | Tipo |
|---|---|---|
| `record.title` | record | evidencia / dato de negocio |
| `schema.summary` | schema | schema content |
| `latestSync.summary` | sync event | evidencia operativa / resumen sensible |
| field values | `record.fields[fieldId]` | evidencia |
| attachment names | attachment metadata | evidencia |
| `record.id`, `secureToken` | record | evidencia operativa |

##### 1.6.10 Hallazgos clave del detail
- **Confirmado:** detail mezcla tres capas en una sola vista:
  - shell local
  - schema-driven content
  - evidencia/operación
- **Confirmado:** las action labels no son locales, salen del schema.
- **Confirmado:** el feedback de error puede ser crudo del backend/service layer.
- **Confirmado:** `Latest sync` usa `syncEvents[0]`, y el store devuelve sync events ordenados por `createdAt desc`.
- **Dudoso:** traducir `stateLabel` y `stateDescription` sin glosario global puede romper coherencia entre detail, inbox y badges.

---

#### 1.7 Mapa del timeline

##### 1.7.1 Estructura general confirmada
- `ActivityTimeline` recibe:
  - `submissions`
  - `syncEvents`
  - `dispatchJobs`
- arma eventos con `createTimelineEntries(...)`
- renderiza lista cronológica descendente
- si no hay eventos, usa empty state local.

##### 1.7.2 Zonas de UI del timeline
| Zona | Qué muestra | Naturaleza | Estado |
|---|---|---|---|
| Empty state | título y descripción | local | Confirmado |
| Entry header | `event.kind`, fecha, meta | runtime-assembled | Confirmado |
| Entry title | title construido por contrato | runtime-assembled / evidence | Confirmado |
| Entry description | description construida por contrato | runtime-assembled | Confirmado |
| State badge | `event.state` | derived semantic layer | Confirmado |
| Detail block | `event.detail` en `<pre>` | evidencia cruda o JSON | Confirmado |

##### 1.7.3 Headings y labels visibles en timeline
| Elemento | Valor visible | Fuente | Ownership tentativo |
|---|---|---|---|
| Empty title | `No activity yet` | local | Frontend-owned |
| Empty description | `New submissions, dispatch attempts and sync signals will land here once the record starts moving.` | local | Frontend-owned |
| kind label | `submission` / `dispatch` / `sync` | runtime contract | Runtime-owned |
| time label | `formatDateTime(event.createdAt)` | shared util | Shared-owned |
| meta | actorId o meta string | runtime/evidence | Dudoso |
| title | depende del tipo de evento | runtime contract + evidence | Runtime-owned / Dudoso |
| description | depende del tipo de evento | runtime contract + evidence | Runtime-owned / Dudoso |

##### 1.7.4 Cómo se construye cada tipo de entrada
| Kind | Title | Description | State badge | Detail | Meta |
|---|---|---|---|---|---|
| submission | `submission.stepId` sanitizado o `Submission captured` | `Captured X field update(s) from {source}.` | `submitted` | JSON del payload | `submission.actorId` |
| dispatch | `Dispatch {job.status}` | `{adapterId} • attempts: N` | `succeeded -> dispatched`, `failed -> failed`, otro -> `in_review` | `job.error` o JSON de `job.response` | none |
| sync | `event.summary` sanitizado o `Sync signal` | `{direction} • {adapterId}` | `synced -> synced`, `failed -> failed`, otro -> `submitted` | `event.error` o JSON de `event.payload` | none |

##### 1.7.5 Semántica operativa sensible del timeline
| Elemento | Qué hace | Riesgo |
|---|---|---|
| `mapDispatchState` | traduce `DispatchStatus` a `RecordState` | Crítico |
| `mapSyncState` | traduce `SyncStatus` a `RecordState` | Crítico |
| `Dispatch {job.status}` | vuelve visible el enum operativo dentro de un título legible | Alto |
| `event.summary` como title | eleva summary a heading de timeline | Crítico |
| `event.detail` | muestra error o payload crudo | Crítico |
| `kind` visible | clasifica historia operacional | Medio |

##### 1.7.6 Errors y evidence en timeline
| Elemento | Fuente | Naturaleza |
|---|---|---|
| submission detail | `safeJson(submission.payload)` | evidencia cruda |
| dispatch detail | `job.error` o `job.response` serializado | evidencia cruda |
| sync detail | `event.error` o `event.payload` serializado | evidencia cruda |

##### 1.7.7 Hallazgos clave del timeline
- **Confirmado:** timeline no es solo UI. Es una **capa narrativa** armada con contratos runtime.
- **Confirmado:** el timeline ya “traduce” eventos técnicos a una historia legible.
- **Confirmado:** esa traducción ya tiene pérdida de granularidad:
  - `pending` y `retryable` no se ven como states propios del badge; se remapean.
- **Crítico:** tocar copy del timeline sin aclarar si se está editando copy o reinterpretando evidencia puede deformar la lectura histórica.
- **Dudoso:** `event.summary` puede ser generado por adapter/service y no por frontend.

---

#### 1.8 Mapa del sync

##### 1.8.1 Estructura general confirmada
- `app/sync/page.tsx` carga `listSyncCenterData()`.
- `listSyncCenterData()` devuelve `events` y `jobs`.
- `SyncCenter` concentra:
  - métricas
  - filtros
  - listas
  - retry
  - feedback

##### 1.8.2 Zonas de UI del sync
| Zona | Qué muestra | Naturaleza | Estado |
|---|---|---|---|
| Header | título, descripción, refresh | local | Confirmado |
| Stat cards | métricas de jobs/events | local + semántica operativa | Confirmado |
| Dispatch jobs panel | jobs, status, error, retry | operativa visible | Confirmado |
| Sync events panel | event summary, status, direction, adapter, timestamp, error | operativa visible | Confirmado |
| Message strip | éxito o fallo de retry | local + backend/service error | Confirmado |

##### 1.8.3 Headings visibles en sync
| Elemento | Valor visible | Ownership tentativo |
|---|---|---|
| Eyebrow | `Sync center` | Frontend-owned |
| Title | `Operational visibility for dispatch and sync health` | Frontend-owned |
| Description | `Inspect outbound execution, watch retryable failures, and keep the audit trail readable at a glance.` | Frontend-owned |
| Panel title | `Dispatch jobs` | Frontend-owned |
| Panel subtitle | `Outbound action execution states with retry controls.` | Frontend-owned |
| Panel title | `Sync events` | Frontend-owned |
| Panel subtitle | `Inbound and outbound audit trail with clearer status visibility.` | Frontend-owned |

##### 1.8.4 Métricas visibles en sync
| Card | Fórmula confirmada | Riesgo |
|---|---|---|
| `Pending jobs` | jobs con `pending` o `running` | Alto |
| `Failed jobs` | jobs con `failed` | Medio |
| `Synced events` | events con `synced` | Medio |
| `Retryable events` | events con `retryable` | Alto |

##### 1.8.5 Filtros visibles en sync
| Grupo | Opciones visibles | Value real |
|---|---|---|
| Jobs | `All`, `Failed`, `Pending`, `Running`, `Succeeded` | `all`, `failed`, `pending`, `running`, `succeeded` |
| Events | `All`, `Retryable`, `Pending`, `Synced`, `Failed` | `all`, `retryable`, `pending`, `synced`, `failed` |

##### 1.8.6 Botones y retries en sync
| Elemento | Comportamiento | Riesgo |
|---|---|---|
| `Refresh data` | `router.refresh()` | Bajo |
| `Retry` | POST `/api/sync/jobs/{jobId}/retry` | Crítico |
| `Retrying...` | estado busy local | Medio |
| disable rule | se deshabilita si hay `busyJob` o si `job.status !== "failed"` | Crítico |

##### 1.8.7 Errors, feedback y evidence en sync
| Elemento | Fuente | Naturaleza | Riesgo |
|---|---|---|---|
| job error card | `job.error` | evidencia operativa | Crítico |
| event error text | `event.error` | evidencia operativa | Crítico |
| retry success strip | `Retry executed for job {jobId}.` | local + id | Medio |
| retry fail strip | `body.error ?? "Retry failed"` | backend/service error crudo o fallback local | Crítico |

##### 1.8.8 Data visible por panel en sync

###### Dispatch jobs
| Campo visible | Fuente | Tipo |
|---|---|---|
| `recordId` como link | job | evidencia operativa |
| `Adapter {adapterId}` | job | wrapper local + evidencia |
| `Attempts {attempts}` | job | wrapper local + evidencia |
| badge `{job.status}` | job | semántica operativa cruda |
| `Updated {updatedAt}` | job | wrapper local + evidencia |
| `job.error` | job | evidencia operativa |
| `Retry` | local, pero amarrado a status real | acción sensible |

###### Sync events
| Campo visible | Fuente | Tipo |
|---|---|---|
| icono por status | event.status | semántica operativa derivada |
| `event.summary` | sync event | resumen sensible / evidencia |
| `recordId` | sync event | evidencia operativa |
| `direction` | sync event | semántica operativa |
| `adapterId` | sync event | evidencia técnica |
| `createdAt` | sync event | evidencia temporal |
| badge `{event.status}` | sync event | semántica operativa cruda |
| `event.error` | sync event | evidencia operativa |

##### 1.8.9 Hallazgos clave del sync
- **Confirmado:** sync es la superficie operativa más delicada del frente.
- **Confirmado:** métricas, filtros, badges y retries están atados a contratos reales de estado.
- **Confirmado:** sync mezcla copy segura con evidence/semantics en la misma card.
- **Confirmado:** retry solo aplica a dispatch jobs fallidos.
- **Crítico:** confundir `failed` con `retryable` o `succeeded` con `synced` rompería el significado operativo.

#### 1.9 Semántica operativa sensible confirmada

| Contrato | Valores visibles o usados | Dónde pega | Estado |
|---|---|---|---|
| `RecordState` | `draft`, `submitted`, `in_review`, `awaiting_update`, `approved`, `rejected`, `dispatched`, `synced`, `failed` | detail, badges, timeline, inbox/shared surfaces | Confirmado |
| `DispatchStatus` | `pending`, `running`, `succeeded`, `failed` | sync, timeline, detail panel | Confirmado |
| `SyncStatus` | `pending`, `synced`, `failed`, `retryable` | sync, timeline, detail latest sync | Confirmado |
| `AdapterDirection` | `inbound`, `outbound` | sync, timeline | Confirmado |
| actor roles visibles | `external_user`, `reviewer`, `approver`, `operator` | detail controls, action availability | Confirmado |
| action execution semantics | `isActionAvailable`, `requiresComment`, `nextState` | detail controls, action route | Confirmado |
| retry semantics | retry de dispatch job fallido, no de event | sync, services/actions | Confirmado |
| timeline semantic remap | dispatch/sync -> record state | timeline | Confirmado |

#### 1.10 Dependencias relevantes por superficie

| Superficie | Dependencias principales | Observación |
|---|---|---|
| Detail | `record-detail.tsx`, `record-view.ts`, `core/state.ts`, `schema-registry.ts`, `services/actions.ts`, `services/records.ts` | mezcla shell, schema, runtime y operativa |
| Timeline | `activity-timeline.tsx`, `record-contracts.ts`, `ui/contracts.ts` | la narrativa se construye en runtime, no llega “lista” |
| Sync | `sync-center.tsx`, `services/actions.ts`, `memory-store.ts`, retry route | la semántica real no está solo en la UI; vive en services/store/contracts |

### Reporte 2. Ownership, lista roja y riesgos

#### 2.1 Matriz de frontend-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `Record detail` | detail | `components/records/record-detail.tsx` | Alta | eyebrow local |
| `Business details` y subtítulo | detail | `components/records/record-detail.tsx` | Alta | shell local |
| `Activity timeline` y subtítulo | detail | `components/records/record-detail.tsx` | Alta | shell local |
| `Record controls` y subtítulo | detail | `components/records/record-detail.tsx` | Alta | shell local |
| `Operational summary` y subtítulo | detail | `components/records/record-detail.tsx` | Alta | shell local |
| `Attachments` y subtítulo | detail | `components/records/record-detail.tsx` | Alta | shell local |
| `Dispatch & sync` y subtítulo | detail | `components/records/record-detail.tsx` | Alta | shell local |
| `Inbox`, `Refresh`, `Open Sync Center`, `Refresh record` | detail | `components/records/record-detail.tsx` | Alta | acciones locales de navegación/refresh |
| labels wrapper `Record id`, `Secure token`, `Created`, `Submitted`, `Last sync` | detail | `components/records/record-detail.tsx` | Alta | wrapper local; no tocar valores |
| empty messages locales del detail | detail | `components/records/record-detail.tsx` | Alta | “No attachments…”, “No dispatch jobs…” |
| `No activity yet` + empty description | timeline | `components/records/activity-timeline.tsx` | Alta | empty state local |
| `Sync center`, title, description, panel titles/subtitles | sync | `components/sync/sync-center.tsx` | Alta | shell local |
| `Refresh data` | sync | `components/sync/sync-center.tsx` | Alta | copy local |
| empty states del sync | sync | `components/sync/sync-center.tsx` | Alta | seguros como copy local |
| wrappers `Adapter`, `Attempts`, `Updated` | sync/detail | `components/sync/sync-center.tsx`, `components/records/record-detail.tsx` | Media-Alta | seguro el wrapper, no el valor |

#### 2.2 Matriz de shared-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `StateBadge` visual shell | detail, timeline, otras | `components/ui/state-badge.tsx` | Alta | shared component |
| `PageHeader`, `Badge`, `Button`, `StatCard`, `Surface`, `EmptyState`, `FilterPills` | detail, sync, otras | `components/ui/*` | Alta | shared visual system |
| `formatDateTime`, `formatRelativeTime`, `formatBytes`, `formatValue` | detail, timeline, sync | `src/lib/utils.ts` | Alta | shared formatting |
| `toneFromSeverity` y utilidades de UI contract | timeline/other UI | `src/lib/ui/contracts.ts` | Alta | shared utilities |
| `stateTone` | badges/shared states | `src/lib/core/record-view.ts` | Media | shared semantics + visual tone |

#### 2.3 Matriz de runtime-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `stateLabel(record.state)` | detail, badges, otras | `src/lib/core/record-view.ts` | Alta | derivación runtime de enum |
| `stateDescription(record.state)` | detail | `src/lib/core/record-view.ts` | Alta | glosario runtime, no schema |
| `createTimelineEntries(...)` | timeline | `src/lib/ui/record-contracts.ts` | Alta | arma narrativa a partir de evidence |
| `Dispatch {job.status}` | timeline | `src/lib/ui/record-contracts.ts` | Alta | wording construido en runtime |
| `Captured X field update(s)...` | timeline | `src/lib/ui/record-contracts.ts` | Alta | copy runtime derivada de payload |
| `mapDispatchState` / `mapSyncState` | timeline | `src/lib/ui/record-contracts.ts` | Alta | remapeo semántico sensible |
| fallback `Submission captured` / `Sync signal` | timeline | `src/lib/ui/record-contracts.ts` | Alta | runtime fallback |
| option set de actor role como control visible | detail | `components/records/record-detail.tsx` + `request-context.ts` | Media | visible, pero acoplado al contrato de actor |

#### 2.4 Matriz de schema-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `schema.title` | detail | `src/lib/core/schema-registry.ts` | Alta | schema content |
| `schema.summary` | detail | `src/lib/core/schema-registry.ts` | Alta | schema content |
| `section.title` en Business details | detail | `src/lib/core/schema-registry.ts` | Alta | schema views |
| `field.label` | detail | `src/lib/core/schema-registry.ts` | Alta | schema definition |
| `action.label` en botones | detail | `src/lib/core/schema-registry.ts` | Alta | schema action labels |
| `action.requiresComment` semantic hint | detail | `src/lib/core/schema-registry.ts` | Alta | gobierna copy local y control |
| field placeholders / helpText del flow | fuera de foco principal, pero relacionados | `src/lib/core/schema-registry.ts` | Alta | impacta validación transversal futura |

#### 2.5 Matriz de backend-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `body.error` devuelto por action route | detail | `app/api/records/[recordId]/action/route.ts` | Alta | error shape de API |
| `body.error` devuelto por retry route | sync | `app/api/sync/jobs/[jobId]/retry/route.ts` | Alta | error shape de API |
| `job.error` | detail, timeline, sync | services/store/adapters | Alta | evidencia operativa |
| `event.error` | detail, timeline, sync | services/store/adapters | Alta | evidencia operativa |
| `response.summary` de dispatch/retry | timeline, sync, events | `src/lib/services/actions.ts` + adapter response | Media-Alta | summary generado fuera del shell local |
| `response.responsePayload` / `event.payload` / `job.response` | timeline | services/store/adapters | Alta | evidencia cruda |

#### 2.6 Matriz de dudoso

| Elemento | Superficie | Por qué es dudoso | Qué falta aclarar |
|---|---|---|---|
| `record.title` | detail | dato de negocio visible como heading | si entra al frente de idioma o debe respetarse como data original |
| `event.summary` | detail, timeline, sync | puede venir de adapter/service/backend y a veces operar como heading | owner real y política de traducción |
| `latestSync.status` mostrado como valor | detail | es enum operativo visible en una stat card editorializada | glosario global |
| `none` como fallback de Latest sync | detail | local, pero incrustado en una card semántica | política de fallback en superficies operativas |
| actor role values visibles `external_user`, `reviewer`, `approver`, `operator` | detail | son contrato de ejecución pero también texto visible | si se muestran crudos o con alias display-only |
| `direction` (`inbound`, `outbound`) | timeline, sync | enum operativo visible | si se display-mapea o se deja técnico |
| `adapterId` | detail, timeline, sync | técnico y visible | si siempre debe quedarse crudo |
| `secureToken` | detail | evidencia sensible | si debe verse, ocultarse o quedar fuera de frentes de idioma |
| `stateLabel` / `stateDescription` | detail/shared | son runtime-owned, pero equivalen a glosario global | contrato terminológico transversal |
| `Retry failed` | sync | fallback local en flujo operativo | si debe existir fallback genérico o normalización previa |

#### 2.7 Lista roja del detail

No debería traducirse ni reinterpretarse todavía sin verificación:
- `record.title`
- `schema.title`
- `schema.summary`
- `section.title`
- `field.label`
- `action.label`
- `StateBadge(record.state)` si implica renombrar estados sin glosario
- `stateLabel(record.state)` / `stateDescription(record.state)` sin contrato global
- `latestSync.status`
- `latestSync.summary`
- actor role values visibles
- feedback de error proveniente de API
- `job.error`
- `event.error`
- `job.status`
- `event.status`
- `record.id`
- `secureToken`
- `adapterId`
- timestamps y counts si el cambio altera su significado percibido

#### 2.8 Lista roja del timeline

No debería traducirse ni reinterpretarse todavía sin verificación:
- `event.kind` si no existe taxonomía display aprobada
- `Dispatch {job.status}`
- `event.summary` usado como title
- `direction`
- `adapterId`
- `event.detail` cuando contiene JSON o evidence raw
- `job.error`, `event.error`
- mapeos `mapDispatchState` y `mapSyncState`
- cualquier intento de “mejorar” la historia del timeline ocultando estados crudos
- cualquier cambio que haga parecer equivalentes `retryable` y `failed`
- cualquier cambio que borre la diferencia entre `dispatch` event y `sync` event

#### 2.9 Lista roja del sync

No debería traducirse ni reinterpretarse todavía sin verificación:
- badges `{job.status}` y `{event.status}`
- labels de filtros si se mueven sin mantener `value` y semántica exacta
- fórmulas de métricas
- `event.summary`
- `job.error`
- `event.error`
- `direction`
- `adapterId`
- `recordId`
- wording que haga pensar que retry opera sobre events y no sobre failed jobs
- cualquier unificación editorial entre `Succeeded` y `Synced`
- cualquier “embellecimiento” de errors crudos que cambie su meaning

#### 2.10 Matriz de riesgos

| Riesgo | Tipo | Superficie | Probabilidad | Impacto | Señal temprana | Mitigación |
|---|---|---|---|---|---|---|
| Traducir evidencia operativa como si fuera copy | evidence | detail, timeline, sync | Alta | Crítico | alguien propone tocar summary/error/id/adapter | congelar lista roja y clasificar owners |
| Renombrar estados sin glosario global | status semantics | detail, timeline, sync | Alta | Crítico | mismo estado aparece con dos nombres | definir diccionario único antes |
| Aplastar diferencias entre `DispatchStatus`, `SyncStatus` y `RecordState` | status semantics | timeline, sync, detail | Alta | Crítico | se intenta “homologar” todo a una sola familia | mantener tabla explícita por dominio |
| Cambiar significado percibido de retry | retries | sync | Media-Alta | Crítico | copy sugiere retry de event o de sync global | documentar que retry opera sobre failed dispatch jobs |
| Tratar error crudo como UX message normalizado | feedback/error messages | detail, sync, timeline | Alta | Alto | se quiere traducir/parafrasear `body.error`, `job.error`, `event.error` | separar raw error vs user message |
| Traducir action labels desde frontend aunque vienen del schema | ownership | detail | Alta | Alto | se quiere tocar botones sin tocar schema strategy | marcar action labels como schema-owned |
| Traducir fields/sections del detail sin política schema | ownership | detail | Alta | Alto | se mezclan labels locales y schema en una misma sección | cerrar política schema-first |
| Timeline reescribe historia operacional | evidence | timeline | Media-Alta | Crítico | cambios en `createTimelineEntries` para sonar “mejor” | tratar timeline como contrato narrativo sensible |
| Métricas y filtros desalineados | metrics | sync | Media | Alto | label no describe exactamente lo que cuenta | validar fórmula vs label |
| Mezcla rara de idiomas en superficies sensibles | transversal | detail, sync | Alta | Alto | cards híbridas mitad local mitad raw | definir política temporal de mixed-language acceptable |
| Exponer o tocar secure token sin criterio | evidence | detail | Media | Alto | token tratado como copy secundaria | mantenerlo fuera de cambios de idioma salvo decisión explícita |
| Actor role visible cambia meaning funcional | actions/metadata | detail | Media | Alto | alias visual confunde permisos reales | separar internal value vs display label, pero solo con contrato |

#### 2.11 Riesgos específicos de evidence

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| title de record tratado como heading traducible | detail | puede ser dato de negocio, no copy |
| summary de sync tratado como copy editorial | detail, timeline, sync | puede ser evidencia generada por adapter/service |
| payload/error en timeline tratados como texto UX | timeline | rompe trazabilidad |
| ids/adapter/token tratados como labels blandos | detail, sync | puede dañar soporte/operación |

#### 2.12 Riesgos específicos de status semantics

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| `stateLabel` y `stateDescription` no alinean con `job.status`/`event.status` | detail | ya son vocabularios distintos |
| `Latest sync` muestra `SyncStatus`, no `RecordState` | detail | fácil confundirlo con el estado general del record |
| timeline remapea dispatch/sync status a `RecordState` | timeline | capa de interpretación, no vista literal |
| filtros y métricas usan dominios distintos por panel | sync | job panel != event panel |

#### 2.13 Riesgos específicos de retries

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| retry de job se comunica como si fuera retry de sync | sync | wording debe preservar el sujeto real |
| retry exitoso cambia record a `synced` bajo ciertas condiciones | services/actions + sync/detail | tiene semántica de reconciliación real |
| retry fallido crea nuevo sync event `retryable` | services/actions | no debe ocultarse detrás de copy vaga |

#### 2.14 Riesgos específicos de feedback/error messages

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| `Action failed` y `Retry failed` conviven con errors crudos | detail, sync | mezcla local + backend |
| success feedback usa `action.label` | detail | si action.label es schema-owned, el feedback también hereda ese owner |
| errors largos rompen layout o se vuelven ilegibles | detail, timeline, sync | necesita validación explícita |

### Reporte 3. Validación y criterios de aceptación

#### 3.1 Validación del detail

| Caso | Qué revisar | Por qué importa | Severidad | Criterio de aceptación | Señal de stop |
|---|---|---|---|---|---|
| Header mixto | eyebrow local + title record + schema summary + badges | mezcla tres ownerships | Crítica | cada texto queda clasificado y no se toca lo dudoso | surge necesidad de traducir `record.title` o `schema.summary` sin política |
| Current state stat | label, value, meta | estado visible con glosario shared/runtime | Crítica | `RecordState` se mantiene consistente con otras vistas | el mismo estado recibe dos nombres |
| Latest sync stat | label, status raw, summary | superficie semántica mixta | Crítica | se preserva diferencia entre estado general y sync outcome | el usuario cree que `Latest sync` == estado del record |
| Business details | titles de sección, labels de campo, values largos | schema content + evidence | Alta | no se altera schema-owned ni evidence | se decide traducir fields sin estrategia schema |
| Record controls | actor role, operator note, available actions | controla comportamiento real | Crítica | display no cambia meaning funcional | alias visual ya no corresponde al rol real |
| Action buttons | label, busy state, note required badge | actions ejecutan backend | Crítica | el texto sigue representando correctamente la acción real | copy sugiere otra transición o conducta |
| Feedback | success/failure after action | mezcla local + backend | Crítica | success sigue fiel; error crudo no se maquilla | el cambio exige reinterpretar body.error |
| Operational summary | wrappers + ids/token/dates | evidence sensible | Alta | solo cambian wrappers seguros; valores intactos | se propone tocar tokens/ids o formatearlos ambiguamente |
| Dispatch & sync panel | statuses, summaries, errors | operativa sensible | Crítica | no se renombra nada sensible sin contrato | `succeeded`, `failed`, `retryable`, `synced` se difuminan |

#### 3.2 Validación del timeline

| Caso | Qué revisar | Por qué importa | Severidad | Criterio de aceptación | Señal de stop |
|---|---|---|---|---|---|
| Empty state | título y descripción | copy segura | Media | cabe bien y no invade semántica | se intenta usarlo para explicar estados reales |
| kind label | `submission`, `dispatch`, `sync` | clasifica historia operativa | Alta | si cambia, existe taxonomía aprobada | se inventa alias sin contrato |
| Title por tipo | submission stepId, `Dispatch {status}`, summary | title mezcla contrato y evidence | Crítica | no se traduce evidence ni se reescribe historia | el title deja de reflejar la fuente real |
| Description por tipo | captured updates / adapter / direction | capa runtime | Alta | wording sigue fiel a la fuente | se borra adapter/direction/attempts por sonar técnico |
| State badge | mapDispatchState / mapSyncState | remapeo semántico sensible | Crítica | badge sigue documentado como derived state | se interpreta como estado literal del evento |
| Detail block | error/payload/response JSON | evidencia cruda | Crítica | contenido intacto, legible y no adornado | se traduce, limpia o resume evidence |
| Ordering | newest first | lectura histórica | Alta | orden descendente intacto | cambios visuales alteran percepción temporal |

#### 3.3 Validación del sync

| Caso | Qué revisar | Por qué importa | Severidad | Criterio de aceptación | Señal de stop |
|---|---|---|---|---|---|
| Header | title/description/refresh | copy segura | Media | puede cambiar sin tocar semántica | se usa para redefinir estados |
| Metrics | labels, fórmulas, meta text | resumen operativo | Crítica | cada label describe exactamente su count | label y count ya no coinciden |
| Job filters | labels, counts, filtered set | semántica de dispatch | Crítica | label visible y `value` siguen alineados | `Running` o `Failed` pierde precisión |
| Event filters | labels, counts, filtered set | semántica de sync | Crítica | `retryable`, `pending`, `synced`, `failed` siguen distinguiéndose | se aplana `retryable` contra `failed` |
| Dispatch job cards | ids, adapter, attempts, badge, updated, error | soporte y operación | Crítica | wrappers pueden cambiar; evidence intacta | se traduce evidence o se altera sujeto del retry |
| Retry | button text, busy state, disable rule, success strip, fail strip | acción con consecuencia real | Crítica | sigue claro que retry aplica a failed jobs | parece que se reintenta el event |
| Sync event cards | summary, direction, adapterId, badge, error | audit trail sensible | Crítica | no se altera evidence ni enum semantics | summary o error se tratan como copy segura |
| Empty states | no-results vs system-failure | UX operativa | Alta | vacío por filtro se distingue de falla | texto induce a pensar outage |

#### 3.4 Validación de actions visibles

| Acción | Superficie | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|---|
| `Inbox` | detail | sigue siendo navegación simple | lleva a `/inbox` y su label sigue inequívoco | pide reinterpretación funcional |
| `Refresh` / `Refresh record` / `Refresh data` | detail, sync | no sugieren side effects falsos | solo refrescan vista | alguien quiere convertirlos en “resync” o similar |
| schema action buttons | detail | label refleja la action real del schema | botón, feedback y note requirement siguen alineados | se quiere “mejorar” label sin política schema |
| `Retry` | sync | sujeto, alcance y resultado percibido | claramente reintenta un failed dispatch job | wording cambia el objeto real de la acción |

#### 3.5 Validación de metadata

| Metadata | Superficie | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|---|
| ids (`recordId`, `jobId`) | detail, sync | siguen visibles y exactos | wrapper puede cambiar; valor no | alguien quiere humanizarlos |
| `secureToken` | detail | no se toca ni se degrada su legibilidad | valor intacto | se intenta traducir, truncar o relabel ambiguamente |
| `adapterId` | detail, timeline, sync | se deja técnico salvo contrato | valor intacto | se cambia a alias sin mapa |
| fechas y tiempos | detail, timeline, sync | wrapper y formato consistentes | no cambian meaning temporal | cambios visuales vuelven ambiguo si es relativo o absoluto |
| counts | detail, sync | label describe count real | counts confiables | labels vagos o inconsistentes |

#### 3.6 Validación de retries

| Caso | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|
| Button enablement | solo `job.status === "failed"` | la UI no habilita retry en otros estados | se habilita o comunica retry fuera de failed jobs |
| Busy label | `Retrying...` | no sugiere otro proceso distinto | se interpreta como sync global |
| Success strip | `Retry executed for job {jobId}.` | outcome acotado y fiel | mensaje sugiere que todo el record quedó synced sin contexto |
| Failure strip | error crudo o fallback | fidelidad al outcome real | se traduce/parafrasea error sin política |

#### 3.7 Validación de métricas

| Métrica | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|
| Pending jobs | incluye `pending` + `running` | label/meta explican la fórmula | se renombra como si fuera solo `pending` |
| Failed jobs | cuenta solo `failed` | ninguna confusión con `retryable events` | se mezclan dominios |
| Synced events | cuenta solo events `synced` | no se confunde con records synced | se interpreta como “records synced” |
| Retryable events | cuenta solo events `retryable` | no se confunde con failed jobs | se aplana con `failed` |

#### 3.8 Validación de errores largos

| Superficie | Qué revisar | Criterio de aceptación | Stop |
|---|---|---|---|
| detail feedback | error de action largo | se mantiene legible, no engañoso | truncado sin contexto o “normalizado” arbitrario |
| detail dispatch/sync panel | error largo | no rompe card, sigue fiel | se oculta por completo |
| timeline detail pre | JSON/error largo | scroll y wrap sanos | se transforma el payload |
| sync jobs/events | error largo | card y strip soportan texto extenso | layout roto o cambio de meaning |

#### 3.9 Criterios de aceptación globales

Se considera este frente **listo para pasar a diseño de intervención** cuando:
- todas las superficies críticas tienen mapa real basado en código
- cada string visible relevante tiene owner tentativo o está marcado como dudoso
- existe lista roja congelada
- los riesgos críticos tienen mitigación y señal de stop
- la diferencia entre `RecordState`, `DispatchStatus` y `SyncStatus` quedó explícita
- la diferencia entre copy segura y evidence quedó documentada
- la validación operativa por superficie está lista
- no hay propuesta de implementación que dependa de inventar ownership

#### 3.10 Señales de stop globales

Detener la intervención si pasa cualquiera de estas:
- aparece necesidad de traducir `event.summary`, `job.error`, `event.error`, `record.title` o `secureToken`
- se detecta que action labels o section labels deben salir de schema y no del shell local
- una decisión de idioma exige cambiar enums, contracts o routes
- el timeline necesita reinterpretación narrativa para “sonar mejor”
- se quiere homologar `failed`, `retryable`, `synced`, `succeeded` como si fueran equivalentes
- se propone mostrar aliases de actor role, adapter o direction sin contrato display-only
- la mezcla de idiomas en detail/sync ya no se puede controlar con una política temporal explícita

### Reporte 4. Hallazgos extra y qué nos deja resuelto

#### 4.1 Quick wins seguros

##### Detail
- títulos y subtítulos de panel locales
- botones de navegación y refresh
- wrappers locales de metadata:
  - `Record id`
  - `Secure token`
  - `Created`
  - `Submitted`
  - `Last sync`
- empty states locales:
  - attachments vacíos
  - dispatch jobs vacíos
  - sync events vacíos
- textos locales de shell del detail

##### Timeline
- empty state local
- quizá el wrapper visual del bloque, pero no el contenido narrativo ni evidence
- iconografía y layout, siempre que no se reetiquete semántica

##### Sync
- header copy
- subtítulos de panel
- `Refresh data`
- empty states
- meta text de métricas
- wrappers como `Adapter`, `Attempts`, `Updated`
- success strip del retry manteniendo ids intactos

#### 4.2 Zonas que deben esperar

##### Detail
- `schema.title`
- `schema.summary`
- `field.label`
- `section.title`
- `action.label`
- `stateLabel` / `stateDescription` sin glosario global
- `latestSync.status`
- `latestSync.summary`
- actor roles visibles
- feedback basado en errors crudos

##### Timeline
- titles runtime construidos con status o summary
- descriptions derivadas de adapter/direction/attempts
- detail pre blocks con payload/error/response
- remapeos semánticos a `RecordState`

##### Sync
- badges de status
- labels de filtros atados a enums
- métricas
- retry semantics
- `event.summary`
- `job.error`
- `event.error`
- `direction`
- `adapterId`

#### 4.3 Artefactos sugeridos para la siguiente etapa

- inventario de strings por owner:
  - frontend
  - shared/runtime
  - schema
  - backend/evidence
  - dudoso
- glosario operativo maestro:
  - `RecordState`
  - `DispatchStatus`
  - `SyncStatus`
  - actor roles
  - direction
  - retry semantics
- matriz de subject-of-action:
  - qué acción actúa sobre record
  - qué acción actúa sobre dispatch job
  - qué acción actúa sobre sync event
- tabla de evidence policy:
  - raw
  - normalized
  - user-facing
  - non-translatable
- checklist visual para errors largos y payload blocks
- pruebas automatizables:
  - status-to-label consistency
  - retry contract
  - metrics-to-filter consistency
  - timeline chronology
  - raw error display stability

#### 4.4 Simplificaciones posibles

Estas simplificaciones podrían bajar riesgo después, pero no deben asumirse todavía:
- separar de forma explícita en UI:
  - **copy local**
  - **schema content**
  - **evidence**
- encapsular display labels de estados en una sola capa con glosario transversal
- encapsular aliases display-only para actor role y direction, si se aprueban
- definir un componente de raw evidence para:
  - errors
  - payloads
  - summaries sensibles
- distinguir en feedback:
  - success local
  - normalized message
  - raw backend detail

#### 4.5 Contratos semánticos que conviene aclarar antes

1. **Glosario oficial de estados**
   - ¿cómo se nombra cada `RecordState`?
   - ¿cómo se nombra cada `DispatchStatus`?
   - ¿cómo se nombra cada `SyncStatus`?
   - ¿qué términos no deben homologarse?

2. **Política de summaries**
   - ¿`event.summary` se trata como evidence?
   - ¿puede traducirse?
   - ¿quién es su owner real?

3. **Política de errors**
   - ¿qué errors quedan crudos?
   - ¿cuáles se normalizan?
   - ¿qué surfaces pueden mostrar raw errors?

4. **Política de schema content**
   - ¿field labels, section titles, action labels, schema summaries entran en el frente de idioma?
   - ¿o quedan fuera hasta tener estrategia schema-driven?

5. **Política de actor roles y direction**
   - ¿se muestran crudos?
   - ¿se permiten aliases display-only?
   - ¿en qué superficies?

6. **Política de retry**
   - ¿qué wording oficial describe retry?
   - ¿retry actúa sobre job, sobre dispatch o sobre sync?
   - ¿qué outcome visible debe comunicar la UI?

#### 4.6 Preguntas abiertas reales

- ¿`event.summary` nace en adapter/backend/service o se considera copy de producto?
- ¿`record.title` es siempre dato del usuario/negocio o a veces copy controlada?
- ¿`stateLabel` y `stateDescription` deben ser el glosario oficial transversal o solo placeholders actuales?
- ¿los actor roles visibles deben quedar crudos para operación o tener alias legibles?
- ¿`direction` debe verse como `inbound/outbound` o como display labels más amables?
- ¿el secure token debe permanecer visible en el detail tal como está?
- ¿qué surfaces pueden mostrar errors crudos sin normalización?
- ¿se aceptará mezcla temporal de idiomas en evidencia operativa mientras no exista glosario global?
- ¿qué diferencia terminológica oficial se quiere preservar entre:
  - `succeeded`
  - `synced`
  - `failed`
  - `retryable`
  - `dispatched`

#### 4.7 Qué nos deja resuelto este chat

Este chat deja **muy bien amarrado** el frente de pre-intervención para `record detail`, `activity timeline` y `sync center` usando el zip como fuente principal de verdad y el formato universal como puerta de control.

##### Resuelto
- ya existe mapa real de superficies críticas
- ya está separada la copy local de:
  - schema content
  - evidence
  - semántica operativa sensible
- ya están identificados los owners tentativos sin inventar los dudosos
- ya existe lista roja por superficie
- ya están explícitos los riesgos de:
  - evidence
  - status semantics
  - retries
  - feedback/error messages
- ya existe validación operativa reusable y señales claras de stop
- ya se ve con nitidez dónde están los quick wins y dónde no conviene meter mano todavía

##### No resuelto todavía, a propósito
- implementación final
- estrategia final de idioma
- glosario oficial de estados
- política final de errors y summaries
- estrategia schema-driven de traducción

##### Valor práctico
La siguiente conversación ya no tendría que empezar desde exploración difusa. Podría arrancar desde una base controlada para decidir:
- primera ola segura
- exclusiones explícitas
- contratos a aclarar
- validaciones a automatizar

En otras palabras: este chat deja el terreno nivelado, marcado con conos, y sin cables sorpresa cruzando el pasillo.

---

## ✅ Cierre

Este dossier deja el trabajo en un punto mucho más civilizado:

- con **frentes separados**
- con **ownership más visible**
- con **riesgos y listas rojas** mejor delimitados
- con **validación** ya pensada antes de tocar implementación
- y con una base mucho más sólida para consolidar luego un plan maestro de ejecución

> **Traducción simple:**
>
> Ya no estamos entrando al template a ciegas ni a puro instinto.  
> Ya tenemos un mapa bastante serio para intervenir sin pisar mina.

