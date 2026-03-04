# PITCH_ENGINE_DIRECTOR

## Director Layer Contract

Director layer combines scene context and timeline DSL to produce deterministic cinematic sequences.

## Definitions

- Scene: route-level context + metadata
- Sequence: timeline payload bound to a scene
- Timeline DSL:
  - duration
  - tracks
  - keyframes
  - markers
  - transitions

## Creation Flow

1. Select existing scene.
2. Choose preset script.
3. Enter sequence name/description.
4. Create sequence.
5. Sequence is attached to scene and selected for editing.

## Preset Scripts

Source: `components/pitch-engine/timeline/preset-scripts.ts`

Preset script defines:

- style type (`cinematic`, `documentary`, `product`, `compliance`)
- marker map
- track map and keyframes
- values (`opacity`, `x`, `y`, `scale`, `visible`)

Injection behavior:

- generates stable IDs
- creates timeline markers for Reveal/Settle/CTA
- writes deterministic track ordering

## Marker Editing

Marker editor supports:

- add marker by type
- remove marker
- sort by time ascending

Marker semantics:

- Reveal: first narrative opening
- Settle: composition stabilization
- CTA: conversion endpoint

## Track Editing

Track editor supports:

- enable/disable track
- inspect keyframe table per track
- track-specific keyframe values

Primary fixed tracks:

- camera
- overlay
- motion
- layers
- lighting
- subtitle
- audio
- annotation

## Replay Semantics

Replay transport uses global store state:

- current time
- duration
- isPlaying
- isLooping
- playbackRate

Behavior:

- loops to zero when loop enabled
- pauses at duration when loop disabled
- jump-to-marker sets exact marker timestamp

## Reduced Motion Mode

When reduced motion is applied via capability downgrade:

- applied mode may be reduced (`debug` -> `full` -> `lite`)
- preview banner displays warning
- replay should be treated as final-state-first for diagnostics

## Scene Recorder Integration

Recorder mode can generate sequence from bridge snapshot:

- capture snapshot
- optionally create sequence with selected preset
- sequence anchors at marker defaults
- undo stack preserves pre-record state

## Integrity Rules

- Duplicate IDs prevented via deterministic suffixing.
- Sequence and scene references remain internal to selected program.
- Updates preserve sort and deterministic ordering.

## API Coupling

UI calls dev-only API for persistence and triage actions.

Key endpoints:

- `GET/POST /api/pitch-engine/programs`
- `PUT/DELETE /api/pitch-engine/programs/:id`
- `POST /api/pitch-engine/triage`
- `POST /api/pitch-engine/support-bundle`

## Operational Expectations

- No production exposure.
- Controlled by debug/env/capability gate.
- Deterministic outputs for same inputs.
- Fully operable offline with local artifact paths.
