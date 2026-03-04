# PITCH_ENGINE_UI

## Scope

This document defines the dev-only Pitch Engine UI delivered under `/dev/pitch-engine?debug=1`.

## Access and Security

- Route access is evaluated in `app/dev/pitch-engine/page.tsx`.
- Production build always returns `404` by calling `notFound()`.
- Access gate requires one of:
  - `debug=1` query token
  - `KEYSTONE_DEV_PITCH_ENGINE=1` env override
  - requested capability mode that resolves to an allowed applied mode
- API routes under `/api/pitch-engine/*` use the same gate and return `404` when denied.

## UI Surfaces

### Program Library

- CRUD actions:
  - create program
  - delete selected program
  - save current program through API
- Import/export:
  - import JSON program using schema validation
  - export selected program as JSON
- Selection:
  - selects active program and updates scene/sequence context

### Timeline Editor

- Track matrix for fixed tracks:
  - camera
  - overlay
  - motion
  - layers
  - lighting
  - subtitle
  - audio
  - annotation
- Marker editor:
  - Reveal
  - Settle
  - CTA
- Marker operations:
  - create
  - remove

### Director Controls

- Sequence list by selected scene
- Sequence creation from cinematic preset script
- Preset script injection creates timeline DSL payload:
  - duration
  - markers
  - tracks
  - keyframes

### Replay Transport

- play/pause
- loop on/off
- scrub bar
- playback rate (0.5x to 2x)
- jump-to-marker buttons

### Scene Recorder

- Secure postMessage bridge listener with:
  - origin allow-list checks
  - zod payload schema validation
- Captured snapshot fields:
  - route
  - canonical URL
  - title
  - resolved flags
  - unknown tokens
  - viewport details
- Generates:
  - scene
  - optional sequence from selected preset
- Collision-safe IDs use deterministic suffixing
- Undo last record is supported

### Operator Status HUD

- server status
- last run status and path
- last error tail
- last artifact run id
- persisted in localStorage

### Support Bundle

- Exports JSON bundle including:
  - selected program/scene/sequence
  - capability status
  - operator HUD status
  - artifact run index snapshot
  - links and DoD path
  - environment summary

### Diff Triage

- Reads artifact index entries through API
- Displays:
  - before image
  - after image
  - diff image thumbnail
  - wipe slider
  - zoom and pan controls
- Actions:
  - Accept
  - Reject
  - Re-run
  - Save Notes (`DIFF_NOTES.md`)

## State Model

Store: `components/pitch-engine/state/use-pitch-engine-store.ts`

- single source of UI state for:
  - capability status
  - program/scene/sequence selection
  - transport
  - recorder status
  - triage runs
  - HUD
- includes action layer for all user operations
- persists key surfaces in localStorage

## Fixtures and Scale

- Default program fixture file: `program-library/default-programs.ts`
- Contains a large deterministic catalog for stress and UX validation:
  - multiple programs
  - multiple scenes per program
  - multiple sequences per scene
  - multi-track keyframes and markers

## Testing Focus

- route and API security gate behavior
- store actions
- timeline preset injection
- recorder capture logic
- triage API contracts

## Constraints

- dev-only feature flags by default
- no edits to package manifests
- no dependency on remote services for baseline behavior
