
# 1. Executive overview

## What this app is
`apps/external_interaction_template` is a Next.js App Router web companion focused on external interactions (collect/review/update/approve/dispatch/sync) using a schema-driven model.

## What it is trying to do
Provide a neutral external-facing workflow layer (not CRM-specific) where behavior is controlled by `RecordTypeSchema` definitions, adapters, and state transitions.

## Current maturity level
Maturity: **7/10 (functional template, not production-complete).**

- End-to-end core loop exists: create record -> update -> actions -> dispatch -> sync visibility.
- API and storage layers are coherent.
- UI is usable and polished enough for demo/internal starter usage.
- Security, authorization, attachment retrieval, and operational hardening are still template-grade.

## Main capabilities already implemented
- Schema-driven flow runner (`service_request`, `approval_packet`, `inspection_checklist`).
- Record inbox with filter/search and list/grid mode.
- Record detail with role-aware action rendering and timeline/sync summaries.
- Sync center with retry action for failed dispatch jobs.
- Inbound and outbound event recording.
- Adapter abstraction with built-ins: `local`, `rest`, `webhook`.
- Store abstraction with Prisma-backed default and memory-backed test mode.

## Main limitations / scaffolded areas
- Access control is header-based placeholder (`x-actor-role`, optional token headers), no real auth session model.
- Attachments are written locally (`storage/attachments`) and metadata is stored, but no download/authz layer.
- Outbound adapters are real code paths but production integrations depend on env endpoints and minimal retry policy.
- UI actions are practical, but some advanced flows (draft resume list, granular field permissions by state) are partial.

---

# 2. App surface map

## Surface 1: Launcher / Home
- Route: `/`
- Source: `apps/external_interaction_template/app/page.tsx`
- Purpose: product launcher + metrics + schema quick starts.
- Primary UI regions:
  - top metrics (`Records`, `Pending Sync`, `Retryable`, `Schemas`)
  - global CTAs (`Open Schema Playground`, `Review Inbox`, `Sync Center`)
  - schema cards with per-schema actions
- Primary user actions:
  - Open schema playground
  - Open inbox
  - Open sync center
  - Start flow by schema
  - Open resume/token mode
- Data read: `listSchemas()`, `listRecords()`, `listSyncCenterData()`
- Depends on: schema registry + records/actions services + UI primitives.
- State transitions possible: none directly.
- Status: Complete.

## Surface 2: Schema Playground
- Route: `/playground`
- Source: `apps/external_interaction_template/app/playground/page.tsx`
- Purpose: inspect included schemas and jump into flows/inbox by schema.
- Primary user actions: `Run flow`, `Inspect inbox`.
- Data read: `listSchemas()`.
- Status: Complete (read-only schema browser).

## Surface 3: Flow Runner Host
- Route: `/flow/[schemaId]`
- Source: `apps/external_interaction_template/app/flow/[schemaId]/page.tsx`
- Purpose: host schema flow with optional token resume.
- Primary user actions: `Resume` (token submit), `New flow session`.
- Data read: `getSchema(schemaId)`, `getRecordByToken(token)`.
- State transitions: indirect via `FlowRunner`.
- Status: Complete.

## Surface 4: Flow Runner (interactive)
- Route context: rendered inside `/flow/[schemaId]`
- Source: `apps/external_interaction_template/components/flow/flow-runner.tsx`
- Purpose: multi-step collect/update/submit with validation and file upload metadata.
- Primary user actions:
  - Edit field values by type
  - `Back`
  - `Save & Continue`
  - `Submit`
  - `Save Draft`
  - Step jump via step navigator
- APIs/services used:
  - local validation: `validateStepPayload`
  - visibility: `isFieldVisible`
  - `POST /api/records` (create)
  - `PATCH /api/records/[recordId]` (update)
  - `POST /api/records/[recordId]/attachments` (per file)
- Status: Mostly complete (attachments are metadata+local write only).

## Surface 5: Inbox / Review
- Route: `/inbox`
- Source: `apps/external_interaction_template/app/inbox/page.tsx`
- Core component: `components/records/record-inbox.tsx`
- Purpose: review/search/filter records.
- Primary user actions: search, schema filter, list/grid toggle, open record detail.
- Data read: `listSchemas()`, `listRecords({schemaId?})`.
- Status: Complete for browsing.

## Surface 6: Record Detail
- Route: `/record/[recordId]`
- Source host: `apps/external_interaction_template/app/record/[recordId]/page.tsx`
- Core component: `components/records/record-detail.tsx`
- Purpose: inspect fields, timeline, attachments, actions, sync/dispatch summary.
- Primary user actions: role switch (simulation), execute action, open sync center, refresh page.
- Data read: `getRecordById`, `listRecordSubresources`, `getSchema`.
- Status: Complete for template scope; auth trust is demo-level.

## Surface 7: Sync Center
- Route: `/sync`
- Source host: `apps/external_interaction_template/app/sync/page.tsx`
- Core component: `components/sync/sync-center.tsx`
- Purpose: inspect dispatch jobs and sync events; retry failed jobs.
- Primary user action: retry failed dispatch job.
- Data read: `listSyncCenterData()`.
- Status: Complete for single-job retries.

## Surface 8: Token lookup/update API-backed flow
- Entry paths:
  - `/flow/[schemaId]?token=...`
  - API `/api/records/token/[token]` (GET/PATCH)
- Purpose: secure-link style resume/update pathway.
- Status: implemented at template level; hardening pending.

## Surface 9: Global shell + visual backdrop
- Sources:
  - `app/layout.tsx`
  - `components/layout/app-shell.tsx`
  - `components/layout/ambient-backdrop.tsx`
- Purpose: persistent nav/frame and atmosphere.
- Status: Complete.

---

# 3. Navigation and flow map

## Journey A: Start a new flow
- Entry point: `/` (Launcher)
- Traversal:
  - Click `Start flow` on schema card -> `/flow/[schemaId]`
  - Fill steps in `FlowRunner`
  - `Save & Continue` between steps
  - `Submit` at final step
- Expected result:
  - Record created/updated in submitted state
  - Submission + inbound sync events created
  - Secure token generated
- Backing modules:
  - `app/page.tsx`
  - `components/flow/flow-runner.tsx`
  - API `POST /api/records`, `PATCH /api/records/[recordId]`
  - services `createRecord`, `updateRecord`
- Rough edge: no first-class draft picker UI.

## Journey B: Resume flow by token
- Entry point: `/flow/[schemaId]?mode=resume` or token form
- Traversal:
  - Enter token -> form submits query param `token`
  - Host page loads initial record
  - Continue editing and save/submit
- Expected result: existing record loaded and patched.
- Backing modules:
  - `app/flow/[schemaId]/page.tsx`
  - `services/getRecordByToken`
  - `PATCH /api/records/[recordId]`
- Rough edge: token has no expiry/rotation policy.

## Journey C: Review records
- Entry point: `/inbox`
- Traversal: search/filter -> list/grid -> open record card.
- Expected result: access detail quickly.
- Backing modules: `RecordInbox`, `recordPreviewFields`.
- Rough edge: text query filter is client-side on fetched records.

## Journey D: Open record detail and take action
- Entry point: `/record/[recordId]`
- Traversal: optional role selection -> click action button -> page refresh.
- Expected result:
  - Action runs if allowed by role/state
  - state/submission/sync/dispatch trails updated
- Backing modules:
  - `RecordDetail`
  - `POST /api/records/[recordId]/action`
  - `services/actions.applyRecordAction`
- Rough edge: role is client-selected and sent by header.

## Journey E: Dispatch/sync monitoring + retry
- Entry point: `/sync`
- Traversal: inspect jobs/events -> click `Retry` on failed job.
- Expected result: job updated + new sync/submission events.
- Backing modules:
  - `SyncCenter`
  - `POST /api/sync/jobs/[jobId]/retry`
  - `services/actions.retryDispatchJob`
- Rough edge: no polling/auto-refresh.

## Journey F: Playground schema switching
- Entry point: `/playground`
- Traversal: inspect schema cards -> `Run flow` / `Inspect inbox`.
- Expected result: demonstrate schema-driven generality.
- Rough edge: registry is static code (no live schema editing).

### High-level interaction diagram

```text
Launcher/Playground
   -> Flow Runner (create/update)
      -> /api/records (+ attachments)
         -> records service
            -> store (Prisma or memory)
               -> submissions/sync events

Inbox
   -> Record Detail
      -> action API
         -> applyRecordAction
            -> adapter dispatch (optional)
            -> dispatch jobs + sync events + state updates

Sync Center
   -> retry API
      -> retryDispatchJob
         -> adapter dispatch
         -> job/event updates
```

---

# 4. Button and action inventory

## Global shell (`components/layout/app-shell.tsx`)

| Label/UI | Location | Source | Behavior | Type | Downstream | Status |
|---|---|---|---|---|---|---|
| Launcher | Header nav | `app-shell.tsx` | Navigate to `/` | Route | Next Link | Fully working |
| Review | Header nav | `app-shell.tsx` | Navigate to `/inbox` | Route | Next Link | Fully working |
| Sync | Header nav | `app-shell.tsx` | Navigate to `/sync` | Route | Next Link | Fully working |
| Playground | Header nav | `app-shell.tsx` | Navigate to `/playground` | Route | Next Link | Fully working |
| Schemas | Header right ghost button | `app-shell.tsx` | Navigate to `/playground` | Route | Next Link | Fully working |
| Start Flow | Header right primary button | `app-shell.tsx` | Navigate to `/flow/service_request` | Route | Next Link | Fully working |

## Launcher (`app/page.tsx`)

| Label | Where | Source | Click behavior | Type | Downstream | Status |
|---|---|---|---|---|---|---|
| Open Schema Playground | Launcher CTA row | `app/page.tsx` | Open `/playground` | Route | Link | Fully working |
| Review Inbox | Launcher CTA row | `app/page.tsx` | Open `/inbox` | Route | Link | Fully working |
| Sync Center | Launcher CTA row | `app/page.tsx` | Open `/sync` | Route | Link | Fully working |
| Start flow | Per schema card | `app/page.tsx` | Open `/flow/[schemaId]` | Route | Link | Fully working |
| Resume / token | Per schema card | `app/page.tsx` | Open `/flow/[schemaId]?mode=resume` | Route | Link | Fully working |

## Playground (`app/playground/page.tsx`)

| Label | Where | Source | Behavior | Type | Downstream | Status |
|---|---|---|---|---|---|---|
| Run flow | Per schema card | `app/playground/page.tsx` | Open `/flow/[schemaId]` | Route | Link | Fully working |
| Inspect inbox | Per schema card | `app/playground/page.tsx` | Open `/inbox?schemaId=[schemaId]` | Route | Link | Fully working |

## Flow page host (`app/flow/[schemaId]/page.tsx`)

| Label | Where | Source | Behavior | Type | Downstream | Status |
|---|---|---|---|---|---|---|
| Resume | Token form | `app/flow/[schemaId]/page.tsx` | GET submit to same route with `token` | Route/query | Server page re-render -> `getRecordByToken` | Fully working |
| New flow session | Host CTA | `app/flow/[schemaId]/page.tsx` | Open `/flow/[schemaId]` without token | Route | Link | Fully working |

## Flow runner (`components/flow/flow-runner.tsx`)

| Label/UI | Where | Behavior | Type | API/service | Status |
|---|---|---|---|---|---|
| Back | action row | decrement step index | Local state | none | Fully working |
| Save & Continue | action row | `persist(false)` then move next step | API + local | `POST /api/records` or `PATCH /api/records/[id]`, optional attachment uploads | Fully working |
| Submit | final step action | `persist(true)` and set UI state submitted | API + local | same record APIs, updates state to submitted | Fully working |
| Save Draft | action row | `persist(false)` | API | same record APIs | Fully working |
| Step button (title per step) | Step Navigator | jump to specific step index | Local state | none | Fully working |
| File field input | dynamic field renderer | stores `FileList`, uploads on persist | API | `POST /api/records/[id]/attachments` per file | Partially wired (metadata+disk, no retrieval surface) |

## Inbox (`components/records/record-inbox.tsx`)

| Label/UI | Where | Behavior | Type | Downstream | Status |
|---|---|---|---|---|---|
| List icon button | Surface actions | set view=list | Local state | none | Fully working |
| Grid icon button | Surface actions | set view=grid | Local state | none | Fully working |
| Search input | filter row | updates `query` and filtered results | Local state | none (client filtering) | Fully working |
| Schema filter select | filter row | updates schema filter | Local state | none (client filtering) | Fully working |
| Record card click | results list/grid | open `/record/[id]` | Route | Link | Fully working |
| Go to Launcher | empty state | open `/` | Route | Link | Fully working |

## Record detail (`components/records/record-detail.tsx`)

| Label/UI | Where | Behavior | Type | API/service | Status |
|---|---|---|---|---|---|
| Actor role select | Available Actions panel | sets role used for action availability and request header | Local state | none | Fully working (template simulation) |
| Dynamic action buttons (Approve/Reject/Dispatch/etc.) | Available Actions panel | run action by id | API call | `POST /api/records/[id]/action` -> `applyRecordAction` | Fully working |
| Open Sync Center | Dispatch/Sync panel | `router.push('/sync')` | Route | Next router | Fully working |
| Refresh | Dispatch/Sync panel | `router.refresh()` | Refresh | Next router re-fetch server data | Fully working |

## Sync center (`components/sync/sync-center.tsx`)

| Label/UI | Where | Behavior | Type | API/service | Status |
|---|---|---|---|---|---|
| Retry | Each failed dispatch job | retry dispatch job | API call | `POST /api/sync/jobs/[jobId]/retry` -> `retryDispatchJob` | Fully working |

---

# 5. Route and API map

## Page routes

| Path | File | Purpose | Inputs | Outputs/render | Data/services | Side effects | Auth assumptions |
|---|---|---|---|---|---|---|---|
| `/` | `app/page.tsx` | launcher dashboard | none | metrics + schema cards + CTAs | `listSchemas`, `listRecords`, `listSyncCenterData` | none | public |
| `/playground` | `app/playground/page.tsx` | schema browser | none | schema cards and quick links | `listSchemas` | none | public |
| `/flow/[schemaId]` | `app/flow/[schemaId]/page.tsx` | flow session host | `schemaId`, optional `token` query | host + `FlowRunner` | `getSchema`, `getRecordByToken` | none directly | public/token modes by schema intent |
| `/inbox` | `app/inbox/page.tsx` | record review listing | optional query `schemaId` | `RecordInbox` | `listSchemas`, `listRecords` | none | public currently |
| `/record/[recordId]` | `app/record/[recordId]/page.tsx` | record detail/actions | `recordId` | `RecordDetail` | `getRecordById`, `listRecordSubresources`, `getSchema` | action calls happen client-side | public currently |
| `/sync` | `app/sync/page.tsx` | dispatch/sync monitor | none | `SyncCenter` | `listSyncCenterData` | retry calls happen client-side | public currently |

## API routes

| Path | File | Purpose | Inputs | Outputs | Services/modules | Side effects |
|---|---|---|---|---|---|---|
| `GET /api/schemas` | `app/api/schemas/route.ts` | expose schema and adapter metadata | none | `{schemas, adapters}` | `listSchemas`, `listAdapters`, bootstrap | ensures record types bootstrapped |
| `GET /api/records` | `app/api/records/route.ts` | list records | query: `schemaId`, `query`, `state` | `{records}` | `listRecords` | none |
| `POST /api/records` | `app/api/records/route.ts` | create record | body: `schemaId,title?,fields?,stepId?,submit?`; headers for actor | `{record}` | `createRecord`, `getActorFromHeaders` | DB create: record + submission + sync event |
| `GET /api/records/[recordId]` | `app/api/records/[recordId]/route.ts` | fetch record + subresources | `recordId` | `{record, submissions, attachments, dispatchJobs, syncEvents}` | `getRecordById`, `listRecordSubresources` | none |
| `PATCH /api/records/[recordId]` | `app/api/records/[recordId]/route.ts` | update fields/state | `recordId`, body `fields,stepId?,state?`, actor headers | `{record}` | `updateRecord` | DB update + submission + inbound sync event |
| `POST /api/records/[recordId]/action` | `app/api/records/[recordId]/action/route.ts` | execute schema action | body `actionId,note?,payload?`, actor headers | action result object | `applyRecordAction` | may update record state, create submission, sync event, dispatch jobs |
| `POST /api/records/[recordId]/attachments` | `app/api/records/[recordId]/attachments/route.ts` | upload attachment metadata + file write | multipart `file` + actor headers | `{attachment}` | `addAttachmentMetadata` + fs write | writes file under `storage/attachments`, creates attachment + sync event |
| `GET /api/records/token/[token]` | `app/api/records/token/[token]/route.ts` | token lookup with details | `token` | `{record,...subresources}` | `getRecordByToken`, `listRecordSubresources` | none |
| `PATCH /api/records/token/[token]` | `app/api/records/token/[token]/route.ts` | update by token | `token`, body `fields,stepId?,state?`, actor headers | `{record}` | token lookup + `updateRecord` | DB update + submission + inbound sync event |
| `GET /api/sync/events` | `app/api/sync/events/route.ts` | sync center aggregate | none | `{events,jobs}` | `listSyncCenterData` | none |
| `POST /api/sync/jobs/[jobId]/retry` | `app/api/sync/jobs/[jobId]/retry/route.ts` | retry failed dispatch | `jobId` + actor headers | retry result | `retryDispatchJob` | updates dispatch job; creates submission + sync event |

### API trust model currently
- Actor context is derived from request headers (`x-actor-role`, etc.) in `src/lib/request-context.ts`.
- This is template-ready, not secure auth.

---

# 6. Component map

## Layout and shell components

### `components/layout/ambient-backdrop.tsx`
- Responsibility: animated atmospheric background (motion orbs).
- Type: presentational with motion.
- Used by: `app/layout.tsx`.
- Business logic: none.
- Reusability: high (visual primitive).

### `components/layout/app-frame.tsx`
- Responsibility: bridge server layout to pathname-aware client shell.
- Type: stateful (reads current route via `usePathname`).
- Used by: `app/layout.tsx`.

### `components/layout/app-shell.tsx`
- Responsibility: global navigation/header + page slot.
- Type: presentational with route-aware active state.
- Composes: `Button`, `Link`.
- Business logic: route matching for active nav and fixed quick links.

## Product components

### `components/flow/flow-runner.tsx`
- Responsibility: schema-driven multi-step form execution and record persistence.
- Type: strongly stateful client component.
- Inputs: `schema`, optional `initialRecord`.
- Internal logic:
  - current step and progress
  - field rendering per `FieldKind`
  - conditional visibility checks
  - per-step validation
  - create/update submit logic
  - attachment upload flow
- Composes: `Surface`, `Button`, `Input`, `Select`, `Textarea`, `Badge`.

### `components/records/record-inbox.tsx`
- Responsibility: browse/filter/select records.
- Type: stateful client component (view/query/filter state).
- Inputs: `records`, `schemas`.
- Logic: client-side filtering and list/grid presentation.
- Composes: `Surface`, `Input`, `Button`, `Badge`.

### `components/records/record-detail.tsx`
- Responsibility: full record inspection and action execution UI.
- Type: stateful client component.
- Inputs: `record`, `schema`, `submissions`, `attachments`, `dispatchJobs`, `syncEvents`.
- Logic:
  - compute available actions by role+state
  - execute actions via API
  - feedback + refresh
- Composes: `Surface`, `Badge`, `Button`.

### `components/sync/sync-center.tsx`
- Responsibility: monitor dispatch/sync and trigger retries.
- Type: stateful client component.
- Inputs: `jobs`, `events`.
- Logic: retry API calls and feedback.
- Composes: `Surface`, `Badge`, `Button`.

## UI primitives

### `components/ui/button.tsx`
- Reusable button with variants (`primary`, `secondary`, `ghost`, `danger`).
- Presentational.

### `components/ui/input.tsx`, `select.tsx`, `textarea.tsx`
- Reusable form controls.
- Presentational.

### `components/ui/badge.tsx`
- Reusable status/category badge with tone variants.
- Presentational.

### `components/ui/surface.tsx`
- Reusable glass panel/card with optional title/subtitle/actions.
- Presentational.

## Parent/child structure (simplified)

```text
RootLayout
  -> AmbientBackdrop
  -> AppFrame
      -> AppShell
          -> page route component
              -> product component(s)
                  -> UI primitives
```

---

# 7. Dependency map

| Dependency | Why it exists | Where used | Category | Usage status |
|---|---|---|---|---|
| `next` | app router pages + API routes + server rendering | `app/**`, route handlers, navigation helpers | Core runtime | Core and heavily used |
| `react` / `react-dom` | UI rendering and client components | all components | Core runtime | Core and heavily used |
| `typescript` | strict typed codebase | whole project | Core dev | Core |
| `tailwindcss` + `postcss` + `autoprefixer` | utility styling and tokenized UI | `globals.css`, component classNames, config | Core styling | Core and heavily used |
| `framer-motion` | subtle animations (backdrop, flow transitions/progress) | `ambient-backdrop.tsx`, `flow-runner.tsx` | UX/cosmetic-functional | Used meaningfully |
| `@prisma/client` + `prisma` | persistence abstraction over SQLite | `db.ts`, `prisma-store.ts`, `prisma/*` | Core data | Core and heavily used |
| SQLite (via Prisma datasource) | local persistence database | `prisma/schema.prisma`, `.env` | Core storage | Core |
| `zod` | runtime payload validation per step | `core/validation.ts` | Core data integrity | Used but narrow scope |
| `lucide-react` | iconography in all major surfaces | pages/components | Cosmetic/UX | Heavily used |
| `clsx` + `tailwind-merge` | className composition helper (`cn`) | `utils.ts`, all UI primitives | Utility | Core utility |
| `vitest` | unit/service tests | `tests/external-template.test.ts` | Testing | Used |
| `tsx` | run prisma seed in TS | script `prisma:seed` | Tooling | Used |
| `@types/node/react/react-dom` | TS typings | compile/test | Tooling | Used |

### Underused / absent relative to README claims
- README says “shadcn/ui”; actual implementation is shadcn-style custom primitives, not official shadcn package.
- No dedicated HTTP client (uses native `fetch`).
- No auth/session dependency.
- No upload SDK/storage provider.

---

# 8. Data and state map

## Schema and model source
- Registry: `src/lib/core/schema-registry.ts`.
- Canonical types: `src/lib/core/types.ts`.
- State transitions: `src/lib/core/state.ts`.
- Field visibility rules: `src/lib/core/visibility.ts`.
- Step validation: `src/lib/core/validation.ts`.

## State model (record lifecycle)
Defined states:
- `draft`
- `submitted`
- `in_review`
- `awaiting_update`
- `approved`
- `rejected`
- `dispatched`
- `synced`
- `failed`

`canTransition` in `core/state.ts` enforces allowed transitions.

## Storage model
- Store interface: `src/lib/store/types.ts` (`ExternalStore`).
- Runtime store selection: `src/lib/store/index.ts`.
  - default: `PrismaExternalStore`
  - test mode: `MemoryExternalStore` when `EXTERNAL_TEMPLATE_STORE=memory` or via test injection.
- Prisma schema entities:
  - `Actor`, `RecordType`, `ExternalRecord`, `Submission`, `Attachment`, `DispatchJob`, `SyncEvent`.

## Request context model
- `getActorFromHeaders()` reads actor role/id/auth/token from headers.
- Used in mutating APIs to scope action eligibility and audit payload.

## UI -> API -> Service -> Store flow

### Create/Update flow
```text
FlowRunner
  -> POST /api/records or PATCH /api/records/[id]
    -> services/records.ts (validate + transition checks)
      -> store.createRecord/updateRecord
      -> store.createSubmission
      -> store.createSyncEvent (inbound)
  -> UI updates recordId/token/state
```

### Action/dispatch flow
```text
RecordDetail
  -> POST /api/records/[id]/action
    -> services/actions.applyRecordAction
      -> state/action availability checks
      -> (dispatch action) store.createDispatchJob + adapter.dispatch + update job + sync events + set state
      -> (non-dispatch action) set state + submission + outbound sync event
```

### Retry flow
```text
SyncCenter
  -> POST /api/sync/jobs/[jobId]/retry
    -> services/actions.retryDispatchJob
      -> adapter.dispatch + job updates + submission + sync event
```

## Token-based access
- `ExternalRecord.secureToken` generated with `randomToken`.
- Token lookup/update endpoints: `GET/PATCH /api/records/token/[token]`.
- Also used in flow route query for resume.
- No expiry/revocation policy implemented.

## Sync/dispatch representation
- Dispatch execution tracked in `DispatchJob` with `status`, `attempts`, `response`, `error`.
- Sync visibility tracked in `SyncEvent` with `direction`, `status`, `summary`, `payload`, `error`.

---

# 9. Adapter and integration map

## Adapter registry
- `src/lib/adapters/index.ts`
- Registered adapters:
  - `LocalAdapter`
  - `RestAdapter`
  - `WebhookAdapter`

## Adapter details

### LocalAdapter
- File: `src/lib/adapters/local-adapter.ts`
- Purpose: local success-path dispatch simulation.
- Direction: `both`.
- Real vs demo: demo-real (real code path, local-only payload echo).
- Config/env: none.
- Retry behavior: supported through generic retry pipeline.
- Local viability: works out of the box.

### RestAdapter
- File: `src/lib/adapters/rest-adapter.ts`
- Purpose: outbound HTTP POST to configured REST endpoint.
- Direction: `both`.
- Real vs demo: real integration boundary with env dependency.
- Env required: `EXTERNAL_INTERACTION_REST_ENDPOINT`.
- Payload: `buildOutboundPayload`.
- Failure handling:
  - missing env -> failed response
  - fetch exception -> failed response
  - non-2xx -> failed response with HTTP status

### WebhookAdapter
- File: `src/lib/adapters/webhook-adapter.ts`
- Purpose: outbound webhook POST with template source header.
- Direction: `outbound`.
- Real vs demo: real integration boundary with env dependency.
- Env required: `EXTERNAL_INTERACTION_WEBHOOK_URL`.
- Payload: `buildOutboundPayload`.
- Failure handling same pattern as REST adapter.

## Transform layer
- File: `src/lib/adapters/transform.ts`
- `buildOutboundPayload` composes normalized payload with record/action/schema metadata and tags.

## Attachment integration point
- API writes file binary to local disk under `storage/attachments`.
- Metadata stored in `Attachment` table.
- No retrieval/serve endpoint currently provided.

## Inbound/outbound scope status
- Inbound: implemented via record create/update APIs and token routes.
- Outbound: implemented via dispatch actions and retry flow.
- External config needed for non-local outbound targets.

---

# 10. Schema/example map

## `service_request`
- Schema id: `service_request`
- Purpose: externally submitted service operation request lifecycle.
- Steps: `requester`, `context`
- Access mode: `public`
- Key fields:
  - `request_title`, `request_description`, `request_priority`, requester identity, `needs_attachment`, `attachments`
- Actions: `confirm`, `request_changes`, `approve`, `dispatch`
- Demonstrates:
  - conditional file field visibility
  - review/approve/dispatch lifecycle
  - webhook outbound binding
- Limitations: dispatcher success depends on env webhook endpoint.
- Routes/components/services: `/flow/service_request`, inbox/detail/sync, records/actions services.

## `approval_packet`
- Schema id: `approval_packet`
- Purpose: token-friendly approval workflow with explicit decision actions.
- Steps: `packet`, `decision`
- Access mode: `token`
- Key fields: packet context + risk/compliance/notes.
- Actions: `approve`, `reject`, `request_changes`, `acknowledge`
- Demonstrates:
  - token-oriented lifecycle
  - role-gated decisions
  - non-dispatch and REST-bound action context
- Limitations: token security policy is basic lookup only.
- Routes/components/services: `/flow/approval_packet`, token API routes, detail action panel.

## `inspection_checklist`
- Schema id: `inspection_checklist`
- Purpose: authenticated-style checklist capture + follow-up + dispatch.
- Steps: `meta`, `checks`
- Access mode: `authenticated`
- Key fields: site meta, condition score, follow-up toggle, findings, photo attachments.
- Actions: `confirm`, `request_changes`, `dispatch`
- Demonstrates:
  - numeric + checkbox + conditional file field
  - local dispatch success path
- Limitations: authenticated mode is declarative; real auth enforcement not implemented.
- Routes/components/services: `/flow/inspection_checklist`, detail, sync center.

---

# 11. Test coverage map

## Existing tests
- File: `apps/external_interaction_template/tests/external-template.test.ts`
- Runner: Vitest (node environment)

## What is covered
1. Schema registry basics (count, expected fields/steps exist).
2. Step validation for required fields (`validateStepPayload`).
3. Conditional field visibility (`isFieldVisible`).
4. Record creation/submission path (`createRecord`, `listRecords`).
5. Token lookup and update path (`getRecordByToken`, `updateRecord`).
6. Record preview field builder (`recordPreviewFields`).
7. Action availability by role/state (`isActionAvailable`).
8. Dispatch success path via local adapter.
9. Retryable sync state when webhook dispatch fails due missing env.
10. Schema switching across all examples using first step synthetic payloads.

## Critical gaps
- No UI interaction tests (no Playwright/RTL flows).
- No API route integration tests (status codes, malformed payloads, auth headers).
- No attachment upload tests (filesystem effects).
- No explicit transition matrix tests across all states.
- No persistence parity tests between memory and Prisma stores.
- No retry idempotency/concurrency tests.

## Test reality alignment
- Strong on service-level correctness.
- Weak on real UX contract and route-level behavior.

---

# 12. Visual structure map

## Navigation model
- Persistent top glass shell (`AppShell`) with 4 nav links + 2 quick actions.

## Page shell
- Global dark canvas + animated ambient orbs + grid fade overlay.
- Main content constrained to `max-w-7xl` with consistent paddings.

## Layout rhythm
- Surfaces (`Surface`) are rounded, translucent cards used across all pages.
- Page composition is card-grid heavy but generally consistent.

## Action hierarchy
- Primary actions use accent-toned `Button primary`.
- Secondary/ghost actions clearly differentiated.

## Typography
- Inter/system stack.
- Clear title/subtitle hierarchy in surfaces.

## Motion usage
- Ambient backdrop motion always on.
- Flow step transitions and progress bar motion via framer-motion.

## Main visual strengths
- Coherent visual language across routes.
- Reusable primitives keep style consistent.
- Good readability in dark mode.

## Main visual weaknesses
- Many surfaces produce "card-in-card" density in detail/flow pages.
- No explicit reduced-motion preference handling.
- Sync/inbox controls are functional but not deeply contextual.
- Some controls (native select/checkbox) still feel less premium than custom counterparts.

## Where UI still feels prototype-like
- Role simulation dropdown in detail page (demo behavior) is product-internal and not user-safe.
- Attachment UX is minimal (metadata-focused).
- Some empty states and status messaging are concise but generic.

---

# 13. Implementation quality assessment

| Dimension | Score (1-10) | Justification |
|---|---:|---|
| architecture clarity | 8 | Clear layering: route -> service -> store -> adapter; typed core model is coherent. |
| reusability | 8 | Schema-driven model + store and adapter interfaces are reusable across domains. |
| UX clarity | 7 | Main journeys are understandable, but token/auth/action trust model can confuse real users. |
| visual polish | 7 | Good baseline design system; still card-dense and partially template-looking in controls. |
| extensibility | 8 | New schemas/adapters can be added with low friction. |
| data modeling | 8 | Neutral model is solid; lifecycle and audit entities are sensible. |
| external integration readiness | 6 | Adapter boundaries exist, but production concerns (auth, retries, resiliency) are basic. |
| test confidence | 7 | Service-level behavior covered; UI/API integration coverage is limited. |
| maintainability | 8 | File boundaries and responsibilities are mostly clean and consistent. |

---

# 14. Gaps, dead zones, and ambiguity

1. Header-based role trust is insecure by design.
   - File: `src/lib/request-context.ts`
   - Risk: clients can spoof privileged role headers.

2. Token flows lack lifecycle controls.
   - Files: token route + record model.
   - Missing: expiry, revocation, one-time use, scoped permissions.

3. Attachment pipeline is one-way.
   - File: `app/api/records/[recordId]/attachments/route.ts`
   - Files are saved and metadata stored, but no retrieval endpoint/storage abstraction.

4. Action comment requirements are backend-enforced but not always prompted in UI.
   - `applyRecordAction` can require `note`; detail UI currently posts only `actionId`.

5. Dispatch retry policy is manual and simplistic.
   - No scheduler/backoff/dead-letter/concurrency guard.

6. Draft resume UX depends on token knowledge.
   - No first-class “my drafts” actor-based list.

7. `editableInStates` exists in field model but is not actively enforced in FlowRunner.
   - Potential mismatch between schema intent and runtime behavior.

8. Flow access mode (`public`, `authenticated`, `token`) is descriptive more than enforced.
   - No route/API guards tied to this metadata.

9. API error contracts are basic strings.
   - Useful for template, but not standardized problem detail payloads.

10. README can overstate stack specifics.
    - Says shadcn/ui; implementation uses custom shadcn-style primitives.

---

# 15. Recommended next decisions

1. Stabilize access/security contract first.
   - Define real auth source of truth, role derivation, and token policy.

2. Define action input contract.
   - Add structured action forms (e.g., required comments) aligned to backend rules.

3. Decide attachment strategy.
   - Keep local for demo, but define storage abstraction + secure retrieval path.

4. Enforce schema access modes at route/API boundary.
   - Move from metadata-only to actual guard behavior.

5. Harden retry/dispatch execution model.
   - Add backoff, idempotency keys, and concurrency protections.

6. Expand tests to route and UI interaction layers.
   - Add API handler tests and core UI journey coverage.

7. Clarify draft/resume user experience.
   - Add actor-scoped draft listing so resume is not token-only.

8. Decide whether `editableInStates` and role-level field permissions are required now.
   - If yes, enforce in renderer + server update validation.

9. Establish integration environment contract.
   - Formalize required env vars, payload guarantees, and adapter health diagnostics.

10. Only then proceed to visual/UX redesign.
   - Keep behavior contracts stable before major redesign to avoid rework.
