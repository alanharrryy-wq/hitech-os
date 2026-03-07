# Hydration Isolation Adoption Guide

## When to adopt

Adopt the isolation pattern when **two or more** of the following are true:

- The route is internal-only
- The UI is form-heavy or debug-control-heavy
- Hydration warnings appear only in normal browser profiles
- Warnings improve or disappear in incognito / clean-profile runs
- The warnings point to attributes that application code does not create
- The affected subtree can be isolated without disabling SSR for unrelated content

## When not to adopt

Do **not** adopt the pattern just to silence warnings when:

- The route is public or SEO-sensitive
- The mismatch is caused by non-deterministic application rendering
- The page can be fixed by making SSR and client render deterministic
- The proposed boundary would wrap a whole layout or large product surface

## Recommended rollout order

1. Audit the repo for hydration-related patterns and risky workarounds.
2. Identify the smallest internal-only subtree that can be isolated.
3. Introduce `InternalToolClientOnlyBoundary` only around that subtree.
4. Enable diagnostics and validate the mount path.
5. Re-test in normal, incognito, and clean-profile runs.
6. Track the adoption outside the standard document itself.

## Anti-patterns

- `dynamic(() => import(...), { ssr: false })` at full-route scope without explicit justification
- global `suppressHydrationWarning`
- applying client-only wrappers to public content
- claiming hydration is fully fixed when the root cause is environmental mutation

## Minimum acceptance checks

A change using this pattern should include:

- a reference to the hydration isolation standard
- a narrow boundary scoped to internal tooling only
- opt-in diagnostics support
- a before/after repro note
- a clean-profile comparison result

## Suggested file organization

- `docs/architecture/hydration-isolation-standard.md`
- `apps/keystone/components/internal-tooling/internal-tool-client-only-boundary.tsx`
- `apps/keystone/components/internal-tooling/use-internal-tool-hydration-diagnostics.ts`
- optional route-local wrappers such as `scene-studio-page-client-only.tsx`

## Tracking adopters

Keep current adopters in a separate operational note, for example:

- route / subtree
- boundary component used
- owner
- date adopted
- evidence link or issue/PR reference

That keeps the standard stable while operational details evolve.
