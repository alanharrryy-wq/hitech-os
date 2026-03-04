# Sequence DSL Contract (v1)

## Object

`DirectorSequence` (`schemaVersion=1`) is a deterministic timeline object.

Required fields:

- `sequenceId`
- `schemaVersion=1`
- `createdAt`, `updatedAt` (UTC ISO)
- `baseSceneRef` (`sceneId` or `inlineScene`)
- `timelineDSL`
- `rules`

## timelineDSL

### tracks

Allowed tracks:

- `camera`
- `overlay`
- `motion`
- `layers`

Track list must be non-empty and contain no duplicates.

### keyframes

Keyframe shape:

- `tMs` (0..120000)
- `track`
- `key`
- `value`
- `easing`

Allowed easing values:

- `linear`
- `easeIn`
- `easeOut`
- `easeInOut`

Allowed deterministic keys by track:

- `camera`: `zoom`, `panX`, `panY`, `tilt`, `focus`
- `overlay`: `opacity`, `headline`, `subhead`, `cta`, `tone`
- `motion`: `heroEntrance`, `parallax`, `pulse`, `drift`, `shake`
- `layers`: `visibility`, `intensity`, `highlight`, `mask`, `order`

Validation invariants:

- keyframes must be sorted by `tMs`
- keyframe signatures (`tMs:track:key`) must be unique
- keyframe track must exist in `timelineDSL.tracks`
- keys must be valid for their track

### markers

Marker shape:

- `tMs` (0..120000)
- `label`

Marker signatures (`tMs:label`) must be unique.

## rules

### motionBudget

- `maxHeroMotions` (0..12)
- `maxTrackKeyframes` (1..2000)

### reducedMotion

- `strategy`: `jumpToFinal`

Behavior:

- keep latest keyframe per `track:key`
- collapse all retained keyframes to `tMs=0`
- normalize markers to `tMs=0`

### perfDegrade

- `strategy`: `lite`

Behavior:

- drop `motion` track keyframes
- reduce `layers` intensity deterministically (factor 0.5)

## Derived Capture Plan

`computeDerived(sequence)` outputs deterministic capture timestamps and entries from:

- start (`tMs=0`)
- all keyframe timestamps
- all marker timestamps
- end timestamp (max timeline timestamp)

Output ordering is stable and repeatable.
