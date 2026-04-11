from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Optional

SCRIPT_NAME = "inject_external_interaction_template_maps.py"
DEFAULT_APP_ROOT = Path(r"F:\repos\hitech-os\apps\external_interaction_template")

DOCS_DIR = Path("docs") / "architecture"
TRACKING_DIR = DOCS_DIR / "_tracking"
README_NAME = "README.md"

README_START = "<!-- EXTERNAL_INTERACTION_TEMPLATE:ARCHITECTURE_MAPS:START -->"
README_END = "<!-- EXTERNAL_INTERACTION_TEMPLATE:ARCHITECTURE_MAPS:END -->"

FRONTEND_VISUAL_MAP = r"""# Frontend Visual Map
**Project:** `apps/external_interaction_template`  
**Scope:** visual structure, safe edit points, and “where do I touch this without detonating the whole surface?”

## 1. Frontend truth in one breath

This app is a **Next.js App Router** surface with a global frame and a reusable visual system:

- `app/layout.tsx` mounts the global shell
- `components/layout/ambient-backdrop.tsx` paints the moving glassy backdrop
- `components/layout/app-frame.tsx` bridges pathname + accessibility into the shell
- `components/layout/app-shell.tsx` decides the current UI area and the chrome around every page
- pages under `app/` render the actual business surfaces
- `components/ui/*` gives the reusable atoms and cards
- `src/lib/ui/runtime.ts` is the visual control brain for area, density, preset, role, motion, contrast, and brand

That means most visual changes fall into **five buckets**:

1. Global shell and page chrome
2. Background and motion mood
3. Runtime visual context
4. Feature surfaces
5. Shared UI primitives

---

## 2. Frontend map

```mermaid
flowchart TD
  A[app/layout.tsx] --> B[AmbientBackdrop]
  A --> C[AppFrame]

  C --> D[AppShell]
  D --> E[src/lib/ui/runtime.ts]

  D --> F[Launcher page]
  D --> G[Inbox page]
  D --> H[Flow page]
  D --> I[Record page]
  D --> J[Sync page]
  D --> K[Playground page]

  F --> L[PageHeader]
  F --> M[StatCard]
  F --> N[Surface]

  G --> O[RecordInbox]
  I --> P[RecordDetail]
  H --> Q[FlowRunner]
  J --> R[SyncCenter]

  O --> S[FilterPills]
  O --> T[InboxRecordCard]
  P --> U[ActivityTimeline]
  P --> V[StateBadge]
  Q --> W[Input / Select / Textarea / Button]
  R --> X[Badge / Button / Surface]

  D --> Y[globals.css]
  N --> Y
  M --> Y
  L --> Y
```

---

## 3. Safe visual edit points

## A. Global shell and chrome

### File
- `components/layout/app-shell.tsx`

### Controls
- top nav
- “current surface” summary card
- role / density / preset / motion / contrast chips
- per-area copy
- area switching by pathname

### Touch this when
- you want the header to look different
- you want different top actions
- you want new chrome, chips, or panel arrangement
- you want page personality to change by area

### High-value functions / blocks
- `resolveArea(currentPath)`
- `areaDescription(area)`
- `AppShell(...)`

### Risk
Medium. This file wraps basically every page.

---

## B. Backdrop and motion atmosphere

### File
- `components/layout/ambient-backdrop.tsx`

### Controls
- radial glows
- animated blobs
- reduced-motion behavior
- background mood

### Touch this when
- you want the app to feel calmer, shinier, darker, or less animated
- you want to reduce visual noise
- you want to tune the premium/glass feel

### Risk
Low to medium. Mostly visual, but easy to make the UI too loud.

---

## C. Runtime visual contract

### File
- `src/lib/ui/runtime.ts`

### Controls
- `area`
- `density`
- `preset`
- `role`
- `motion`
- `contrast`
- `brandProfile`

### The real power knobs
- `UI_AREAS`
- `UI_DENSITIES`
- `UI_PRESETS`
- `UI_ROLES`
- `UI_MOTION_PREFERENCES`
- `UI_CONTRAST_PREFERENCES`
- `BRAND_PROFILES`
- `createRuntimeUiContext(...)`
- `runtimeDataAttributes(...)`
- `runtimeSpacing(...)`
- `runtimeMotionClass(...)`
- `runtimeContrastClass(...)`
- `runtimeShellClass(...)`

### Touch this when
- you want visual behavior to vary by page type
- you want compact vs comfortable vs spacious tuning
- you want brand presets to change globally
- you want accessibility-aware styling changes

### Risk
Medium to high. This is the **frontend control brain**.

---

## D. Feature surfaces

### 1) Launcher
**Files**
- `app/page.tsx`
- `components/ui/page-header.tsx`
- `components/ui/stat-card.tsx`
- `components/ui/surface.tsx`

**Controls**
- hero copy
- stat tiles
- available flow cards
- CTA layout

**Touch this when**
- you want the homepage/dashboard to change

---

### 2) Inbox
**Files**
- `app/inbox/page.tsx`
- `components/records/record-inbox.tsx`
- `components/records/inbox-record-card.tsx`

**Controls**
- triage layout
- filters
- queue cards
- scan density

**Touch this when**
- you want review ergonomics to change

---

### 3) Flow runner
**Files**
- `app/flow/[schemaId]/page.tsx`
- `components/flow/flow-runner.tsx`

**Controls**
- stepper
- save/submit notices
- field rendering
- token resume UX
- progress summary
- attachment handling UI

**Touch this when**
- you want external-user form UX to change

**Important note**
This surface mixes **visual composition** and **client behavior**. Treat it carefully.

---

### 4) Record detail
**Files**
- `app/record/[recordId]/page.tsx`
- `components/records/record-detail.tsx`
- `components/records/activity-timeline.tsx`

**Controls**
- detail page layout
- timeline
- action area
- status presentation
- attachments / dispatch / sync sections

**Touch this when**
- you want operator review detail to change

---

### 5) Sync center
**Files**
- `app/sync/page.tsx`
- `components/sync/sync-center.tsx`

**Controls**
- metrics
- retry controls
- event list
- failed-job visibility
- filter pills

**Touch this when**
- you want operational visibility to change

---

### 6) Schema playground
**File**
- `app/playground/page.tsx`

**Controls**
- side-by-side schema cards
- design-system validation surface

**Touch this when**
- you want a safer place to compare schema visual differences

---

## E. Shared UI primitives

### Files
- `components/ui/button.tsx`
- `components/ui/badge.tsx`
- `components/ui/input.tsx`
- `components/ui/select.tsx`
- `components/ui/textarea.tsx`
- `components/ui/surface.tsx`
- `components/ui/page-header.tsx`
- `components/ui/stat-card.tsx`
- `components/ui/state-badge.tsx`
- `components/ui/status-panel.tsx`
- `components/ui/filter-pills.tsx`

### Touch this when
- you want a broad, systematic visual change
- the same issue appears in multiple screens
- spacing, borders, shadow, typography, or variants feel off everywhere

### Risk
High leverage. Tiny changes here ripple across the app.

---

## 4. If you want X, touch Y

| Goal | First file to touch | Second place to inspect |
|---|---|---|
| Change header / top chrome | `components/layout/app-shell.tsx` | `src/lib/ui/runtime.ts` |
| Change backdrop glow / motion | `components/layout/ambient-backdrop.tsx` | `app/globals.css` |
| Change density / contrast / preset logic | `src/lib/ui/runtime.ts` | `components/layout/app-shell.tsx` |
| Change launcher cards and stats | `app/page.tsx` | `components/ui/stat-card.tsx` |
| Change inbox review UX | `components/records/record-inbox.tsx` | `components/records/inbox-record-card.tsx` |
| Change multi-step form UX | `components/flow/flow-runner.tsx` | `app/flow/[schemaId]/page.tsx` |
| Change record detail experience | `components/records/record-detail.tsx` | `components/records/activity-timeline.tsx` |
| Change sync dashboard | `components/sync/sync-center.tsx` | `components/ui/filter-pills.tsx` |
| Change broad card styling | `components/ui/surface.tsx` | `app/globals.css` |
| Change buttons globally | `components/ui/button.tsx` | screens that use variant props |

---

## 5. Safe edit order

When changing visuals, follow this order:

1. **Copy / labels / composition props**
2. **Shared component variant**
3. **Runtime visual rules**
4. **Global shell**
5. **Global CSS**
6. **Behavior inside client components**

That order keeps the blast radius smaller.

---

## 6. Frontend danger zones

These are the places where visual edits can secretly become logic bugs:

### `components/flow/flow-runner.tsx`
Why dangerous:
- validation
- persistence
- attachment upload
- step navigation
- draft vs submit logic

### `components/sync/sync-center.tsx`
Why dangerous:
- retry button wires to backend
- filters are stateful
- refresh behavior matters

### `components/records/record-detail.tsx`
Why dangerous:
- action buttons likely reflect state availability
- audit data needs consistent ordering and visibility

### `src/lib/ui/runtime.ts`
Why dangerous:
- this changes the visual contract app-wide

---

## 7. Recommended workflow for frontend changes

### Cosmetic-only
- change feature page component first
- then shared primitive only if repetition appears

### System-wide style
- change UI primitive or runtime contract first
- then inspect launcher, inbox, flow, record, sync surfaces

### Big redesign
- prototype in `playground`
- validate `launcher`
- validate `flow`
- validate `record`
- validate `sync`

That sequence catches most ugly regressions before production.

---

## 8. Suggested file ownership map

| Layer | Files |
|---|---|
| Global frame | `app/layout.tsx`, `components/layout/app-frame.tsx`, `components/layout/app-shell.tsx` |
| Ambient mood | `components/layout/ambient-backdrop.tsx`, `app/globals.css` |
| Visual runtime contract | `src/lib/ui/runtime.ts` |
| Launcher | `app/page.tsx` |
| Inbox | `app/inbox/page.tsx`, `components/records/record-inbox.tsx` |
| Flow | `app/flow/[schemaId]/page.tsx`, `components/flow/flow-runner.tsx` |
| Record detail | `app/record/[recordId]/page.tsx`, `components/records/record-detail.tsx` |
| Sync | `app/sync/page.tsx`, `components/sync/sync-center.tsx` |
| System validation | `app/playground/page.tsx` |
| Shared atoms | `components/ui/*` |

---

## 9. Bottom line

If the question is:

- **“Where do I change the shell?”** → `app-shell.tsx`
- **“Where do I change the mood?”** → `ambient-backdrop.tsx`
- **“Where do I change density / preset / contrast?”** → `runtime.ts`
- **“Where do I change a business surface?”** → the page component + its feature component
- **“Where do I change the design system?”** → `components/ui/*`

That is the cleanest frontend map for moving fast without editing blind.
"""
BACKEND_FLOW_MAP = r"""# Backend Flow Map
**Project:** `apps/external_interaction_template`  
**Scope:** actual request flow, service boundaries, storage model, adapters, and safe backend edit points.

## 1. Backend truth in one breath

This app is a **schema-driven workflow backend** wrapped by Next.js route handlers.

The backend shape is:

1. App Route receives request
2. Request actor is derived from headers or token context
3. Service layer loads schema + validates rules
4. Bootstrap ensures schemas exist in storage
5. Store layer reads/writes records, submissions, attachments, jobs, sync events
6. Adapter layer handles outbound dispatch
7. Prisma persists the durable version when not using memory store

So the real backend pillars are:

- `app/api/*` route handlers
- `src/lib/request-context.ts`
- `src/lib/services/*`
- `src/lib/core/*`
- `src/lib/store/*`
- `src/lib/adapters/*`
- `prisma/schema.prisma`

---

## 2. Backend map

```mermaid
flowchart TD
  A[HTTP request] --> B[Next.js route handler]
  B --> C[request-context]
  B --> D[services layer]

  D --> E[ensureTemplateBootstrap]
  E --> F[schema-registry]
  E --> G[store.ensureRecordType]

  D --> H[records service]
  D --> I[actions service]

  H --> J[validation]
  H --> K[state rules]
  H --> L[visibility]
  H --> M[store layer]

  I --> K
  I --> N[adapter registry]
  I --> M

  M --> O[memory store]
  M --> P[prisma store]

  P --> Q[Prisma client]
  Q --> R[SQLite database]

  I --> S[local adapter]
  I --> T[rest adapter]
  I --> U[webhook adapter]

  M --> V[submissions]
  M --> W[attachments]
  M --> X[dispatch jobs]
  M --> Y[sync events]
```

---

## 3. Actual backend entrypoints

## A. Route handlers

### Files
- `app/api/schemas/route.ts`
- `app/api/records/route.ts`
- `app/api/records/[recordId]/route.ts`
- `app/api/records/[recordId]/action/route.ts`
- `app/api/records/[recordId]/attachments/route.ts`
- `app/api/records/token/[token]/route.ts`
- `app/api/sync/events/route.ts`
- `app/api/sync/jobs/[jobId]/retry/route.ts`

### Responsibility
- parse request
- gather URL params / JSON / form-data
- derive actor
- call service layer
- normalize HTTP responses

### Safe rule
Keep route handlers thin. Business logic belongs below them.

---

## B. Actor / request context

### File
- `src/lib/request-context.ts`

### Responsibility
- read `x-actor-role`
- read `x-authenticated`
- read `x-actor-id`
- read `x-actor-label`
- read `x-flow-token`
- normalize role into allowed actor values

### Touch this when
- access context changes
- you need new header-based identity metadata
- token behavior changes

### Risk
High. Small edits here change authorization flavor across many routes.

---

## C. Bootstrap / schema registration

### File
- `src/lib/services/bootstrap.ts`

### Responsibility
- ensure every schema in the registry exists in storage
- avoid duplicate bootstrapping within a process

### Key function
- `ensureTemplateBootstrap()`

### Touch this when
- adding initialization behavior
- adding storage-level schema metadata
- changing how startup registration works

### Risk
Medium. Safe if kept idempotent.

---

## D. Records service

### File
- `src/lib/services/records.ts`

### Responsibility
- list records
- get record by id
- get record by token
- create record
- update record
- add attachment metadata
- collect record subresources

### Important behavior
- calls `ensureTemplateBootstrap()`
- loads schema from registry
- validates the active step payload
- creates submissions
- creates inbound sync events
- issues secure tokens on create

### Touch this when
- create/update rules change
- submission lifecycle changes
- attachment metadata behavior changes
- inbound event behavior changes

### Risk
High. This is the main business workflow pipe.

---

## E. Actions service

### File
- `src/lib/services/actions.ts`

### Responsibility
- apply stateful actions like approve, reject, dispatch
- enforce action availability
- create dispatch jobs
- call adapters
- write outbound sync events
- retry failed jobs
- reconcile state after success/failure

### Touch this when
- approval behavior changes
- dispatch behavior changes
- retry logic changes
- sync status semantics change

### Risk
Very high. This is where workflow state and outbound integration shake hands.

---

## F. Core workflow rules

### Files
- `src/lib/core/schema-registry.ts`
- `src/lib/core/state.ts`
- `src/lib/core/validation.ts`
- `src/lib/core/visibility.ts`
- `src/lib/core/record-view.ts`
- `src/lib/core/types.ts`

### Responsibilities

#### `schema-registry.ts`
Defines the workflow universe:
- schemas
- steps
- fields
- actions
- views
- inbound/outbound adapter bindings

#### `state.ts`
Defines:
- legal state transitions
- action availability by role and state

#### `validation.ts`
Defines:
- per-step validation
- required fields
- coercion by field kind

#### `visibility.ts`
Defines:
- conditional field visibility
- role-based field visibility

#### `record-view.ts`
Defines:
- inbox sort behavior
- preview fields
- status labels / descriptions

### Touch this when
- product rules change
- schemas evolve
- field logic changes
- review logic changes

### Risk
Very high. These files are the backend constitution.

---

## G. Store layer

### Files
- `src/lib/store/index.ts`
- `src/lib/store/memory-store.ts`
- `src/lib/store/prisma-store.ts`
- `src/lib/store/types.ts`

### Responsibility
Abstract persistence behind a common store interface.

### Store selection
- `EXTERNAL_TEMPLATE_STORE=memory` → memory store
- otherwise → Prisma store

### Touch this when
- persistence behavior changes
- tests need different storage semantics
- audit data shape changes

### Risk
High. Easy place to create hidden regressions in data behavior.

---

## H. Adapter layer

### Files
- `src/lib/adapters/index.ts`
- `src/lib/adapters/local-adapter.ts`
- `src/lib/adapters/rest-adapter.ts`
- `src/lib/adapters/webhook-adapter.ts`
- `src/lib/adapters/transform.ts`
- `src/lib/adapters/types.ts`

### Responsibility
Handle outbound dispatch.

### Built-ins
- `local`
- `rest`
- `webhook`

### Behavior map
- `local` succeeds locally and stores payload-like response
- `rest` posts to `EXTERNAL_INTERACTION_REST_ENDPOINT`
- `webhook` posts to `EXTERNAL_INTERACTION_WEBHOOK_URL`

### Touch this when
- integration shape changes
- headers/payload mapping change
- you add a new external system adapter

### Risk
Medium to very high depending on environment coupling.

---

## 4. Data model map

### Prisma models
- `Actor`
- `RecordType`
- `ExternalRecord`
- `Submission`
- `Attachment`
- `DispatchJob`
- `SyncEvent`

### What they really mean

| Model | Purpose |
|---|---|
| `RecordType` | durable registration of schema definitions |
| `ExternalRecord` | the active workflow entity |
| `Submission` | every create/update/action payload event |
| `Attachment` | file metadata tied to a record |
| `DispatchJob` | outbound execution attempt state |
| `SyncEvent` | audit trail of inbound/outbound sync moments |
| `Actor` | optional person/system context |

### Safe mental model
`ExternalRecord` is the center of the galaxy.  
Everything else is orbiting evidence or transport state.

---

## 5. Real request flows

## A. Create record flow

```mermaid
sequenceDiagram
  participant UI as FlowRunner
  participant API as POST /api/records
  participant RC as request-context
  participant SRV as records service
  participant BOOT as bootstrap
  participant CORE as schema + validation
  participant STORE as external store

  UI->>API: schemaId + fields + stepId + submit
  API->>RC: derive actor
  API->>SRV: createRecord(...)
  SRV->>BOOT: ensureTemplateBootstrap()
  SRV->>CORE: getSchema + validateStepPayload
  SRV->>STORE: createRecord
  SRV->>STORE: createSubmission
  SRV->>STORE: createSyncEvent(inbound)
  API-->>UI: created record + secure token
```

---

## B. Update record flow

```mermaid
sequenceDiagram
  participant UI as FlowRunner or token client
  participant API as PATCH /api/records/:id or /token/:token
  participant SRV as records service
  participant CORE as state + validation
  participant STORE as external store

  UI->>API: fields + stepId + desired state
  API->>SRV: updateRecord(...)
  SRV->>STORE: getRecordById / getRecordByToken
  SRV->>CORE: validateStepPayload
  SRV->>CORE: canTransition
  SRV->>STORE: updateRecord
  SRV->>STORE: createSubmission
  SRV->>STORE: createSyncEvent(inbound)
  API-->>UI: updated record
```

---

## C. Dispatch / action flow

```mermaid
sequenceDiagram
  participant UI as Record detail
  participant API as POST /api/records/:id/action
  participant SRV as actions service
  participant CORE as action/state rules
  participant STORE as external store
  participant ADP as adapter

  UI->>API: actionId + note + payload
  API->>SRV: applyRecordAction(...)
  SRV->>STORE: get record
  SRV->>CORE: ensureActionAvailable
  SRV->>STORE: createDispatchJob
  SRV->>ADP: dispatch(...)
  ADP-->>SRV: success or failure
  SRV->>STORE: update job
  SRV->>STORE: set record state
  SRV->>STORE: createSubmission
  SRV->>STORE: createSyncEvent(outbound)
  API-->>UI: result
```

---

## 6. If you want X, touch Y

| Goal | First file to touch | Second place to inspect |
|---|---|---|
| Add a new workflow/schema | `src/lib/core/schema-registry.ts` | `prisma/schema.prisma` only if persistence shape must change |
| Change state transitions | `src/lib/core/state.ts` | tests |
| Change validation rules | `src/lib/core/validation.ts` | `src/lib/core/visibility.ts` |
| Change create/update behavior | `src/lib/services/records.ts` | API route handlers |
| Change action/dispatch behavior | `src/lib/services/actions.ts` | adapter files |
| Change persistence implementation | `src/lib/store/prisma-store.ts` | `src/lib/store/types.ts` |
| Add new outbound integration | `src/lib/adapters/*` | `src/lib/adapters/index.ts` |
| Change actor/header model | `src/lib/request-context.ts` | affected API routes |
| Change attachment persistence | `app/api/records/[recordId]/attachments/route.ts` | `src/lib/services/records.ts` |

---

## 7. Backend danger zones

## `src/lib/core/state.ts`
One tiny state map edit can break approval/dispatch/retry flows.

## `src/lib/services/actions.ts`
This is where:
- role checks
- state checks
- dispatch jobs
- adapter responses
- sync events
all pile into one lane.

## `src/lib/store/prisma-store.ts`
Easy to create partial persistence drift here if payload serialization changes.

## `prisma/schema.prisma`
Schema edits are real migrations, not casual text changes.

## `src/lib/request-context.ts`
Header interpretation bugs can silently change who is allowed to do what.

---

## 8. README status and what is missing

The current README is solid for:

- scope
- stack
- included schemas
- local run commands
- API surface
- adapter model
- schema extension
- security/access model
- tests

What it **does not currently document** in a concrete way:

- frontend change map
- backend dependency / flow map
- change tracking
- rollback workflow
- managed docs section

That is why the injector in this bundle patches a **managed README section** instead of replacing the file.

---

## 9. Bottom line

If the question is:

- **“Where do records actually get created/updated?”** → `src/lib/services/records.ts`
- **“Where do actions and dispatch happen?”** → `src/lib/services/actions.ts`
- **“Where are the workflow rules defined?”** → `src/lib/core/*`
- **“Where is persistence decided?”** → `src/lib/store/index.ts`
- **“Where do external systems get called?”** → `src/lib/adapters/*`
- **“Where do HTTP requests enter?”** → `app/api/*`

That is the clean backend map for changing behavior without spelunking blind through the repo.
"""
CHANGE_TRACKING = r"""# Change Tracking Strategy
**Project:** `apps/external_interaction_template`  
**Goal:** let you touch frontend or backend with a clear rollback point instead of cowboy-editing the repo into the void.

## 1. Is this viable?

Yes. Very viable.

This project is already modular enough to track safely because:

- frontend changes can be isolated to docs + README managed section
- backend rules live in clear modules
- the app already has strong boundaries between routes, services, store, adapters, and schema rules
- the uploaded visual artifacts also suggest a **sidecar / forensics mindset**, which is perfect for change tracking

---

## 2. What this bundle tracks

### Managed docs
- `docs/architecture/FRONTEND_VISUAL_MAP.md`
- `docs/architecture/BACKEND_FLOW_MAP.md`
- `docs/architecture/CHANGE_TRACKING.md`

### Managed README section
- `README.md` only inside a marked block

### Tracking artifacts
- `docs/architecture/_tracking/manifests/*.json`
- `docs/architecture/_tracking/snapshots/*_before.json`
- `docs/architecture/_tracking/snapshots/*_after.json`
- `docs/architecture/_tracking/backups/<run_id>/...`
- `docs/architecture/_tracking/baselines/<baseline_id>/...`
- `docs/architecture/_tracking/LAST_KNOWN_GOOD.json`
- `docs/architecture/_tracking/CHANGELOG_TRACKING.md`

---

## 3. The safety model

## A. Managed section, not full README replacement
The injector only owns a bounded block:

```md
<!-- EXTERNAL_INTERACTION_TEMPLATE:ARCHITECTURE_MAPS:START -->
...managed content...
<!-- EXTERNAL_INTERACTION_TEMPLATE:ARCHITECTURE_MAPS:END -->
```

That means:
- your manual README content stays intact
- reruns are idempotent
- updates are predictable

---

## B. Before / after snapshots
Each run writes:
- a `before` snapshot
- an `after` snapshot
- hashes
- file sizes
- timestamps

That gives you a forensic breadcrumb trail instead of vibes.

---

## C. Run manifest
Each run writes one manifest with:
- `run_id`
- `generated_at_utc`
- `app_root`
- `changed_files`
- `before`
- `after`
- `backups_dir`
- `git_head` if available
- `git_branch` if available

---

## D. Backups
Before the injector overwrites a managed file, it copies the previous version into:

`docs/architecture/_tracking/backups/<run_id>/<relative-path>.bak`

That lets you roll back the latest run even if you did not set a baseline.

---

## E. Baseline / clear point
When you run with `--set-baseline`, the injector creates a known-good checkpoint:

- copies current managed files into `baselines/<baseline_id>/...`
- updates `LAST_KNOWN_GOOD.json`

That becomes your **clear point**.

---

## 4. Recommended workflow

## Normal safe run
1. run `--dry-run`
2. inspect output
3. run real write
4. if happy, run `--set-baseline`

## When experimenting hard
1. set a baseline first
2. make your changes
3. if things go sideways, use `--rollback-baseline`

## When you just want to undo the last injector pass
1. run `--rollback-latest`

---

## 5. Rollback modes

## A. Latest rollback
Use this when:
- the last injector run was bad
- you want to restore the previous state of managed files

Command:
```powershell
$root = 'F:\repos\hitech-os\apps\external_interaction_template'
python "$root\inject_external_interaction_template_maps.py" --app-root "$root" --rollback-latest
```

---

## B. Baseline rollback
Use this when:
- the repo drifted after several edits
- you want to go back to your last known-good checkpoint

Command:
```powershell
$root = 'F:\repos\hitech-os\apps\external_interaction_template'
python "$root\inject_external_interaction_template_maps.py" --app-root "$root" --rollback-baseline
```

---

## 6. What should count as tracked later

Once you want to go beyond docs, the next logical tracked targets are:

### Frontend
- `components/layout/app-shell.tsx`
- `components/layout/ambient-backdrop.tsx`
- `components/flow/flow-runner.tsx`
- `components/records/record-inbox.tsx`
- `components/records/record-detail.tsx`
- `components/sync/sync-center.tsx`
- `src/lib/ui/runtime.ts`

### Backend
- `src/lib/services/records.ts`
- `src/lib/services/actions.ts`
- `src/lib/core/schema-registry.ts`
- `src/lib/core/state.ts`
- `src/lib/core/validation.ts`
- `src/lib/store/prisma-store.ts`
- `app/api/*`

I would not make the injector auto-edit those yet unless you deliberately want a broader managed footprint.

---

## 7. Safe vs dangerous changes

## Safe-ish
- changing docs
- changing README managed section
- changing copy
- changing visual primitives with local validation

## Medium risk
- changing runtime UI presets
- changing inbox/record/sync layout
- changing schema view sections

## High risk
- changing state transitions
- changing validation logic
- changing adapter dispatch logic
- changing Prisma persistence
- changing request-context role normalization

---

## 8. Clear-point rule

A baseline is only valid if:

- docs generated cleanly
- README managed block updated cleanly
- tracked file hashes look sane
- no unexpected files changed
- the app still boots
- at least smoke tests pass

If those conditions are not true, do **not** bless the baseline.

---

## 9. Suggested practical routine

For this repo, the clean routine is:

1. `--dry-run`
2. real apply
3. inspect git diff
4. run tests / smoke check
5. `--set-baseline`

That gives you a crisp, human-readable, machine-restorable clear point.
"""

README_MANAGED_SECTION = r"""
## Architecture maps and safe change workflow

This section is managed by `inject_external_interaction_template_maps.py`.

### Managed docs
- `docs/architecture/FRONTEND_VISUAL_MAP.md`
- `docs/architecture/BACKEND_FLOW_MAP.md`
- `docs/architecture/CHANGE_TRACKING.md`

### Why this exists
These docs give the team:
- a frontend visual map
- a backend flow map
- a change tracking and rollback strategy

### Safe workflow
1. Run the injector in `--dry-run`.
2. Apply the docs for real.
3. Review the git diff.
4. Validate the app or tests.
5. Set a baseline if the result is clean.
""".strip()

MANAGED_FILES = {
    DOCS_DIR / "FRONTEND_VISUAL_MAP.md": FRONTEND_VISUAL_MAP,
    DOCS_DIR / "BACKEND_FLOW_MAP.md": BACKEND_FLOW_MAP,
    DOCS_DIR / "CHANGE_TRACKING.md": CHANGE_TRACKING,
}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def normalize_text(content: str) -> str:
    return content.rstrip() + "\n"


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_rel_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() and path.is_file() else ""


def collect_snapshot(root: Path, paths: Iterable[Path]) -> Dict[str, Dict[str, object]]:
    snapshot: Dict[str, Dict[str, object]] = {}
    for path in paths:
        rel = safe_rel_path(root, path)
        exists = path.exists()
        is_file = path.is_file()
        stat = path.stat() if exists else None
        snapshot[rel] = {
            "exists": exists,
            "is_file": is_file,
            "sha256": sha256_file(path) if is_file else "",
            "size": stat.st_size if stat and is_file else 0,
            "modified_utc": dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc).isoformat() if stat and is_file else None,
        }
    return snapshot


def build_readme_block() -> str:
    return "\n".join([README_START, README_MANAGED_SECTION, README_END]) + "\n"


def upsert_readme_section(existing: str) -> str:
    block = build_readme_block()
    if README_START in existing and README_END in existing:
        start = existing.index(README_START)
        end = existing.index(README_END) + len(README_END)
        updated = existing[:start] + block + existing[end:]
        return normalize_text(updated)

    base = existing.rstrip()
    if not base:
        base = "# External Interaction Template\n"
    updated = f"{base}\n\n{block}"
    return normalize_text(updated)


def write_file(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        return
    ensure_parent(path)
    path.write_text(normalize_text(content), encoding="utf-8")


def copy_backup(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run or not src.exists() or not src.is_file():
        return
    ensure_parent(dst)
    shutil.copy2(src, dst)


def restore_file(src: Path, dst: Path) -> None:
    ensure_parent(dst)
    shutil.copy2(src, dst)


def delete_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def get_git_info(app_root: Path) -> Dict[str, Optional[str]]:
    def run_git(*args: str) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(app_root), *args],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() or None
        except Exception:
            return None

    return {
        "git_branch": run_git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_head": run_git("rev-parse", "HEAD"),
        "git_status_short": run_git("status", "--short"),
    }


def infer_app_root(cli_value: Optional[str]) -> Path:
    if cli_value:
        return Path(cli_value).resolve()

    script_dir = Path(__file__).resolve().parent
    if (script_dir / README_NAME).exists():
        return script_dir
    return DEFAULT_APP_ROOT.resolve()


def latest_manifest_path(tracking_root: Path) -> Optional[Path]:
    manifests_dir = tracking_root / "manifests"
    if not manifests_dir.exists():
        return None
    manifests = sorted(manifests_dir.glob("*_manifest.json"), reverse=True)
    return manifests[0] if manifests else None


def load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rollback_from_manifest(app_root: Path, tracking_root: Path) -> Dict[str, object]:
    manifest_path = latest_manifest_path(tracking_root)
    if manifest_path is None:
        raise FileNotFoundError("No manifest found for rollback.")

    manifest = load_json(manifest_path)
    run_id = str(manifest["run_id"])
    before = manifest["before"]
    backups_dir = tracking_root / "backups" / run_id

    restored: List[str] = []
    deleted: List[str] = []

    for rel, meta in before.items():
        rel_path = Path(rel)
        target = app_root / rel_path
        backup_candidate = backups_dir / rel_path.with_suffix(rel_path.suffix + ".bak")

        existed_before = bool(meta.get("exists"))
        if backup_candidate.exists():
            restore_file(backup_candidate, target)
            restored.append(rel)
        elif not existed_before and target.exists():
            delete_if_exists(target)
            deleted.append(rel)

    return {
        "ok": True,
        "mode": "rollback-latest",
        "manifest": str(manifest_path),
        "restored_files": restored,
        "deleted_files": deleted,
    }


def rollback_from_baseline(app_root: Path, tracking_root: Path) -> Dict[str, object]:
    baseline_pointer = tracking_root / "LAST_KNOWN_GOOD.json"
    if not baseline_pointer.exists():
        raise FileNotFoundError("No baseline pointer found for rollback.")

    baseline = load_json(baseline_pointer)
    baseline_id = str(baseline["baseline_id"])
    baseline_dir = tracking_root / "baselines" / baseline_id
    files = baseline["files"]

    restored: List[str] = []
    for rel in files.keys():
        source = baseline_dir / rel
        target = app_root / rel
        if source.exists():
            restore_file(source, target)
            restored.append(rel)

    return {
        "ok": True,
        "mode": "rollback-baseline",
        "baseline_id": baseline_id,
        "restored_files": restored,
    }


def append_tracking_log(path: Path, run_id: str, changed_files: List[str], dry_run: bool) -> None:
    if dry_run:
        return
    ensure_parent(path)
    header = "# Tracking Changelog\n"
    current = path.read_text(encoding="utf-8") if path.exists() else header
    lines = [
        f"## {run_id}",
        "",
        f"- generated_at_utc: `{utc_now().isoformat()}`",
        f"- changed_files: {len(changed_files)}",
    ]
    for item in changed_files:
        lines.append(f"- `{item}`")
    lines.append("")
    path.write_text(normalize_text(current.rstrip() + "\n\n" + "\n".join(lines)), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject architecture maps and tracking docs for external_interaction_template.")
    parser.add_argument("--app-root", default=None, help="Absolute path to apps/external_interaction_template")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--set-baseline", action="store_true", help="Write a last-known-good baseline after applying changes")
    parser.add_argument("--rollback-latest", action="store_true", help="Restore managed files from the latest manifest backup")
    parser.add_argument("--rollback-baseline", action="store_true", help="Restore managed files from LAST_KNOWN_GOOD baseline")
    args = parser.parse_args()

    selected_rollbacks = [args.rollback_latest, args.rollback_baseline]
    if sum(bool(x) for x in selected_rollbacks) > 1:
        raise SystemExit("Use only one rollback mode at a time.")

    app_root = infer_app_root(args.app_root)
    if not app_root.exists():
        raise SystemExit(f"App root does not exist: {app_root}")

    readme_path = app_root / README_NAME
    tracking_root = app_root / TRACKING_DIR

    if args.rollback_latest:
        result = rollback_from_manifest(app_root, tracking_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.rollback_baseline:
        result = rollback_from_baseline(app_root, tracking_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    run_id = utc_now().strftime("%Y%m%d_%H%M%S")
    manifests_dir = tracking_root / "manifests"
    snapshots_dir = tracking_root / "snapshots"
    backups_dir = tracking_root / "backups" / run_id
    baselines_dir = tracking_root / "baselines"
    changelog_path = tracking_root / "CHANGELOG_TRACKING.md"

    managed_paths = [app_root / rel for rel in MANAGED_FILES.keys()] + [readme_path]
    before = collect_snapshot(app_root, managed_paths)

    for path in managed_paths:
        if path.exists() and path.is_file():
            rel = Path(safe_rel_path(app_root, path))
            backup_path = backups_dir / rel.with_suffix(rel.suffix + ".bak")
            copy_backup(path, backup_path, args.dry_run)

    for rel, content in MANAGED_FILES.items():
        write_file(app_root / rel, content, args.dry_run)

    current_readme = read_text_if_exists(readme_path)
    updated_readme = upsert_readme_section(current_readme)
    write_file(readme_path, updated_readme, args.dry_run)

    after = collect_snapshot(app_root, managed_paths)

    changed_files: List[str] = []
    for rel in before.keys():
        if before[rel] != after[rel]:
            changed_files.append(rel)

    manifest = {
        "run_id": run_id,
        "generated_at_utc": utc_now().isoformat(),
        "app_root": str(app_root),
        "dry_run": args.dry_run,
        "set_baseline": args.set_baseline,
        "managed_files": list(before.keys()),
        "changed_files": changed_files,
        "before": before,
        "after": after,
        "backups_dir": str(backups_dir),
        **get_git_info(app_root),
    }

    manifest_path = manifests_dir / f"{run_id}_manifest.json"
    before_path = snapshots_dir / f"{run_id}_before.json"
    after_path = snapshots_dir / f"{run_id}_after.json"

    if not args.dry_run:
        ensure_parent(manifest_path)
        ensure_parent(before_path)
        ensure_parent(after_path)

        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        before_path.write_text(json.dumps(before, indent=2, ensure_ascii=False), encoding="utf-8")
        after_path.write_text(json.dumps(after, indent=2, ensure_ascii=False), encoding="utf-8")
        append_tracking_log(changelog_path, run_id, changed_files, dry_run=False)

        if args.set_baseline:
            baseline_id = run_id
            baseline_dir = baselines_dir / baseline_id
            files_pointer: Dict[str, Dict[str, object]] = {}

            for path in managed_paths:
                rel = safe_rel_path(app_root, path)
                if path.exists() and path.is_file():
                    dest = baseline_dir / rel
                    ensure_parent(dest)
                    shutil.copy2(path, dest)
                    files_pointer[rel] = {
                        "sha256": sha256_file(path),
                        "size": path.stat().st_size,
                    }

            baseline_pointer = {
                "baseline_id": baseline_id,
                "generated_at_utc": utc_now().isoformat(),
                "app_root": str(app_root),
                "files": files_pointer,
            }
            ensure_parent(tracking_root / "LAST_KNOWN_GOOD.json")
            (tracking_root / "LAST_KNOWN_GOOD.json").write_text(
                json.dumps(baseline_pointer, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    result = {
        "ok": True,
        "run_id": run_id,
        "app_root": str(app_root),
        "dry_run": args.dry_run,
        "changed_files": changed_files,
        "manifest_path": str(manifest_path),
        "before_snapshot_path": str(before_path),
        "after_snapshot_path": str(after_path),
        "baseline_pointer_path": str(tracking_root / "LAST_KNOWN_GOOD.json"),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
