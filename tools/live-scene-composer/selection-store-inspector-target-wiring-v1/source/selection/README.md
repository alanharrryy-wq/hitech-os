# selection/

This folder contains a reference implementation for the Selection Store + InspectorTarget wiring seam.

## Files

- `contracts.ts`: durable contract types and helpers
- `selection-store.ts`: store implementation with transitions and subscriptions
- `selection-selectors.ts`: selectors for active selection and selection-key matching
- `inspector-target.ts`: deterministic derivation helpers
- `selection-sync.ts`: surface sync plan helpers
- `mutation-intent.ts`: explicit target helpers for mutation payload composition
- `surface-adapters.ts`: typed adapters from canvas/tree events to selection inputs
- `react-hooks.ts`: minimal React hooks over the store
- `selection-fixtures.ts`: sample fixtures for tests and examples
- `examples/selection-store-demo.ts`: reference demo flow
- `index.ts`: public exports

## Design goals

- plain TypeScript first
- deterministic derivation
- minimal runtime assumptions
- safe stale handling
- explicit target contracts
