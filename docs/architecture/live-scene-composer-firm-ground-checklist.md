# Live Scene Composer Firm-Ground Checklist

Before adding any Composer feature, all items below must be true.

1. Read first:
- `docs/architecture/allowed-dependency-matrix.md`
- `docs/architecture/protected-nodes.md`
- `docs/architecture/live-scene-composer-wiring.md`
- `docs/dev-console/CONSTITUTION.md`
- `docs/dev-console/LAWS.md`

2. Boundary rules:
- Runtime Debug Console and Live Scene Composer remain sibling products.
- `console-core` is the only shared infrastructure layer.
- Do not register composer modules in runtime-debug registries.

3. Mutation rules:
- Any write-capable runtime change must go through `runtime-mutation-bridge`.
- No direct composer write path to pitch/scene-studio runtime.
- No direct dispatch of runtime-debug mutation events from composer code.

4. Dependency rules:
- Composer imports only allowed areas from dependency matrix.
- No `dev-console/runtime-debug-console` imports in composer files.
- No legacy `dev-console/core` imports anywhere.

5. Guard/test rules before merge:
- `python tools/dev-console/architecture_guard.py --repo-root . --strict`
- focused dev-console architecture tests
- focused bridge/composer tests for new command paths
- `pnpm -C apps/keystone typecheck`

6. Protected-node changes:
- If touching protected nodes, include explicit risk note and validation evidence.
- Require designated reviewer class from protected-nodes doc.

7. Stop condition:
- If a feature requires bypassing bridge or coupling into runtime-debug internals, stop and redesign with an adapter seam.
