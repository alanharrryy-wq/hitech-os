# PRISMA Visual Core Contract

Status: `VISCORE1_SOURCE_READY`

## Purpose

PRISMA has one editable visual authority and many generated/runtime projections. The system must make visual work fast without turning Tablet, PC, Mobile, Web, Chart Lab, Control Center, Shared UI, Atlasfin and site catalogs into competing sources of truth.

## Canonical chain

`neutral meaning -> identity profile -> surface adapter -> certified owner/route/region/slot/layer binding -> compiled projection -> governed product projection -> static gates -> runtime visual evidence -> READY`

## Authority roles

1. `authority/rifat/identity` owns neutral visual meaning: profiles, semantic tokens, recipes, assets and surface adapters.
2. `authority/rifat/prisma-ui` owns where the meaning lands: surfaces, routes, owners, regions, editable slots and layers.
3. `authority/rifat/visual-source-manifest.json` owns deterministic source-to-product projection declarations.
4. `extras/atlasfin` is the canonical human cockpit. It is a consumer/operator of authority, never a second editable authority.
5. Product/app runtime files are consumers or generated projections. They do not become authority because they are visible at runtime.
6. `sistema-ui/catalogo`, `sistema-ui/identidad` and `sistema-ui/css/tokens` are reference/compatibility/site-presentation surfaces unless explicitly promoted by a governed contract.

## Duplication policy

The objective is not zero copies. The objective is zero competing editable copies.

Allowed duplication:

- deterministic generated projections;
- immutable evidence snapshots;
- public/reference views derived from authority;
- compatibility exports with provenance.

Forbidden duplication:

- two editable registries for the same semantic meaning;
- manually maintained route/layer counts when they can be derived;
- product CSS that silently becomes a second visual source of truth;
- README or catalog prose overriding machine-readable authority;
- generated files edited by hand.

## READY policy

`READY` is a certification state, not a synonym for "compiled" or "looks fine".

A surface may only become `READY` after:

1. route/source discovery is current;
2. route, owner, region, editable-slot and layer bindings are certified;
3. identity compilation has no drift;
4. product projection is authorized and deterministic;
5. static gates pass;
6. runtime/browser visual evidence passes;
7. rollback/evidence is available;
8. no fake-green contract is satisfied.

If any step is missing, VISCORE reports the exact blocker and does not promote the surface.

## Human workflow

The intended daily workflow is:

1. Open Atlasfin.
2. Select/inspect identity and recipe intent.
3. Select a certified surface/owner/slot/layer target.
4. Preview the governed projection.
5. Ask for `ready <surface>`.
6. Let tooling compile, project, validate and gather evidence.
7. Promote only when all gates are green; otherwise show blockers and preserve rollback.

Humans should not need to hunt through CSS files, parallel registries or stale README counters to discover visual truth.

## Non-goals of VISCORE1

VISCORE1 does not redesign product screens and does not auto-certify missing runtime evidence. It establishes the single authority contract, canonical readiness computation, Atlasfin status feed and the tooling path required for later multi-surface certification without duplicating architecture.
