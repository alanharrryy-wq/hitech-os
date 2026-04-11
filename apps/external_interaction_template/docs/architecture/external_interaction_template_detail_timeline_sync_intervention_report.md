# Reporte 1. Mapa y alcance

## 1.1 Base obligatoria usada

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

## 1.2 Convenciones de lectura

- **Confirmado:** sale de inspección directa del código real del zip.
- **Inferido:** deducción razonable a partir del código revisado, pero no validada en runtime.
- **Dudoso:** ownership o semántica no suficientemente clara como para tocarla sin contrato previo.

## 1.3 Resumen ejecutivo

### Qué cubre este trabajo
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

### Qué deja resuelto
- Dónde vive realmente la carga de UI y semántica.
- Qué cosas sí parecen seguras para una primera ola controlada.
- Qué partes no deben tocarse todavía por mezclar frontend con contratos operativos o schema-driven content.
- Qué señales deben detener cualquier intervención antes de que el cambio se vuelva una granada con glitter.

### Riesgos operativos detectados
- `record-detail`, `activity-timeline` y `sync-center` mezclan copy editorial con evidencia operativa visible.
- El timeline **reinterpreta** estados operativos en estados de record, y esa traducción ya es una capa semántica delicada.
- `sync-center` expone errores crudos, summaries y badges atados a enums reales.
- `record-detail` muestra labels schema-driven, action labels schema-driven y estados shared/runtime, todo en la misma vista.
- La semántica de retry existe en backend/service logic y se proyecta en UI con wording local.

## 1.4 Alcance y no alcance

### Entra en esta intervención
- Mapeo estructural y operativo de:
  - `/record/[recordId]`
  - `ActivityTimeline`
  - `/sync`
- Identificación de ownership tentativo por elemento visible.
- Inventario de zonas seguras vs zonas sensibles.
- Validación operativa reusable antes de tocar implementación.

### No entra todavía
- Implementación final de idioma.
- Refactor de i18n/provider/dictionary.
- Normalización final de errores.
- Rediseño de estados o contratos de retry.
- Traducción definitiva de schema content.
- Redefinición de summary, payload o evidence rendering.

### Condiciones de corte
Se debe detener cualquier intervención si aparece cualquiera de estas señales:
- ownership incierto de un texto visible
- necesidad de cambiar enums, estados o rutas para “hacer calzar” un label
- necesidad de tocar schema definitions para resolver una decisión de UI no cerrada
- necesidad de reinterpretar errors o summaries del backend
- mezcla no documentada entre copy local y evidencia operativa
- desalineación entre métricas, filtros y estados reales

## 1.5 Mapa de superficies impactadas

### Superficie principal
| Superficie | Archivo(s) principal(es) | Por qué es principal | Riesgo |
|---|---|---|---|
| Record detail | `app/record/[recordId]/page.tsx`, `components/records/record-detail.tsx` | concentra UI de detalle, actions, metadata, panel operativo y acceso al timeline | Crítico |
| Activity timeline | `components/records/activity-timeline.tsx`, `src/lib/ui/record-contracts.ts` | reordena y resume evidencia operativa en historia legible | Crítico |
| Sync center | `app/sync/page.tsx`, `components/sync/sync-center.tsx` | superficie operativa más sensible: métricas, filtros, retries, errors, summaries | Crítico |

### Dependencias visibles relevantes
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

## 1.6 Mapa del detail

### 1.6.1 Estructura general confirmada
- `app/record/[recordId]/page.tsx`:
  - resuelve `recordId`
  - carga `record`
  - obtiene `schema`
  - carga subrecursos con `listRecordSubresources(recordId)`
  - renderiza `RecordDetail`
- `components/records/record-detail.tsx` concentra casi toda la superficie visible.

### 1.6.2 Zonas de UI del detail
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

### 1.6.3 Headings visibles en detail
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

### 1.6.4 Metadata visible en detail
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

### 1.6.5 Actions visibles en detail
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

### 1.6.6 States visibles en detail
| Superficie | Representación visible | Fuente | Riesgo |
|---|---|---|---|
| Header badge | `StateBadge(record.state)` | `stateLabel`, `stateTone`, `ensureRecordState` | Alto |
| Stat card | `stateLabel(record.state)` + `stateDescription(record.state)` | `record-view.ts` | Alto |
| Latest sync stat | `latestSync.status` | `SyncStatus` raw | Crítico |
| Dispatch & sync panel | `job.status`, `event.status` | `DispatchStatus`, `SyncStatus` raw | Crítico |
| availableActions | depende de `isActionAvailable(record.state, action, { role })` | runtime/state contract | Crítico |

### 1.6.7 Retries en detail
- **Confirmado:** el detail no ejecuta retry directo.
- **Confirmado:** el detail solo:
  - expone jobs/events resumidos
  - redirige al `/sync`
  - refresca el record
- **Inferido:** cualquier copy en detail que sugiera retry o reconciliación directa sería engañosa porque el control real vive en sync/service logic.

### 1.6.8 Errors y feedback en detail
| Elemento | Fuente | Naturaleza | Riesgo |
|---|---|---|---|
| guard-rail de nota requerida | local | copy preventiva | Medio |
| feedback éxito | `${action.label} executed successfully.` | local + schema label | Alto |
| feedback error | `body.error ?? "Action failed"` | backend/service error crudo o fallback local | Crítico |
| dispatch job error | `job.error` | evidencia operativa | Crítico |
| sync event error | `event.error` | evidencia operativa | Crítico |

### 1.6.9 Summaries / evidence en detail
| Elemento | Fuente | Tipo |
|---|---|---|
| `record.title` | record | evidencia / dato de negocio |
| `schema.summary` | schema | schema content |
| `latestSync.summary` | sync event | evidencia operativa / resumen sensible |
| field values | `record.fields[fieldId]` | evidencia |
| attachment names | attachment metadata | evidencia |
| `record.id`, `secureToken` | record | evidencia operativa |

### 1.6.10 Hallazgos clave del detail
- **Confirmado:** detail mezcla tres capas en una sola vista:
  - shell local
  - schema-driven content
  - evidencia/operación
- **Confirmado:** las action labels no son locales, salen del schema.
- **Confirmado:** el feedback de error puede ser crudo del backend/service layer.
- **Confirmado:** `Latest sync` usa `syncEvents[0]`, y el store devuelve sync events ordenados por `createdAt desc`.
- **Dudoso:** traducir `stateLabel` y `stateDescription` sin glosario global puede romper coherencia entre detail, inbox y badges.

---

## 1.7 Mapa del timeline

### 1.7.1 Estructura general confirmada
- `ActivityTimeline` recibe:
  - `submissions`
  - `syncEvents`
  - `dispatchJobs`
- arma eventos con `createTimelineEntries(...)`
- renderiza lista cronológica descendente
- si no hay eventos, usa empty state local.

### 1.7.2 Zonas de UI del timeline
| Zona | Qué muestra | Naturaleza | Estado |
|---|---|---|---|
| Empty state | título y descripción | local | Confirmado |
| Entry header | `event.kind`, fecha, meta | runtime-assembled | Confirmado |
| Entry title | title construido por contrato | runtime-assembled / evidence | Confirmado |
| Entry description | description construida por contrato | runtime-assembled | Confirmado |
| State badge | `event.state` | derived semantic layer | Confirmado |
| Detail block | `event.detail` en `<pre>` | evidencia cruda o JSON | Confirmado |

### 1.7.3 Headings y labels visibles en timeline
| Elemento | Valor visible | Fuente | Ownership tentativo |
|---|---|---|---|
| Empty title | `No activity yet` | local | Frontend-owned |
| Empty description | `New submissions, dispatch attempts and sync signals will land here once the record starts moving.` | local | Frontend-owned |
| kind label | `submission` / `dispatch` / `sync` | runtime contract | Runtime-owned |
| time label | `formatDateTime(event.createdAt)` | shared util | Shared-owned |
| meta | actorId o meta string | runtime/evidence | Dudoso |
| title | depende del tipo de evento | runtime contract + evidence | Runtime-owned / Dudoso |
| description | depende del tipo de evento | runtime contract + evidence | Runtime-owned / Dudoso |

### 1.7.4 Cómo se construye cada tipo de entrada
| Kind | Title | Description | State badge | Detail | Meta |
|---|---|---|---|---|---|
| submission | `submission.stepId` sanitizado o `Submission captured` | `Captured X field update(s) from {source}.` | `submitted` | JSON del payload | `submission.actorId` |
| dispatch | `Dispatch {job.status}` | `{adapterId} • attempts: N` | `succeeded -> dispatched`, `failed -> failed`, otro -> `in_review` | `job.error` o JSON de `job.response` | none |
| sync | `event.summary` sanitizado o `Sync signal` | `{direction} • {adapterId}` | `synced -> synced`, `failed -> failed`, otro -> `submitted` | `event.error` o JSON de `event.payload` | none |

### 1.7.5 Semántica operativa sensible del timeline
| Elemento | Qué hace | Riesgo |
|---|---|---|
| `mapDispatchState` | traduce `DispatchStatus` a `RecordState` | Crítico |
| `mapSyncState` | traduce `SyncStatus` a `RecordState` | Crítico |
| `Dispatch {job.status}` | vuelve visible el enum operativo dentro de un título legible | Alto |
| `event.summary` como title | eleva summary a heading de timeline | Crítico |
| `event.detail` | muestra error o payload crudo | Crítico |
| `kind` visible | clasifica historia operacional | Medio |

### 1.7.6 Errors y evidence en timeline
| Elemento | Fuente | Naturaleza |
|---|---|---|
| submission detail | `safeJson(submission.payload)` | evidencia cruda |
| dispatch detail | `job.error` o `job.response` serializado | evidencia cruda |
| sync detail | `event.error` o `event.payload` serializado | evidencia cruda |

### 1.7.7 Hallazgos clave del timeline
- **Confirmado:** timeline no es solo UI. Es una **capa narrativa** armada con contratos runtime.
- **Confirmado:** el timeline ya “traduce” eventos técnicos a una historia legible.
- **Confirmado:** esa traducción ya tiene pérdida de granularidad:
  - `pending` y `retryable` no se ven como states propios del badge; se remapean.
- **Crítico:** tocar copy del timeline sin aclarar si se está editando copy o reinterpretando evidencia puede deformar la lectura histórica.
- **Dudoso:** `event.summary` puede ser generado por adapter/service y no por frontend.

---

## 1.8 Mapa del sync

### 1.8.1 Estructura general confirmada
- `app/sync/page.tsx` carga `listSyncCenterData()`.
- `listSyncCenterData()` devuelve `events` y `jobs`.
- `SyncCenter` concentra:
  - métricas
  - filtros
  - listas
  - retry
  - feedback

### 1.8.2 Zonas de UI del sync
| Zona | Qué muestra | Naturaleza | Estado |
|---|---|---|---|
| Header | título, descripción, refresh | local | Confirmado |
| Stat cards | métricas de jobs/events | local + semántica operativa | Confirmado |
| Dispatch jobs panel | jobs, status, error, retry | operativa visible | Confirmado |
| Sync events panel | event summary, status, direction, adapter, timestamp, error | operativa visible | Confirmado |
| Message strip | éxito o fallo de retry | local + backend/service error | Confirmado |

### 1.8.3 Headings visibles en sync
| Elemento | Valor visible | Ownership tentativo |
|---|---|---|
| Eyebrow | `Sync center` | Frontend-owned |
| Title | `Operational visibility for dispatch and sync health` | Frontend-owned |
| Description | `Inspect outbound execution, watch retryable failures, and keep the audit trail readable at a glance.` | Frontend-owned |
| Panel title | `Dispatch jobs` | Frontend-owned |
| Panel subtitle | `Outbound action execution states with retry controls.` | Frontend-owned |
| Panel title | `Sync events` | Frontend-owned |
| Panel subtitle | `Inbound and outbound audit trail with clearer status visibility.` | Frontend-owned |

### 1.8.4 Métricas visibles en sync
| Card | Fórmula confirmada | Riesgo |
|---|---|---|
| `Pending jobs` | jobs con `pending` o `running` | Alto |
| `Failed jobs` | jobs con `failed` | Medio |
| `Synced events` | events con `synced` | Medio |
| `Retryable events` | events con `retryable` | Alto |

### 1.8.5 Filtros visibles en sync
| Grupo | Opciones visibles | Value real |
|---|---|---|
| Jobs | `All`, `Failed`, `Pending`, `Running`, `Succeeded` | `all`, `failed`, `pending`, `running`, `succeeded` |
| Events | `All`, `Retryable`, `Pending`, `Synced`, `Failed` | `all`, `retryable`, `pending`, `synced`, `failed` |

### 1.8.6 Botones y retries en sync
| Elemento | Comportamiento | Riesgo |
|---|---|---|
| `Refresh data` | `router.refresh()` | Bajo |
| `Retry` | POST `/api/sync/jobs/{jobId}/retry` | Crítico |
| `Retrying...` | estado busy local | Medio |
| disable rule | se deshabilita si hay `busyJob` o si `job.status !== "failed"` | Crítico |

### 1.8.7 Errors, feedback y evidence en sync
| Elemento | Fuente | Naturaleza | Riesgo |
|---|---|---|---|
| job error card | `job.error` | evidencia operativa | Crítico |
| event error text | `event.error` | evidencia operativa | Crítico |
| retry success strip | `Retry executed for job {jobId}.` | local + id | Medio |
| retry fail strip | `body.error ?? "Retry failed"` | backend/service error crudo o fallback local | Crítico |

### 1.8.8 Data visible por panel en sync

#### Dispatch jobs
| Campo visible | Fuente | Tipo |
|---|---|---|
| `recordId` como link | job | evidencia operativa |
| `Adapter {adapterId}` | job | wrapper local + evidencia |
| `Attempts {attempts}` | job | wrapper local + evidencia |
| badge `{job.status}` | job | semántica operativa cruda |
| `Updated {updatedAt}` | job | wrapper local + evidencia |
| `job.error` | job | evidencia operativa |
| `Retry` | local, pero amarrado a status real | acción sensible |

#### Sync events
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

### 1.8.9 Hallazgos clave del sync
- **Confirmado:** sync es la superficie operativa más delicada del frente.
- **Confirmado:** métricas, filtros, badges y retries están atados a contratos reales de estado.
- **Confirmado:** sync mezcla copy segura con evidence/semantics en la misma card.
- **Confirmado:** retry solo aplica a dispatch jobs fallidos.
- **Crítico:** confundir `failed` con `retryable` o `succeeded` con `synced` rompería el significado operativo.

## 1.9 Semántica operativa sensible confirmada

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

## 1.10 Dependencias relevantes por superficie

| Superficie | Dependencias principales | Observación |
|---|---|---|
| Detail | `record-detail.tsx`, `record-view.ts`, `core/state.ts`, `schema-registry.ts`, `services/actions.ts`, `services/records.ts` | mezcla shell, schema, runtime y operativa |
| Timeline | `activity-timeline.tsx`, `record-contracts.ts`, `ui/contracts.ts` | la narrativa se construye en runtime, no llega “lista” |
| Sync | `sync-center.tsx`, `services/actions.ts`, `memory-store.ts`, retry route | la semántica real no está solo en la UI; vive en services/store/contracts |

# Reporte 2. Ownership, lista roja y riesgos

## 2.1 Matriz de frontend-owned

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

## 2.2 Matriz de shared-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `StateBadge` visual shell | detail, timeline, otras | `components/ui/state-badge.tsx` | Alta | shared component |
| `PageHeader`, `Badge`, `Button`, `StatCard`, `Surface`, `EmptyState`, `FilterPills` | detail, sync, otras | `components/ui/*` | Alta | shared visual system |
| `formatDateTime`, `formatRelativeTime`, `formatBytes`, `formatValue` | detail, timeline, sync | `src/lib/utils.ts` | Alta | shared formatting |
| `toneFromSeverity` y utilidades de UI contract | timeline/other UI | `src/lib/ui/contracts.ts` | Alta | shared utilities |
| `stateTone` | badges/shared states | `src/lib/core/record-view.ts` | Media | shared semantics + visual tone |

## 2.3 Matriz de runtime-owned

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

## 2.4 Matriz de schema-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `schema.title` | detail | `src/lib/core/schema-registry.ts` | Alta | schema content |
| `schema.summary` | detail | `src/lib/core/schema-registry.ts` | Alta | schema content |
| `section.title` en Business details | detail | `src/lib/core/schema-registry.ts` | Alta | schema views |
| `field.label` | detail | `src/lib/core/schema-registry.ts` | Alta | schema definition |
| `action.label` en botones | detail | `src/lib/core/schema-registry.ts` | Alta | schema action labels |
| `action.requiresComment` semantic hint | detail | `src/lib/core/schema-registry.ts` | Alta | gobierna copy local y control |
| field placeholders / helpText del flow | fuera de foco principal, pero relacionados | `src/lib/core/schema-registry.ts` | Alta | impacta validación transversal futura |

## 2.5 Matriz de backend-owned

| Elemento | Superficie | Archivo base | Confianza | Nota |
|---|---|---|---|---|
| `body.error` devuelto por action route | detail | `app/api/records/[recordId]/action/route.ts` | Alta | error shape de API |
| `body.error` devuelto por retry route | sync | `app/api/sync/jobs/[jobId]/retry/route.ts` | Alta | error shape de API |
| `job.error` | detail, timeline, sync | services/store/adapters | Alta | evidencia operativa |
| `event.error` | detail, timeline, sync | services/store/adapters | Alta | evidencia operativa |
| `response.summary` de dispatch/retry | timeline, sync, events | `src/lib/services/actions.ts` + adapter response | Media-Alta | summary generado fuera del shell local |
| `response.responsePayload` / `event.payload` / `job.response` | timeline | services/store/adapters | Alta | evidencia cruda |

## 2.6 Matriz de dudoso

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

## 2.7 Lista roja del detail

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

## 2.8 Lista roja del timeline

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

## 2.9 Lista roja del sync

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

## 2.10 Matriz de riesgos

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

## 2.11 Riesgos específicos de evidence

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| title de record tratado como heading traducible | detail | puede ser dato de negocio, no copy |
| summary de sync tratado como copy editorial | detail, timeline, sync | puede ser evidencia generada por adapter/service |
| payload/error en timeline tratados como texto UX | timeline | rompe trazabilidad |
| ids/adapter/token tratados como labels blandos | detail, sync | puede dañar soporte/operación |

## 2.12 Riesgos específicos de status semantics

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| `stateLabel` y `stateDescription` no alinean con `job.status`/`event.status` | detail | ya son vocabularios distintos |
| `Latest sync` muestra `SyncStatus`, no `RecordState` | detail | fácil confundirlo con el estado general del record |
| timeline remapea dispatch/sync status a `RecordState` | timeline | capa de interpretación, no vista literal |
| filtros y métricas usan dominios distintos por panel | sync | job panel != event panel |

## 2.13 Riesgos específicos de retries

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| retry de job se comunica como si fuera retry de sync | sync | wording debe preservar el sujeto real |
| retry exitoso cambia record a `synced` bajo ciertas condiciones | services/actions + sync/detail | tiene semántica de reconciliación real |
| retry fallido crea nuevo sync event `retryable` | services/actions | no debe ocultarse detrás de copy vaga |

## 2.14 Riesgos específicos de feedback/error messages

| Riesgo | Dónde aparece | Nota |
|---|---|---|
| `Action failed` y `Retry failed` conviven con errors crudos | detail, sync | mezcla local + backend |
| success feedback usa `action.label` | detail | si action.label es schema-owned, el feedback también hereda ese owner |
| errors largos rompen layout o se vuelven ilegibles | detail, timeline, sync | necesita validación explícita |

# Reporte 3. Validación y criterios de aceptación

## 3.1 Validación del detail

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

## 3.2 Validación del timeline

| Caso | Qué revisar | Por qué importa | Severidad | Criterio de aceptación | Señal de stop |
|---|---|---|---|---|---|
| Empty state | título y descripción | copy segura | Media | cabe bien y no invade semántica | se intenta usarlo para explicar estados reales |
| kind label | `submission`, `dispatch`, `sync` | clasifica historia operativa | Alta | si cambia, existe taxonomía aprobada | se inventa alias sin contrato |
| Title por tipo | submission stepId, `Dispatch {status}`, summary | title mezcla contrato y evidence | Crítica | no se traduce evidence ni se reescribe historia | el title deja de reflejar la fuente real |
| Description por tipo | captured updates / adapter / direction | capa runtime | Alta | wording sigue fiel a la fuente | se borra adapter/direction/attempts por sonar técnico |
| State badge | mapDispatchState / mapSyncState | remapeo semántico sensible | Crítica | badge sigue documentado como derived state | se interpreta como estado literal del evento |
| Detail block | error/payload/response JSON | evidencia cruda | Crítica | contenido intacto, legible y no adornado | se traduce, limpia o resume evidence |
| Ordering | newest first | lectura histórica | Alta | orden descendente intacto | cambios visuales alteran percepción temporal |

## 3.3 Validación del sync

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

## 3.4 Validación de actions visibles

| Acción | Superficie | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|---|
| `Inbox` | detail | sigue siendo navegación simple | lleva a `/inbox` y su label sigue inequívoco | pide reinterpretación funcional |
| `Refresh` / `Refresh record` / `Refresh data` | detail, sync | no sugieren side effects falsos | solo refrescan vista | alguien quiere convertirlos en “resync” o similar |
| schema action buttons | detail | label refleja la action real del schema | botón, feedback y note requirement siguen alineados | se quiere “mejorar” label sin política schema |
| `Retry` | sync | sujeto, alcance y resultado percibido | claramente reintenta un failed dispatch job | wording cambia el objeto real de la acción |

## 3.5 Validación de metadata

| Metadata | Superficie | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|---|
| ids (`recordId`, `jobId`) | detail, sync | siguen visibles y exactos | wrapper puede cambiar; valor no | alguien quiere humanizarlos |
| `secureToken` | detail | no se toca ni se degrada su legibilidad | valor intacto | se intenta traducir, truncar o relabel ambiguamente |
| `adapterId` | detail, timeline, sync | se deja técnico salvo contrato | valor intacto | se cambia a alias sin mapa |
| fechas y tiempos | detail, timeline, sync | wrapper y formato consistentes | no cambian meaning temporal | cambios visuales vuelven ambiguo si es relativo o absoluto |
| counts | detail, sync | label describe count real | counts confiables | labels vagos o inconsistentes |

## 3.6 Validación de retries

| Caso | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|
| Button enablement | solo `job.status === "failed"` | la UI no habilita retry en otros estados | se habilita o comunica retry fuera de failed jobs |
| Busy label | `Retrying...` | no sugiere otro proceso distinto | se interpreta como sync global |
| Success strip | `Retry executed for job {jobId}.` | outcome acotado y fiel | mensaje sugiere que todo el record quedó synced sin contexto |
| Failure strip | error crudo o fallback | fidelidad al outcome real | se traduce/parafrasea error sin política |

## 3.7 Validación de métricas

| Métrica | Qué validar | Criterio de aceptación | Stop |
|---|---|---|---|
| Pending jobs | incluye `pending` + `running` | label/meta explican la fórmula | se renombra como si fuera solo `pending` |
| Failed jobs | cuenta solo `failed` | ninguna confusión con `retryable events` | se mezclan dominios |
| Synced events | cuenta solo events `synced` | no se confunde con records synced | se interpreta como “records synced” |
| Retryable events | cuenta solo events `retryable` | no se confunde con failed jobs | se aplana con `failed` |

## 3.8 Validación de errores largos

| Superficie | Qué revisar | Criterio de aceptación | Stop |
|---|---|---|---|
| detail feedback | error de action largo | se mantiene legible, no engañoso | truncado sin contexto o “normalizado” arbitrario |
| detail dispatch/sync panel | error largo | no rompe card, sigue fiel | se oculta por completo |
| timeline detail pre | JSON/error largo | scroll y wrap sanos | se transforma el payload |
| sync jobs/events | error largo | card y strip soportan texto extenso | layout roto o cambio de meaning |

## 3.9 Criterios de aceptación globales

Se considera este frente **listo para pasar a diseño de intervención** cuando:
- todas las superficies críticas tienen mapa real basado en código
- cada string visible relevante tiene owner tentativo o está marcado como dudoso
- existe lista roja congelada
- los riesgos críticos tienen mitigación y señal de stop
- la diferencia entre `RecordState`, `DispatchStatus` y `SyncStatus` quedó explícita
- la diferencia entre copy segura y evidence quedó documentada
- la validación operativa por superficie está lista
- no hay propuesta de implementación que dependa de inventar ownership

## 3.10 Señales de stop globales

Detener la intervención si pasa cualquiera de estas:
- aparece necesidad de traducir `event.summary`, `job.error`, `event.error`, `record.title` o `secureToken`
- se detecta que action labels o section labels deben salir de schema y no del shell local
- una decisión de idioma exige cambiar enums, contracts o routes
- el timeline necesita reinterpretación narrativa para “sonar mejor”
- se quiere homologar `failed`, `retryable`, `synced`, `succeeded` como si fueran equivalentes
- se propone mostrar aliases de actor role, adapter o direction sin contrato display-only
- la mezcla de idiomas en detail/sync ya no se puede controlar con una política temporal explícita

# Reporte 4. Hallazgos extra y qué nos deja resuelto

## 4.1 Quick wins seguros

### Detail
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

### Timeline
- empty state local
- quizá el wrapper visual del bloque, pero no el contenido narrativo ni evidence
- iconografía y layout, siempre que no se reetiquete semántica

### Sync
- header copy
- subtítulos de panel
- `Refresh data`
- empty states
- meta text de métricas
- wrappers como `Adapter`, `Attempts`, `Updated`
- success strip del retry manteniendo ids intactos

## 4.2 Zonas que deben esperar

### Detail
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

### Timeline
- titles runtime construidos con status o summary
- descriptions derivadas de adapter/direction/attempts
- detail pre blocks con payload/error/response
- remapeos semánticos a `RecordState`

### Sync
- badges de status
- labels de filtros atados a enums
- métricas
- retry semantics
- `event.summary`
- `job.error`
- `event.error`
- `direction`
- `adapterId`

## 4.3 Artefactos sugeridos para la siguiente etapa

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

## 4.4 Simplificaciones posibles

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

## 4.5 Contratos semánticos que conviene aclarar antes

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

## 4.6 Preguntas abiertas reales

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

## 4.7 Qué nos deja resuelto este chat

Este chat deja **muy bien amarrado** el frente de pre-intervención para `record detail`, `activity timeline` y `sync center` usando el zip como fuente principal de verdad y el formato universal como puerta de control.

### Resuelto
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

### No resuelto todavía, a propósito
- implementación final
- estrategia final de idioma
- glosario oficial de estados
- política final de errors y summaries
- estrategia schema-driven de traducción

### Valor práctico
La siguiente conversación ya no tendría que empezar desde exploración difusa. Podría arrancar desde una base controlada para decidir:
- primera ola segura
- exclusiones explícitas
- contratos a aclarar
- validaciones a automatizar

En otras palabras: este chat deja el terreno nivelado, marcado con conos, y sin cables sorpresa cruzando el pasillo.
