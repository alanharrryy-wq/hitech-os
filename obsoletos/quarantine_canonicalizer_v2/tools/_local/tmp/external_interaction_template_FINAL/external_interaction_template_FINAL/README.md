# External Interaction Template

`external_interaction_template` is the web/light companion to the desktop control-center template.

It provides a domain-neutral external interaction system for:

1. Collect
2. Review
3. Update
4. Approve
5. Dispatch
6. Sync

## Scope

This template is intentionally neutral. Core abstractions are:

- `Actor`
- `Record`
- `RecordType`
- `Flow`
- `Step`
- `Field`
- `Action`
- `Submission`
- `Attachment`
- `Adapter`
- `DispatchJob`
- `SyncEvent`

No CRM-specific nouns are hardcoded in architecture.

## Tech Stack

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- shadcn-style reusable UI primitives
- Framer Motion
- Prisma + SQLite
- REST APIs
- Adapter boundaries for outbound dispatch

## Included Example Schemas

- `service_request`
- `approval_packet`
- `inspection_checklist`

These examples demonstrate generality; the engine remains schema-driven and reusable.

## Run Locally

```powershell
pnpm --filter @hitech/external_interaction_template install
pnpm --filter @hitech/external_interaction_template db:setup
pnpm --filter @hitech/external_interaction_template dev
```

Default URL:

- `http://127.0.0.1:3110`

## API Surface (template)

- `GET /api/schemas`
- `GET|POST /api/records`
- `GET|PATCH /api/records/[recordId]`
- `POST /api/records/[recordId]/action`
- `POST /api/records/[recordId]/attachments`
- `GET|PATCH /api/records/token/[token]`
- `GET /api/sync/events`
- `POST /api/sync/jobs/[jobId]/retry`

## Adapter Model

Current built-ins:

- `LocalAdapter`
- `RestAdapter`
- `WebhookAdapter`

Environment variables for outbound adapters:

- `EXTERNAL_INTERACTION_REST_ENDPOINT`
- `EXTERNAL_INTERACTION_WEBHOOK_URL`

## Schema Extension

Add new record types in:

- `src/lib/core/schema-registry.ts`

Each schema defines:

- flow steps
- fields
- conditional visibility
- actions by state/role
- view sections
- adapter bindings

## Security / Access Model (template-level)

Supports:

- public flow access
- authenticated placeholder (header based)
- secure token lookup and update
- role-aware action availability

## Tests

```powershell
pnpm --filter @hitech/external_interaction_template test
```

Covers schema-driven rendering/validation, conditional visibility, record create/update, token resume,
action/state behavior, dispatch outcome handling, sync visibility, and schema switching.
