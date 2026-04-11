# 📘 Dossier Maestro Operativo
## `apps/external_interaction_template`
### Consolidado ejecutivo de profundización para intervención segura, rápida y trazable

> **Propósito**
>
> Unificar en un solo documento los **5 reportes de profundización operativa** generados por frentes paralelos, para convertir el mapeo previo en una base de ejecución más segura, más guiada, más simple de dividir y mejor preparada para trabajo en paralelo.
>
> Este documento **no propone implementación final todavía**.
> Su objetivo es dejar lista la cancha para intervenir sin hacer nada a lo pendejo.

---

## ✨ Qué contiene este consolidado

Este dossier reúne y normaliza estos frentes:

1. 🧭 **Shell global, top area, backdrop y layout global**
2. 🧱 **Shared UI, sistema visual y límites con runtime/theme**
3. 🏠 **Launcher e Inbox**
4. 🧪 **Flow runner, schema text y coupling con validation/state**
5. 🛰️ **Record detail, timeline y sync center**

---

## 🧠 Cómo usar este documento

### Orden recomendado de lectura
1. **Shell** para entender el techo visual y el presupuesto del top area.
2. **Shared UI / sistema visual** para congelar fronteras y evitar blast radius.
3. **Launcher / Inbox** para quick wins y casos piloto de superficie.
4. **Flow** con casco, porque aquí copy y persistencia ya se rozan.
5. **Detail / Timeline / Sync** con doble casco, porque aquí vive evidence y semántica operativa sensible.

### Regla madre
**Primero freeze, luego mini intervención, luego validación, luego evidencia, y solo después siguiente paso.**

### Leyenda rápida
- **✅ Confirmado**: sale del código o del dossier base y está tratado como confiable.
- **🧠 Inferido**: deducción operativa razonable para organizar la ejecución.
- **⚠️ Dudoso**: no conviene tocarlo sin contrato claro.
- **🛑 Zona roja**: debe quedar fuera de la primera ola de intervención.

---

## 🗂️ Índice

- [🧭 Shell global, top area, backdrop y layout global](#-capitulo-1--shell-global-top-area-backdrop-y-layout-global)
- [🧱 Shared UI, sistema visual y límites con runtime/theme](#-capitulo-2--shared-ui-sistema-visual-y-límites-con-runtimetheme)
- [🏠 Launcher e Inbox](#-capitulo-3--launcher-e-inbox)
- [🧪 Flow runner, schema text y coupling con validation/state](#-capitulo-4--flow-runner-schema-text-y-coupling-con-validationstate)
- [🛰️ Record detail, timeline y sync center](#-capitulo-5--record-detail-timeline-y-sync-center)
- [🚦 Siguiente jugada recomendada](#-siguiente-jugada-recomendada)

---

## 🎯 Resumen ejecutivo consolidado

### Lo más importante que ya quedó claro
- El template **sí puede dividirse en mini intervenciones seguras**, pero no por archivo completo sino por **frontera funcional**.
- Hay tres capas que disparan blast radius muy rápido:
  - **shell / top area**
  - **shared UI + formatting + runtime boundaries**
  - **semántica operativa** en flow, detail, timeline y sync
- Las superficies más nobles para empezar no son “las más fáciles visualmente”, sino las que tienen:
  - ownership más claro
  - menor dependencia de schema/state/backend
  - mejor validación observable

### Lo que conviene congelar antes de meter mano
- presupuestos del top area
- fronteras shell vs runtime
- qué shareds son shells nobles y cuáles son puentes peligrosos
- qué sale completamente de primera ola:
  - labels de estado
  - schema text
  - summaries operativos
  - retries
  - raw errors
  - evidence/timeline narrative

### Lo que sí se puede empujar con buen ROI
- baseline y budgets
- inventarios y matrices reutilizables
- shell local y consumers con bajo blast radius
- controls densos del inbox
- shells locales del detail/sync
- contratos y freeze maps de flow/detail/sync
- checklists de validación y evidencia

### Lo que no conviene mezclar
- shell + globals + consumers en el mismo batch
- layout + formatting global
- flow CTAs + state semantics
- sync shell + retry semantics
- timeline shell + timeline narrative
- shared noble cleanup + puentes semánticos

---

## 🧰 Artefactos que este dossier deja listos para la siguiente fase

- matriz de decisiones a congelar por frente
- mapa de mini intervenciones seguras
- mapa de paralelización por frente
- mapa de dependencias y acoplamientos reales
- checklist de validación por mini paso
- política de trazabilidad y evidencia
- identificación de quick wins vs zonas rojas

---


---

# 🧭 Capítulo 1 · Shell global, top area, backdrop y layout global

# 1. Resumen ejecutivo de profundización

## Qué frente me tocó
Este análisis trabaja **solo** el frente de:
- shell global
- top area / chrome superior
- sticky behavior
- backdrop / atmósfera
- layout global
- `globals.css` y ritmo vertical superior

## Qué ya estaba resuelto en el dossier
El dossier ya dejó bien aterrizado que:
- el shell se monta desde `app/layout.tsx` → `components/layout/app-frame.tsx` → `components/layout/app-shell.tsx` [Confirmado]
- `app-shell.tsx` concentra navegación, CTA globales, copy visible, chips runtime y la tarjeta `Current surface` [Confirmado]
- `ambient-backdrop.tsx` y `.grid-fade` son capas decorativas globales [Confirmado]
- `globals.css` es transversal y pega a densidad, superficies, chips, queue header, contraste y motion [Confirmado]
- el sistema ya es **top-heavy** porque en rutas principales se apilan `AppShell sticky` + `PageHeader` + stats + superficies de control [Confirmado]
- la frontera más delicada está entre **visual shell** y **runtime semantics** (`runtime.ts`, `use-accessibility-signals.ts`) [Confirmado]

## Qué huecos detecté
El dossier base explica bien el mapa, pero todavía faltaba inteligencia operativa sobre:
- cómo **partir** la futura intervención en mini pasos seguros
- qué mini pasos sí pueden ir **en paralelo** y cuáles no
- qué dependencias reales vuelven a `app-shell.tsx` y `globals.css` piezas de alto blast radius
- qué validar **antes y después** de cada mini paso
- qué conviene congelar primero para no abrir un frente de decisiones a mitad de la ejecución
- qué evidencia hay que guardar para no perder trazabilidad entre iteraciones

## Qué nueva inteligencia operativa agrego
Este documento agrega una segunda capa enfocada en ejecución controlada:
- un mapa de **mini intervenciones seguras**
- una matriz de **paralelización real**
- una tabla de **decisiones previas a congelar**
- un mapa de **acoplamientos concretos** por archivo/componente
- una validación **operativa** por mini paso, no solo por ruta
- una política de **trazabilidad y evidencia** para no perder contexto en corridas sucesivas
- una separación útil entre **quick wins reales** y **zonas rojas**

---

# 2. Lo que aún falta investigar o confirmar

| Incógnita | Por qué importa | Riesgo que evita | ¿Bloquea una primera intervención? | Dónde confirmarlo | Estado |
|---|---|---|---|---|---|
| Si el bloque inferior del shell (`Current surface` + chips runtime) es diagnóstico o futura zona de preferencias | Define cuánto puede simplificarse, moverse o compactarse sin abrir semántica nueva | Evita convertir una limpieza visual en cambio de producto/comportamiento | **No** bloquea una primera intervención visual, pero sí bloquea cambios estructurales fuertes | `components/layout/app-shell.tsx`, `src/lib/ui/runtime.ts`, criterio de producto | Dudoso |
| Si `Brand` es solo adorno visual o identidad funcional real | Cambia si puede moverse/reducirse sin afectar meaning | Evita tocar algo que luego represente tenant/modo/entorno | **No** bloquea quick wins visuales; **sí** bloquea rediseño semántico del shell | `src/lib/ui/runtime.ts`, uso real en otras superficies | Dudoso |
| Si el patrón `AppShell sticky + PageHeader` se conservará o se considera deuda visual a reducir | Afecta por completo el presupuesto de altura del top area | Evita arreglar spacing fino sobre una estructura que luego cambiará de forma mayor | **No** bloquea microajustes; **sí** bloquea una intervención de jerarquía global | `components/layout/app-shell.tsx` + `components/ui/page-header.tsx` + rutas `/`, `/inbox`, `/sync`, `/flow/*`, `/record/*` | Dudoso |
| Presupuesto máximo aceptable de altura del shell por breakpoint | Sin budget no hay criterio objetivo para aceptar o rechazar ajustes | Evita discusión subjetiva tipo “se ve pesado” sin métrica | **Sí**, conviene definirlo antes de tocar sticky/top area | QA visual por breakpoint; captura de shell en `sm`, `md`, `lg`, `xl` | Pendiente |
| Si `globals.css` es el lugar correcto para tocar ritmo vertical o si parte del ritmo vive mejor en componentes | Cambia el orden de intervención y el riesgo de regresión transversal | Evita tocar tokens globales para resolver un problema local de una ruta | **No** bloquea investigación; **sí** bloquea cambios globales de spacing | `app/globals.css`, consumidores con `page-stack`, `queue-header`, `surface-*` | Pendiente |
| Si las vistas con sidebars sticky (`record`, `flow`) toleran otro shell height sin colisión visual | Es el punto más frágil en desktop `xl` | Evita arreglar launcher/inbox y romper detail/flow | **Sí** para cualquier cambio de sticky/top offsets | `components/records/record-detail.tsx`, `components/flow/flow-runner.tsx` | Confirmar con validación |
| Qué parte del backdrop se percibe como valor y qué parte es puro costo visual | Permite decidir si se toca atmósfera o se congela | Evita perder tiempo en una capa decorativa mientras el problema real está en jerarquía y spacing | **No** bloquea una primera intervención de shell/layout | `components/layout/ambient-backdrop.tsx`, `app/layout.tsx`, percepción comparada con shell | Inferido |
| Si `page-stack` debe seguir siendo el espaciado dominante transversal | Afecta ritmo vertical de todas las vistas con header + stats + surface | Evita duplicar spacing en componente y utility al mismo tiempo | **No** bloquea quick wins locales; **sí** bloquea normalización transversal | `app/globals.css`, rutas que usan `page-stack` | Pendiente |
| Si los `PageHeader` de rutas deben compactarse cuando ya existe shell “grande” arriba | Impacta mucho la densidad del primer viewport | Evita tratar el síntoma en shell cuando parte del exceso vive en consumidores | **No** bloquea investigación; **sí** bloquea una solución final del top-heavy layout | `components/ui/page-header.tsx` y consumidores por ruta | Dudoso |
| Si motion/contrast deben permanecer completamente runtime-driven sin overrides locales | Toca a11y, data attributes y clases globales | Evita meter hacks visuales que rompan accesibilidad | **Sí** para cambios que involucren backdrop, blur o contrast tokens | `src/lib/ui/use-accessibility-signals.ts`, `src/lib/ui/runtime.ts`, `app/globals.css` | Confirmado como dependencia |

---

# 3. Decisiones previas que conviene congelar

| Decisión | Opciones | Recomendación | Por qué | Costo de no decidirla ahora | ¿Bloquea ejecución? |
|---|---|---|---|---|---|
| Presupuesto del top area por breakpoint | no definirlo / definirlo por feeling / definirlo con budget explícito | **Congelar un budget explícito** | El shell sticky ya es una superficie dominante; sin presupuesto cualquier ajuste es debatible y regresivo | Alto: se hacen cambios “bonitos” que luego no pasan QA visual | **Sí** |
| Trato del bloque inferior del shell | dejarlo como está / compactarlo visualmente / reinterpretarlo como panel de preferencias | **Tratarlo como resumen diagnóstico por ahora** | Permite intervenir layout sin abrir semántica nueva | Medio: se mezclan cambios visuales con producto/comportamiento | **Sí** para cambios estructurales grandes |
| Estrategia sobre doble encabezado | mantener shell + PageHeader / compactar PageHeader en rutas / replantear jerarquía después | **Aceptar el patrón actual como baseline temporal** y solo medirlo | Así la primera intervención puede ser incremental y no arquitectónica | Alto: sin decisión, cualquier ajuste de spacing se vuelve discutible | **Sí** para rediseño jerárquico; **no** para microtuning |
| Alcance de `globals.css` | tocar tokens globales ya / primero tocar solo estructura local / mezclar ambos | **Primero ajustes locales, luego tokens si siguen siendo necesarios** | Baja el blast radius inicial | Alto: tocar global primero puede romper muchas superficies por arreglar una | **Sí** para cambios de spacing global |
| Backdrop | intervenirlo en la misma ola / congelarlo salvo bugs evidentes | **Congelarlo salvo quick wins visuales triviales** | No parece ser el principal origen del top-heavy layout | Medio: distrae del problema real del shell | **No** |
| Sticky strategy | tocar `top-4`, `z-30`, margins y offsets al inicio / dejar sticky igual hasta medir budgets | **Medir primero, tocar después** | `record` y `flow` ya tienen sidebars sticky en `xl:top-24` | Alto: tocar sticky a ciegas puede generar colisiones sutiles | **Sí** |
| Qué carril corre primero | shell + globals + consumers todo junto / shell primero / consumers primero / budget y validación primero | **Budget + validación base → shell local → consumers → globals si hace falta** | Reduce ruido y separa causa de síntoma | Alto: si se mezcla todo, no sabrás qué cambio mejoró o rompió algo | **Sí** |
| Qué hacer con `runtime.ts` | tocarlo junto al shell / evitarlo salvo necesidad fuerte | **Evitar tocarlo salvo necesidad muy justificada** | Es mezcla de visual + runtime semantics | Alto: scope creep y ownership dudoso | **Sí** |
| Qué considerar evidencia mínima de cada mini paso | capturas informales / nada / checklist + capturas + diff de archivos | **Checklist + capturas + archivo tocado + decisión registrada** | Permite comparar sin reabrir exploración desde cero | Medio | **No**, pero sí acelera y ordena |

---

# 4. Mapa de mini intervenciones seguras

## Mini intervención 1. Baseline de altura y jerarquía del top area
- **Objetivo:** fijar presupuesto visual y puntos de control antes de mover una sola pieza.
- **Archivos probables:** ninguno obligatorio para cambio; referencia principal en `components/layout/app-shell.tsx`, `components/ui/page-header.tsx`, rutas `/`, `/inbox`, `/sync`, `/flow/[schemaId]`, `/record/[recordId]`.
- **Qué sí toca:** medición, captura y checklist comparativa.
- **Qué no toca:** código, tokens, sticky offsets.
- **Precondiciones:** dossier base leído, rutas críticas identificadas.
- **Riesgo:** bajo.
- **Resultado visible esperado:** queda una línea base objetiva de altura/jerarquía por breakpoint.
- **Validación mínima:** capturas de primer viewport en `sm`, `md`, `lg`, `xl`; registro de dónde el shell ya compite con el contenido.
- **¿Puede correrse en paralelo?:** sí, y debería ser el primer carril.

## Mini intervención 2. Limpieza local del shell superior
- **Objetivo:** reducir ruido o rigidez dentro de `app-shell.tsx` sin tocar semántica runtime.
- **Archivos probables:** `components/layout/app-shell.tsx`.
- **Qué sí toca:** orden visual de zonas, alineación interna, spacing local, relación nav/CTA/chips, estructura interna del shell.
- **Qué no toca:** `runtime.ts`, `use-accessibility-signals.ts`, consumers de `PageHeader`, tokens globales.
- **Precondiciones:** mini intervención 1 terminada; decisión congelada sobre no reinterpretar el bloque runtime como panel de preferencias.
- **Riesgo:** medio-alto.
- **Resultado visible esperado:** shell más legible y menos cargado sin cambiar meaning ni contracts.
- **Validación mínima:** revisar launcher + inbox + sync + flow + record en primer viewport; nav/CTA no deben empeorar wrap.
- **¿Puede correrse en paralelo?:** **no** con cambios globales de `globals.css`; **sí** con documentación/evidencia.

## Mini intervención 3. Ajuste de sticky y offsets
- **Objetivo:** afinar `sticky`, `top`, `margin-bottom` y convivencia con sidebars sticky.
- **Archivos probables:** `components/layout/app-shell.tsx`, potencialmente consumidores con `xl:sticky xl:top-24`.
- **Qué sí toca:** `header.sticky top-4 z-30 mb-6` y posibles offsets relacionados.
- **Qué no toca:** copy, backdrop, tokens globales salvo necesidad concreta.
- **Precondiciones:** baseline de altura definida; evaluación previa en detail/flow.
- **Riesgo:** alto.
- **Resultado visible esperado:** menor invasión del shell al scrollear y mejor convivencia con sidebars.
- **Validación mínima:** scroll real en `/record/*` y `/flow/*`; no colisión visual entre shell y panel derecho sticky.
- **¿Puede correrse en paralelo?:** **no** con mini intervención 4 o 5.

## Mini intervención 4. Compactación de top-area consumers
- **Objetivo:** bajar peso del primer viewport atacando consumidores inmediatos, no solo el shell.
- **Archivos probables:** `components/ui/page-header.tsx`, `app/page.tsx`, `components/records/record-inbox.tsx`, `components/sync/sync-center.tsx`, `app/flow/[schemaId]/page.tsx`, `components/records/record-detail.tsx`.
- **Qué sí toca:** uso de `PageHeader`, densidad local de stats, ritmo entre header y siguiente bloque.
- **Qué no toca:** shell global, runtime semantics, backdrop.
- **Precondiciones:** aceptar temporalmente el patrón shell + PageHeader y decidir qué rutas son candidatas a compactación primero.
- **Riesgo:** medio-alto.
- **Resultado visible esperado:** contenido útil aparece antes sin rediseñar el shell completo.
- **Validación mínima:** launcher e inbox primero; luego detail/flow/sync.
- **¿Puede correrse en paralelo?:** sí entre rutas **si** no se toca `PageHeader` base en la misma corrida.

## Mini intervención 5. Normalización local de spacing en shell y top area
- **Objetivo:** corregir huecos verticales/horizontales demasiado generosos o inconsistentes.
- **Archivos probables:** `components/layout/app-shell.tsx`, `components/ui/page-header.tsx`, consumidores puntuales.
- **Qué sí toca:** `gap-*`, `mt-*`, `mb-*`, padding local, separación entre shell y contenido.
- **Qué no toca:** `globals.css` global, runtime, backdrop.
- **Precondiciones:** mini 1 terminada; idealmente mini 2 parcialmente definida.
- **Riesgo:** medio.
- **Resultado visible esperado:** top area menos inflado y más consistente sin blast radius global.
- **Validación mínima:** revisar launcher/inbox y una ruta con sidebar sticky.
- **¿Puede correrse en paralelo?:** **sí** con baseline/documentación; **no** con cambios globales de spacing.

## Mini intervención 6. Revisión controlada de `globals.css`
- **Objetivo:** tocar solo lo que de verdad sea transversal, después de probar que lo local no basta.
- **Archivos probables:** `app/globals.css`.
- **Qué sí toca:** `--page-gap`, `.page-stack`, `.shell-chip`, `.queue-header`, superficies/tokens que realmente expliquen el problema.
- **Qué no toca:** copy, runtime semantics, layout de rutas específico si puede evitarse.
- **Precondiciones:** mini 2 y/o 5 ejecutadas o descartadas; evidencia de que el problema sigue siendo transversal.
- **Riesgo:** alto.
- **Resultado visible esperado:** mejora sistémica del ritmo vertical y consistencia entre superficies.
- **Validación mínima:** todas las rutas críticas; especial atención a inbox, sync y detail.
- **¿Puede correrse en paralelo?:** **no** con mini 2, 3, 4 o 5.

## Mini intervención 7. Quick win visual del backdrop
- **Objetivo:** simplificar o estabilizar atmósfera si está metiendo ruido visual real.
- **Archivos probables:** `components/layout/ambient-backdrop.tsx`, quizá `app/layout.tsx`.
- **Qué sí toca:** intensidad, blobs, profundidad, relación con `.grid-fade`.
- **Qué no toca:** shell, sticky, spacing del contenido.
- **Precondiciones:** confirmar que el problema percibido sí viene del backdrop y no del top area.
- **Riesgo:** bajo-medio.
- **Resultado visible esperado:** fondo más limpio o menos competitivo.
- **Validación mínima:** comparar con shell actual en launcher y sync.
- **¿Puede correrse en paralelo?:** sí, siempre que no se mezcle con `globals.css` global de contrast/motion.

## Mini intervención 8. Hardening de loading/error/not-found dentro del shell
- **Objetivo:** asegurar que estados sistémicos no rompan la jerarquía del frente.
- **Archivos probables:** `app/loading.tsx`, `components/ui/page-loading.tsx`, `app/error.tsx`, `app/not-found.tsx`.
- **Qué sí toca:** proporción visual y consistencia con el shell.
- **Qué no toca:** shell runtime, backdrop, consumer headers normales.
- **Precondiciones:** baseline visual lista.
- **Riesgo:** medio.
- **Resultado visible esperado:** estados sistémicos no se sienten “afuera del sistema”.
- **Validación mínima:** cargar loading/error/not-found en primer viewport y compararlos contra rutas normales.
- **¿Puede correrse en paralelo?:** sí, porque su acoplamiento con shell es visual pero acotado.

---

# 5. Mapa de paralelización

| Tareas paralelizables | Tareas no paralelizables | Dependencias | Orden mínimo recomendado | Combinaciones peligrosas |
|---|---|---|---|---|
| Baseline de altura + documentación de evidencia | Cambios de `app-shell.tsx` + cambios de `globals.css` | Ninguna fuerte para baseline | 1) baseline 2) shell local 3) consumers 4) globals si hace falta | tocar `app-shell.tsx` y `globals.css` a la vez |
| Backdrop audit + baseline visual | Sticky offsets + sidebars sticky | backdrop puede evaluarse solo | corre en paralelo con baseline | tocar backdrop y contrast/motion global al mismo tiempo |
| Hardening de loading/error/not-found | Cambio de top-area consumers usando `PageHeader` base | loading/error/not-found son acotados | puede correr después del baseline | tocar `PageHeader` base y loading shell al mismo tiempo sin baseline |
| Compactación por ruta en launcher vs sync | Revisión global de `PageHeader` base + compactación de todas las rutas a la vez | cada ruta puede explorarse separada si no se toca base | launcher → inbox → sync → flow/detail | compactar `PageHeader` base mientras varias rutas lo modifican indirectamente |
| Documentación de decisiones + registro de riesgos | `runtime.ts` + `app-shell.tsx` + sticky offsets | la documentación siempre puede correr | continuo durante todo el frente | ninguno si es solo trazabilidad |
| Revisión de wrappers locales de spacing en rutas | Ajuste global de `--page-gap` | primero descartar que el problema sea local | shell local antes de tokens globales | tocar `page-stack` global y además gaps locales en la misma corrida |
| QA de sidebars sticky (`record`, `flow`) | cambios de sticky shell sin revisar sidebars | detail/flow dependen de shell height | antes o inmediatamente después del cambio sticky | tocar `top-4` del shell y asumir que `xl:top-24` seguirá bien |

## Orden mínimo recomendado
1. **Baseline y evidencia**
2. **Congelar decisiones previas**
3. **Ajustes locales de `app-shell.tsx`**
4. **Validación transversal rápida**
5. **Compactación de consumers si sigue top-heavy**
6. **Solo después considerar `globals.css`**
7. **Backdrops y refinamientos atmosféricos al final**

## Combinaciones peligrosas
- `app-shell.tsx` + `app/globals.css` en una sola corrida
- sticky shell + compactación de `PageHeader` base al mismo tiempo
- `runtime.ts` + shell visual en el mismo batch
- top-area consumers múltiples + cambio global de `page-stack`
- backdrop + contrast/motion global sin aislar causa visual

---

# 6. Dependencias y acoplamientos reales

| Archivo / componente | De qué depende | Tipo de acoplamiento | Nivel de riesgo | Implicación para la intervención |
|---|---|---|---|---|
| `app/layout.tsx` | `AmbientBackdrop`, `.grid-fade`, `AppFrame`, metadata raíz | estructural global | alto | cualquier cambio pega a todas las rutas y estados sistémicos |
| `components/layout/app-frame.tsx` | `usePathname()`, `useAccessibilitySignals()`, `AppShell` | routing + runtime bridge | medio-alto | es un puente del shell; no conviene mezclar cambios visuales con lógica aquí |
| `components/layout/app-shell.tsx` | `createRuntimeUiContext`, `runtimeDataAttributes`, `runtimeMotionClass`, `runtimeContrastClass`, `formatHumanLabel`, navegación y CTA globales | visual + runtime semantics | **muy alto** | hotspot principal; ideal para cambios locales, peligroso para scope creep |
| `components/layout/ambient-backdrop.tsx` | `framer-motion`, `useReducedMotion` | decorativo + a11y motion | medio | puede ajustarse sin tocar shell, pero no resuelve top-heavy layout por sí solo |
| `app/globals.css` | data attributes runtime, tokens, components shared (`surface-*`, `shell-chip`, `queue-header`, `page-stack`) | estilo transversal | **muy alto** | tocar aquí exige validación amplia y control fino |
| `src/lib/ui/runtime.ts` | áreas, densidad, preset, role, contrast, brand, data attributes | runtime semántico | **muy alto** | no tocar salvo necesidad fuerte; mezclarlo con shell visual amplía el frente |
| `src/lib/ui/use-accessibility-signals.ts` | media queries del navegador | accesibilidad/runtime | alto | si cambias motion/contrast/blurs debes respetar este contrato |
| `components/ui/page-header.tsx` | consumers por ruta, `runtimeShellClass` opcional | shared layout consumer-heavy | alto | tocarlo impacta launcher, inbox, sync, flow, detail y playground |
| `components/ui/page-loading.tsx` | `Surface`, `LiveRegion`, variantes de loading | shared sistémico | medio | conviene validarlo porque forma parte del shell percibido |
| `app/page.tsx` | `PageHeader`, `StatCard`, `Surface`, shell visible | consumer top-heavy | medio-alto | buen caso piloto para compactación segura |
| `components/records/record-inbox.tsx` | `PageHeader`, `StatCard`, `Surface`, `FilterPills`, `queue-header`, shell visible | consumer top-heavy + scan-speed | **alto** | cualquier cambio debe respetar velocidad de triage |
| `components/sync/sync-center.tsx` | `PageHeader`, `StatCard`, `Surface`, shell visible | consumer top-heavy + panels dobles | alto | útil para validar ritmo vertical y panels shell/inner shell |
| `components/records/record-detail.tsx` | `PageHeader`, stats, side panel sticky `xl:top-24` | top-heavy + sticky collision | **muy alto** | principal prueba de fuego para cambios de sticky shell |
| `components/flow/flow-runner.tsx` + `app/flow/[schemaId]/page.tsx` | `PageHeader`, resume surface, side panel sticky `xl:top-24` | top-heavy + sticky collision | **muy alto** | segundo caso crítico para offsets y primer viewport |

---

# 7. Validación operativa por mini paso

| Mini intervención | Qué validar | Dónde validar | Tipo de validación | Criterio de aceptación | Señal de stop | Evidencia a guardar |
|---|---|---|---|---|---|---|
| Baseline de altura y jerarquía | altura relativa shell vs primer contenido útil | `/`, `/inbox`, `/sync`, `/flow/*`, `/record/*` | visual comparativa | existe baseline clara por breakpoint | no se logra acordar qué se considera “demasiado alto” | capturas `sm/md/lg/xl` + nota de altura percibida |
| Limpieza local del shell | nav, CTA, chips, bloque inferior, wraps | todas las rutas | visual + responsive | el shell se siente más claro sin perder info ni meaning | aparecen wraps peores o se vuelve más difícil encontrar nav/CTA | capturas antes/después + diff de `app-shell.tsx` |
| Ajuste de sticky y offsets | shell sticky no tapa ni domina demasiado; sidebars no chocan | `/record/*`, `/flow/*`, `/inbox` | scroll real + visual | shell visible pero no invasivo; sidebars siguen legibles | colisión con `xl:top-24`, contenido tapado o saltos raros al scrollear | video corto/gif o secuencia de capturas durante scroll |
| Compactación de consumers | `PageHeader` + stats + surface superior respiran mejor | launcher e inbox primero; luego sync/detail/flow | visual por ruta | primer contenido útil aparece antes y la jerarquía no se rompe | mejora una ruta y empeora scan speed en inbox o clarity en detail | capturas por ruta + nota de qué se compactó |
| Normalización local de spacing | gaps/padding más consistentes | shell + ruta piloto | visual comparativa | menor sensación de aire inflado sin sensación de hacinamiento | aparecen inconsistencias entre rutas o componentes hermanos | diff + check rápido en 3 rutas |
| Revisión de `globals.css` | cambio realmente transversal, no arreglo local disfrazado | todas las rutas críticas | visual transversal | mejora consistente en varias superficies | una ruta mejora y dos se degradan | listado exacto de clases/tokens tocados + capturas multi-ruta |
| Quick win del backdrop | la atmósfera compite menos sin perder identidad | `/` y `/sync` mínimo | visual comparativa | shell/contenido gana claridad y backdrop sigue “de fondo” | el cambio es perceptible pero no resuelve nada del problema central | comparativa A/B de capturas |
| Hardening de loading/error/not-found | estados sistémicos entran bien al sistema del shell | loading, not-found, error | visual + consistencia | no se sienten pantallas “huérfanas” ni demasiado densas | alguno queda con jerarquía o spacing fuera del sistema | capturas de cada estado |

---

# 8. Trazabilidad y evidencia

## Qué registrar

### Decisiones
Registrar al menos:
- presupuesto de altura aprobado por breakpoint
- si el bloque inferior del shell se trata como diagnóstico o no
- si el patrón `AppShell + PageHeader` queda congelado temporalmente
- si `globals.css` entra o queda fuera en cada corrida
- si alguna ruta se usa como piloto antes que las demás

### Hallazgos
Registrar:
- dónde realmente estaba el exceso de altura
- si el problema vino de shell, consumers o ambos
- qué rutas fueron más sensibles (`inbox`, `record`, `flow` son candidatas obvias)
- si algún ajuste visual arrastró semántica/runtime sin querer

### Bloqueos
Registrar:
- dudas sobre `runtime.ts`
- dudas sobre `Brand`
- dudas sobre el bloque runtime como futura zona de preferencias
- conflictos entre sticky shell y sticky sidebars
- necesidad de tocar `globals.css` sin evidencia suficiente

### Riesgos
Registrar por mini paso:
- blast radius esperado
- superficies de validación obligatoria
- combinaciones que no deben mezclarse
- stop conditions específicas

### Validaciones
Guardar por cada mini paso:
- checklist corrida
- rutas verificadas
- breakpoints usados
- resultado: pasa / pasa con observaciones / stop

### Archivos tocados
Para cada corrida:
- lista exacta de archivos modificados
- propósito de cada archivo dentro del mini paso
- si el cambio fue local o transversal

### Checkpoints conceptuales
Conviene tener checkpoints explícitos:
1. baseline aprobada
2. decisiones previas congeladas
3. shell local mejorado
4. sticky validado contra sidebars
5. consumers compactados o descartados
6. globals solo si sigue siendo necesario

### Artefactos a conservar
- capturas por ruta y breakpoint
- diff resumido por mini paso
- tabla de budgets del top area
- tabla de riesgos por mini intervención
- lista de rutas que se usaron como smoke test
- versión del checklist de validación aplicada en cada corrida

---

# 9. Quick wins reales vs zonas rojas

## Quick wins

### 1) Baseline de altura y jerarquía del top area
**Por qué cae aquí:** no toca código y reduce muchísimo la fricción posterior.

### 2) Reorganización visual local dentro de `app-shell.tsx`
**Por qué cae aquí:** concentra mucho del problema visible y se puede tocar sin entrar a `runtime.ts`.

### 3) Ajustes locales de spacing en shell antes de tocar `globals.css`
**Por qué cae aquí:** baja riesgo transversal y suele capturar el 80% del “se siente pesado”.

### 4) Hardening de `loading`, `error` y `not-found`
**Por qué cae aquí:** son superficies chicas, visibles y alineadas con el frente, con acoplamiento controlado.

### 5) Compactación piloto en launcher
**Por qué cae aquí:** launcher es el consumidor más limpio para ensayar reducción de top-heaviness sin semántica delicada.

### 6) Auditoría del backdrop sin tocar su lógica de accesibilidad
**Por qué cae aquí:** permite decidir si vale la pena intervenir atmósfera o congelarla.

## Zonas rojas

### 1) `app/globals.css` como primer martillo
**Por qué cae aquí:** cambia demasiado de una sola vez; si arregla algo en shell puede romper inbox, sync o detail.

### 2) `runtime.ts`
**Por qué cae aquí:** mezcla config, semántica runtime y labels visibles. Tocar esto para resolver un problema de layout es camino a scope creep.

### 3) Sticky shell + sidebars sticky en la misma corrida sin baseline
**Por qué cae aquí:** detail y flow ya usan `xl:sticky xl:top-24`; un ajuste pequeño arriba puede desalinear todo abajo.

### 4) Rehacer a la vez shell y `PageHeader` base
**Por qué cae aquí:** dobla el frente. Ya no sabrás si el problema o la mejora viene del chrome superior o de los consumers.

### 5) Usar backdrop como distractor estético
**Por qué cae aquí:** el problema principal detectado es jerarquía/altura/spacing, no falta de ambientación.

### 6) Cambios simultáneos en múltiples consumers + cambio global de spacing
**Por qué cae aquí:** hace imposible atribuir causa y complica muchísimo la trazabilidad.

---

# 10. Artefactos adicionales que conviene producir

| Nombre | Para qué sirve | Prioridad | ¿Bloquea o solo ayuda? |
|---|---|---|---|
| `shell-top-area-budget-matrix.md` | documentar altura/jerarquía aceptable por breakpoint | alta | **Bloquea** una intervención seria del top area |
| `shell-mini-steps-checklist.md` | checklist operativo por mini intervención | alta | ayuda mucho; casi debería tratarse como obligatoria |
| `shell-validation-smoke-routes.md` | lista mínima de rutas y vistas a revisar siempre | alta | ayuda, pero no bloquea |
| `shell-risk-register.md` | registro vivo de riesgos, stops y mitigaciones del frente | media-alta | ayuda mucho |
| `shell-before-after-capture-grid.md` | matriz de capturas antes/después por breakpoint y ruta | media-alta | ayuda mucho |
| `shell-acoplamientos-reales.md` | resumen corto de dependencias reales del shell | media | ayuda |
| `shell-decisions-frozen.md` | documento corto con decisiones congeladas del frente | alta | **Bloquea** rediseños o cambios estructurales sin dirección |
| `shell-consumer-pilot-order.md` | orden oficial de rutas piloto para compactación | media | ayuda |

---

# 11. Qué nos deja resuelto este chat

## Qué parte del frente quedaría lista para ejecución
Después de este entregable queda prácticamente lista la **fase de diseño de intervención** del frente shell/top area:
- ya hay orden sugerido de mini pasos
- ya está separada la parte que sí puede correrse en paralelo de la que no
- ya está claro que el primer carril debe ser **baseline + decisiones congeladas**, no cambio de código a ciegas
- ya están ubicados los puntos de mayor riesgo real: `app-shell.tsx`, `globals.css`, sticky offsets y sidebars sticky
- ya existe una validación operativa por mini paso, no solo una checklist genérica

## Qué seguiría bloqueado
Seguiría bloqueado hasta congelar decisiones:
- tocar sticky offsets sin budget de altura
- tocar `runtime.ts` por razones visuales
- meter `globals.css` a una primera corrida sin descartar ajustes locales
- replantear la jerarquía shell + `PageHeader` sin decidir si el patrón actual es baseline temporal o deuda a atacar

## Qué decisiones quedarían casi cerradas
Quedan casi cerradas estas decisiones, salvo que el equipo quiera reabrirlas deliberadamente:
- **no** empezar por `globals.css`
- **no** mezclar shell visual con `runtime.ts`
- **no** correr a la vez shell, sticky y consumers sin baseline
- usar launcher como piloto limpio y detail/flow como pruebas de fuego para sticky
- tratar backdrop como carril secundario, no como solución principal

## Qué intervención futura se volvería más rápida gracias a este entregable
Se vuelve mucho más rápida la futura intervención de:
- simplificación del shell superior
- reducción de top-heaviness
- ajuste controlado de sticky behavior
- compactación de consumers del top area
- refinamiento de spacing global solo si queda demostrado que lo local no alcanza
- trazabilidad de cambios sucesivos sin perder el hilo entre corridas

## Qué nos deja resuelto este chat
Este chat nos deja resuelto el **andamiaje operativo** del frente.

No repite el dossier: lo convierte en secuencia de trabajo.

En concreto, deja pavimentado:
- **cómo dividir** el frente en mini intervenciones seguras
- **qué congelar antes** de mover piezas
- **qué puede correr en paralelo** y qué no
- **qué validar** antes y después de cada mini paso
- **qué registrar** para no perder trazabilidad
- **dónde están los quick wins** y dónde están las zonas rojas

En una línea:

> la siguiente intervención sobre shell/top area ya no tendría que arrancar con exploración difusa ni con cirugía a ciegas; puede arrancar con carriles, gates, validación y evidencia listos para trabajar más rápido y con mucho menos blast radius.

---

# 🧱 Capítulo 2 · Shared UI, sistema visual y límites con runtime/theme

# 1. Resumen ejecutivo de profundización

## Qué frente me tocó
La profundización se enfoca en el frente de **shared UI, sistema visual compartido, boundaries con runtime/theme y formatting layer como dependencia visual/operativa**, usando como base principal el capítulo del dossier sobre arquitectura i18n, shared UI y formatting layer, pero **sin convertir este entregable en otro frente de idioma**.

## Qué ya estaba resuelto en el dossier
El dossier ya dejó amarrado lo esencial:
- que varios shared son solo **shells visuales** y no dueños del copy;
- que `runtime.ts` no debe volverse dueño de labels visibles, locale ni formatting humano;
- que `utils.ts`, `ui/contracts.ts`, `record-view.ts`, `page-loading.tsx`, `filter-pills.tsx` y `app-shell.tsx` concentran fugas reales;
- que el shell y el formatting layer son frentes transversales con alto blast radius;
- que `schema` y `data` no deben colarse a la primera ola de centralización.

## Qué huecos detecté
El dossier deja bien mapeado el qué, pero todavía había varios huecos operativos para una intervención segura:
1. **No estaba suficientemente separado el concepto de “shared crítico” vs “shared noble”**.
2. **Faltaba aterrizar mini intervenciones ejecutables sin meter mano a runtime ni a theme de forma accidental**.
3. **No estaba explicitado cuáles props y patrones generan deriva visual aunque el texto venga correcto**.
4. **Faltaba una vista clara de paralelización** para que varias piezas se preparen sin chocar.
5. **Faltaba una política de evidencia y checkpoints** para que el cleanup futuro no se convierta en arqueología triste.

## Qué nueva inteligencia operativa agrego
Esta profundización agrega cinco capas de control:
- clasificación de **shared críticos** vs **shared shell**;
- decisiones previas que conviene congelar antes de cualquier intervención real;
- mapa de **mini intervenciones seguras** y su paralelización;
- mapa de **acoplamientos reales** entre visual system, runtime y formatting;
- estructura de **trazabilidad, evidencia y artefactos** para que el cleanup posterior sea más rápido y menos riesgoso.

## Tesis operativa de este entregable
La intervención más segura no empieza “traduciendo shareds” ni “tocando runtime”. Empieza por:
1. congelar fronteras,
2. identificar contratos visuales,
3. consolidar formatting leaks,
4. separar shells de puentes semánticos,
5. y dejar el terreno listo para mini pasos paralelizables.

# 2. Lo que aún falta investigar o confirmar

| Incógnita | Por qué importa | Riesgo que evita | ¿Bloquea una primera intervención? | Dónde confirmarlo | Certeza |
|---|---|---|---|---|---|
| Si el bloque inferior del `AppShell` es solo diagnóstico o futuro panel de preferencias | cambia la frontera entre runtime visible y controles reales | meter controles en una zona pensada solo para lectura | No bloquea una primera ola documental; sí bloquea mover piezas del shell | `components/layout/app-shell.tsx`, `src/lib/ui/runtime.ts`, decisión de producto | [D] |
| Si `BrandProfile.label` debe seguir existiendo como label visible o quedarse como dato técnico | define si esa semántica sale de runtime o permanece ahí | mezclar label traducible con config técnica | No bloquea inventario; sí bloquea cleanup de shell | `src/lib/ui/runtime.ts`, `components/layout/app-shell.tsx` | [D] |
| Si `PageHeader` y el shell sticky convivirán como patrón estable o deuda visual temporal | afecta consistencia de top area y budget vertical | tocar headers locales cuando el problema real es arquitectura de top area | No bloquea mini pasos de inventario; sí bloquea refino visual estructural | `components/layout/app-shell.tsx`, `components/ui/page-header.tsx`, rutas principales | [D] |
| Cuál será la política oficial de fallback visual para valores vacíos (`-`, vacío, placeholder textual) | hoy hay fallback disperso en `utils.ts`, `ui/contracts.ts` y callers | mezcla de placeholders, inconsistencia visual y ruido semántico | No bloquea inventario; sí bloquea consolidación de formatting | `src/lib/utils.ts`, `src/lib/ui/contracts.ts`, consumers de cards/stats/detail | [C][D] |
| Si `toDisplayText()` o `formatValue()` será la autoridad única de formatting visible | hoy hay duplicación real | divergencia entre stats, detail, timeline y cards | Sí bloquea una intervención real sobre formatting | `src/lib/utils.ts`, `src/lib/ui/contracts.ts`, `src/lib/ui/record-contracts.ts`, `components/ui/stat-card.tsx` | [C] |
| Si los labels de estado quedan congelados como shared canónicos antes de tocar `StateBadge` | `StateBadge` es puente, no shell puro | tocar badge y reventar consistencia cross-surface | Sí bloquea tocar `state-badge` más allá de inventario | `src/lib/core/record-view.ts`, `components/ui/state-badge.tsx`, dossier de inbox/detail/sync | [C][D] |
| Si la clave del top-area budget será por breakpoint o por “familia de superficie” | determina cómo validar cambios del shell y headers | corregir un layout en desktop y romper tablet/móvil | No bloquea inventario; sí bloquea cambios visuales del shell | `components/layout/app-shell.tsx`, `app/globals.css`, rutas `/`, `/inbox`, `/record/[recordId]`, `/flow/[schemaId]`, `/sync` | [I] |
| Si `Surface` debe seguir soportando dos patrones de header distintos | hoy puede renderizar con `SectionHeader` o con un bloque alterno | drift visual y decisiones inconsistentes de spacing/copy | No bloquea quick wins; sí bloquea cleanup de sistema visual | `components/ui/surface.tsx`, `components/ui/section-header.tsx` | [C] |
| Si `DetailList` debe seguir usando `label:value` como key derivada | el render actual acopla estabilidad del key a copy y value | rerenders innecesarios y fragilidad si cambia el copy | No bloquea inventario; sí es deuda clara de cleanup | `components/ui/detail-list.tsx` | [C] |
| Si `Badge` uppercase fijo es contrato del sistema visual o solo una convención local heredada | influye en longitud, densidad y scan speed | empujar labels largos a una base tipográfica demasiado rígida | No bloquea inventario; sí bloquea ajustes de densidad global | `components/ui/badge.tsx`, `components/ui/state-badge.tsx`, pills y stats | [C][D] |
| Si el formatting temporal debe usar timezone del sistema, del record o del usuario | afecta largo de fechas y consistencia cross-route | una consolidación visual que luego contradiga producto | No bloquea inventario; sí bloquea consolidación final de formatting | `src/lib/utils.ts`, consumers detail/sync/inbox/flow | [D] |
| Si habrá capa formal de a11y shared más allá de `Filter options` y `LiveRegion` | define si se documentan defaults o un dominio entero | olvidar texto no visible que sí forma parte del contrato UX | No bloquea primeras mini intervenciones | `components/ui/filter-pills.tsx`, `components/ui/live-region.tsx`, `components/ui/page-loading.tsx` | [C][I] |

# 3. Decisiones previas que conviene congelar

| Decisión | Opciones | Recomendación | Por qué | Costo de no decidirla ahora | ¿Bloquea ejecución? | Certeza |
|---|---|---|---|---|---|---|
| Dueño de labels visibles de runtime | a) `runtime.ts` b) caller c) dominio shared separado | **No dejar labels visibles traducibles en `runtime.ts`**; dejar ahí ids y defaults técnicos | mantiene limpia la frontera runtime/theme vs copy visible | cualquier cleanup del shell acaba tocando config técnica | Sí, para tocar shell copy con seguridad | [C][I] |
| Autoridad única de formatting visible | a) `utils.ts` b) `ui/contracts.ts` c) capa consolidada futura | **Congelar que no habrá dos autoridades** | hoy ya hay duplicación de booleanos, fechas y pluralización | inconsistencias por ruta y por componente | Sí, para intervención real del formatting layer | [C][I] |
| Naturaleza de `PageHeader`, `SectionHeader`, `Surface`, `EmptyState`, `StatusPanel`, `StatCard` | a) shells b) componentes con copy propia fuerte | **Congelarlos como shells** y no meterles defaults nuevos salvo mínimos explícitos | reduce blast radius y evita meter semántica en base components | cada caller empieza a resolver copy distinto dentro del shared | Sí, para limpieza de shared UI | [C][I] |
| Contrato del top area | a) shell + page header conviven b) uno absorbe al otro después | **Congelar el patrón actual como vigente, pero tratarlo como deuda visual observada** | evita tocar arquitectura del shell antes de tiempo | cambios locales terminan parchando síntomas | No bloquea quick wins; sí bloquea restructura visual | [C][D] |
| Política de fallback visual de valores vacíos | a) `-` universal b) placeholder contextual c) vacío silencioso | **Definir una política única antes del cleanup de formatting** | hoy hay mezcla de señales | ruido visual y decisiones inconsistentes entre stats/cards/detail | Sí, para consolidación de formatting | [C][D] |
| Contrato de densidad para componentes compactos | a) cada shared decide b) runtime dicta todo c) budget visual documentado | **Usar budget documentado, no decisiones ad hoc por componente** | badge, pills, stats y detail-list ya compiten por densidad | se arregla un shared y se rompe el ritmo en otro | No bloquea inventario; sí bloquea tuning visual serio | [I] |
| Naturaleza de `Brand` en shell | a) señal visual b) estado de producto c) preferencia futura | **Tratarlo como visual/diagnóstico hasta que se pruebe lo contrario** | evita sobrecargar runtime con semántica no validada | decisiones prematuras de theme/control | No bloquea primeras olas | [D] |
| Scope permitido de mini intervenciones | a) documentación + validación b) ajustes de contracts visuales c) refactor visual profundo | **Permitir a corto plazo solo documentación, inventario, budgets y estandarización conceptual** | mantiene velocidad sin abrir blast radius | saltar directo a refactor y terminar mezclando shell, runtime y formatting | No, más bien protege | [I] |
| Tratamiento de `StateBadge` | a) shared visual b) puente semántico | **Congelarlo como puente semántico, no shell puro** | así no se toca sin glosario y ownership claros | romper consistencia de estados en múltiples superficies | Sí, para cambios directos sobre badge | [C] |
| Header alterno de `Surface` | a) mantener dualidad b) converger luego | **Permitir dualidad por ahora, pero registrarla como deuda de consistencia** | evita refactor prematuro | variación silenciosa de spacing y jerarquía | No bloquea quick wins | [C][I] |

# 4. Mapa de mini intervenciones seguras

| Nombre corto | Objetivo | Archivos probables | Qué sí toca | Qué no toca | Precondiciones | Riesgo | Resultado visible esperado | Validación mínima | ¿Paralelo? | Certeza |
|---|---|---|---|---|---|---|---|---|---|---|
| Inventario de defaults shared | aislar textos propios mínimos de shared UI | `components/ui/page-loading.tsx`, `components/ui/filter-pills.tsx`, `components/ui/live-region.tsx` | catálogo de defaults y a11y copy | schema, runtime ids, backend | ninguna más allá del dossier | bajo | mapa claro de defaults que sí son shared-owned | revisar todos los defaults visibles/no visibles y su uso en rutas | Sí | [C] |
| Ledger de boundaries runtime-shell | separar ids, labels visibles y zonas diagnósticas del shell | `components/layout/app-shell.tsx`, `src/lib/ui/runtime.ts`, `components/layout/app-frame.tsx`, `src/lib/ui/use-accessibility-signals.ts` | clasificación y freeze de fronteras | theme overhaul, provider, persistencia | acordar que no se rediseña el shell aún | medio | mapa limpio de qué no debe vivir en runtime | revisar shell, chips, brand, role/density/preset/motion/contrast | Sí | [C][I] |
| Censo de formatting leaks | enumerar todos los puntos donde formatting afecta consistencia visual u operativa | `src/lib/utils.ts`, `src/lib/ui/contracts.ts`, `src/lib/ui/record-contracts.ts`, `components/ui/stat-card.tsx`, consumers principales | matriz de duplicidades, fallbacks y riesgos | refactor funcional | freeze de autoridad única pendiente | medio | lista accionable de leaks y consumers | validar presencia de Yes/No, items, fechas, relative time, fallback vacío | Sí | [C] |
| Mapa de contratos visuales densos | priorizar componentes donde longitud y densidad se vuelven riesgo sistémico | `components/ui/badge.tsx`, `components/ui/filter-pills.tsx`, `components/ui/stat-card.tsx`, `components/ui/detail-list.tsx`, `components/ui/page-header.tsx`, `components/ui/section-header.tsx` | budgets, constraints y zonas de presión | copy de negocio, schema labels | usar rutas críticas ya mapeadas | medio | criterio claro de qué componentes son críticos de scan speed | inspección en `/`, `/inbox`, `/record/[recordId]`, `/flow/[schemaId]`, `/sync` | Sí | [C][I] |
| Clasificación de shells nobles | blindar qué shareds no deben recibir copy global nueva | `components/ui/page-header.tsx`, `components/ui/status-panel.tsx`, `components/ui/empty-state.tsx`, `components/ui/section-header.tsx`, `components/ui/surface.tsx` | documentación de rol, props y límites | labels de estado, formatting, schema-driven copy | ninguna | bajo | menor riesgo de sobrecentralizar donde no hace falta | verificar que solo reciban copy del caller o defaults mínimos explícitos | Sí | [C] |
| Freeze de fallback policy | preparar cleanup futuro de placeholders y vacíos | `src/lib/utils.ts`, `src/lib/ui/contracts.ts`, callers que muestran vacíos | política conceptual de fallback por tipo visual | traducción de negocio o evidence policy profunda | censo de formatting leaks disponible | medio | base común para fechas, booleans, vacíos y counts | revisar detail, sync, stat-card, record-card, timeline contracts | No, depende del censo | [C][I] |
| Budget del top area | fijar límites de altura y wrapping para shell + headers | `components/layout/app-shell.tsx`, `components/ui/page-header.tsx`, `app/globals.css`, rutas principales | criterio de budget, no implementación | rediseño del shell, selector de idioma, merge estructural | ledger runtime-shell y mapa de contratos densos | medio | validación más rápida y menos subjetiva del top area | screenshots o revisión por breakpoint de rutas críticas | No, depende de ledger y mapa denso | [I] |
| Registro de deuda de `Surface` y `DetailList` | dejar preparada la limpieza posterior de patrones inconsistentes | `components/ui/surface.tsx`, `components/ui/detail-list.tsx` | deuda explícita, contratos a revisar después | cambios de API o refactor inmediato | clasificación de shells nobles | bajo | cleanup futuro más barato y ordenado | verificar doble patrón de header y keying por label:value | Sí | [C][I] |
| Matriz de validación transversal shared | convertir el conocimiento en checklist reusable | rutas principales + shared críticos | checklist y criterios | cambios de código | haber completado inventario y acoplamientos | bajo | intervención futura más segura y medible | correr checklist mínimo por ruta y por componente crítico | Sí | [I] |

## Lectura rápida de mini intervenciones
- Las primeras cinco son **preparación limpia del terreno**.
- Las siguientes dos son **puentes directos al cleanup futuro**.
- La última vuelve reusable todo el aprendizaje y reduce retrabajo.

# 5. Mapa de paralelización

| Tareas paralelizables | Tareas no paralelizables | Dependencias | Orden mínimo recomendado | Combinaciones peligrosas | Certeza |
|---|---|---|---|---|---|
| inventario de defaults shared + clasificación de shells nobles + ledger de runtime-shell | freeze de fallback policy | el freeze necesita conocer antes los leaks | 1) inventarios 2) leaks 3) freeze | congelar fallback antes de saber dónde están los duplicados | [C][I] |
| censo de formatting leaks + mapa de contratos visuales densos | budget del top area | el budget necesita entender densidad real | 1) mapa denso 2) budget | tocar top area sin budget ni mapa denso | [I] |
| registro de deuda de `Surface` y `DetailList` + matriz de validación transversal | cualquier cleanup real de componentes | el cleanup necesita deuda y validación ya listas | 1) deuda 2) validación 3) cleanup posterior | refactor de `Surface` o `DetailList` sin deuda documentada | [C][I] |
| revisión de shell chips/labels + revisión de `FilterPills`/`Badge` como pressure points | tocar `StateBadge` | `StateBadge` depende de glosario y ownership de estados | 1) pressure points 2) freeze de estados 3) recién después badge | tocar badge como si fuera solo visual | [C][D] |
| revisión de `PageLoading` defaults + `LiveRegion` | cambios a loading route callers | los callers deben obedecer defaults ya mapeados | 1) defaults 2) callers | ajustar callers sin saber qué es shared-owned y qué es caller-owned | [C][I] |

## Orden mínimo recomendado
1. **Inventario de defaults shared**
2. **Clasificación de shells nobles**
3. **Ledger de boundaries runtime-shell**
4. **Censo de formatting leaks**
5. **Mapa de contratos visuales densos**
6. **Freeze de fallback policy**
7. **Budget del top area**
8. **Registro de deuda `Surface` / `DetailList`**
9. **Matriz de validación transversal shared**

## Combinaciones peligrosas
- tocar `runtime.ts` y `app-shell.tsx` mientras todavía no se decide qué labels son técnicas y cuáles son visibles;
- intentar consolidar formatting y a la vez ajustar layout del top area;
- tocar `StateBadge` al mismo tiempo que se revisan labels de estado en detail/inbox/sync;
- meter ajustes de `globals.css` antes de fijar budgets y pressure points;
- usar `Surface` como lugar para resolver copy global cuando su problema real es de patrón visual, no de ownership de texto.

# 6. Dependencias y acoplamientos reales

| Archivo / componente | Depende de | Tipo de acoplamiento | Nivel de riesgo | Implicación para la intervención | Certeza |
|---|---|---|---|---|---|
| `components/layout/app-shell.tsx` | `createRuntimeUiContext`, `runtimeDataAttributes`, `runtimeMotionClass`, `runtimeContrastClass`, `formatHumanLabel`, `Button` | visual + runtime + humanización | alto | no es shell puro; cualquier cambio visual puede tocar runtime y formatting | [C] |
| `src/lib/ui/runtime.ts` | enums `UiArea`, `UiDensity`, `UiPreset`, `UiRole`, `UiMotionPreference`, `UiContrastPreference`, `BRAND_PROFILES`, data attributes | config técnica + theme/runtime | alto | debe quedarse técnico; sacar de ahí labels visibles traducibles | [C][I] |
| `components/layout/app-frame.tsx` | `usePathname`, `useAccessibilitySignals`, `AppShell` | routing + accessibility + shell | medio | frontera útil para no meter copy ni lógica visual extra aquí | [C] |
| `app/layout.tsx` | metadata, `<html lang="en">`, `AmbientBackdrop`, `AppFrame` | root document + shell mounting | medio/alto | cualquier decisión global de lenguaje o theme toca aquí, pero este frente no debe reabrir eso | [C] |
| `components/ui/page-loading.tsx` | `LiveRegion`, `Surface`, `SegmentedMeter`, defaults de title/subtitle | visible + a11y + defaults shared | alto | es shared crítico; cualquier cambio pega en loading visual y accesible | [C] |
| `components/ui/filter-pills.tsx` | `ariaLabel`, labels, counts, keyboard interaction, wrap | dense UI + a11y + scan speed | alto | pressure point real; no es solo un tab bonito | [C] |
| `components/ui/state-badge.tsx` | `stateLabel`, `stateTone`, `ensureRecordState`, `Badge` | visual + domain bridge | muy alto | no tocar como shell; depende de glosario y semántica compartida | [C] |
| `components/ui/stat-card.tsx` | `toDisplayText`, `toneFromSeverity`, trend label | visual + formatting | alto | formatting leak entra directo al componente | [C] |
| `components/ui/detail-list.tsx` | labels y values caller-owned, key derivada `label:value` | visual + estabilidad de render | medio | el cleanup futuro debe desacoplar estabilidad de render del copy | [C][I] |
| `components/ui/page-header.tsx` | `runtimeShellClass` opcional, actions/stats slots | shell visual + slots abiertos | medio/alto | noble shell, pero sensible a longitud y densidad | [C] |
| `components/ui/section-header.tsx` | title, description, badge, actions | shell visual + densidad | medio | base noble, pero su badge y actions pueden romper ritmo visual | [C] |
| `components/ui/surface.tsx` | `SectionHeader`, variant, padding, header dual | wrapper visual + patrón dual | medio/alto | registra deuda de consistencia; no resolver con copy | [C] |
| `components/ui/status-panel.tsx` | `toneFromSeverity`, title/description/eyebrow/actions/meta | shell visual con tono | medio | shell noble, útil para centralizar criterios visuales, no copy global | [C] |
| `components/ui/empty-state.tsx` | `toneFromSeverity`, title/description/action/footer | shell visual con tono | medio | shell noble; sensible a longitud, no dueño de copy de negocio | [C] |
| `src/lib/utils.ts` | `Intl.*("en")`, `formatHumanLabel`, `formatValue` | formatting + humanización | muy alto | fuente fuerte de leak visual y semántico | [C] |
| `src/lib/ui/contracts.ts` | `toDisplayText`, `sanitizeText`, `toneFromSeverity`, JSON/ISO fallback | formatting + sanitización shared | muy alto | duplica parte del formatting visible | [C] |
| `src/lib/ui/record-contracts.ts` | `toDisplayText`, timeline contracts, fallback `Record {id}` | domain bridge + formatting | alto | no es solo helper; hereda y propaga leaks hacia detail/timeline | [C] |
| `src/lib/core/record-view.ts` | `formatHumanLabel`, schema fields, state descriptions | domain bridge + shared semantics | muy alto | shared crítico, no noble shell | [C] |
| `app/globals.css` | data-density, shell classes, badge pressure, spacing tokens | visual system global | muy alto | tocarlo sin budget y validación puede regar efectos por todas las rutas | [C] |
| `src/lib/ui/use-accessibility-signals.ts` | media queries de motion/contrast | runtime accessibility | medio | debe seguir libre de copy; es boundary técnico puro | [C] |

## Lectura del mapa de acoplamientos
### Shareds realmente críticos
- `app-shell.tsx`
- `page-loading.tsx`
- `filter-pills.tsx`
- `state-badge.tsx`
- `utils.ts`
- `ui/contracts.ts`
- `record-view.ts`
- `globals.css`

### Shareds nobles
- `page-header.tsx`
- `section-header.tsx`
- `status-panel.tsx`
- `empty-state.tsx`
- gran parte de `surface.tsx`

### Puentes peligrosos
- `state-badge.tsx`
- `stat-card.tsx`
- `record-contracts.ts`
- `app-shell.tsx`

# 7. Validación operativa por mini paso

| Mini intervención | Qué validar | Dónde validar | Tipo de validación | Criterio de aceptación | Señal de stop | Evidencia a guardar | Certeza |
|---|---|---|---|---|---|---|---|
| Inventario de defaults shared | que todos los defaults propios estén listados y clasificados por ownership | `page-loading`, `filter-pills`, `live-region`, fallbacks shared | documental + coverage | no queda default suelto relevante fuera del inventario | aparece un default oculto en rutas críticas después del cierre | matriz de defaults y consumers | [C] |
| Ledger de boundaries runtime-shell | que cada label visible del shell tenga dueño tentativo claro | `app-shell`, `runtime.ts`, `app-frame`, `layout` | documental + ownership | ids y labels visibles quedan separados conceptualmente | una decisión del shell obliga a tocar runtime por copy | tabla ids vs labels vs zonas diagnósticas | [C][I] |
| Censo de formatting leaks | que cada formatter visible tenga lista de consumers y duplicidades | `utils`, `ui/contracts`, `record-contracts`, `stat-card`, detail/flow/sync/inbox | documental + consistency | todos los leaks relevantes quedan localizados | aparece un tercer formatter visible no registrado | matriz formatter -> consumer -> fallback -> riesgo | [C] |
| Mapa de contratos visuales densos | que se identifiquen pressure points y budgets preliminares | `/`, `/inbox`, `/record/[recordId]`, `/flow/[schemaId]`, `/sync` | visual + scan speed | queda claro qué shareds son compactos críticos y por qué | se detecta overflow o wrapping severo sin budget definido | tabla de pressure points por ruta/breakpoint | [C][I] |
| Clasificación de shells nobles | que cada shared noble quede explícitamente fuera de sobrecentralización | `PageHeader`, `SectionHeader`, `Surface`, `StatusPanel`, `EmptyState` | documental + architecture | el equipo deja de tratarlos como dueños de copy global | surge propuesta de meter defaults fuertes dentro de shell noble | tabla shell noble -> copy owner -> límites | [C] |
| Freeze de fallback policy | que exista política única para vacío, booleanos, arrays y fechas inválidas | components con stats/cards/detail/timeline | policy + consistency | la política se puede aplicar sin contradicciones obvias | detail/sync exigen evidence policy distinta aún no resuelta | ficha de fallback por tipo de valor | [C][I] |
| Budget del top area | que exista presupuesto de altura y wrapping por breakpoint | shell + page headers en rutas principales | visual + responsive | el top area se puede evaluar con criterio objetivo | cualquier ajuste necesita tocar `globals.css` a ciegas | tabla de budget y capturas comparativas | [I] |
| Registro de deuda `Surface` / `DetailList` | que la deuda quede formulada como cleanup concreto y no como intuición vaga | `Surface`, `DetailList` | documental + cleanup prep | existe lista de deuda, no solo malestar difuso | se propone refactor inmediato sin contrato previo | backlog de cleanup con motivos y riesgos | [C][I] |
| Matriz de validación transversal shared | que la futura ejecución tenga checklist común | rutas principales y shared críticos | QA conceptual | cualquier mini paso futuro sabe dónde validar y qué guardar | se intenta ejecutar sin ruta, criterio y evidencia definidos | checklist reusable y carpeta de evidencia | [I] |

# 8. Trazabilidad y evidencia

## Qué registrar siempre

### Decisiones
Registrar:
- decisión tomada;
- opciones consideradas;
- recomendación adoptada;
- motivo;
- impacto esperado;
- si desbloquea o no la siguiente mini intervención.

### Hallazgos
Registrar:
- componente o helper observado;
- hallazgo operativo;
- por qué importa;
- si afecta visual system, runtime boundary, formatting o cleanup.

### Bloqueos
Registrar:
- incertidumbre concreta;
- dueño tentativo del bloqueo;
- qué evidencia falta;
- si el bloqueo detiene ejecución o solo una rama.

### Riesgos
Registrar:
- riesgo;
- ruta/componente afectado;
- blast radius;
- señal temprana;
- mitigación propuesta.

### Validaciones
Registrar:
- qué se validó;
- dónde;
- con qué viewport o ruta;
- resultado;
- issues encontrados;
- evidencia adjunta.

### Archivos tocados
Aunque este entregable no toca código, la traza futura debe registrar:
- archivo;
- propósito del cambio;
- mini intervención a la que pertenece;
- impacto esperado.

### Checkpoints conceptuales
Conviene guardar checkpoints como estos:
- `shared-defaults-frozen`
- `runtime-boundaries-frozen`
- `formatting-authority-decided`
- `fallback-policy-frozen`
- `top-area-budget-defined`
- `shared-validation-checklist-ready`

### Artefactos a conservar
- inventario de defaults shared;
- ledger de runtime boundaries;
- matriz de formatting leaks;
- pressure map de componentes densos;
- tabla de budget del top area;
- checklist transversal de validación;
- backlog de cleanup diferido.

## Formato mínimo recomendado de evidencia

| Tipo | Campo mínimo | Ejemplo de uso |
|---|---|---|
| decisión | fecha, decisión, motivo, impacto | congelar `runtime.ts` como técnico-only para labels |
| hallazgo | fecha, archivo, hallazgo, relevancia | `StatCard` depende de `toDisplayText()` |
| bloqueo | fecha, bloqueo, qué falta, stop/no stop | timezone policy sin definir |
| validación | fecha, ruta, viewport, criterio, resultado | top area en `/inbox` `md` se mantiene bajo budget |
| artefacto | nombre, objetivo, estado | `shared-defaults-inventory.md` listo |

# 9. Quick wins reales vs zonas rojas

## Quick wins

### 1) Inventariar y congelar defaults shared mínimos
Por qué sí:
- tienen ownership más claro;
- no tocan schema ni backend;
- despejan rápido qué sí es shared-owned de verdad.

### 2) Separar shells nobles de puentes semánticos
Por qué sí:
- baja el riesgo de meter copy o lógica donde no pertenece;
- acelera después cualquier extracción, cleanup o validación.

### 3) Hacer el censo formal de formatting leaks
Por qué sí:
- hoy la fuga es real y ya afecta consistencia visual;
- no requiere todavía decidir locale/provider;
- prepara una sola autoridad futura de formatting.

### 4) Levantar el pressure map de componentes compactos
Por qué sí:
- convierte “se siente apretado” en evidencia reusable;
- protege scan speed y densidad antes de cualquier cambio visible.

### 5) Congelar el ledger runtime-shell
Por qué sí:
- evita que el shell absorba problemas de idioma, theme y runtime como si fueran lo mismo;
- prepara una intervención más limpia del sistema visual.

### 6) Documentar deuda concreta de `Surface` y `DetailList`
Por qué sí:
- son deudas pequeñas, pero de esas que después cobran interés con bata de cobrador;
- no requieren tocar código hoy para aportar claridad mañana.

## Zonas rojas

### 1) `StateBadge` y cualquier ajuste de labels de estado
Por qué no todavía:
- no es solo visual;
- depende de `record-view` y de semántica transversal.

### 2) `runtime.ts` como destino de labels visibles nuevos
Por qué no todavía:
- mezcla config técnica con copy;
- contamina theme/runtime boundary.

### 3) Reorganizar shell sticky y `PageHeader` en la misma corrida
Por qué no todavía:
- es una deuda arquitectónica del top area, no un quick win;
- sin budget y sin freeze previo se vuelve plastilina radioactiva.

### 4) Tocar `globals.css` para “acomodar un caso”
Por qué no todavía:
- pega transversalmente;
- sin pressure map y budget es tiro al aire.

### 5) Resolver formatting real mientras siguen coexistiendo dos autoridades
Por qué no todavía:
- sin decisión previa se crean arreglos parciales y UI híbrida.

### 6) Meter copy global nueva en shells nobles
Por qué no todavía:
- es exactamente la forma elegante de crear caos reutilizable.

# 10. Artefactos adicionales que conviene producir

| Nombre | Para qué sirve | Prioridad | ¿Bloquea o solo ayuda? | Certeza |
|---|---|---|---|---|
| `shared-defaults-inventory.md` | inventario de defaults propios de shared UI | alta | ayuda fuerte; desbloquea más rápido | [I] |
| `runtime-shell-boundary-ledger.md` | separar ids, labels visibles y zonas diagnósticas del shell | alta | bloquea tocar shell con seguridad | [I] |
| `formatting-leak-matrix.md` | mapear duplicidades, consumers y políticas pendientes | alta | bloquea consolidación real de formatting | [I] |
| `visual-pressure-map.md` | documentar componentes compactos críticos y riesgos por longitud | alta | ayuda fuerte; protege scan speed | [I] |
| `top-area-budget-table.md` | fijar budget por breakpoint para shell + page headers | media/alta | no bloquea inventario, sí bloquea ajustes de top area | [I] |
| `shared-shells-vs-bridges.md` | distinguir shareds nobles vs puentes semánticos | alta | ayuda fuerte; reduce errores de ownership | [I] |
| `fallback-policy-sheet.md` | definir vacío, booleanos, counts, fechas inválidas | media/alta | bloquea cleanup de formatting | [I] |
| `cross-route-shared-validation-checklist.md` | checklist reusable por ruta y shared crítico | alta | ayuda fuerte; acelera ejecución segura | [I] |
| `cleanup-backlog-shared-visual-system.md` | registrar deuda concreta de `Surface`, `DetailList`, `Badge`, top area | media | ayuda | [I] |
| `evidence-register-template.md` | unificar decisiones, hallazgos, bloqueos y validaciones | media | ayuda | [I] |

# 11. Qué nos deja resuelto este chat

## Qué parte del frente quedaría lista para ejecución
Después de este entregable quedaría prácticamente lista la fase previa para ejecutar con seguridad:
- el **inventario de defaults shared**;
- el **ledger de boundaries runtime-shell**;
- el **censo de formatting leaks**;
- el **pressure map** de componentes densos;
- la **matriz transversal de validación shared**.

Eso no es todavía implementación, pero sí deja el terreno con carriles pintados y conos puestos, que ya es bastante más sexy que correr a oscuras.

## Qué seguiría bloqueado
Seguiría bloqueado, o al menos bajo llave:
- cualquier ajuste directo a `StateBadge` y labels de estado;
- cualquier movimiento de labels visibles dentro de `runtime.ts` sin decisión previa;
- cualquier consolidación real del formatting sin decidir autoridad única;
- cualquier ajuste del top area que rebase el scope documental y de budgets;
- cualquier cleanup de `globals.css` sin pressure map y validación por rutas.

## Qué decisiones quedarían casi cerradas
Quedarían casi cerradas estas decisiones:
- los **shared nobles** no deben absorber copy global nueva;
- los **puentes semánticos** deben tratarse como zonas de cuidado especial;
- `runtime.ts` debe quedarse técnico y no convertirse en dueño de labels visibles;
- el cleanup futuro del sistema visual debe apoyarse en budgets, no en intuición;
- el formatting visible necesita una sola autoridad, no dos voces cantando la misma rola en tonos distintos.

## Qué intervención futura se volvería más rápida gracias a este entregable
Se volverían mucho más rápidas estas intervenciones futuras:
1. limpieza de defaults shared;
2. consolidación del formatting layer;
3. saneamiento del shell como superficie visual separada de runtime técnico;
4. preparación de budgets y revisión del top area;
5. cleanup de contratos visuales en `Surface`, `DetailList`, `Badge`, `FilterPills`, `StatCard` y `PageLoading`.

## Qué nos deja resuelto este chat
Este chat deja resuelto el **segundo piso operativo** del frente de shared UI y sistema visual.

En concreto, deja:
- claro cuáles shareds son realmente críticos y cuáles son marcos nobles;
- claro qué props y patrones favorecen deriva visual o de ownership;
- claro qué debe quedarse fuera de runtime y por qué;
- claro qué mini pasos sí son seguros, cuáles se pueden correr en paralelo y cuáles no;
- clara una estructura de validación, trazabilidad y evidencia reusable;
- y claro cómo preparar el cleanup futuro para que sea más corto, más ordenado y con mucho menos blast radius.

Dicho de forma simple: el dossier ya te había dibujado el mapa. Este entregable ya te marcó por dónde conviene entrar, por dónde no, qué compuertas cerrar primero y qué cables no hay que cortar todavía.

---

# 🏠 Capítulo 3 · Launcher e Inbox

# 1. Resumen ejecutivo de profundización

## Qué frente me tocó
Profundización operativa del frente **Launcher e Inbox** para `apps/external_interaction_template`, con foco en ejecución futura segura, división en mini pasos, paralelización, validación y trazabilidad.

## Qué ya estaba resuelto en el dossier
El dossier ya dejó resuelto el mapa base de superficies, ownership, lista roja, hotspots de longitud, hotspots de scan speed, dependencias visibles y validación mínima de launcher e inbox [C]. También dejó explícito que ambas pantallas heredan shell global visible, que el inbox mezcla copy local con estados/schema/helpers, y que hay dudas abiertas sobre shell, estados, `schema-registry`, `formatHumanLabel` y `formatDateTime` [C].

## Qué huecos detecté
1. Faltaba convertir el mapa en **plan de ejecución por mini intervención**, con cortes más seguros y menores radios de explosión. [I]
2. Faltaba distinguir qué piezas son **parallel-friendly** y cuáles son dominó puro. [I]
3. Faltaba un **orden mínimo recomendado** que cuide scan speed y jerarquía visual, en especial en inbox list mode. [I]
4. Faltaba bajar el análisis a **checkpoints de validación por mini paso** y a una matriz de evidencia guardable. [I]
5. Faltaba marcar qué partes pueden resolverse como **deuda visual compartida** sin tocar semántica, y cuáles no. [I]

## Qué nueva inteligencia operativa agrego
- una lista de **incógnitas activas** con criterio de bloqueo
- una tabla de **decisiones que conviene congelar antes de ejecutar**
- un **mapa de mini intervenciones seguras** y acotadas
- un **mapa de paralelización** con combinaciones peligrosas
- un desglose de **acoplamientos reales** entre launcher, inbox, shell, states, schema y helpers
- una **validación operativa por mini paso**
- una propuesta de **trazabilidad y evidencia** para que la futura intervención no se vuelva bruma con patas

---

# 2. Lo que aún falta investigar o confirmar

| Incógnita | Por qué importa | Riesgo que evita | ¿Bloquea primera intervención? | Dónde confirmarlo | Estado |
|---|---|---|---|---|---|
| Si **shell entra en la misma ola** o se congela como dependencia visible | Launcher e inbox ya lo muestran; cualquier cambio parcial puede dejar mezcla arriba/abajo | inconsistencia transversal y doble jerarquía rara | **Sí**, para cualquier paso que toque copy visible integral | dossier + `components/layout/app-shell.tsx` | [D] |
| Si **list mode es la vista prioritaria** del inbox para optimización | scan speed no pega igual en list que en grid | optimizar lo equivocado primero | **No**, pero sí condiciona prioridades | dossier + `record-inbox.tsx` | [I] |
| Si `stateLabel` y `stateDescription` quedan **fuera de primera ola** | viven en helper de dominio y pegan en varias superficies | tocar labels de estado como si fueran copy local | **Sí**, para cualquier cambio en pills/lanes/badges que pretenda alterar semántica | dossier + `src/lib/core/record-view.ts` | [D] |
| Si `schema-registry.ts` se trata como **source of display temporal o estable** | titles/summaries/field labels aparecen en cards, selects y preview | meter manos donde parece UI pero es contrato display | **Sí**, para cualquier paso que cambie summaries/titles/labels visibles | dossier + `src/lib/core/schema-registry.ts` | [D] |
| Si `formatDateTime("en")` queda fuera de este frente o no | footer de cards mezcla helper visible con consistencia de superficie | dejar launcher/inbox “arreglados” pero con cola inglesa en fechas | **No** para primer paso visual, **Sí** para cierre de consistencia | dossier + `src/lib/utils.ts` | [D] |
| Si `formatHumanLabel()` puede seguir como fallback visible en shell/estados | hoy alimenta labels runtime y algunos labels compartidos | consolidar deuda invisible que luego toca varias superficies | **No** para layout puro, **Sí** para consistencia final | dossier + `src/lib/utils.ts`, `app-shell.tsx`, `record-view.ts` | [D] |
| Si la fila de **queue summary** debe seguir siendo narrativa o volverse más seca | hoy ocupa espacio cognitivo y vertical | matar scan speed con prosa operativa | **No** | `record-inbox.tsx` | [I] |
| Si los **view toggles icon-only** necesitan apoyo textual o tooltip futuro | afectan claridad operativa pero no ownership textual principal | bajar comprensión al cambiar entre list/grid | **No** | `record-inbox.tsx` | [I] |
| Si `Resume / token`, `Retryable`, `Outbound adapter` son deuda nominal congelada o entran a limpieza futura | son labels tensas y compactas | desperdiciar tiempo en micro copy sin cerrar frente | **No** para layout, **Sí** para consistencia terminológica | dossier + `app/page.tsx` | [I] |
| Si se acepta un **budget formal de altura** para shell + hero por breakpoint | el shell sticky ya es top-heavy y compite con launcher/inbox | arreglar una fila y romper el primer viewport | **Sí**, si shell entra en la ola | dossier + `app-shell.tsx` + validación visual | [I] |

### Lectura operativa
- **No bloquean** una primera intervención puramente de inventario, budget, evidencia y layout local de launcher/inbox: list-priority, queue-summary style, empty states, grid/list validation kit. [I]
- **Sí bloquean** cualquier intervención que quiera sentirse “cerrada” visualmente sin dejar mezcla: shell incluido/excluido, estados, schema-display y helpers visibles. [I]

---

# 3. Decisiones previas que conviene congelar

| Decisión | Opciones | Recomendación | Por qué | Costo de no decidirla ahora | ¿Bloquea ejecución? |
|---|---|---|---|---|---|
| Shell entra en la misma ola o no | `entra` / `se congela aparte` | **Congelarlo aparte, pero tratarlo como dependencia visible obligatoria** | evita que launcher/inbox se conviertan en refactor del shell con disfraz | PRs híbridos y validación difusa | **Sí**, para cierre de superficie |
| Vista prioritaria del inbox | `list-first` / `grid-first` / `paridad total` | **list-first** | el propio dossier ya marca scan speed como riesgo principal del inbox [C] | optimización repartida y lenta | No |
| Dominio de estados entra o no | `entra` / `sale` | **sale de primera ola** | es semántica compartida; no es copy local del inbox [C] | tocar pills/lanes y terminar rompiendo consistencia cross-surface | **Sí**, para cualquier cambio de label de estado |
| `schema-registry` display entra o no | `entra` / `sale` | **sale de primera ola** | reduce blast radius y deja claro que launcher/inbox no son dueños del schema text [C] | cards medio arregladas y ownership borroso | **Sí**, para titles/summaries/preview labels |
| Budget de altura de top area | `formal` / `informal` | **formal** | launcher e inbox no deben competir con shell sticky | arreglos bonitos en local pero fold destruido | **Sí**, si shell participa |
| Budget de densidad de queue controls | `formal` / `informal` | **formal y breve** | controls + pills + queue header son núcleo del scan speed | overfitting visual sin criterio | No |
| Queue summary row | `narrativa` / `operativa breve` | **operativa breve** | en inbox triage cada línea compite por atención | desgaste cognitivo | No |
| Orden de intervención | `por pantalla completa` / `por mini paso` | **por mini paso** | más simple de validar y paralelizar | PRs gordos y ambiguos | No |
| Grid mode | `entra junto con list` / `entra después` | **entra después de estabilizar list** | list es el modo con más carga de triage [I] | dispersión de esfuerzo | No |
| Helpers visibles (`formatDateTime`, `formatHumanLabel`) | `entran` / `se registran como deuda visible` | **registrarlos como deuda visible, no mezclarlos con el primer pase** | evitas cruzar layout con i18n/formatting | frontera difusa del cambio | No |

---

# 4. Mapa de mini intervenciones seguras

## 4.1 Vista general
La estrategia más segura no es “arreglar launcher e inbox” de un jalón. Es partirlos como navaja suiza: hoja corta por hoja corta.

| Nombre corto | Objetivo | Archivos probables | Qué sí toca | Qué no toca | Precondiciones | Riesgo | Resultado visible esperado | Validación mínima | ¿Paralelo? |
|---|---|---|---|---|---|---|---|---|---|
| **scope-freeze-li-inbox** | congelar alcance operativo de launcher/inbox y sus dependencias visibles | docs / checklist / decisión previa | alcance, exclusiones, lista roja operativa | código | dossier leído + responsables alineados | bajo | frente listo para ejecutar sin ambigüedad | checklist firmado | Sí |
| **launcher-local-copy-boundary** | separar y registrar el copy estrictamente launcher-owned | `app/page.tsx` | hero, stats, section title, metric labels, CTAs locales | schema titles/summaries/badges, shell | freeze de lista roja | bajo | inventario limpio y extraíble | diff de inventario + revisión visual rápida | Sí |
| **launcher-card-compact-budget** | fijar budget visual de schema cards sin tocar semántica | `app/page.tsx`, `components/ui/badge.tsx`, `components/ui/button.tsx`, tal vez `components/ui/surface.tsx` | spacing, prioridades visuales, validación de badges/rows/CTA compacta | `schema-registry`, accessMode/category/adapter labels | freeze de schema-owned fuera | medio | cards más estables y menos frágiles | md/xl cards + worst-case sample | No con shell |
| **inbox-controls-density-pass** | compactar y jerarquizar controls para mantener scan speed | `components/records/record-inbox.tsx`, `components/ui/filter-pills.tsx`, `components/ui/select.tsx`, `components/ui/input.tsx` | search row, select row, lane pills, queue summary | state labels semánticas, schema titles, shell | freeze de estados/schema fuera | medio | controls más legibles, menos verbosos, más respirables | sm/md/xl + filtros activos | Sí |
| **inbox-list-lane-readability-pass** | mejorar legibilidad de list mode lanes sin tocar significado de estados | `components/records/record-inbox.tsx`, `components/ui/state-badge.tsx` | composición de lane header, count placement, spacing | `stateLabel`, `stateDescription`, order semántico | freeze de dominio state fuera | medio | list mode más rápido de escanear | list mode con 4+ lanes | Sí, pero no con cambios a states |
| **inbox-card-scan-pass** | reforzar jerarquía visual dentro de la card del inbox | `components/records/inbox-record-card.tsx`, `components/ui/detail-list.tsx` | orden visual, pesos, spacing, compact zones | schema summary text, record values, helper semantics | schema/data fuera | medio | cards con lectura más rápida y menos ruido | list + grid + títulos largos | Sí |
| **empty-state-safe-pass** | alinear empty states con jerarquía del frente | `components/records/record-inbox.tsx`, quizá `components/ui/empty-state.tsx` | empty state copy container, spacing, CTA prominence | shell, states, schema, formatting | none | bajo | fallback más limpio y consistente | empty state con filtros activos | Sí |
| **launcher-inbox-validation-pack** | crear pack mínimo de validación y evidencia | docs/checklist/screenshots baseline | casos, evidencia, rutas, breakpoints | producción visual final | mini pasos definidos | bajo | ejecución futura más rápida | checklist completo | Sí |
| **shell-alignment-pass-optional** | alinear shell con launcher/inbox si se decide incluirlo | `components/layout/app-shell.tsx`, `app/globals.css` | jerarquía, budget de altura, nav/actions/context budget | runtime semantics, brand logic, state labels | decisión explícita de incluir shell | alto | menos competencia visual en top area | shell + `/` + `/inbox` en 4 breakpoints | No |

## 4.2 Comentario operativo por mini intervención

### `scope-freeze-li-inbox`
- Es la válvula anti-caos.
- No produce UI nueva, pero ahorra retrabajo.
- Debe cerrar explícitamente: shell, estados, schema text, helpers visibles.

### `launcher-local-copy-boundary`
- Es el mini paso más limpio del frente.
- Conviene hacerlo antes que cualquier ajuste de layout para saber qué sí pertenece realmente al launcher.

### `launcher-card-compact-budget`
- Aquí vive una deuda visual compartida: badges compactas, rows justify-between, CTAs sm y summaries libres.
- No debe confundirse con renombrar categorías, access modes o adapters.

### `inbox-controls-density-pass`
- Es de los quick wins más reales.
- Los controls concentran densidad, longitud y scan speed en el mismo tablero.
- El grid actual de controls ya revela el riesgo: una columna flexible y dos selects angostos de 220px. [C]

### `inbox-list-lane-readability-pass`
- Debe optimizar primero el modo list.
- La regla aquí es quirúrgica: mejorar ritmo visual sin tocar el significado de los estados.

### `inbox-card-scan-pass`
- Es la pieza que más impacta sensación de “inbox usable”.
- Toca títulos truncados, summary, preview fields, state badge y footer compacta.
- Debe ir después o en paralelo controlado con controls, no antes del freeze de states/schema.

### `empty-state-safe-pass`
- Bajo riesgo, buen rendimiento moral.
- Sirve para cerrar el frente con una superficie muy visible y casi sin coupling semántico.

### `shell-alignment-pass-optional`
- Debe ser opcional, no implícito.
- Si se mete sin decisión previa, se come el timeline como cocodrilo con hambre.

---

# 5. Mapa de paralelización

| Tareas paralelizables | Tareas no paralelizables | Dependencias | Orden mínimo recomendado | Combinaciones peligrosas |
|---|---|---|---|---|
| `scope-freeze-li-inbox` + `launcher-inbox-validation-pack` | cualquier cambio que altere shell + page content a la vez | ninguna fuerte, salvo alineación de equipo | **0** | empezar con código sin freeze |
| `launcher-local-copy-boundary` + `empty-state-safe-pass` | `launcher-card-compact-budget` junto con cambios a `schema-registry` | lista roja congelada | **1** | tocar titles/summaries/schema y layout a la vez |
| `inbox-controls-density-pass` + `launcher-local-copy-boundary` | `inbox-list-lane-readability-pass` junto con cambios a `record-view.ts` | estados fuera de alcance | **2** | tocar lanes y labels de estado en la misma corrida |
| `inbox-card-scan-pass` + `launcher-card-compact-budget` | `inbox-card-scan-pass` junto con cambios a `formatDateTime` o `formatHumanLabel` | schema/data/helpers fuera | **3** | mezclar jerarquía visual con formatting/i18n |
| pack de evidencia + checklist de breakpoints en paralelo a cualquier mini paso | `shell-alignment-pass-optional` junto con `inbox-controls-density-pass` | decisión de shell | **4** | tocar top area y queue controls en el mismo PR |
| documentación de decisiones + captura de riesgos | cambios a `app-shell.tsx` y `app/globals.css` sin budget formal | shell in/out | según decisión | shell + globals + cards + controls en un solo bloque |

## Orden mínimo recomendado
1. **Freeze operativo**: alcance, exclusiones, lista roja, decisiones mínimas.
2. **Pack de validación y evidencia**.
3. **Launcher local boundary**.
4. **Inbox controls density**.
5. **Inbox list lane readability**.
6. **Inbox card scan pass**.
7. **Launcher card compact budget**.
8. **Empty state pass**.
9. **Shell alignment optional**, solo si se decidió formalmente.

## Combinaciones peligrosas
- `AppShell` + `record-inbox.tsx` + `globals.css` en la misma intervención.
- `record-view.ts` + `StateBadge` + `FilterPills` si no está congelado el dominio de estados.
- `schema-registry.ts` + launcher cards + inbox cards, porque convierte una mejora visual en refactor semántico.
- `formatDateTime`/`formatHumanLabel` + cards/lanes/controls, porque mezcla layout con otra capa transversal.

---

# 6. Dependencias y acoplamientos reales

| Archivo / componente | De qué depende | Tipo de acoplamiento | Nivel de riesgo | Implicación para la intervención |
|---|---|---|---|---|
| `app/page.tsx` | `listSchemas`, `listRecords`, `listSyncCenterData`, `PageHeader`, `StatCard`, `Surface`, `Badge`, `Button` | composición local + schema/data display | medio | buen punto de corte para copy local; mal punto para tocar schema text |
| `app/inbox/page.tsx` | records + schemas server-side hacia `RecordInbox` | pass-through de datos | bajo | casi no vale la pena usarlo como frente principal de cambio |
| `components/records/record-inbox.tsx` | `record-view`, `RECORD_STATES`, `FilterPills`, `Select`, `Input`, `PageHeader`, `InboxRecordCard` | controller UI + domain helper | **alto** | archivo más sensible del inbox; aquí vive el triage real |
| `components/records/inbox-record-card.tsx` | `normalizeRecordTitle`, `normalizePreviewFields`, `formatDateTime`, `StateBadge`, `DetailList` | card UI + helper bridge | **alto** | gran parte de scan speed depende de esta card |
| `components/layout/app-shell.tsx` | `createRuntimeUiContext`, `formatHumanLabel`, `Button`, routing actual | shared shell + runtime coupling | **alto** | si entra, amplía el frente inmediatamente |
| `components/ui/filter-pills.tsx` | labels + counts que recibe, wrap true por default, aria default compartida | shared presentational con densidad sensible | medio-alto | ideal para intervención visual, no semántica |
| `components/ui/state-badge.tsx` | `stateLabel`, `stateTone`, `ensureRecordState` | bridge entre UI y semántica de estado | **alto** | no tocar labels si el dominio state sigue fuera |
| `components/ui/detail-list.tsx` | labels/value pairs recibidos | presentational compact grid | medio-alto | influye fuerte en scan speed de cards |
| `src/lib/core/record-view.ts` | `schema-registry`, `formatHumanLabel`, record ordering logic | helper de dominio visible | **alto** | no es lugar seguro para primera ola de layout |
| `src/lib/core/schema-registry.ts` | definiciones de schema display | schema-owned display source | **alto** | dejar fuera de primera ola |
| `src/lib/ui/record-contracts.ts` | sanitización, fallback `Record {id}`, normalización preview | helper cross-surface | medio-alto | útil para entender card, malo para mezclar con layout |
| `src/lib/utils.ts` | `formatDateTime`, `formatHumanLabel`, `formatValue` | formatting/humanization transversal | **alto** | registrar como deuda visible, no meterlo junto al pase visual |
| `app/globals.css` | `page-stack`, `eyebrow`, `metric-label`, `queue-header`, `shell-chip` | deuda visual compartida por utility classes | medio-alto | tocarlo requiere prueba cruzada, no solo local |
| `components/ui/page-header.tsx` | props caller-owned, wrap flex entre texto y acciones | shared header shell | medio | influye en hero de launcher e inbox, pero no es dueño del texto |

## Lectura operativa
- **Launcher** depende mucho de `app/page.tsx`; por eso sí permite una mini intervención limpia. [C]
- **Inbox** depende de `record-inbox.tsx` como controlador completo y de `inbox-record-card.tsx` como célula de lectura; por eso conviene cortarlo en controls, lanes y cards, no tratarlo como una sola masa. [C][I]
- **Shell**, `record-view`, `schema-registry` y `utils` son capas que pueden contagiar otras superficies; conviene tocarlas solo con decisión explícita. [C]

---

# 7. Validación operativa por mini paso

| Mini intervención | Qué validar | Dónde validar | Tipo de validación | Criterio de aceptación | Señal de stop | Evidencia a guardar |
|---|---|---|---|---|---|---|
| `scope-freeze-li-inbox` | alcance, exclusiones, lista roja | documento de trabajo | revisión de control | no hay dudas abiertas sobre shell/estados/schema/helpers dentro del mini paso | aparece un “ya que estamos” transversal | acta breve de freeze |
| `launcher-local-copy-boundary` | hero, stats, section title, metric labels, CTAs locales | `/` | revisión de inventario + visual rápida | todo launcher-owned separado de schema/data/shell | alguien intenta meter `schema.*` o shell text | inventario marcado por archivo |
| `launcher-card-compact-budget` | launcher hero, launcher cards, badges, metrics, CTA row | `/` en `md/xl` | visual por breakpoint | cards se mantienen legibles y más parejas sin tocar schema text | para arreglar card hay que tocar `schema-registry` o enums visibles | screenshots `md/xl` con caso largo |
| `inbox-controls-density-pass` | inbox controls, queue controls surface, state lanes, queue summary | `/inbox` en `sm/md/xl` | visual + uso básico | búsqueda, selects y pills se leen rápido y no generan pared de UI | los pills requieren cambiar `stateLabel` para “verse bien” | screenshots con filtros vacíos y activos |
| `inbox-list-lane-readability-pass` | inbox lanes, lane headers, counts, relación badge/description | `/inbox` list mode | visual + scan-speed | lanes se distinguen más rápido sin aumentar ruido | la mejora exige renombrar estados o cambiar order semántico | captura de 4 lanes y nota de lectura |
| `inbox-card-scan-pass` | inbox cards, title row, summary, detail list, footer | `/inbox` list + grid | visual + comparación before/after | la card prioriza estado/título/preview y no se vuelve más alta sin razón | la solución obliga a tocar values o summary schema-owned | pack de 3 cards: corta, media, larga |
| `empty-state-safe-pass` | empty states de inbox | `/inbox` con 0 resultados | visual + funcional | empty state se entiende rápido y CTA se ve bien | el shell compite más que el empty | screenshot empty + filtros activos |
| `launcher-inbox-validation-pack` | launcher hero, launcher cards, inbox controls, inbox lanes, inbox cards, grid/list mode, empty states, scan speed | `/` y `/inbox` | checklist | existe un pack repetible y usable por otro dev | checklist demasiado ambigua | checklist versionada + nombres de capturas |
| `shell-alignment-pass-optional` | shell sticky, nav, chips, top area budget | `/` y `/inbox` | visual transversal | el shell no compite con hero/controls y respeta budget | cualquier ajuste local obliga a tocar runtime semantics | capturas shell-only y shell+page |

## Casos que deben atenderse sí o sí

### Launcher hero
- bloque de texto vs actions en desktop/tablet/mobile
- impacto visual del shell sticky encima
- orden visual: shell → hero → stats → flows

### Launcher cards
- badge row
- metric rows compactas
- CTA row sm
- summaries con distinta longitud

### Inbox controls
- row de búsqueda
- dos selects angostos
- pills con count
- queue summary row
- clear filters condicionado por estado de filtros

### Inbox lanes
- encabezado por estado
- count por lane
- densidad del bloque description + badge
- continuidad de scan entre lanes

### Inbox cards
- schema eyebrow
- record title truncado
- summary de schema
- preview fields (`DetailList`)
- footer `Updated ...` + id

### Grid/list mode
- **List mode** es la prioridad operativa
- **Grid mode** se valida después como modo secundario, no como frontera primaria de triage

### Empty states
- relación con shell y hero
- CTA visible
- altura razonable

### Scan speed
Se considera aceptable si:
- el ojo identifica estado, título y campos preview sin paseos innecesarios
- pills y lane headers no dominan el ancho visual
- el queue summary no roba más atención que las cards
- el primer contenido accionable del inbox aparece rápido

---

# 8. Trazabilidad y evidencia

## Qué registrar

| Tipo | Qué registrar | Formato sugerido | Prioridad |
|---|---|---|---|
| Decisiones | freeze de shell, states, schema, helpers visibles, list-first vs grid-second | tabla simple con fecha y responsable | alta |
| Hallazgos | cualquier coupling nuevo descubierto durante ejecución | registro incremental | alta |
| Bloqueos | dependencias que empujan el mini paso fuera de alcance | lista con trigger y dueño | alta |
| Riesgos | nuevos riesgos de longitud, densidad o scan speed | matriz corta con probabilidad/impacto | alta |
| Validaciones | qué se probó y con qué resultado | checklist por mini paso | alta |
| Archivos tocados | set real por mini intervención | lista exacta por PR/paso | alta |
| Checkpoints conceptuales | “shell fuera”, “states fuera”, “schema display fuera” | semáforo o checkbox | alta |
| Artefactos a conservar | capturas, inventarios, budget tables, checklist | carpeta o sección de docs | media-alta |

## Evidencia mínima por mini paso
- **antes/después** visual por breakpoint relevante
- lista de **archivos tocados**
- lista de **archivos explícitamente no tocados**
- decisión de ownership o exclusión reaplicada
- resultado de validación breve
- señal de stop, si apareció

## Checkpoints conceptuales sugeridos
1. `shell_in_wave = yes/no`
2. `states_in_wave = yes/no`
3. `schema_display_in_wave = yes/no`
4. `format_helpers_in_wave = yes/no`
5. `list_mode_priority = yes`
6. `top_area_budget_defined = yes/no`
7. `queue_density_budget_defined = yes/no`

## Artefactos que conviene conservar
- baseline visual de `/` y `/inbox`
- screenshots de `sm`, `md`, `lg`, `xl`
- caso con schema title largo
- caso con state lane cargada
- caso con empty state
- caso list vs grid
- matriz de decisiones congeladas
- checklist de scan speed

---

# 9. Quick wins reales vs zonas rojas

## Quick wins

| Quick win | Por qué sí conviene | Riesgo |
|---|---|---|
| Separar copy local de `app/page.tsx` | el launcher tiene bloque limpio y bien delimitado | bajo |
| Separar copy local de `record-inbox.tsx` | concentra hero, stats, controls, summary y empty state del inbox | bajo |
| Fijar `list-first` como prioridad operativa | alinea el frente con scan speed real del inbox | bajo |
| Crear budget formal de queue controls | baja ruido y acelera validación | bajo |
| Crear budget formal de cards compactas | evita perseguir bugs de ancho uno por uno | medio |
| Pasar queue summary a criterio más operativo | reduce prosa compitiendo con cards | bajo/medio |
| Empty-state pass separado | visible, barato y casi sin coupling | bajo |
| Pack de validación + evidencia antes de tocar visual fino | acelera todas las olas siguientes | bajo |

## Zonas rojas

| Zona roja | Por qué | Riesgo |
|---|---|---|
| `components/layout/app-shell.tsx` sin freeze previo | impacta launcher e inbox al mismo tiempo y compite con top area | alto |
| `src/lib/core/record-view.ts` | concentra labels/descriptions/order de estados | alto |
| `src/lib/core/schema-registry.ts` | titles/summaries/field labels visibles, pero no locales | alto |
| `src/lib/utils.ts` (`formatDateTime`, `formatHumanLabel`) | mezcla formatting/humanización transversal | alto |
| `app/globals.css` sin validación cruzada | una mejora local puede regarse a múltiples superficies | alto |
| atacar list y grid con ambición simétrica desde el inicio | dispersa foco y retrasa scan speed | medio-alto |
| mezclar layout pass con limpieza terminológica | convierte un paso seguro en frente de naming/idioma/semántica | alto |

## Regla práctica
- **Quick win**: mejora local, visible, validable y reversible sin tocar semántica compartida.
- **Zona roja**: cualquier cosa que cambie el significado de estados, schema display, runtime o helpers transversales.

---

# 10. Artefactos adicionales que conviene producir

| Nombre | Para qué sirve | Prioridad | ¿Bloquea o solo ayuda? |
|---|---|---|---|
| `launcher-inbox-mini-steps.md` | convertir este plan en checklist ejecutable por mini paso | alta | ayuda fuerte |
| `launcher-inbox-validation-pack.md` | checklist reusable de validación por breakpoint y modo | alta | ayuda fuerte |
| `launcher-inbox-evidence-log.md` | guardar capturas, archivos tocados, resultados y stops | alta | ayuda fuerte |
| `top-area-budget-matrix.md` | fijar altura tolerable de shell + hero por breakpoint | media-alta | bloquea si shell entra |
| `queue-density-budget.md` | fijar límites visuales de controls, pills, summary y cards | alta | ayuda fuerte |
| `launcher-inbox-red-lines.md` | lista roja resumida para no abrir semántica sin querer | alta | ayuda fuerte |
| `worst-case-copy-stress-pack.md` | set de casos largos para probar cards, lanes y controls | media | ayuda |
| `affected-files-ledger.md` | ledger por mini intervención con “sí toca / no toca” | media-alta | ayuda fuerte |
| `scan-speed-review-sheet.md` | hoja breve para revisar lectura rápida del inbox | alta | ayuda fuerte |
| `decision-freeze-log.md` | congelar shell/states/schema/helpers/list-first | alta | ayuda fuerte |

---

# 11. Qué nos deja resuelto este chat

Este chat deja listo el **salto de mapa a ejecución controlada** del frente Launcher e Inbox.

## Qué parte del frente quedaría lista para ejecución
- el **orden mínimo recomendado**
- la división en **mini intervenciones seguras**
- la separación entre **quick wins** y **zonas rojas**
- la matriz de **dependencias reales**
- la validación por mini paso para:
  - launcher hero
  - launcher cards
  - inbox controls
  - inbox lanes
  - inbox cards
  - grid/list mode
  - empty states
  - scan speed
- la estructura de **trazabilidad y evidencia**

## Qué seguiría bloqueado
- decidir si **shell entra o sale** de la ola
- decidir si **states** siguen fuera como dominio propio
- decidir si **schema display** se congela fuera
- decidir si **format helpers visibles** se tocan o solo se registran como deuda
- decidir el **budget formal del top area** si shell participa

## Qué decisiones quedarían casi cerradas
- trabajar el inbox como **superficie de triage**, no como canvas narrativo
- priorizar **list mode** sobre grid mode para optimización inicial
- partir el frente por **controls → lanes → cards**, no por pantalla completa
- tratar launcher como **superficie premium de aterrizaje** con foco en hero y compact zones, no como refactor semántico de schemas
- usar evidencia y checklist como parte del trabajo, no como adorno de posproducción

## Qué intervención futura se volvería más rápida gracias a este entregable
1. extracción o limpieza de copy local de launcher
2. pase de densidad de inbox controls
3. pase de scan speed de inbox list mode
4. refinamiento visual de inbox cards
5. validación estructurada de launcher/inbox por breakpoint
6. eventual alineación de shell, pero ya con casco, mapa y cinta amarilla

## Qué nos deja resuelto este chat
Deja resuelta la **capa operativa** que faltaba encima del dossier: ya no solo sabemos qué hay, sino **cómo dividirlo, en qué orden tocarlo, qué puede correr en paralelo, qué no debe mezclarse, cómo validarlo y qué evidencia guardar**. Eso vuelve la futura intervención de Launcher e Inbox más rápida, más segura, más simple, más paralelizable y mucho menos propensa a romper scan speed o jerarquía visual.

---

# 🧪 Capítulo 4 · Flow runner, schema text y coupling con validation/state

# 1. Resumen ejecutivo de profundización

## Qué frente me tocó
Solo este frente:
- **Flow runner**
- **texto schema-driven visible dentro del flow**
- **coupling con validation / state / records service**
- **fugas semánticas o de persistencia que convierten copy aparente en semántica real**

## Qué ya estaba resuelto en el dossier
El dossier ya dejaba resuelto:
- el **mapa general del flow**
- la **separación base de ownership** entre local, schema, validation, state y backend
- la **lista roja inicial**
- la **validación mínima de alto nivel**
- las **minas grandes**: attachments, resume token, `accessMode`, `allowDrafts`, role mismatch, backend error propagation

## Qué huecos detecté
El dossier todavía no aterrizaba con suficiente filo operativo:
1. **Cómo partir una futura intervención en mini pasos de bajo blast radius.**
2. **Qué decisiones conviene congelar antes de tocar copy visible.**
3. **Qué sí puede correrse en paralelo y qué no.**
4. **Qué validación mínima exige cada mini paso y qué evidencia conviene guardar.**
5. **Qué etiquetas locales parecen seguras, pero en realidad están semánticamente infladas.**

## Qué nueva inteligencia operativa agrego

### Hallazgos nuevos o más aterrizados
1. **`Save Draft` no siempre “draft-ea”.** [Confirmado]  
   En create con `submit=false` sí crea en `draft`. Pero en update, el runner manda `state: recordState`, no `draft`. O sea: si el record ya venía en `submitted`, `awaiting_update` o `in_review`, el botón `Save Draft` solo actualiza el record conservando su estado actual.  
   **Implicación:** el label del CTA es local, pero su semántica real es más estrecha y potencialmente engañosa.

2. **Guardar draft no significa guardar incompleto.** [Confirmado]  
   `persist(false)` valida el step actual igual que `Save and Continue`. No existe hoy un draft permisivo por step incompleto.  
   **Implicación:** el concepto visible de “draft” no significa “partial save de cualquier cosa”; significa “save sin submit, pero con step válido”.

3. **`allowDrafts` hoy es puramente ornamental y todos los schemas de ejemplo lo traen en `true`.** [Confirmado]  
   El tipo lo soporta, el page lo muestra, pero el runner no lo usa para gobernar los CTAs. Además, en los tres schemas ejemplo el valor actual es `true`.  
   **Implicación:** no urge una bifurcación visual hoy, pero sí urge congelar el contrato antes de tocar CTA copy o capability labels.

4. **`editableInStates` existe en tipos, pero el flow runner no lo usa.** [Confirmado]  
   El modelo prevé gating por estado, pero el runner hoy renderiza/edita sin enforcement de ese campo.  
   **Implicación:** cualquier cambio a helper copy tipo “you can update this now” o cualquier lectura fuerte del estado puede volverse falsa.

5. **El progreso mide presencia/llenado, no validez semántica completa.** [Confirmado]  
   `getStepSummary()` usa `hasMeaningfulValue()`, no `validation.data`. Un field puede contar como presente y aun así fallar validación o ser semánticamente dudoso.  
   **Implicación:** copy de progreso, “required remaining” y step status no debe tocarse como si expresara “valid” sin decidirlo antes.

6. **Checkbox “required” no significa necesariamente “true”.** [Confirmado]  
   En validation, un checkbox required pasa con `false`; required significa presencia/coerción válida, no aceptación afirmativa.  
   **Implicación:** cualquier copy fuerte en required states o hints puede meter semántica falsa.

7. **`lastSavedAt` del sidebar es optimista y client-side.** [Confirmado]  
   Tras save/update, el runner usa `new Date().toISOString()` local en vez de tomar `body.record.updatedAt`.  
   **Implicación:** el sidebar muestra una verdad útil para UX, pero no estrictamente backend-canonical.

8. **`handleSubmit()` fuerza client-side `submitted` después del save exitoso.** [Confirmado]  
   Aunque `persist(true)` ya recibe `body.record.state`, luego `handleSubmit()` vuelve a hacer `setRecordState("submitted")`.  
   **Implicación:** el CTA final asume contrato rígido de estado objetivo.

### Resultado de esta profundización
Lo que sigue ya puede organizarse como:
- **mini intervenciones seguras**
- **decisiones previas a congelar**
- **tareas paralelizables**
- **bloqueos reales**
- **validación operativa por mini paso**
- **evidencia mínima a guardar**

---

# 2. Lo que aún falta investigar o confirmar

| Incógnita | Por qué importa | Riesgo que evita | ¿Bloquea primera intervención? | Dónde confirmarlo |
|---|---|---|---|---|
| ¿`Save Draft` debe significar “volver a draft”, “guardar sin submit” o “guardar progreso del estado actual”? | El CTA hoy promete más de lo que garantiza en update | Semántica falsa en CTA principal | **Sí**, para tocar copy de CTAs | `components/flow/flow-runner.tsx`, `src/lib/services/records.ts`, `src/lib/core/state.ts` |
| ¿Guardar draft debe permitir step incompleto o debe seguir exigiendo validación del step actual? | Define si el flow es realmente resumable a mitad de step | UX engañosa y frustración operativa | **Sí**, para tocar helper copy y CTA semantics | `flow-runner.tsx`, `validation.ts` |
| ¿`allowDrafts` debe ocultar/deshabilitar `Save Draft` o quedarse solo como metadata visual? | Hoy el header lo exhibe como capability real | Etiqueta de capability sin enforcement | **No** para copy muy local, **sí** para tocar capability labels/CTAs | `page.tsx`, `types.ts`, `schema-registry.ts`, `flow-runner.tsx` |
| ¿`accessMode` debe aplicarse operativamente en esta ruta o seguirá siendo solo descriptor? | Hoy muestra semántica de acceso sin enforcement visible | Copy que aparenta control de acceso real | **No** para copy muy local, **sí** para tocar header chips o flujo token/auth | `page.tsx`, `types.ts`, búsquedas globales de `accessMode` |
| ¿El actor canónico del flow es `public` o `external_user`? | Cliente y servidor hoy divergen | Inconsistencias de visibilidad y validación | **Sí**, para cualquier intervención que toque validation-related UX | `flow-runner.tsx`, `request-context.ts`, rutas API |
| ¿El token debe ser solo lookup inicial o también canal real de persistencia posterior? | Hoy existe API token PATCH, pero el runner no la usa | Contrato token-resume roto a medias | **No** para shell local, **sí** para tocar resume token copy fuerte | `page.tsx`, `flow-runner.tsx`, `app/api/records/token/[token]/route.ts` |
| ¿Cuál es la fuente de verdad para attachments en superficies futuras: `fields[fieldId]`, metadata de attachments o ambas? | Hoy hay doble representación | Persistencia contaminada, duplicidad visual, búsquedas engañosas | **Sí**, para tocar cualquier texto o UI relacionada con attachments persistidos | `flow-runner.tsx`, `services/records.ts`, stores, detail/inbox consumers |
| ¿`editableInStates` debe empezar a gobernar edición del flow o es ruido de modelo aún no usado? | Existe en tipos pero no en runtime | Cambios visuales que prometen permisos falsos | **No** para quick wins locales, **sí** para helper copy que implique editabilidad | `types.ts`, búsquedas globales de `editableInStates` |
| ¿El progreso debe representar “campos presentes”, “required completos” o “step válido”? | Hoy mezcla presencia con required y visibilidad | Progreso narrado como validez cuando no lo es | **Sí**, para tocar progreso/required-related copy | `flow-runner.tsx`, `validation.ts` |
| ¿Las labels y descripciones de estado son catálogo canónico compartido o helper transitorio? | Pegan en flow, inbox y detail | Divergencia transversal entre superficies | **No** para local shell, **sí** para sidebar/state-related copy | `record-view.ts`, `state-badge.tsx`, consumers |
| ¿Los errores visibles deben venir crudos de service/API o pasar por una capa de normalización? | Hoy la notice puede mostrar `error.message` tal cual | UX inconsistente, mensajes demasiado técnicos | **No** para fallback local puro, **sí** para tocar error UX de forma seria | `flow-runner.tsx`, rutas API, `services/records.ts` |
| ¿El `updatedAt` visible debe ser client-optimistic o backend-canonical? | Hoy el sidebar usa hora local al guardar | Divergencia sutil de evidencia operativa | **No** para primera ola local, **sí** para robustecer sidebar/status | `flow-runner.tsx`, respuestas API |

---

# 3. Decisiones previas que conviene congelar

| Decisión | Opciones | Recomendación | Por qué | Costo de no decidirla ahora | ¿Bloquea ejecución? |
|---|---|---|---|---|---|
| Semántica real de `Save Draft` | a) volver a `draft` siempre, b) guardar sin submit manteniendo estado, c) renombrar el CTA | **Congelar explícitamente la opción b o renombrar después** | Es lo que el código hace hoy en update | El CTA queda semánticamente inflado | **Sí** para tocar CTA copy |
| Política de validación al guardar draft | a) exigir step válido, b) permitir parcial, c) híbrido | **Congelar a corto plazo la opción a como “comportamiento actual”** | Es la verdad operativa actual | Se redacta ayuda engañosa | **Sí** para footer/help copy |
| Gobernanza de `allowDrafts` | a) display-only, b) es capability real, c) feature flag futura | **Congelar temporalmente como display-only documentado** | Hoy no gobierna nada | Se introduce copy o UI inconsistente | **Sí** para tocar chips/capability copy |
| Gobernanza de `accessMode` | a) descriptor, b) enforcement route-level, c) enforcement API-level | **Congelar temporalmente como descriptor** | Hoy no se aplica en el flow runner | Header puede vender seguridad inexistente | **Sí** para tocar copy fuerte de acceso |
| Contrato del actor | a) `public`, b) `external_user`, c) token-auth híbrido | **Cerrar un actor canónico antes de tocar validation-related UX** | Cliente y servidor hoy divergen | Bugs de visibilidad, validación y futuros fields role-gated | **Sí** |
| Contrato del resume token | a) lookup-only, b) canal de persistencia posterior, c) mixed mode | **Congelar como lookup-only hasta que se rediseñe** | Es lo que realmente hace hoy el runner | Copy y UX prometen más de lo que pasa | **Sí** para tocar token copy fuerte |
| Fuente de verdad de attachments | a) field string, b) metadata estructurada, c) dual con contrato explícito | **Cerrar antes de tocar cualquier texto persistido o surfaces conectadas** | Hoy hay doble representación | Se perpetúa contaminación de persistencia | **Sí** |
| Semántica del progreso | a) presencia, b) required completos, c) validez de step | **Documentar hoy que es “presencia/required”, no “valid”** | Es lo que computa el runner | Se reescribe copy con semántica falsa | **Sí** para intervenir progreso |
| Política de error visible | a) raw backend, b) normalized catalog, c) híbrido | **Congelar una política antes de tocar notices serias** | Hoy el runner mezcla fallback local y error crudo | Mensajes inconsistentes o demasiado técnicos | **No** para quick wins locales, **sí** para error UX seria |
| Canonicidad del estado visible | a) `record-view` manda, b) state catalog separado, c) fallback transitorio | **Aceptar por ahora que `record-view` manda** | Hoy es la fuente efectiva | Se toca sidebar y se rompe consistencia con inbox/detail | **Sí** para tocar state-related copy |

---

# 4. Mapa de mini intervenciones seguras

> Nota: aquí “segura” significa **bajo blast radius** y **frontera clara**. Algunas son ejecutables de inmediato; otras son seguras solo como precondición documental o de freeze, no como cambio visual todavía.

| Nombre corto | Objetivo | Archivos probables | Qué sí toca | Qué no toca | Precondiciones | Riesgo | Resultado visible esperado | Validación mínima | ¿Paralelo? |
|---|---|---|---|---|---|---|---|---|---|
| **MI-01 Page shell local** | Aislar y preparar solo el copy local del page shell | `app/flow/[schemaId]/page.tsx` | eyebrow, description, CTAs locales, surface de resume, labels locales del form | `schema.title`, `accessMode`, `allowDrafts`, `ext_xxx` | Dossier base ya aceptado | bajo | Shell del page claramente separado de schema/runtime | Flow con y sin `token` en query; nada schema/state/backend cambia | **Sí** |
| **MI-02 Runner local notices** | Encapsular notices y fallback locales del runner | `components/flow/flow-runner.tsx` | config issue local, success/fallback notices, helper local de attention banner | `errors[fieldId]`, `error.message`, validation strings, service errors | Ninguna extra | bajo | Notice channel local identificado y listo para intervención futura | Forzar validación fallida y save exitoso; verificar qué parte sigue siendo backend/validation | **Sí** |
| **MI-03 Sidebar chrome split** | Separar labels locales del sidebar/helper panels de lo que ya es state/shared | `components/flow/flow-runner.tsx`, `src/lib/utils.ts`, `src/lib/core/record-view.ts` | `Session summary`, `Why this feels safe`, labels locales del panel, helper cards | `StateBadge`, `stateDescription`, `formatRelativeTime` | Aceptar que estado y relative time quedan fuera | bajo-medio | Sidebar con frontera clara entre shell local y semántica compartida | Validar sidebar en record nuevo y reanudado; cero cambio en badge/description/time formatter | **Sí** |
| **MI-04 CTA semantic freeze** | Congelar significado real de CTAs antes de tocar copy | `flow-runner.tsx`, `services/records.ts`, `state.ts` | documentación operativa, truth table de CTA vs estado | labels finales, implementación, state catalog | Confirmar create/update flows | medio | Queda una matriz inequívoca de qué hace cada CTA en create/update/resume | Casos: create draft, update from draft, update from submitted/awaiting_update, submit final | **Sí**, como análisis |
| **MI-05 Progress contract freeze** | Definir qué expresa realmente progreso/required | `flow-runner.tsx`, `validation.ts`, `visibility.ts` | contrato conceptual de progreso y required states | algoritmo final, visual final, schema text | Ninguna extra | medio | Queda claro qué frases pueden usarse sin mentir | Casos: field visible/hidden, required vacío, invalid number, checkbox false required | **Sí**, como análisis |
| **MI-06 Attachment seam freeze** | Documentar la costura exacta donde attachments dejan de ser solo UI | `flow-runner.tsx`, `services/records.ts`, stores, attachments API | data-flow completo attachment -> field string -> upload metadata | rediseño de persistencia, detail/inbox final | Ninguna extra | alto pero controlado | Queda una verdad operativa única sobre attachments | Selección local, payload create/update, upload fail, record persistido, metadata separada | **Sí**, como análisis |
| **MI-07 Role alignment freeze** | Cerrar divergencia cliente `external_user` vs servidor `public` | `flow-runner.tsx`, `request-context.ts`, routes API, `validation.ts`, `visibility.ts` | contrato de actor y tabla de implicaciones | enforcement final | Ninguna extra | medio-alto | Queda claro si el flow es verdaderamente external-user o public | Validar headers ausentes vs presentes; visibilidad/validation por role | **Sí**, como análisis |
| **MI-08 Resume token contract** | Aclarar si el token es lookup-only o canal operativo posterior | `page.tsx`, `flow-runner.tsx`, token route API, `request-context.ts` | truth table del token en page, sidebar y persistencia | cambios de routing, auth, implementation final | Ninguna extra | medio | Queda nítido qué partes del token son solo UX y cuáles son contrato real | Token válido, inválido, create nuevo, PATCH por id, API PATCH por token | **Sí**, como análisis |
| **MI-09 Error source split** | Separar error local, validation, service y API | `flow-runner.tsx`, `validation.ts`, `services/records.ts`, routes API | inventario y clasificación de mensajes visibles | catalog final, traducción, remapeo de errores | Dossier base ya aceptado | medio | Error UX listo para intervención futura sin mezclar sources | Invalid step, invalid transition, upload fail, token missing, validation fail | **Sí** |
| **MI-10 Field rendering local-only sweep** | Aislar solo los textos de UI local dentro del render de fields | `flow-runner.tsx` | `Required`, `Select...`, `Enabled/Disabled`, helper de checkbox, helper de file | `field.label`, `helpText`, `placeholder`, `options[]` | Aceptar schema text como fuera | bajo-medio | Render de fields partido entre local shell y schema-owned | Text, textarea, select, checkbox, file, number, date; comprobar que schema text no se tocó | **Sí** |

---

# 5. Mapa de paralelización

| Tareas paralelizables | Tareas no paralelizables | Dependencias | Orden mínimo recomendado | Combinaciones peligrosas |
|---|---|---|---|---|
| MI-01 Page shell local, MI-02 Runner local notices, MI-03 Sidebar chrome split, MI-06 Attachment seam freeze, MI-07 Role alignment freeze, MI-08 Resume token contract, MI-09 Error source split, MI-10 Field rendering local-only sweep | Cualquier cambio serio en CTAs antes de MI-04, cualquier ajuste de progreso antes de MI-05, cualquier retoque semántico de sidebar/state antes de cerrar estado canónico | MI-04 depende de revisar create/update/resume flows; MI-05 depende de revisar summary + validation + visibility; cualquier cambio de attachments depende de MI-06 | 1) MI-06 + MI-07 + MI-08 + MI-09, 2) MI-01 + MI-02 + MI-03 + MI-10, 3) MI-04, 4) MI-05 | CTA copy + state semantics; file helper copy + attachment persistence; token UX copy + token contract ambiguo; progress copy + algoritmo no congelado; error UX + raw backend errors sin política |

## Orden recomendado en versión simple
1. **Congelar costuras peligrosas**: attachments, actor role, token, error sources.  
2. **Separar shell local seguro**: page shell, notices, helper panels, local field-render copy.  
3. **Congelar semántica de CTAs**.  
4. **Congelar semántica de progreso / required states**.  
5. Solo después pensar en una intervención visible más amplia.

## Combinaciones especialmente peligrosas
- **CTAs + state labels** en la misma corrida.
- **File-field helper copy + cualquier cambio de persistencia de attachments**.
- **Resume token shell copy + decisiones de auth/persistencia posterior**.
- **Progress copy + required/validation semantics**.
- **Sidebar local labels + `StateBadge` / `stateDescription()`** sin frontera explícita.

---

# 6. Dependencias y acoplamientos reales

| Archivo / componente | De qué depende | Tipo de acoplamiento | Nivel de riesgo | Implicación para la intervención |
|---|---|---|---|---|
| `app/flow/[schemaId]/page.tsx` | `getSchema()`, `getRecordByToken()`, `PageHeader`, `Surface`, `FlowRunner` | composición + schema + token lookup | medio | El shell del page sí puede aislarse, pero title/chips ya tocan schema y capability metadata |
| `components/flow/flow-runner.tsx` | schema, validation, visibility, state view, utils, APIs | acoplamiento central multi-capa | **muy alto** | Aquí vive la mayor parte de la frontera entre UI local y semántica real |
| `src/lib/core/schema-registry.ts` | tipos de schema | schema-driven display + flow semantics | **muy alto** | Step titles, descriptions, labels, placeholders, options y `accessMode/allowDrafts` no son copy local |
| `src/lib/core/validation.ts` | `getFieldById()`, `isFieldVisible()`, zod | validation semantics + mensajes visibles | alto | Los errores inline y parte de required/error states nacen aquí |
| `src/lib/core/visibility.ts` | field rules + role | visibility semantics | alto | Visible fields, progreso y validación dependen de este gating |
| `src/lib/core/state.ts` | state machine | transition semantics | alto | CTAs y save/update no deben hablar de estado a la ligera |
| `src/lib/core/record-view.ts` | `formatHumanLabel()`, schema helpers | state presentation shared | alto | Sidebar y badge del flow dependen de un catálogo compartido con inbox/detail |
| `components/ui/state-badge.tsx` | `stateLabel()`, `stateTone()`, `ensureRecordState()` | shared wrapper + state semantics | medio-alto | El wrapper es shared, pero el label no es suyo |
| `src/lib/services/records.ts` | schema, validation, transitions, store, sync events | service semantics + persistence | **muy alto** | Aquí varios strings dejan de ser UI y se vuelven data, title o evidence operativa |
| `src/lib/request-context.ts` | request headers | actor/source-of-truth | alto | Role mismatch actual impacta visibilidad y validación futura |
| `app/api/records/route.ts` | request-context + `createRecord()` | API error propagation | alto | Create errors pueden llegar crudos al runner |
| `app/api/records/[recordId]/route.ts` | request-context + `updateRecord()` | API update propagation | alto | El runner usa esta ruta para persistencia posterior al resume |
| `app/api/records/token/[token]/route.ts` | token lookup + `updateRecord()` | token channel alterno | medio-alto | Existe contrato API que el runner actual no usa |
| `app/api/records/[recordId]/attachments/route.ts` | form-data upload + metadata add | attachment persistence seam | **muy alto** | No es atómico con create/update; deja persistencia parcial posible |
| `src/lib/store/memory-store.ts` / `prisma-store.ts` | record fields JSON + attachment subresource | storage contract | **muy alto** | Confirman que el string de attachments sí se persiste como `fields` |
| `src/lib/utils.ts` | `formatRelativeTime()`, `formatHumanLabel()` | shared formatting | medio | El flow sidebar y estados no son 100% locales |
| `tests/external-template.test.ts` | create/update/token/state behavior | evidencia de intención actual | medio | Ayuda a confirmar qué contratos ya parecen asumidos por el proyecto |

## Acoplamientos finos que conviene no perder de vista
- **CTA label local vs state transition real**.
- **Progress copy local vs visibility/required semantics**.
- **Sidebar shell local vs state catalog shared**.
- **File helper local vs field string persistido + metadata separada**.
- **Resume token shell UX vs save/update por `recordId`**.
- **Validation local banner vs messages nacidos en `validation.ts` y `services/records.ts`**.

---

# 7. Validación operativa por mini paso

| Mini intervención | Qué validar | Dónde validar | Tipo de validación | Criterio de aceptación | Señal de stop | Evidencia a guardar |
|---|---|---|---|---|---|---|
| MI-01 Page shell local | Header shell, panel de resume, CTAs `New session` / `Open inbox` / `Resume with token` / `Clear` | `/flow/[schemaId]` con y sin `?token=` | visual + smoke nav | Solo cambia shell local; `schema.title`, chips y token técnico siguen intactos | Algún chip o valor schema parece local y se tocó por accidente | captura de page shell antes/después, lista exacta de literales intervenidos |
| MI-02 Runner local notices | fallback local, success notice, danger fallback, attention banner | step con validación fallida y save exitoso | funcional + source-tracing | Queda claro qué notice es local y cuál sigue siendo backend/validation | aparece `error.message` crudo mezclado dentro del mismo alcance | tabla notice -> source real, screenshots de 3 casos |
| MI-03 Sidebar chrome split | labels locales del sidebar, helper panels, cards de seguridad | record nuevo, record ya guardado, record reanudado | visual + ownership | `StateBadge`, `stateDescription`, `formatRelativeTime` quedan explícitamente fuera | se intenta tocar badge/description/time formatter como si fueran locales | matriz sidebar field -> local/shared/state |
| MI-04 CTA semantic freeze | `Save Draft`, `Save and Continue`, `Submit for Review`, `Back` | create nuevo, update de draft, resume de submitted, resume de awaiting_update | truth-table funcional | Cada CTA queda descrito por comportamiento real, no por intuición | el label visible contradice la tabla y no se acepta documentarlo | truth table por estado inicial / resultado / endpoint usado |
| MI-05 Progress contract freeze | steps, `% complete`, `x/y required`, `Required remaining`, attention banner | step vacío, invalid number, select inválido, hidden field, checkbox false required | funcional + semántica | Queda documentado qué significa progreso hoy | se descubre que copy futura intentaría llamar “valid” a algo que solo es “present” | tabla de casos con valores, summary y validation outcome |
| MI-06 Attachment seam freeze | file selection local, serialización, create/update payload, upload posterior, persistencia parcial | step con file field visible, create, update, upload fail | data-flow + funcional | Queda una sola verdad del seam attachment | alguien intenta tocar `attachment(s)` como si fuera texto decorativo | payloads capturados, flujo secuencial, nota sobre `fields` y metadata |
| MI-07 Role alignment freeze | visibilidad y validación con role cliente vs role servidor | requests sin headers y, si aplica, simulación con headers | contract validation | Se cierra cuál actor manda y dónde | sigue habiendo dos verdades no reconciliadas | matriz cliente/server role + implicaciones |
| MI-08 Resume token contract | token válido, token inválido, save posterior, API token PATCH existente | page load, runner save, token API | funcional + contract | Queda claro que el token hoy es lookup-only o se eleva a contrato mayor | se reescribe token UX sin cerrar el contrato | diagrama simple query token -> initialRecord -> save path |
| MI-09 Error source split | required/error states, validation strings, API/service errors, attachment errors | invalid field, invalid transition, token missing, upload fail | source-tracing | Cada error visible queda etiquetado por source real | se intenta “arreglar” un error backend con copy local | inventario error -> source -> surface |
| MI-10 Field rendering local-only sweep | `Required`, `Select...`, checkbox labels, file helper, local file count | text, select, checkbox, file, date, number | visual + ownership | El render de fields queda partido entre local shell y schema text | `field.label`, `placeholder`, `options[]` o `helpText` se tratan como locales | inventario por kind con source confirmado |

## Cobertura explícita pedida
- **steps:** MI-05  
- **progreso:** MI-05  
- **CTAs:** MI-04  
- **required/error states:** MI-02 + MI-05 + MI-09  
- **attachments:** MI-06  
- **save/submit:** MI-04 + MI-06  
- **resume token:** MI-08  
- **sidebars / status / helper panels:** MI-03

---

# 8. Trazabilidad y evidencia

## Qué registrar siempre

| Qué registrar | Qué incluir mínimo | Formato sugerido |
|---|---|---|
| Decisiones | decisión, fecha, owner, racional, impacto, si bloquea o no | tabla de decisiones |
| Hallazgos | hallazgo, source real, confirmación o inferencia, impacto | registro de hallazgos |
| Bloqueos | bloqueo, qué lo destraba, severidad, dependencia asociada | tabla de bloqueos |
| Riesgos | riesgo, superficie, probabilidad, impacto, stop signal | matriz de riesgos |
| Validaciones | caso, resultado esperado, resultado real, evidencia | checklist + tabla |
| Archivos tocados o candidatos | archivo, zona, tipo de texto, ownership | inventario por archivo |
| Checkpoints conceptuales | CTA semantics, token contract, attachments source of truth, progress semantics, actor source of truth | lista de checkpoints |
| Artefactos a conservar | tablas, truth tables, capturas, payload examples, matrices | carpeta o sección dedicada |

## Checkpoints conceptuales que no deberían faltar
1. **CTA semantics frozen**  
2. **Attachment seam documented**  
3. **Actor role source of truth frozen**  
4. **Resume token contract frozen**  
5. **Progress semantic contract frozen**  
6. **Sidebar split local vs shared/state confirmed**

## Evidencia mínima recomendable por frente
- screenshot o nota estructurada de:
  - flow nuevo vacío
  - flow con token válido
  - validation fail actual
  - submit actual
  - upload fail actual
- captura de payload o pseudo-payload de:
  - create
  - update
  - attachment upload
- tabla de:
  - local literal -> source file
  - non-local literal -> source file
- truth table de:
  - CTA -> endpoint -> state expected -> state real

## Artefactos a conservar aunque no bloqueen
- matriz CTA / state
- matriz progress / validity
- diagrama attachment field string vs metadata
- diagrama token lookup vs update by id
- matriz actor cliente/servidor
- inventario sidebar local vs shared/state

---

# 9. Quick wins reales vs zonas rojas

## Quick wins

### 1) Shell local del page
**Por qué sí**  
Tiene frontera clara y el blast radius es bajo si se excluyen `schema.title`, `accessMode`, `allowDrafts` y `ext_xxx`.

### 2) Notices locales del runner
**Por qué sí**  
`Flow configuration issue`, success notices, fallback local y parte del attention banner son claramente del runner. La clave es no meter dentro de esa bolsa `validation.ts` ni `error.message` propagado.

### 3) Helper panels locales
**Por qué sí**  
`Session summary`, `Why this feels safe` y varias labels del sidebar sí son shells locales. El truco es dejar fuera `StateBadge`, `stateDescription()` y `formatRelativeTime()`.

### 4) Sweep local del render de fields
**Por qué sí**  
`Required`, `Select...`, `Enabled/Disabled`, helper del checkbox y helper del file field tienen source local claro. Solo hay que no confundirlos con schema text.

### 5) Congelar contratos antes de tocar superficies semánticas
**Por qué sí**  
No cambia código, pero reduce mucho el riesgo. Aquí entran CTA semantics, attachment seam, role alignment, token contract y progress semantics.

## Zonas rojas

### 1) CTAs sin freeze previo
**Por qué roja**  
`Save Draft` ya no significa lo que parece en todos los casos. Cambiar texto sin congelar contrato es receta para una UX tramposa.

### 2) Attachments
**Por qué roja**  
Aquí la UI ya se volvió persistencia. El string `"n attachment(s)"` ya no es detalle de UI. Es dato persistido y además convive con metadata real de attachments.

### 3) Estado visible
**Por qué roja**  
`StateBadge` y `stateDescription()` son shared semantics, no copy aislada del flow.

### 4) Validation strings
**Por qué roja**  
Nacen en `validation.ts` y también son reemitidas/encapsuladas por service/API. Tocarlas solo desde el runner deja costuras abiertas.

### 5) Header chips de capability
**Por qué roja**  
`Access: ...` y `Drafts: enabled/disabled` parecen decorativos, pero expresan capacidad real o metadatos que el runtime no aplica todavía.

### 6) Resume token fuerte
**Por qué roja**  
El token sí existe y sí sirve, pero solo para lookup inicial en el flujo actual. No conviene sobrerredactar su poder operativo.

### 7) Relative time / formatting shared
**Por qué roja**  
El sidebar depende de `formatRelativeTime()` compartido. No es un texto puramente local del flow.

---

# 10. Artefactos adicionales que conviene producir

| Nombre | Para qué sirve | Prioridad | ¿Bloquea o solo ayuda? |
|---|---|---|---|
| `flow_cta_truth_table.md` | Congelar semántica real de `Save Draft`, `Save and Continue`, `Submit for Review`, `Back` | alta | **Bloquea** CTA work serio |
| `flow_attachment_seam.md` | Documentar string persistido vs metadata estructurada y persistencia parcial | alta | **Bloquea** cualquier trabajo serio sobre attachments |
| `flow_actor_role_matrix.md` | Cerrar cliente `external_user` vs servidor `public` | alta | **Bloquea** validation/state-sensitive work |
| `flow_resume_token_contract.md` | Aclarar si el token es lookup-only o canal de persistencia | alta | **Bloquea** token UX serio |
| `flow_progress_contract.md` | Definir si progreso = presencia, required completo o validez | alta | **Bloquea** progreso/required copy seria |
| `flow_error_source_inventory.md` | Separar local / validation / service / API errors | media-alta | ayuda fuerte; bloquea solo error UX profunda |
| `flow_sidebar_split_inventory.md` | Partir sidebar entre local shell y shared/state/time | media | ayuda fuerte |
| `flow_field_render_inventory.md` | Mapear por kind qué texto es local y qué es schema-owned | media | ayuda fuerte |
| `flow_partial_persistence_cases.md` | Registrar save-ok/upload-fail y otros casos parciales | media | ayuda fuerte |
| `flow_execution_checklist.md` | Checklist por mini intervención con stop signals y evidencia mínima | media | ayuda fuerte |

---

# 11. Qué nos deja resuelto este chat

## Qué parte del frente quedaría lista para ejecución
Queda lista, o casi lista, una ejecución controlada sobre:
- shell local del page
- notices locales del runner
- helper panels locales del runner
- sweep local del render de fields
- inventario de errores por source
- freeze documental de CTAs, attachments, actor role, token y progreso

En otras palabras: la parte **visual-local y de segmentación operativa** del flow ya puede organizarse con bisturí, sin volver a empezar desde cero.

## Qué seguiría bloqueado
Seguiría bloqueado hasta cerrar contrato:
- cualquier cambio serio en CTAs
- cualquier retoque semántico de progreso / required states
- cualquier intervención sobre attachments persistidos
- cualquier copy fuerte de resume token
- cualquier cambio que mezcle state labels/descriptions
- cualquier intento de “arreglar” errores sin decidir política de source
- cualquier cambio que dependa de resolver `public` vs `external_user`

## Qué decisiones quedarían casi cerradas
Después de este entregable, quedan casi listas para cierre estas decisiones:
1. **El flow necesita una truth table formal de CTAs antes de tocar labels.**
2. **Attachments son zona de contrato, no de copy.**
3. **El actor canónico del flow debe definirse antes de tocar validación visible.**
4. **El token actual debe tratarse como lookup-only hasta prueba contraria.**
5. **Progreso no debe narrarse como “valid” sin cerrar contrato.**
6. **Sidebar y helper panels sí pueden separarse local vs shared/state sin invadir semántica real.**

## Qué intervención futura se volvería más rápida gracias a este entregable
Se volverían mucho más rápidas:
- una futura intervención visual-local del flow
- una futura extracción controlada de copy local del flow
- una futura validación por mini paso
- la discusión de CTAs, token y attachments, porque ya llegarían con mesa puesta en vez de pelear contra niebla
- cualquier rollout posterior que quiera partir el flow en piezas paralelizables con evidencia y stop signals claros

## Qué nos deja resuelto este chat
Este chat deja resuelto algo muy específico y muy útil:

- el flow ya no está solo “mapeado”
- ahora también está **operacionalizado**

Eso significa que ya quedó claro:
- **qué mini pasos son seguros**
- **qué decisiones hay que congelar primero**
- **qué tareas pueden correr en paralelo**
- **qué validación mínima necesita cada paso**
- **qué evidencia conviene guardar**
- **qué zonas siguen rojas aunque visualmente parezcan inocentes**

La diferencia práctica es enorme: la próxima intervención ya no tendría que entrar al flow con casco genérico y rezos. Entraría con ruta, checkpoints, fronteras claras y un mapa bastante preciso de dónde empieza la UI local y dónde empieza el cableado con dientes.

---

# 🛰️ Capítulo 5 · Record detail, timeline y sync center

# 1. Resumen ejecutivo de profundización

## Qué frente me tocó
Profundización operativa del frente **record detail + activity timeline + sync center**, tomando como base el capítulo ya consolidado del dossier y el zip real del template.

## Qué ya estaba resuelto en el dossier
**Ya venía resuelto** que estas tres superficies mezclan copy local con evidencia operativa y semántica sensible, que el timeline no es solo UI sino una capa narrativa, y que sync contiene métricas, filtros, retries, errors y summaries atados a contratos reales. También venía resuelta la lista roja base, el mapa de ownership tentativo y la validación operativa gruesa.

## Qué huecos detecté
El dossier dejaba bien nivelada la cancha, pero todavía faltaba bajar a terreno estas piezas de ejecución:
- **cómo partir el frente en mini intervenciones pequeñas y seguras**
- **qué puede correrse en paralelo y qué no**
- **qué decisiones conviene congelar antes de tocar una línea**
- **qué dependencia bloquea solo cierto mini paso, no todo el frente**
- **qué evidencia mínima guardar por mini intervención para no perder trazabilidad**
- **cómo separar detail en subfrentes internos**, porque hoy está demasiado fácil tratarlo como una sola cosa

## Qué nueva inteligencia operativa agrego
### Confirmado
1. **`record-detail.tsx` no es una sola superficie lógica.** Tiene al menos cuatro subfrentes distintos:
   - shell local del detail
   - bloque `Business details` schema-driven
   - bloque `Record controls` acoplado a acciones y roles
   - bloque lateral operativo con metadata, attachments, dispatch y sync
2. **El timeline no debe tratarse como lista de eventos crudos.** `ActivityTimeline` consume `createTimelineEntries()`, y esa función ya convierte submissions, dispatch jobs y sync events en una narración ordenada con `title`, `description`, `state`, `detail` y `meta`. Eso ya es una reinterpretación, no una simple vista. **Confirmado.**
3. **El sync center sí se puede partir.** Tiene una capa local segura muy nítida: header, subtítulos, empty states, wrappers y meta text. Luego tiene otra capa operativa de alto riesgo: métricas, filtros, badges, errors, summary, direction y retry semantics. **Confirmado.**
4. **La futura ejecución conviene organizarse por mini pasos con distinto owner operativo**, no por archivo completo.

### Inferido
- La forma más segura de mover este frente no es “detail/timeline/sync” como tres bloques, sino una rejilla más controlada:
  - **detail shell local**
  - **detail metadata wrappers**
  - **detail controls chrome**
  - **detail operational side-panel wrappers**
  - **timeline shell/empty wrapper**
  - **sync shell local**
  - **sync operational semantics freeze**
- Esto permite trabajar rápido sin tocar todavía evidence, summary, retries ni glosario operativo.

---

# 2. Lo que aún falta investigar o confirmar

| Incógnita | Por qué importa | Riesgo que evita | ¿Bloquea primera intervención? | Dónde confirmarlo |
|---|---|---|---|---|
| Si `record.title` debe tratarse siempre como data-owned visible | hoy es el `title` del `PageHeader` del detail | tocar un heading que en realidad es dato del negocio | **No** para shell local; **sí** para tocar el heading | `components/records/record-detail.tsx`, `src/lib/services/records.ts` |
| Si `schema.summary` puede convivir temporalmente sin tocarse dentro del header del detail | hoy alimenta la descripción principal del detail | mezclar shell local con schema content en una misma corrida | **No** si se excluye el header description; **sí** si se quiere tocar el header completo | `record-detail.tsx`, `src/lib/core/schema-registry.ts` |
| Si `action.label` es intocable por ser schema-owned o si habrá una capa display-only futura | hoy el botón visible en controls usa `action.label` directo | cambiar UI de controls y deformar el contrato de acción | **Sí** para intervenir labels de acciones; **no** para wrapper/chrome de controls | `record-detail.tsx`, `schema-registry.ts` |
| Si los roles visibles (`external_user`, `reviewer`, `approver`, `operator`) pueden tener alias display-only | el selector de role mezcla contrato de ejecución con texto visible | confundir permisos reales con una versión “bonita” | **Sí** para tocar el selector; **no** para el resto del panel | `record-detail.tsx`, `src/lib/request-context.ts`, `src/lib/core/types.ts` |
| Si `stateLabel/stateDescription` son glosario oficial o placeholders actuales | detail y timeline usan el mismo glosario shared | divergencia entre detail, inbox, timeline y futuros labels | **Sí** para tocar estados; **no** para wrappers locales | `src/lib/core/record-view.ts` |
| Si `latestSync.status` debe permanecer raw o merece display mapping | hoy vive en una stat card editorializada | que una métrica editorial o card mezcle state domains | **Sí** para tocar esa stat card | `record-detail.tsx`, `src/lib/core/types.ts` |
| Owner real de `event.summary` | aparece en detail, timeline y sync | tratar evidence como copy local | **Sí** para tocar summaries; **no** para shell local del sync | `record-detail.tsx`, `record-contracts.ts`, `sync-center.tsx`, `services/actions.ts`, `services/records.ts` |
| Política de raw error vs normalized error | detail y sync muestran error crudo junto a feedback local | maquillar errores o volverlos inconsistentes | **Sí** para feedback/error texts; **no** para wrappers seguros | `record-detail.tsx`, `sync-center.tsx`, action/retry routes, services |
| Si `secureToken` debe seguir visible tal cual | detail lo muestra como metadata operativa | tocar evidencia sensible o degradar soporte operativo | **Sí** para cualquier intervención sobre ese valor | `record-detail.tsx` |
| Si el timeline debe preservar exactamente su narrativa actual | hoy `createTimelineEntries()` remapea estados y compacta evidence | deformar la historia histórica del record | **Sí** para cualquier cambio en title/description/state/detail del timeline | `activity-timeline.tsx`, `record-contracts.ts` |
| Si retry debe comunicarse siempre como sujeto `dispatch job` | UI del sync puede inducir a pensar en “sync retry” | desalinear sujeto real de la acción | **Sí** para wording de retry y feedback | `sync-center.tsx`, `services/actions.ts`, retry route |
| Si `direction` y `adapterId` admiten alias display-only | aparecen en timeline y sync como metadata visible | romper trazabilidad operativa | **Sí** para tocar metadata visible técnica | `record-contracts.ts`, `sync-center.tsx`, `types.ts` |

### Lectura operativa
- **No todo bloquea todo.**
- Las incógnitas fuertes bloquean **acciones**, **estados**, **summaries**, **errors**, **roles** y **retry semantics**.
- No bloquean una primera ola enfocada en **shell local**, **wrappers seguros**, **empty states**, y **segmentación del trabajo**.

---

# 3. Decisiones previas que conviene congelar

| Decisión | Opciones | Recomendación | Por qué | Costo de no decidirla ahora | ¿Bloquea ejecución? |
|---|---|---|---|---|---|
| Política de `record.title` en detail | data-owned / display-mapped / editable copy | **Tratarlo como data-owned visible** | hoy viene del record y participa como heading | tocar el title arrastra ownership incierto desde el arranque | **Bloquea** tocar el heading principal |
| Política de `schema.summary` en detail | dejar cruda / display-map / excluir temporalmente | **Excluirla de la primera ola** | mezcla header local con contenido schema-driven | cualquier mini paso sobre header se vuelve mixto | **Bloquea** tocar description del header |
| Política de action labels | schema-owned / alias display-only / glosario central | **Congelar como schema-owned por ahora** | los botones ejecutan contratos reales y el success feedback los reutiliza | cambiar labels sin contrato ensucia controls y feedback a la vez | **Bloquea** tocar CTA text de actions |
| Política de actor role display | crudo / alias display-only | **Dejar crudo hasta contrato** | el valor visible coincide con el valor funcional | un alias bonito puede romper lectura operativa | **Bloquea** tocar selector de role |
| Política de states (`RecordState`, `DispatchStatus`, `SyncStatus`) | raw / display-mapped / glosario oficial | **Congelar sin reinterpretar** | hay tres dominios distintos y timeline ya los mezcla | se aplana semántica sensible entre superficies | **Bloquea** tocar badges, filtros, latestSync, timeline state |
| Política de `event.summary` | evidence / copy de producto / híbrido | **Tratarlo como evidence hasta demostrar lo contrario** | aparece como heading en timeline y detail/sync | tocar summaries contamina tres superficies a la vez | **Bloquea** tocar summaries |
| Política de raw errors | raw / normalized / dual-layer | **Congelar dualidad actual y no “mejorarla” todavía** | hoy UI local convive con error crudo propagado | se pierde fidelidad operativa o coherencia transversal | **Bloquea** tocar feedback/error texts sensibles |
| Política de retry subject | retry de job / retry de sync / wording híbrido | **Congelar como retry de dispatch job** | el endpoint y la lógica operan sobre `jobId` | wording ambiguo rompe comprensión operativa | **Bloquea** tocar retry wording |
| Política de secure token visible | visible íntegro / truncado / oculto | **No tocar hasta decisión explícita** | es evidencia sensible y útil de soporte | truncarlo o “embellecerlo” puede degradar soporte | **Bloquea** cambios al valor |
| Política del timeline | contrato narrativo / simple vista / UX-editable | **Tratarlo como contrato narrativo sensible** | `createTimelineEntries()` ya hace remapeo | cualquier mejora de copy puede ser reinterpretación histórica | **Bloquea** cambios en contenido del timeline |
| Política de metadata técnica (`adapterId`, `direction`, `jobId`, `recordId`) | raw / alias display-only | **Mantener raw por ahora** | hoy sirven como trazabilidad literal | alias sin mapa rompe soporte y debugging | **Bloquea** tocar valores visibles técnicos |

---

# 4. Mapa de mini intervenciones seguras

## Mini intervención 1
| Campo | Detalle |
|---|---|
| Nombre corto | `detail-shell-local` |
| Objetivo | Aislar y preparar la parte puramente local del detail sin tocar schema, states ni evidence |
| Archivos probables | `components/records/record-detail.tsx` |
| Qué sí toca | títulos locales de panel, subtítulos locales, botones locales de navegación/refresh, textos locales de empty state no operativos |
| Qué no toca | `record.title`, `schema.summary`, `stateLabel`, `latestSync`, `action.label`, `secureToken`, `event.summary`, errores |
| Precondiciones | congelar exclusión explícita del header principal y de la columna controls |
| Riesgo | Bajo |
| Resultado visible esperado | detail con shell local más claramente aislado, sin tocar contenido sensible |
| Validación mínima | screenshots antes/después del detail; diff de strings tocados; confirmar que el header principal sigue intacto |
| ¿Puede correrse en paralelo? | **Sí** |

## Mini intervención 2
| Campo | Detalle |
|---|---|
| Nombre corto | `detail-metadata-wrappers` |
| Objetivo | Tratar wrappers locales de metadata como subfrente aparte, preservando valores íntegros |
| Archivos probables | `components/records/record-detail.tsx`, quizá `src/lib/utils.ts` solo para inspección, no para cambio |
| Qué sí toca | wrappers como `Record id`, `Secure token`, `Created`, `Submitted`, `Last sync` |
| Qué no toca | valores de id/token/fecha; formato temporal; `latestSync.status`; `latestSync.summary` |
| Precondiciones | congelar política: wrapper sí, valor no |
| Riesgo | Bajo-Medio |
| Resultado visible esperado | metadata más controlable como capa local sin tocar evidencia ni formato |
| Validación mínima | comprobar que valores exactos no cambian; snapshots con ids largos y token largo |
| ¿Puede correrse en paralelo? | **Sí**, si no se toca formatting global |

## Mini intervención 3
| Campo | Detalle |
|---|---|
| Nombre corto | `detail-controls-chrome-only` |
| Objetivo | Separar el chrome local del panel de controls del contenido funcional |
| Archivos probables | `components/records/record-detail.tsx` |
| Qué sí toca | títulos del panel, subtítulo, label `Operator note`, placeholders puramente locales, nota local de “note required”, estado vacío del bloque de acciones cuando no hay acciones |
| Qué no toca | selector `Actor role`, option labels de role, `action.label`, feedback de éxito/fallo, `Running...`, `Note required` si se considera semánticamente acoplado |
| Precondiciones | congelar que action labels y role values quedan fuera |
| Riesgo | Medio |
| Resultado visible esperado | controls más segmentables sin tocar semántica de ejecución |
| Validación mínima | probar con estados/roles donde haya acciones y donde no haya acciones; asegurar que disponibilidad y payload no cambian |
| ¿Puede correrse en paralelo? | **Sí**, pero no junto con una intervención sobre feedback o actions |

## Mini intervención 4
| Campo | Detalle |
|---|---|
| Nombre corto | `detail-operational-sidepanel-shell` |
| Objetivo | Aislar shell local del panel `Dispatch & sync` sin tocar evidence |
| Archivos probables | `components/records/record-detail.tsx` |
| Qué sí toca | título del panel, subtítulo, empty states locales, botones locales `Open Sync Center` y `Refresh record`, wrappers `Attempts` / layout local de metadata |
| Qué no toca | `job.status`, `event.status`, `event.summary`, `adapterId`, `job.error`, `event.error` |
| Precondiciones | congelar que dispatch/sync entries quedan raw |
| Riesgo | Medio |
| Resultado visible esperado | panel lateral operativo más separable del contenido sensible |
| Validación mínima | verificar que badges, summaries y errors permanecen exactos; revisar estado vacío y no vacío |
| ¿Puede correrse en paralelo? | **Sí**, con cuidado |

## Mini intervención 5
| Campo | Detalle |
|---|---|
| Nombre corto | `timeline-shell-empty-only` |
| Objetivo | Tratar timeline como contrato narrativo sensible y limitar la primera ola a shell y empty state |
| Archivos probables | `components/records/activity-timeline.tsx` |
| Qué sí toca | empty title, empty description, quizá wrappers puramente locales del bloque si existieran |
| Qué no toca | `createTimelineEntries`, `kind`, `title`, `description`, `state`, `detail`, `meta`, timestamps |
| Precondiciones | congelar que timeline content no entra |
| Riesgo | Bajo |
| Resultado visible esperado | timeline preparado para intervención mínima sin tocar narrativa ni evidence |
| Validación mínima | caso timeline vacío y timeline poblado; comprobar que entradas no cambian |
| ¿Puede correrse en paralelo? | **Sí** |

## Mini intervención 6
| Campo | Detalle |
|---|---|
| Nombre corto | `sync-shell-local` |
| Objetivo | Ejecutar la porción más limpia del sync center |
| Archivos probables | `components/sync/sync-center.tsx` |
| Qué sí toca | eyebrow, title, description, subtítulos de panel, `Refresh data`, empty states, meta text editorial de stat cards, wrappers `Adapter`, `Attempts`, `Updated` |
| Qué no toca | labels de filtros, badges de status, `event.summary`, `direction`, `adapterId` values, retry wording, message strip en falla |
| Precondiciones | congelar filtros, statuses y retry semantics |
| Riesgo | Bajo |
| Resultado visible esperado | sync con shell local listo y semántica operativa preservada |
| Validación mínima | dashboard con datos y sin datos; comprobar counts/filtros/status exactos; revisar layout con errors largos |
| ¿Puede correrse en paralelo? | **Sí** |

## Mini intervención 7
| Campo | Detalle |
|---|---|
| Nombre corto | `feedback-boundaries-map` |
| Objetivo | No tocar copy visible todavía, sino delimitar formalmente qué feedback es local, cuál hereda schema y cuál propaga backend |
| Archivos probables | `components/records/record-detail.tsx`, `components/sync/sync-center.tsx`, `app/api/records/[recordId]/action/route.ts`, `app/api/sync/jobs/[jobId]/retry/route.ts`, `src/lib/services/actions.ts` |
| Qué sí toca | documentación/inventario de fronteras; ningún código |
| Qué no toca | implementación |
| Precondiciones | ninguna |
| Riesgo | Muy bajo |
| Resultado visible esperado | ninguno todavía; deja piso sólido para no romper feedback después |
| Validación mínima | tabla que separe success local / fallback local / raw backend / schema-derived |
| ¿Puede correrse en paralelo? | **Sí** |

## Mini intervención 8
| Campo | Detalle |
|---|---|
| Nombre corto | `timeline-evidence-contract-map` |
| Objetivo | Congelar por escrito la política operativa del timeline antes de cualquier cambio visible más ambicioso |
| Archivos probables | `src/lib/ui/record-contracts.ts`, `components/records/activity-timeline.tsx` |
| Qué sí toca | documentación y contrato; ningún cambio UI todavía |
| Qué no toca | títulos, descriptions, remapeos, payload rendering |
| Precondiciones | ninguna |
| Riesgo | Muy bajo |
| Resultado visible esperado | ninguno; reduce riesgo futuro brutalmente |
| Validación mínima | tabla por kind: source, title source, description source, state source, detail source, meta source |
| ¿Puede correrse en paralelo? | **Sí** |

## Mini intervención 9
| Campo | Detalle |
|---|---|
| Nombre corto | `sync-operational-freeze` |
| Objetivo | Definir explícitamente todo lo que sync no debe tocar todavía |
| Archivos probables | `components/sync/sync-center.tsx`, `src/lib/services/actions.ts`, retry route, tests |
| Qué sí toca | inventario, checklist y freeze list |
| Qué no toca | UI final |
| Precondiciones | ninguna |
| Riesgo | Muy bajo |
| Resultado visible esperado | ninguno; evita una intervención Frankenstein en filtros/métricas/retries |
| Validación mínima | checklist de subject-of-action, metrics-to-filter consistency y raw error stability |
| ¿Puede correrse en paralelo? | **Sí** |

---

# 5. Mapa de paralelización

| Tareas paralelizables | Tareas no paralelizables | Dependencias | Orden mínimo recomendado | Combinaciones peligrosas |
|---|---|---|---|---|
| `detail-shell-local` + `timeline-shell-empty-only` + `sync-shell-local` | cualquier cosa que toque states, action labels, retry wording o summaries | casi independientes, mientras la lista roja siga congelada | 1) congelar decisiones 2) correr shells locales | tocar a la vez shell local y semántica operativa en el mismo commit |
| `detail-metadata-wrappers` + `feedback-boundaries-map` | intervención sobre formatting global de fechas | depende de que wrapper vs valor quede separado | 1) freeze wrappers 2) validar que el valor no cambió | tocar wrappers y formato temporal en la misma corrida |
| `detail-controls-chrome-only` + `sync-operational-freeze` | cualquier cambio visible de action feedback o retry feedback | controls depende de exclusión de `action.label` y role aliasing | 1) congelar labels/roles 2) tocar solo chrome local | tocar controls chrome al mismo tiempo que actor role display |
| `timeline-evidence-contract-map` + `feedback-boundaries-map` | cambio visual del timeline | ambos son mapas/documentación, no UI final | pueden correr muy temprano | tocar timeline content mientras el contrato aún está abierto |
| `detail-operational-sidepanel-shell` + `sync-shell-local` | cambios en errors, statuses, summaries o metrics | ambos comparten semántica operativa sensible, pero shell local sí se puede mover | 1) congelar status/error/summaries 2) tocar solo wrappers/chrome | mezclar wrappers de panel con reinterpretación de badges o summaries |

## Orden mínimo recomendado
1. **Congelar decisiones previas** de ownership y exclusiones.
2. **Levantar mapas de fronteras**: timeline evidence contract + feedback boundaries + sync operational freeze.
3. **Ejecutar shells locales paralelizables**: detail shell, timeline empty, sync shell.
4. **Ejecutar wrappers seguros**: metadata wrappers y shell local del panel operativo del detail.
5. **Evaluar si vale la pena entrar a controls chrome**, solo si action labels y role display siguen congelados fuera.
6. **Dejar actions, states, summaries, retries y raw errors para una fase posterior con contrato.**

## Combinaciones peligrosas
- `detail-controls-chrome-only` + cambio a `action.label`
- `sync-shell-local` + cambio a filtros/status badges
- `timeline-shell-empty-only` + cambio en `createTimelineEntries()`
- `detail-metadata-wrappers` + cambio en `formatDateTime()`
- cualquier cambio de wrappers locales + “mejora” de raw errors

---

# 6. Dependencias y acoplamientos reales

| Archivo / componente | De qué depende | Tipo de acoplamiento | Nivel de riesgo | Implicación para la intervención |
|---|---|---|---|---|
| `app/record/[recordId]/page.tsx` | `getRecordById`, `getSchema`, `listRecordSubresources`, `RecordDetail` | composición server -> UI | Medio | no es hotspot de copy; sirve para entender entrada de datos |
| `components/records/record-detail.tsx` | `schema.summary`, `schema.views.detailSections`, `schema.actions`, `stateLabel`, `stateDescription`, `isActionAvailable`, `format*`, `ActivityTimeline` | mezcla local + schema + runtime + operativa | **Crítico** | no debe tocarse como un solo bloque; necesita subsegmentación |
| `record-detail.tsx` header | `record.title`, `schema.summary`, `record.state`, `schema.title`, `formatRelativeTime`, attachment count | header híbrido | Alto | el título y la descripción no son shell puro |
| `record-detail.tsx` business details | `schema.views.detailSections`, `getFieldById`, `record.fields`, `formatValue` | schema-driven render | **Crítico** | no meter mano sin política schema/data |
| `record-detail.tsx` controls | `schema.actions`, `isActionAvailable`, role state, action note, action route | UI ligada a state machine | **Crítico** | chrome local sí; labels, roles, feedback y actions no |
| `record-detail.tsx` feedback | success local + error route fallback + backend/service error | frontera UI/backend | Alto | conviene mapear antes de tocar |
| `record-detail.tsx` operational summary | `record.id`, `secureToken`, `createdAt`, `submittedAt`, `lastSyncAt` | wrapper local + evidence/data | Alto | wrapper sí, valor no |
| `record-detail.tsx` dispatch/sync side panel | `dispatchJobs`, `syncEvents`, `formatDateTime` | evidencia operativa visible | **Crítico** | tocar shell del panel, no content |
| `components/records/activity-timeline.tsx` | `createTimelineEntries`, `formatDateTime`, `StateBadge` | presentational sobre contrato narrativo | **Crítico** | el archivo es UI, pero el meaning vive en `record-contracts` |
| `src/lib/ui/record-contracts.ts:createTimelineEntries` | submissions, dispatchJobs, syncEvents, `safeJson`, `sanitizeText`, remapeos de state | ensamblaje narrativo de evidence | **Crítico** | cualquier cambio aquí reescribe historia visible |
| `record-contracts.ts:mapDispatchState` | `DispatchStatus -> RecordState` | remapeo semántico | **Crítico** | no tocar sin glosario y política histórica |
| `record-contracts.ts:mapSyncState` | `SyncStatus -> RecordState` | remapeo semántico | **Crítico** | aplaza cualquier mejora “cosmética” del timeline |
| `components/sync/sync-center.tsx` | `jobs`, `events`, filters locales, retry route, `formatDateTime` | shell local + operativa visible | **Crítico** | dividir claramente capa segura vs capa sensible |
| `sync-center.tsx` metrics | filtros por status reales | semántica de conteo | Alto | label y fórmula deben permanecer alineados |
| `sync-center.tsx` retry UI | `/api/sync/jobs/[jobId]/retry`, `busyJob`, message strip | acción operativa visible | **Crítico** | sujeto real es `job`, no “sync” genérico |
| `src/lib/core/record-view.ts` | `formatHumanLabel`, descriptions literales | glosario shared de estado | Alto | es dependencia transversal; no arreglarla localmente en detail |
| `src/lib/core/state.ts` | `isActionAvailable`, `canTransition` | state machine | **Crítico** | cualquier cambio visible que contradiga esto rompe coherencia |
| `src/lib/services/actions.ts:applyRecordAction` | schema action, store, adapter, transitions, sync event creation | semántica real de actions y dispatch | **Crítico** | success/error/retry wording toca lógica real indirectamente |
| `src/lib/services/actions.ts:retryDispatchJob` | job, record, schema, adapter, transition reconciliation | retry semantics | **Crítico** | explica por qué retry no es solo UI del sync |
| `app/api/records/[recordId]/action/route.ts` | `getActorFromHeaders`, `applyRecordAction` | error boundary visible | Alto | `Action failed` es solo fallback; el meaning real puede venir del service |
| `app/api/sync/jobs/[jobId]/retry/route.ts` | `getActorFromHeaders`, `retryDispatchJob` | error boundary visible | Alto | `Retry failed` es fallback local, no semántica completa |
| `src/lib/services/records.ts` | create/update/subresources, sync event inbound creation | timeline/detail source | Alto | detail y timeline heredan summaries y eventos desde aquí |
| `src/lib/store/memory-store.ts` | orden de jobs y events por `updatedAt/createdAt` | read model / ordering | Medio-Alto | latest sync/detail y sync lists dependen de este orden |
| `src/lib/utils.ts` | `formatDateTime`, `formatRelativeTime`, `formatValue` | formatting leak transversal | Alto | no mezclar un mini paso local con cambios globales de format |

---

# 7. Validación operativa por mini paso

| Mini intervención | Qué validar | Dónde validar | Tipo de validación | Criterio de aceptación | Señal de stop | Evidencia a guardar |
|---|---|---|---|---|---|---|
| `detail-shell-local` | headings y subtítulos locales de panel; botones `Inbox`, `Refresh`, `Open Sync Center` | `/record/[recordId]` | visual + funcional básica | los paneles siguen iguales en contenido sensible; botones navegan/refrescan igual | el cambio exige tocar `record.title` o `schema.summary` | screenshots antes/después; lista de strings tocados |
| `detail-metadata-wrappers` | wrappers `Record id`, `Secure token`, `Created`, `Submitted`, `Last sync` | `/record/[recordId]` | visual + integridad de datos | el wrapper puede cambiar, el valor exacto no cambia | alguien propone truncar, humanizar o reinterpretar valores | captura de cada card; diff visual de valores |
| `detail-controls-chrome-only` | título/subtítulo del panel, label `Operator note`, placeholder local, empty state local de actions | `/record/[recordId]` con distintos roles/estados | visual + funcional | action availability y payload no cambian; solo cambia chrome local permitido | tocar role option labels, action labels o feedback | matriz simple role/state -> acciones visibles; screenshots |
| `detail-operational-sidepanel-shell` | empty states de attachments/jobs/events; botones locales; wrappers tipo `Attempts` | `/record/[recordId]` con y sin jobs/events/errors | visual + fidelidad operativa | summaries, badges y errors siguen idénticos; solo cambia shell local | el cambio toca `job.status`, `event.summary` o raw errors | screenshot estado vacío/no vacío; comparación textual de entries |
| `timeline-shell-empty-only` | empty title/description del timeline, no contenido poblado | `/record/[recordId]` con timeline vacío y con timeline poblado | visual + regresión | cuando hay eventos, ninguna entrada cambia; cuando no hay eventos, empty state es correcto | cualquier diff en `kind/title/description/state/detail/meta` | screenshots vacío/no vacío; snapshot textual de entries antes/después |
| `sync-shell-local` | header, subtítulos, `Refresh data`, empty states, meta text de métricas, wrappers `Adapter`, `Attempts`, `Updated` | `/sync` | visual + funcional ligera | filtros, badges, métricas y retry siguen idénticos; solo cambia shell local seguro | se intenta tocar labels de filtros, badges, retry o summary | capturas del dashboard con datos y sin datos; diff de strings tocados |
| `feedback-boundaries-map` | clasificación de feedback messages | detail + sync + routes/services | documental / trazabilidad | cada mensaje queda clasificado como local, schema-derived, backend-derived o fallback | aparece un mensaje sin owner claro | tabla de feedback con owner y source path |
| `timeline-evidence-contract-map` | contrato por entry kind | `record-contracts.ts` + `activity-timeline.tsx` | documental / semántica | queda claro qué viene de evidence, qué se remapea y qué es shell local | no se puede explicar el origen de `title/description/state/detail/meta` | tabla por kind; nota de riesgos por remapeo |
| `sync-operational-freeze` | freeze list de filtros, métricas, retries, errors, summaries | `/sync`, `services/actions.ts`, tests | documental + validación conceptual | queda una lista explícita de no tocar y del porqué | alguien interpreta `retryable` = `failed` o `synced` = `record synced` | checklist firmada por mini paso; referencias a tests/servicios |

## Focos específicos exigidos
### Headings y metadata locales
- Validar solo donde el texto es claramente shell o wrapper.
- **Stop:** cuando el heading depende de `record.title`, `schema.summary` o `event.summary`.

### Actions visibles
- Validar separación entre **chrome del panel** y **label de acción**.
- **Stop:** si tocar una cadena visible obliga a entrar a `schema.actions`.

### Role selector
- Validar solo integridad funcional, no renombre.
- **Stop:** cualquier alias display-only sin contrato explícito.

### Feedback messages
- Guardar mapa de owners antes de cualquier retoque.
- **Stop:** feedback que mezcla success local con raw error “mejorado”.

### Timeline entries
- Validación tipo snapshot conceptual por entry.
- **Stop:** cualquier cambio en title/description/state/detail/meta sin contrato.

### Errors largos
- Revisar wrap, scroll, overflow, pero no reescritura.
- **Stop:** truncado destructivo o “normalización” improvisada.

### Metrics/filtros del sync
- Validar que label, fórmula y población filtrada sigan alineadas.
- **Stop:** un label empieza a describir otra cosa distinta de lo que cuenta.

### Retries
- Validar sujeto de la acción, enablement y success/failure messaging.
- **Stop:** UI sugiere retry de sync global cuando el endpoint opera sobre `jobId`.

### Consistency entre detail/timeline/sync
- Validar que ningún mini paso local contradiga glosario o evidence en otra superficie.
- **Stop:** el mismo término cambia de meaning entre detail, timeline y sync.

---

# 8. Trazabilidad y evidencia

## Qué registrar

### Decisiones
Registrar al menos:
- exclusiones congeladas por mini paso
- owner tentativo de cada string tocado
- razones explícitas para no tocar cada zona roja
- decisiones de “wrapper sí / valor no”

### Hallazgos
Registrar:
- dónde una cadena local termina pegada a schema, runtime o backend
- dónde una mejora aparente exige tocar state machine o services
- dónde el timeline pierde granularidad por remapeo

### Bloqueos
Registrar:
- falta de glosario oficial de states
- falta de política de raw errors
- falta de política de `event.summary`
- falta de política de actor role display
- falta de política de retry wording

### Riesgos
Registrar por mini paso:
- riesgo de deformar semántica operativa
- riesgo de mezclar copy local con evidence
- riesgo de pérdida de trazabilidad técnica
- riesgo de inconsistencia transversal con detail/timeline/sync

### Validaciones
Guardar por mini paso:
- ruta validada
- estado de datos usado para validar
- checklist pasado/fallado
- señal de stop disparada o no
- nota de qué quedó explícitamente fuera

### Archivos tocados
Guardar siempre:
- archivo
- zona del archivo
- motivo del cambio
- owner tentativo del texto tocado
- exclusiones relevantes cercanas

### Checkpoints conceptuales
Recomiendo checkpoint corto cuando se cierre cada frontera:
1. shell local
2. wrappers seguros
3. controls chrome
4. timeline freeze
5. sync freeze
6. feedback boundaries

### Artefactos a conservar
- tabla de mini intervenciones aprobadas
- freeze list por superficie
- mapa de feedback boundaries
- timeline evidence contract map
- screenshots antes/después por mini paso
- snapshots de casos con raw errors largos
- matriz role/state -> actions visibles
- matriz metric/filter -> expected population

---

# 9. Quick wins reales vs zonas rojas

## Quick wins

### 1) Shell local del detail
**Por qué sí:** está concentrado en títulos, subtítulos y botones locales de navegación/refresh que no necesitan reinterpretar evidence.

### 2) Wrappers locales de metadata en detail
**Por qué sí:** permiten intervención controlada sin tocar valores reales. Es un quick win quirúrgico si se congela la regla “wrapper sí, valor no”.

### 3) Empty state del timeline
**Por qué sí:** vive en `ActivityTimeline` y no exige tocar `createTimelineEntries()`.

### 4) Shell local del sync center
**Por qué sí:** header, subtítulos, `Refresh data`, empty states y ciertos wrappers están nítidamente separados de la capa operativa cruda.

### 5) Congelar mapas de frontera antes de tocar UI sensible
**Por qué sí:** `feedback-boundaries-map`, `timeline-evidence-contract-map` y `sync-operational-freeze` no cambian el producto aún, pero aceleran muchísimo la fase siguiente y evitan accidentes caros.

### 6) Segmentar `record-detail.tsx` por subzonas
**Por qué sí:** evita que un cambio pequeño arrastre business details, controls y panel operativo en la misma corrida.

## Zonas rojas

### 1) Header principal del detail
**Por qué es roja:** mezcla `record.title` y `schema.summary`, o sea data/schema en una superficie que parece puro shell.

### 2) `Business details`
**Por qué es roja:** renderiza `section.title`, `field.label` y `record.fields` desde schema/data. Es una pared mixta, no copy local.

### 3) Labels de actions y selector de role
**Por qué es roja:** los labels de acción salen del schema y los roles visibles son contrato funcional directo.

### 4) `latestSync` stat card
**Por qué es roja:** mezcla copy editorial con `SyncStatus` y `summary` operativos.

### 5) Timeline populated content
**Por qué es roja:** la narrativa ya remapea estados y eleva summaries/evidence a texto visible.

### 6) Filtros, badges, métricas y retry del sync
**Por qué es roja:** cualquier “mejora” aquí toca semántica operativa real o su comprensión.

### 7) Raw errors en detail, timeline y sync
**Por qué es roja:** hoy son evidencia visible. Tocarlos sin política rompe fidelidad y soporte.

### 8) `event.summary`, `adapterId`, `direction`, `secureToken`
**Por qué es roja:** son evidence o metadata técnica de alta sensibilidad operativa.

---

# 10. Artefactos adicionales que conviene producir

| Nombre | Para qué sirve | Prioridad | ¿Bloquea o solo ayuda? |
|---|---|---|---|
| `detail-mini-steps-checklist.md` | listar mini pasos, exclusiones y validación mínima del detail | Alta | **Ayuda mucho** |
| `timeline-evidence-contract-map.md` | congelar source-of-truth de cada parte de una entry del timeline | Muy alta | **Bloquea** cualquier cambio más ambicioso del timeline |
| `feedback-boundaries-map.md` | separar feedback local, schema-derived, backend-derived y fallback | Muy alta | **Bloquea** tocar feedback sensible con seguridad |
| `sync-operational-freeze.md` | dejar explícito qué no entra todavía en sync | Muy alta | **Bloquea** evitar que se mezcle shell local con semántica operativa |
| `role-state-action-matrix.md` | ver qué acciones aparecen por `record.state` y `role` | Alta | **Ayuda** a validar controls |
| `metrics-filter-consistency-grid.md` | documentar fórmula de métricas y filtros del sync | Alta | **Ayuda** y reduce riesgo de regressions |
| `raw-evidence-display-checklist.md` | checklist para errors largos, payloads y summaries sensibles | Alta | **Ayuda** |
| `detail-surface-split-map.md` | partir `record-detail.tsx` en subzonas y owners tentativos | Alta | **Ayuda**; acelera ejecución |
| `owner-register-detail-timeline-sync.md` | registro corto de strings tocables vs excluidos | Media-Alta | **Ayuda** |
| `before-after-proof-pack/` | carpeta conceptual de screenshots y snapshots por mini paso | Media | **Ayuda** fuerte para trazabilidad |

---

# 11. Qué nos deja resuelto este chat

## Qué parte del frente quedaría lista para ejecución
Queda lista para ejecución controlada una **primera ola pequeña y paralelizable** compuesta por:
- `detail-shell-local`
- `detail-metadata-wrappers`
- `timeline-shell-empty-only`
- `sync-shell-local`
- más la documentación congeladora:
  - `feedback-boundaries-map`
  - `timeline-evidence-contract-map`
  - `sync-operational-freeze`

Eso ya permite avanzar sin tocar estados, summaries, retries ni evidence cruda.

## Qué seguiría bloqueado
Seguiría bloqueado, correctamente, todo lo que dependa de:
- `record.title` como heading tratable
- `schema.summary`
- `action.label`
- alias de actor role
- glosario oficial de `RecordState`, `DispatchStatus`, `SyncStatus`
- `latestSync.status` / `latestSync.summary`
- `event.summary`
- raw errors y summaries operativos
- retry wording más allá del shell local
- remapeos del timeline

## Qué decisiones quedarían casi cerradas
Después de este entregable quedarían casi cerradas estas decisiones tácticas:
- **detail no se ejecuta por archivo completo, sino por subzonas**
- **timeline se trata como contrato narrativo sensible**
- **sync se parte en shell local seguro vs semántica operativa congelada**
- **wrappers locales pueden entrar antes que values/evidence**
- **feedback necesita mapa de fronteras antes de cualquier mejora visible**
- **paralelización sí es viable, pero solo si la lista roja queda congelada**

## Qué intervención futura se volvería más rápida gracias a este entregable
Se volvería mucho más rápida la siguiente intervención real de ejecución porque ya no tendría que gastar tiempo en:
- descubrir si detail es una superficie o cuatro
- debatir en caliente si timeline es UI o contrato narrativo
- mezclar shell local de sync con filtros/retries/métricas
- improvisar validación por mini paso
- correr cambios seriales que sí podían paralelizarse
- perder trazabilidad de qué se tocó y qué quedó fuera

En práctico: este chat deja el frente **desarmado en piezas manejables**, con conos puestos, con carriles paralelizables, y con una frontera mucho más clara entre UI local y semántica operativa sensible.

## Qué nos deja resuelto este chat
Este chat deja resuelto el siguiente nivel de inteligencia operativa que el dossier todavía no bajaba a tierra:
- convierte el capítulo `record detail + timeline + sync center` en **mini intervenciones ejecutables**
- separa **qué bloquea toda la fase** de **qué solo bloquea un mini paso puntual**
- deja un **orden mínimo recomendado** para ejecutar con menos blast radius
- deja un **mapa de paralelización segura**
- deja un **registro de decisiones a congelar** antes de tocar zonas con cable vivo
- deja una **matriz de validación mínima por mini paso**
- deja definida la evidencia que conviene guardar para no perder control ni trazabilidad

No propone implementación final todavía. Hace algo más útil en este punto: deja el frente listo para entrar después con bisturí y no con machete.

---

# 🚦 Siguiente jugada recomendada

## Orden operativo sugerido
1. **Freeze transversal**
   - decisiones previas críticas
   - exclusiones y zonas rojas
   - budgets del top area
   - autoridad de formatting
   - shells nobles vs puentes peligrosos

2. **Pack de validación y evidencia**
   - rutas críticas
   - breakpoints
   - screenshots base
   - tabla de checkpoints
   - matriz de archivos tocados

3. **Primera ola segura**
   - shell baseline / shell local
   - shared UI noble + contracts visuales
   - launcher local + inbox controls / scan speed
   - shells locales de sync/detail/timeline
   - freezes documentales de flow/detail/sync

4. **Segunda ola con casco**
   - sticky/offset tuning
   - consumers top-heavy
   - card compact budgets
   - wrappers de metadata
   - controls chrome del detail
   - field-render local-only del flow

5. **Tercera ola solo con contrato cerrado**
   - formatting consolidado real
   - state labels / descriptions
   - schema display strategy
   - retry semantics
   - timeline narrative
   - raw error policy

## Qué NO conviene hacer
- brincar directo a implementación grande
- mezclar dos frentes semánticamente calientes en la misma corrida
- tocar schema/state/backend “porque ya estamos ahí”
- arreglar layout sin baseline
- arreglar copy sin ownership
- arreglar shared sin distinguir shell noble de puente peligroso

## Cierre
Este dossier ya no es solo “mapa”.
Ya es una **base operativa de intervención**.

La jugada correcta desde aquí es:
**freeze corto, mini paso pequeño, validación dura, evidencia limpia, y siguiente corte.**

