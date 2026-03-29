# Hydration Guard for Internal Tooling

## Symptom Signature

Hydration warnings on internal tooling routes where React reports extra attributes on form controls, commonly:

- `field_signature`
- `form_signature`
- `alternative_form_signature`
- `visibility_annotation`

This signature indicates DOM mutation before React hydration.

## What the App Can and Cannot Control

- Can control: whether internal tooling form trees are SSR-rendered.
- Cannot control: browser extensions, password managers, or browser autofill engines mutating DOM before hydration.

Because external mutation is outside app control, the mitigation is defensive isolation, not a full prevention claim.

## Architectural Rule (Repository Standard)

For internal, form-heavy debug panels that are likely to be externally mutated pre-hydration:

1. Render behind `InternalToolClientOnlyBoundary`.
2. Keep boundary scope narrow (tooling/debug subtree only).
3. Do not apply broad no-SSR to public, SEO-relevant content.

Reference implementation:

- `apps/keystone/components/internal-tooling/internal-tool-client-only-boundary.tsx`

## Current Protected Subtrees

- Scene Studio route workspace (`/dev/scene-studio`) via `SceneStudioPageClientOnly`
- Pitch debug HUD tooling via `PitchLayerDevToolsClientOnly` on pitch routes
- Legacy Scene Studio Control Room overlay subtree (`ControlRoom`)

## Lightweight Diagnostics (Opt-in)

Mount diagnostics are intentionally off by default.

Enable one of:

- query parameter: `?hydrationDiag=1`
- env flag: `NEXT_PUBLIC_INTERNAL_TOOL_HYDRATION_DIAGNOSTICS=1`

When enabled, console logs include:

- component name
- route
- client-only boundary strategy

## Repro Checklist

1. Reproduce on the target internal route with normal profile and extensions enabled.
2. Repeat with `?hydrationDiag=1` and confirm protected panel mount log appears.
3. Repeat in Incognito/private window (extensions disabled by default).
4. Repeat in a clean browser profile.
5. Compare warning behavior across the runs.

Interpretation:

- warning gone in clean/incognito but present in normal profile: likely extension/autofill mutation.
- warning persists outside protected subtrees: isolate that subtree and apply the same boundary rule if internal-only.

