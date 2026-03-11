# Dev Console Constitution

Status: active  
Scope: `apps/keystone/components/dev-console/**`, `apps/keystone/components/pitch/debug/**`, `tools/dev-console/**`

## 1. System Philosophy

The Dev Console is an internal platform, not a debug widget.

Its purpose is to guarantee:
- deterministic operator behavior
- stable observability
- safe visual composition
- bounded extensibility

The architecture is intentionally opinionated:
- `ConsoleCore` handles infrastructure only
- `InspectConsole` handles runtime observation
- `ComposeConsole` handles visual composition

## 2. Domain Separation

The platform has three domains:
- `core`: shell, panel registration, lifecycle, event transport, layout persistence, runtime assertions
- `inspect`: diagnostics, bridge health, layer state, performance, event topology, snapshot inspection
- `compose`: visual controls and scene look composition

Allowed cross-domain interaction:
- `InspectConsole` may read diagnostics and runtime state
- `ComposeConsole` may mutate visual state through `SceneLookModel`
- `ConsoleCore` may host utilities used by both domains without implementing domain behavior

Disallowed interaction:
- inspect panels mutating presentation state
- compose panels mutating diagnostics transport/state
- core modules embedding inspect/compose panel logic

## 3. Canonical Visual Model

All visual composition controls must converge into `SceneLookModel`.

`SceneLookModel` is canonical for:
- background
- overlays
- visual effects
- stage style
- card style
- motion
- density

No compose panel may introduce a parallel visual state store for these fields.

## 4. Runtime Invariants

Runtime assertions must continuously validate:
- diagnostics integrity (`route`, `timestamp`, payload shape)
- scene look model integrity (`SceneLookModel` normalization contract)
- required event consumer presence for contractual console events

Invariant failures are considered architectural health faults, not cosmetic warnings.

## 5. Forbidden Patterns

Forbidden by constitution:
- inspect panels performing direct DOM mutation
- compose panels calling diagnostics mutation APIs
- panels not declared in architecture contracts
- uncontracted event channels for core console actions
- visual composition bypassing `SceneLookModel` where contract requires it

## 6. Approved Extension Mechanisms

New panel workflow:
1. add panel implementation file
2. assign domain in panel registry
3. add panel contract entry in `docs/dev-console/contracts/panels.json`
4. add tests and scanner compliance

New event workflow:
1. define event constant in `dev-console-events.ts`
2. register emitter/listener implementations
3. add contract entry in `docs/dev-console/contracts/events.json`
4. pass architecture guard

## 7. Architectural Decay Prevention

Architectural decay is prevented by:
- contract files (`panels.json`, `events.json`)
- runtime invariants
- static architecture scanner (`tools/dev-console/architecture_guard.py`)
- CI enforcement (`dev-console-architecture-guard` workflow)

A change that violates contracts must fail fast before merge.
