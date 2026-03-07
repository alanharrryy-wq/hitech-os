# Hydration Isolation Standard for Internal Tooling

## Status
Accepted

## Purpose

Reduce noisy or misleading React hydration warnings in internal, form-heavy tooling subtrees that are prone to third-party DOM mutation before hydration.

## Problem

Some internal tooling routes emit hydration warnings where React reports unexpected attributes on form controls, including examples such as:

- `field_signature`
- `form_signature`
- `alternative_form_signature`
- `visibility_annotation`

This signature strongly suggests the DOM was mutated before or during hydration, commonly by agents outside application control such as browser extensions, password managers, or browser autofill tooling.

## What the application controls

- Whether a subtree is server-rendered
- Whether internal tooling subtrees are isolated behind a client-only boundary
- Whether diagnostics are emitted when a boundary mounts

## What the application does not control

- Browser extension DOM mutation
- Password manager DOM mutation
- Browser autofill engines mutating fields before hydration

Because those mutation sources are external, the correct mitigation is **defensive isolation** of the affected internal subtree, not a claim of full prevention.

## Non-goals

This standard does **not**:

- guarantee prevention of all hydration warnings
- justify broad disabling of SSR across layouts or public routes
- replace debugging of genuine app-side render divergence
- treat all hydration warnings as extension-induced

## Decision

For internal-only, form-heavy debug or tooling subtrees with recurring hydration warnings consistent with pre-hydration DOM mutation, render the affected subtree behind `InternalToolClientOnlyBoundary`.

## Decision criteria

Apply `InternalToolClientOnlyBoundary` only when the subtree satisfies most of the following:

- internal-only route or internal-only overlay/panel
- form-heavy or control-heavy UI
- not SEO-relevant
- warning signature points to attributes not produced by application code
- issue reproduces in normal profiles and improves or disappears in incognito / clean-profile runs
- the subtree is narrow enough to isolate without disabling SSR for unrelated content

## Scope rule

Keep the client-only boundary as narrow as possible.

### Preferred targets

- tooling subtree only
- debug HUD only
- control overlay only
- internal workspace panel only

### Avoid wrapping

- full route trees unless separately justified
- shared layouts
- public content
- primary product UI unless separately documented

## Rationale

The application can decide whether a subtree is hydrated from SSR output. It cannot prevent extensions or browser autofill systems from mutating form nodes before hydration starts.

That makes narrow client-only isolation the appropriate architectural mitigation for internal tooling routes that repeatedly produce environment-driven hydration noise.

## Tradeoffs

### Benefits

- lowers false-positive hydration noise on internal tooling routes
- reduces wasted debugging time on environment-driven warnings
- keeps public content SSR-enabled
- makes route-specific diagnostics easier to reason about

### Costs

- the affected subtree loses SSR
- the subtree may render slightly later on the client
- careless overuse can mask legitimate hydration defects
- broad adoption can erode SSR discipline if not governed

## Implementation reference

Reference component name:

- `InternalToolClientOnlyBoundary`

Suggested supporting wrappers:

- `SceneStudioPageClientOnly`
- `PitchLayerDevToolsClientOnly`
- `ControlRoomClientOnly`

## Diagnostics

Diagnostics must remain off by default.

Enable diagnostics with one of:

- query parameter: `?hydrationDiag=1`
- environment flag: `NEXT_PUBLIC_INTERNAL_TOOL_HYDRATION_DIAGNOSTICS=1`

When enabled, console output should include:

- component name
- route or pathname
- boundary strategy
- mount timestamp

## Verification checklist

1. Reproduce on the target internal route with the normal browser profile.
2. Repeat with `?hydrationDiag=1` and confirm the protected subtree mount log appears.
3. Repeat in incognito/private mode.
4. Repeat in a clean browser profile.
5. Compare warning behavior across runs.

## Interpretation

- Warning disappears in clean/incognito runs: likely external DOM mutation.
- Warning remains inside a protected subtree: inspect boundary placement or client-only implementation.
- Warning remains outside protected subtrees: isolate the offending internal-only subtree and evaluate it against this standard.
- Warning persists in clean environments and maps to app-generated attributes or render divergence: treat it as a real application defect.

## Governance rule

Current adopters should be tracked separately from this standard so the rule stays valid even if route names or component names change.
