# PRISMA Full-Stack Recipe Contract

## Purpose

`REC.button.primary` is neutral visual meaning. IDRECIPE1 extends it with a
registry-driven full visual stack for the exact Tablet POS Cobrar binding
without generating or applying CSS.

## Separation of authority

`neutral meaning → identity profile → recipe → surface adapter → binding → layer → generated runtime`

The recipe never substitutes for a binding, an application gate or runtime
visual certification.

## Independent statuses

- `compatibilityStatus`: schema/version interoperability only.
- `bindingStatus`: concrete owner/route/region/slot/layer resolution only.
- `recipeCoverageStatus`: known visual-stack coverage only.
- `applicationReadiness`: authorization to produce/apply source changes.
- `evidenceStatus`: strength and kind of available evidence.

These states are not interchangeable.

## Hard coverage rule

Every known selector, state, pseudo-element, subcomponent and asset must be
registered. New or unrecognized coverage blocks `COMPLETE` with the most
specific status:

- `BLOCKED_BY_INCOMPLETE_RECIPE_COVERAGE`
- `BLOCKED_BY_UNGOVERNED_STATE`
- `BLOCKED_BY_UNGOVERNED_SUBCOMPONENT`
- `BLOCKED_BY_UNGOVERNED_PSEUDO_ELEMENT`
- `BLOCKED_BY_UNGOVERNED_ASSET`

Implicit legacy preservation is forbidden.

## Zero semantics

Every property declares its zero/none/transparent behavior. A zero visual knob
must produce actual absence or transparency rather than an opaque placeholder.

## IDRECIPE1 safety

The authority is `instructionOnly=true`,
`runtimeMutationAllowed=false` and `productApplicationAllowed=false`.
Tablet CSS, components and runtime remain outside this gate.
