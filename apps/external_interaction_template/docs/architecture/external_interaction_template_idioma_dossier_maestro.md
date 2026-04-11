# 🧭 Dossier Maestro de Pre-Intervención
## 🌐 Frente de idioma para `apps/external_interaction_template`

> **Propósito**
>
> Unificar en un solo documento reusable todo el material recabado sobre el frente de idioma, rollout, ownership, riesgos, gates y superficies sensibles de `apps/external_interaction_template`, **sin entrar todavía a implementación final**.

---

## ✨ Cómo leer este documento

### Leyenda
- **✅ Confirmado**: visto directamente en el zip o explicitado en el material recabado.
- **🧠 Inferido**: deducción razonable por acoplamiento entre archivos, superficies o contratos.
- **⚠️ Dudoso**: no conviene tocar todavía sin resolver ownership o semántica real.
- **🛑 Lista roja**: zona que debe quedar fuera de la primera ola.

### Regla madre
**Primero mapa, luego ownership, luego riesgo, luego validación, y solo después ejecución.**

---

# 1. 🎯 Resumen ejecutivo

## Qué busca cerrar este dossier
- Definir el marco operativo del frente de idioma.
- Congelar las decisiones mínimas para una **V1 segura**.
- Ordenar el rollout por capas y superficies.
- Evitar que la primera corrida mezcle copy de UI con semántica operativa, schema text o backend.

## Qué deja resuelto
- Una **política operativa base** para idioma.
- Un **rollout por fases** con gates y señales de stop.
- Un **mapa maestro de ownership**.
- Una **lista roja global** de lo que no debe traducirse todavía.
- Una **matriz de validación transversal** reusable.
- Un **anexo por superficie**: shell, launcher, inbox, flow, detail, sync y shared UI.

## Qué riesgos baja
- Traducir texto con semántica real creyendo que es copy local.
- Meter backend antes de tiempo.
- Romper layout por longitud.
- Sacar una UI mezclada, tipo Frankenstein bilingüe.
- Rehacer trabajo por no haber congelado default locale, fallback y persistencia.

## Estado actual de la verdad operativa
- ✅ Hoy **no existe una capa formal de i18n**.
- ✅ `app/layout.tsx` usa `html lang="en"`.
- ✅ `src/lib/utils.ts` trae fuga de idioma con locale fijo, `Yes/No`, `item/items` y humanización automática.
- ✅ `src/lib/core/record-view.ts` ya funciona de facto como mini diccionario de estados.
- ⚠️ Varias superficies mezclan **copy local** con **schema text**, **estado**, **validation**, **runtime** y **backend-propagated errors**.

---

# 2. 🧱 Decisiones operativas oficiales para V1

## 2.1 Idiomas iniciales recomendados
- **Recomendación**: `en`, `es`
- **Estado**: ✅ recomendado

### Por qué conviene
- Prueba arquitectura, persistencia, fallback y longitud real.
- Mantiene el blast radius controlado.
- Obliga a ordenar el ownership desde el inicio.

### Qué evita
- Sobrediseñar soporte para muchos idiomas antes de cerrar la base.
- Abrir desde ya el zoológico de variantes regionales.

### Complejidad que mete
- Diccionarios paralelos mínimos.
- Validación visual en dos idiomas.

### ¿Bloquea la primera ola?
- **No**. La habilita.

---

## 2.2 Idioma default recomendado
- **Recomendación**: `en`
- **Estado**: ✅ recomendado

### Por qué conviene
- Hoy el repo ya está plantado en inglés.
- Reduce huecos y fallbacks visibles en la primera ola.
- Hace que `en` sea baseline canónico de cobertura.

### Qué evita
- Voltear el default a español cuando todavía hay muchísima semántica real en inglés.
- Fallback silencioso constante hacia inglés desde una UI que dice ser española.

### Complejidad que mete
- Documentar que `es` es soportado, pero **`en` sigue siendo la referencia canónica inicial**.

### ¿Bloquea la primera ola?
- **Sí, si no se congela.** Esta decisión debe cerrarse antes del provider.

---

## 2.3 Persistencia local recomendada
- **Recomendación**: `localStorage`
- **Estado**: ✅ recomendado para V1

### Política sugerida
- El árbol arranca con `defaultLocale` estable.
- El cliente hidrata y recupera preferencia persistida.
- El cambio de idioma debe sobrevivir a recarga.

### Por qué conviene
- No requiere backend.
- Es suficiente para preferencia por navegador.
- Reduce fricción para arrancar.

### Qué evita
- Abrir auth, usuario, tenant o sync cross-device demasiado pronto.

### Complejidad que mete
- Posible flash inicial si no se monta bien.
- Necesidad de dejar clara una sola fuente de verdad.

### ¿Bloquea la primera ola?
- **No**, pero sí debe quedar definida antes del provider.

---

## 2.4 Storage key oficial sugerida
- **Recomendación**: `external_interaction_template.locale`
- **Estado**: ✅ recomendado

### Por qué conviene
- Es explícita.
- Evita llaves genéricas tipo `locale` que luego chocan.
- Facilita debugging.

### ¿Bloquea la primera ola?
- **No**, pero debe congelarse antes de la primera persistencia real.

---

## 2.5 Fallback policy oficial sugerida
- **Recomendación**: `requested -> default(en) -> marcador explícito en dev/test`
- **Estado**: ✅ recomendado

### Política concreta
1. Buscar key en el idioma solicitado.
2. Si falta, caer a `en`.
3. Si tampoco existe, mostrar marcador explícito en dev/test, por ejemplo:
   - `[[missing:i18n.key]]`
4. En producción, jamás renderizar vacío.

### Regla crítica
Para textos **schema-driven**, **state-driven**, **backend-propagated** o **timeline-semantic**, no fingir que ya quedaron internacionalizados. Si no están bajo contrato, **se quedan fuera de la primera ola**.

### Qué evita
- Fallback silencioso que tape hoyos.
- UI vacía.
- Sensación falsa de cobertura completa.

### ¿Bloquea la primera ola?
- **Sí.** Sin esto, el rollout sale ciego.

---

## 2.6 ¿Conviene backend en primera versión?
- **Recomendación**: **No**
- **Estado**: ✅ recomendado

### Backend solo entra si aparece alguno de estos casos
- Preferencia por usuario autenticado cross-device.
- Idioma por tenant.
- Contenido localizado servido por API.
- Emails, notificaciones o localización server-side.
- Reglas fuertes de negociación por actor/token.

### Qué evita
- Acoplar idioma con auth, schema, adapters y API antes de tiempo.
- Meter dos frentes de complejidad donde hoy alcanza con uno.

### ¿Bloquea la primera ola?
- **No.** Más bien la protege.

---

## 2.7 Decisiones que sí se pueden posponer sin dolor
- variantes regionales (`es-MX`, `en-US`)
- detección por `Accept-Language`
- persistencia server-side
- locale en URL
- metadata/SEO localizada por ruta
- TMS o pipeline formal de traducción
- pluralización avanzada
- localización completa de schema content
- localización de backend errors / audit evidence

---

# 3. 🗺️ Principios rectores del rollout

## Principio 1
**Idioma no debe alterar conducta.**

## Principio 2
**Shell y shared primero; superficies semánticas después.**

## Principio 3
**No mezclar copy de UI con evidencia operativa.**

## Principio 4
**Todo lo dudoso se queda fuera de la primera ola.**

## Principio 5
**Más vale una primera ola pequeña y limpia que una “gran victoria” llena de deuda rara.**

---

# 4. 🚦 Mapa de rollout recomendado

## Orden real ideal
1. **Freeze operativo**
2. **Infraestructura mínima de idioma**
3. **Provider/contexto + persistencia**
4. **Shell global + selector**
5. **Launcher + shared UI seguros**
6. **Inbox**
7. **Sync**
8. **Auditoría fina de ownership dudoso**
9. **Flow**
10. **Detail**

## Por qué este orden sí conviene
- Shell y shared prueban la columna vertebral sin entrar todavía a semántica pesada.
- Launcher permite validar longitud, CTA y chrome con bajo riesgo.
- Inbox entra antes que flow/detail porque, aunque mezcla shared/schema/data, sigue siendo menos peligroso que tocar transitions y action semantics.
- Sync entra antes de flow/detail solo para su **copy segura**, no para sus estados operativos.
- Flow y detail quedan al final porque son las superficies donde la semántica real está más entretejida con el texto visible.

---

# 5. 🚪 Gates y criterios por fase

| Fase | Precondiciones | Evidencia mínima | Validación mínima | Señal de stop | Criterio para avanzar |
|---|---|---|---|---|---|
| 0. Freeze operativo | alcance claro | tabla oficial de decisiones | revisión de riesgos | default/fallback sin cerrar | decisiones congeladas + lista roja creada |
| 1. Infra mínima | fase 0 cerrada | contrato de locales, keys y fallback | formatter y missing-key policy | contratos ambiguos | diccionario y fallback únicos |
| 2. Provider/contexto | contratos listos | provider, lectura/escritura, sync de idioma | cambio de idioma persistente tras reload | doble fuente de verdad o hydration rara | shell puede leer/cambiar idioma consistentemente |
| 3. Shell global | provider estable | shell traducible + selector visible | nav, CTAs, top area, chips | header saturado o layout roto | shell estable en ambos idiomas |
| 4. Launcher/shared | shell estable | hero, stats, CTAs, shared seguros | visual + layout + fallback | mezcla shell/schema sin delimitar | copy segura cubierta |
| 5. Inbox | shared básicos listos | empty state, controles locales y copy segura | filtros, layout, lanes, consistencia | labels de estado sin contrato | quick wins del inbox cerrados |
| 6. Sync | política semántica clara | copy segura separada de status | filtros, retries, métricas, empty states | se desdibuja `failed` vs `retryable` | copy segura del sync aislada |
| 7. Auditoría dudosa | olas anteriores estables | inventario por ownership | clasificación completa | aparece texto sin owner claro | lista roja refinada y aprobada |
| 8. Flow | auditoría aprobada | mapa de qué entra y qué no | save, submit, resume, required, attachments | se toca schema/validation/backend sin contrato | quick wins del flow separados |
| 9. Detail | auditoría aprobada | mapa por zonas rojas | timeline, actions, metadata, feedback | action labels o timeline pierden precisión | solo entra lo aprobado |

---

# 6. ☠️ Qué NO debe mezclarse en la misma corrida

## Combinaciones peligrosas
- idioma + theme + runtime profundo
- shell + ownership dudoso
- flow + validación semántica sin aclarar
- shared UI + backend semantics
- idioma + migración de schema text
- persistencia local + persistencia server-side
- flow + detail juntos
- sync semántico + glosario no cerrado
- launcher + renaming grande de schema/accessMode/adapters

## Regla de oro
**Si un cambio toca a la vez copy, estado, schema, validation y backend, ya no es “una corrida de idioma”; es una re-arquitectura disfrazada.**

---

# 7. 🛑 Lista roja global

No conviene traducir esto todavía sin contrato aprobado:

## Estados, status y semántica operativa
- `stateLabel(...)`
- `stateDescription(...)`
- status crudos tipo `pending`, `running`, `failed`, `retryable`, `synced`, `succeeded`
- métricas calculadas directamente por status
- labels de filtros que espejan enums operativos

## Texto schema-driven
- `schema.title`
- `schema.summary`
- `field.label`
- `field.helpText`
- `field.placeholder`
- `field.options`
- `detailSections[].title`
- `action.label` del schema

## Texto backend/data/evidence
- `job.error`, `event.error`
- `event.summary`
- `adapterId`, `recordId`, `jobId`, `direction`
- payloads, JSON, detail raw del timeline
- errores crudos propagados por API o service layer

## Zonas particularmente venenosas
- role selector visible si sigue acoplado al value técnico
- feedback messages compuestos con semántica real
- `submission.stepId` mostrado como título
- cualquier string persistido como data de negocio

---

# 8. 🧩 Hotspots shared y de infraestructura

## Hotspots prioritarios a sacar de hardcode
- `components/layout/app-shell.tsx`
- `components/ui/filter-pills.tsx` default `ariaLabel`
- `components/ui/page-loading.tsx`
- `app/error.tsx`
- `app/not-found.tsx`
- `src/lib/core/record-view.ts`
- `src/lib/utils.ts`

## Hallazgos clave
- ✅ `record-view.ts` ya es casi un mini diccionario de estados.
- ✅ `utils.ts` fuga idioma por cuatro frentes: locale fijo, yes/no, pluralización, humanización automática.
- 🧠 `runtime.ts` **no debería convertirse** en owner de idioma.
- 🧠 `surface.tsx`, `section-header.tsx`, `detail-list.tsx` y `page-loading.tsx` son buenos candidatos para evitar que el copy vuelva a regarse como confeti.

---

# 9. 🏗️ Arquitectura central recomendada para i18n

> **Ojo**
>
> Esto no es implementación final. Es **dirección arquitectónica recomendada** para que la ejecución futura no salga chueca.

## Principio rector
La capa de idioma debe vivir **separada** de runtime visual, theme, preset, density, brand y motion.

## Estructura sugerida
```txt
src/lib/i18n/
  config.ts
  types.ts
  dictionary.ts
  provider.tsx
  use-language.ts
  use-t.ts
  messages/
    en.ts
    es.ts
```

## Recomendaciones por pieza

### `config.ts`
- locales soportados
- default locale
- storage key
- fallback locale

### `types.ts`
- tipos mínimos para locale y diccionarios
- tipado útil, no circo barroco

### `messages/en.ts`
- baseline canónico
- no dejar `en` “viviendo en el código” como no-op

### `messages/es.ts`
- misma estructura que `en`
- solo textos frontend-owned en V1

### `dictionary.ts`
- lookup central
- fallback único
- sin absorber estado React

### `provider.tsx`
- owner global del estado de idioma
- persistencia
- sync opcional con `document.documentElement.lang`
- **no** mezclar theme/runtime aquí

### `use-language.ts`
- acceso al locale y cambio de idioma

### `use-t.ts`
- helper de traducción
- interfaz limpia y simple

## Namespaces recomendados
- `shell.*`
- `launcher.*`
- `inbox.*`
- `sync.*`
- `flow.*`
- `detail.*`
- `common.*`
- `runtimeLabels.*`
- `routesShared.*`
- `status.record.*`

## Namespaces que NO conviene usar
- mega diccionario plano sin dominios
- keys acopladas al nombre físico del componente cuando representan semántica compartida
- meter schema/backend evidence en el mismo namespace de copy local

---

# 10. 🔍 Anexo por superficie

## 10.1 Shell global

### Qué cubre
- `app/layout.tsx`
- `components/layout/app-frame.tsx`
- `components/layout/app-shell.tsx`

### Confirmado
- ✅ no existe hoy una arquitectura i18n dedicada
- ✅ `html lang="en"` es el único punto global explícito de idioma
- ✅ el shell ya trae bastante carga visual: nav, chips, CTAs, current surface, métricas runtime

### Riesgos principales
- selector de idioma metido “porque cabe” en un header ya apretado
- mezclar idioma con `runtime.ts`
- layout roto por longitud en nav, chips, descripción de área y tarjeta de `Current surface`

### Quick wins
- labels del nav del shell
- CTAs del shell
- labels compartidos del top area que sí sean chrome global

### Lista roja local
- valores runtime humanizados desde `runtime.ts`
- branding o labels que rocen identidad de sistema y no solo copy visual

### Qué nos deja resuelto
- el provider global debe montarse arriba del shell
- el selector debe vivir en chrome global, no escondido en superficies de negocio
- el shell es la mejor primera validación visible del frente de idioma

---

## 10.2 Launcher / Home

### Qué cubre
- `app/page.tsx`
- `PageHeader`, `StatCard`, `Surface`, `SectionHeader`, `Badge`, `Button`, `AppShell`

### Confirmado
- ✅ `app/page.tsx` mezcla copy local con `schema.title`, `schema.summary`, `schema.category`, `accessMode`, tags y adapter bindings
- ✅ el shell sticky header es foco rojo por truncado y longitud
- ✅ hay duplicación semántica tipo `Schemas`, `Open schemas`, `Schema Playground`, `Start flow`, `Start Flow`

### Quick wins
- hero del launcher
- labels/meta de stats
- títulos y subtítulos de `Available flows`
- CTAs como `Open schemas`, `Review inbox`, `Start flow`, `Resume / token`

### Lista roja local
- `schema.title`
- `schema.summary`
- `schema.category`
- `schema.flow.accessMode`
- tags de schema
- adapter labels visibles

### Riesgos particulares
- cards sensibles a longitud
- badges uppercase compactos
- métricas `Steps / Fields / Outbound adapter` con values largos

### Qué nos deja resuelto
- launcher sirve como banco de prueba excelente para shell + chrome + layout largo
- no conviene traducir schema content desde `launcher.*`

---

## 10.3 Inbox

### Qué cubre
- `app/inbox/page.tsx`
- `components/records/record-inbox.tsx`
- `components/records/inbox-record-card.tsx`
- dependencias: `record-view.ts`, `schema-registry.ts`, `record-contracts.ts`, `utils.ts`

### Hallazgo central
El inbox mezcla **5 orígenes de texto**:
1. literales del propio inbox
2. labels/descripciones de `record-view`
3. títulos/resúmenes/field labels de `schema-registry`
4. valores reales de datos del record
5. formatters shared

### Quick wins
- literales de `record-inbox.tsx`
- empty state del inbox
- fallback literal de `inbox-record-card.tsx`

### Lista roja local
- `stateLabel(state)`
- `stateDescription(state)`
- `schema.title`
- `schema.summary`
- `field.label`
- `formatDateTime`, `formatValue`, `formatHumanLabel`
- texto cuya verdad depende de filtros y dataset prefiltrado

### Riesgos particulares
- labels de estado largas revientan pills, select y lanes
- placeholder de búsqueda promete cosas más específicas que la búsqueda real
- grid/list toggle no tiene unidad textual formal clara para accesibilidad

### Qué nos deja resuelto
- el inbox ya quedó como caso maestro para inventariar una superficie que mezcla UI local, shared, schema y data
- es un buen frente para quick wins controlados, pero no para resolver estados todavía

---

## 10.4 Flow

### Qué cubre
- `app/flow/[schemaId]/page.tsx`
- `components/flow/flow-runner.tsx`
- dependencias: `schema-registry`, `validation`, `state`, `record-view`, `records.ts`

### Hallazgos gordos
- ✅ el runner mezcla copy local con schema text, state labels, validation y errores de API
- ✅ `StateBadge` y state description no son decorativos
- ✅ hay fuga semántica crítica en attachments: `FileList -> "n attachment(s)"` se persiste como data

### Quick wins
- shell superior del flow
- resume token block seguro
- footer/hints/safety copy
- mensajes puramente locales como `Draft saved successfully.` o `Check the highlighted fields...`

### Lista roja local
- `activeStep.title`
- `activeStep.description`
- `field.label/helpText/placeholder/options`
- `Required`, `Must be a number`, `Invalid value`
- state labels/descriptions
- backend errors
- `attachment(s)` persistido
- accessMode visible si no hay display map aprobado

### Riesgos particulares
- traducir algo que altera percepción de transición real
- contaminar datos de negocio por tocar strings persistidas
- mezclar UI local con validation/backend errors

### Qué nos deja resuelto
- flow no está listo para una intervención amplia de idioma
- sí permite una primera ola **muy acotada** de chrome local

---

## 10.5 Record Detail

### Qué cubre
- `app/record/[recordId]/page.tsx`
- `components/records/record-detail.tsx`
- `components/records/activity-timeline.tsx`
- dependencias: `schema-registry`, `record-view`, `record-contracts`, `actions`, `utils`

### Hallazgos gordos
- ✅ estados visibles salen de helpers compartidos
- ✅ acciones visibles salen del schema y gobiernan disponibilidad real
- ✅ timeline mezcla frontend, schema, runtime, adapter y errores
- ✅ role selector no es decorativo
- ✅ relative time y fechas siguen pegados a locale `en`

### Quick wins
- headings y subtitles locales del detail
- labels laterales de metadata
- empty states locales
- botones locales como `Inbox`, `Refresh`, `Open Sync Center`, `Refresh record`
- empty state default del timeline

### Lista roja local
- `action.label`
- `stateLabel/stateDescription`
- status operativos crudos
- `event.kind`, `event.summary`
- `submission.stepId`
- `adapterId`, `direction`, `meta`
- feedback messages con semántica real
- role option text si sigue amarrado al valor técnico

### Riesgos particulares
- timeline y feedback pueden volverse engañosos
- detail puede verse “traducido” arriba y semánticamente roto abajo

### Qué nos deja resuelto
- detail sí permite quick wins puntuales, pero casi todo lo sabroso sigue bloqueado por ownership y semántica real

---

## 10.6 Sync

### Qué cubre
- `app/sync/page.tsx`
- `components/sync/sync-center.tsx`
- contratos: `DispatchStatus`, `SyncStatus`, retry route, etc.

### Hallazgos gordos
- ✅ `/sync` es consola operativa, no solo UI bonita
- ✅ filtros y métricas dependen de statuses reales
- ✅ errores crudos se exponen como UI
- ✅ `event.summary` no parece frontend-owned puro

### Quick wins
- header copy
- subtítulos
- meta text de stat cards
- empty states
- `Refresh data`
- wrappers tipo `Updated`, `Adapter`, `Attempts`
- success copy controlado del retry, preservando ids

### Lista roja local
- badges con raw status
- labels de filtros que espejan enums
- `event.summary`
- `job.error`, `event.error`
- `direction`
- `adapterId`
- cualquier intento de unificar `Succeeded` con `Synced`

### Riesgos particulares
- borrar la distinción entre `job failed` y `event retryable`
- traducir evidencia operativa como si fuera copy editorial

### Qué nos deja resuelto
- sync ya quedó partido entre **copy segura** y **semántica operativa sensible**
- es la superficie con validación más delicada del frente

---

## 10.7 Shared UI

### Qué cubre
- `page-header.tsx`
- `button.tsx`
- `filter-pills.tsx`
- `status-panel.tsx`
- `empty-state.tsx`
- `state-badge.tsx`
- `stat-card.tsx`
- `detail-list.tsx`
- `surface.tsx`
- `section-header.tsx`
- `page-loading.tsx`

### Hallazgos clave
- ✅ varios shareds no tienen mucho copy, pero sí concentran defaults y puntos de emisión
- ✅ `filter-pills.tsx` ya trae `ariaLabel` default
- ✅ `state-badge.tsx` vuelve a meter labels de estado compartidos
- 🧠 shared UI es lugar ideal para estandarizar sin dejar que el copy de negocio se fugue

### Qué conviene centralizar primero
- navegación común
- acciones comunes (`clear`, `refresh`, `open`, `review`, etc.)
- empty states comunes
- labels de estado canónicos
- helpers compartidos de formato
- encabezados recurrentes

### Qué nos deja resuelto
- shared UI participa en la estrategia de idioma
- pero **no debe decidir copy de negocio** por sí sola

---

# 11. 🧠 Mapa maestro de ownership

## Frontend-owned
- copy local del shell y de superficies
- headings y subtitles hardcodeados en la vista
- empty states locales
- wrappers visuales tipo `Updated`, `Adapter`, `Attempts`
- CTAs locales de navegación o chrome

## Shared-owned
- componentes shared
- state badge como componente visual
- helpers/formateadores compartidos
- posibles labels transversales de estado, formato o a11y

## Schema-owned
- títulos, summaries y labels definidos en schema
- labels de acciones del schema
- options/placeholders/helpText del schema

## State / validation / action-owned
- state labels y descriptions canónicos
- validation messages
- transiciones y action availability
- role labels si están pegadas al token técnico

## Backend / data / evidence-owned
- ids, adapter ids, tokens, direction
- errores crudos
- summaries derivados de adapters/backend
- payloads y evidence del timeline

## Dudoso
- todo texto visible cuya capa dueña aún no está cerrada
- todo lo que parece UI, pero en realidad expresa contrato operativo

---

# 12. 📏 Matriz maestra de validación

## 12.1 Gate reusable

| Tipo | Qué revisar | Criterio de aceptación | Señal de stop |
|---|---|---|---|
| Funcional | que idioma no cambie acciones, filtros, routing ni submits/retries | misma acción, mismo resultado | una acción deja de representar lo real |
| Visual | truncado, wraps, pills, badges, cards, buttons, headers, empty states | sin clipping ni saltos raros | el texto ya no cabe o tapa data |
| Transversal | mezcla de idiomas, consistencia de labels, top area, scroll, densidad | política coherente por superficie | vista híbrida sin criterio |
| Ownership | separar frontend/shared/schema/backend/dudoso | cada string tiene dueño tentativo claro | aparece texto sin owner claro |
| Por superficie | peculiaridades de cada ruta | checklist por ruta completo | una ruta exige excepciones no documentadas |

## 12.2 Rutas mínimas a revisar siempre
- `/`
- `/inbox`
- `/flow/[schemaId]`
- `/record/[recordId]`
- `/sync`
- `/playground`

## 12.3 Checklist transversal
- [ ] no hay mezcla rara de idiomas en una misma entidad
- [ ] top area no se satura
- [ ] headers no saltan feo
- [ ] pills y badges no colapsan
- [ ] stat cards no desbordan
- [ ] empty states caben completos
- [ ] labels equivalentes mantienen el mismo término en todas las superficies
- [ ] nada dudoso entró a la primera ola sin contrato

---

# 13. ⚠️ Matriz de riesgos operativos global

| Riesgo | Prob. | Impacto | Señal temprana | Mitigación |
|---|---:|---:|---|---|
| No cerrar default locale a tiempo | alta | alta | discusiones repetidas sobre fallback | congelar `defaultLocale = en` antes del provider |
| Persistencia inconsistente | media | alta | cambia idioma, recargas y regresa raro | una sola key y una sola fuente de verdad |
| Fallback silencioso | alta | alta | “todo parece bien” pero no sabes qué falta | marcador explícito en dev/test |
| Shell saturado | media | media/alta | nav + CTAs + selector + chips + current surface revientan | selector fuera de zonas ya densas |
| Layout roto por longitud | alta | alta | wraps feos en nav, cards, pills, badges | validar strings largas por breakpoint |
| Mezclar idioma con runtime/theme | media | alta | labels traducidos aparecen en runtime.ts | separar idioma en `src/lib/i18n/*` |
| Ownership ambiguo | alta | alta | se empieza a traducir schema/state/evidence como si fuera UI | lista roja + rollout acotado |
| Traducir semántica real | alta | alta | labels “bonitas” pero falsamente precisas | glosario/diccionario oficial por dominio |
| Errores backend tratados como UI | media | alta | se adornan errores crudos | separar raw vs normalized |
| Rollout desordenado | alta | alta | cambian muchas superficies a la vez y no sabes qué rompió | fases cortas + evidencia mínima |

---

# 14. 🧪 Checklist de readiness antes de ejecutar

- [ ] default locale congelado
- [ ] idiomas iniciales congelados
- [ ] storage key congelada
- [ ] fallback policy congelada
- [ ] backend explícitamente fuera de V1
- [ ] namespaces iniciales definidos
- [ ] hotspots shared identificados
- [ ] lista roja global aprobada
- [ ] rollout por fases aprobado
- [ ] gates por fase aprobados
- [ ] validación transversal definida
- [ ] criterio explícito para aceptar o no mezcla temporal de idiomas

---

# 15. 📦 Artefactos que este dossier deja listos

## Ya deja listos
- tabla oficial de decisiones operativas
- rollout por fases
- gates por fase
- checklist de readiness
- lista roja global
- mapa maestro de ownership
- matriz maestra de validación
- mapa de riesgos global
- anexos por superficie
- hotspots shared / shell
- base para mini fichas por frente

## Mini ficha reutilizable sugerida
- **Objetivo:**
- **Archivo(s):**
- **Ownership confirmado:**
- **Qué NO se va a tocar:**
- **Riesgo principal:**
- **Validación mínima:**
- **Señal de stop:**
- **Resultado esperado:**

---

# 16. 🔓 Qué nos deja resuelto este dossier

## Queda prácticamente listo para pasar a ejecución
- el **marco operativo** del frente de idioma
- la **política mínima de V1**
- el **orden sano de rollout**
- la **frontera entre copy segura y semántica sensible**
- la **lista de gates y stops**
- la **validación transversal**

## Queda semi-listo, pero sujeto a auditoría fina
- flow
- detail
- todo lo que dependa de schema text
- todo lo que dependa de state/validation vocabulary
- todo lo que venga como evidence o backend-propagated message

## Queda explícitamente fuera de esta primera corrida
- backend
- persistencia server-side
- locale negotiation avanzada
- traducción completa de schema-driven content
- traducción de evidence operativa
- variants regionales

## Traducción brutalmente honesta
Este dossier ya deja **la cancha pintada, las porterías puestas y las minas marcadas**. Todavía no se juega el partido, pero ya no estamos entrando a oscuras ni a puro presentimiento.

---

# 17. 📝 Cierre

Si seguimos este documento como puerta de entrada del frente de idioma:
- no vamos a improvisar naming,
- no vamos a invadir ownership dudoso,
- no vamos a traducir evidencia operativa como si fuera copy local,
- y la primera ola puede salir limpia, reversible y verificable.

**En una línea:**

> **Shell + shared + quick wins seguros primero. Semántica real después. Backend no entra todavía.**

