# Live Scene Composer Minimum Safe Wiring Model

Status: proposal-ready (implementation-safe)

## Provider location

Place `LiveSceneComposerProvider` under:
- `apps/keystone/components/live-scene-composer/provider.tsx`

It should be mounted only by future composer host routes/surfaces, never by Runtime Debug Console mounts.

## Allowed imports

`LiveSceneComposerProvider` may import:
- `apps/keystone/components/live-scene-composer/**` local contracts/model/state
- `apps/keystone/components/dev-console/console-core/**` shell/registry primitives only
- `apps/keystone/components/runtime-mutation-bridge/**` command contracts + apply API

## Forbidden imports

`LiveSceneComposerProvider` must not import:
- `apps/keystone/components/dev-console/runtime-debug-console/**`
- `apps/keystone/components/dev-console/domains/inspect/**`
- `apps/keystone/components/dev-console/panels/**` runtime-debug panels
- `apps/keystone/components/dev-console/DevConsoleContext.tsx`
- `apps/keystone/components/pitch/debug/**` direct runtime-debug modules

## Reuse of `console-core`

Composer may reuse only:
- shell primitives
- panel/module registration primitives
- layout persistence primitives

Composer must not reuse:
- runtime debug event handlers
- diagnostics-specific provider state

## Module registration independence

Composer should register modules through a composer-local registry seam:
- `apps/keystone/components/live-scene-composer/registry.ts`

Runtime debug registry remains independent:
- `apps/keystone/components/dev-console/runtime-debug-console/runtime-debug-console-panels.tsx`

No cross-registration allowed.

## Runtime capability access

Composer must access runtime writes through:
- `apps/keystone/components/runtime-mutation-bridge/contract.ts`

Required flow:
1. composer builds typed command
2. command validated in bridge layer
3. bridge routes to adapter for pitch/scene-studio runtime mutation

Direct composer writes to runtime are forbidden.

## Adapter placement

Place adapters under bridge boundary:
- `apps/keystone/components/runtime-mutation-bridge/adapters/pitch/*`
- `apps/keystone/components/runtime-mutation-bridge/adapters/scene-studio/*`

Adapters should be the only layer touching runtime/product-specific write APIs.

## What stays stubbed now

Keep stubbed until first MVP slice:
- actual adapter implementations
- commit execution path
- persistence reconciliation

Keep implemented now:
- command contract types
- policy metadata
- validation entry point
- guardrails/tests preventing boundary bypass
