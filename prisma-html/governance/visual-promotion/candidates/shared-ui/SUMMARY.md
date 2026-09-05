# Chat 4 Shared UI visual-promotion candidate shard

Base head: `57b01ad8bda043ec25763203354b686341bace09`

Scope: `shared-ui` only. Write ownership: `prisma-html/governance/visual-promotion/candidates/shared-ui/**`.

## Result

The current Shared UI census was reused without broad rediscovery. All 70 `VISUAL_CONTROL_CENSUS_TARGET / DISCOVERY_ONLY` records remain physically current and retain their existing target IDs, selectors, implementation-layer IDs and exact-byte projection evidence.

- Candidate outcomes: **40**. Each has exactly one current expanded Visual Control region row. Its `visualMeaningCandidate` is copied verbatim from that row's `human_id`; no new canonical `VIS.*`, NDC, binding, recipe, target or application-layer ID is minted.
- Unresolved outcomes: **19**. The physical target is current, but no exact expanded region row was proven for its `implementationLayerId`.
- Conflict outcomes: **11**. Multiple current expanded region rows address the same `implementationLayerId`; this worker does not choose among stronger machine-readable authorities.
- Zero-loss: **40 + 19 + 11 = 70 = 70**.

## Atlasfin-first

Canonical Atlasfin registries were inspected first for visual matching. The Shared UI adapter is `atlasfin::ADP.SHARED.NEUTRAL.V2`. The current Atlasfin visual recipe bundle exposes 12 target selectors and none exactly match a Shared UI census selector at this base head. No stronger family, preset or recipe correspondence is machine-proven, so every row remains `atlasfinMatchStatus=NO_MATCH`. Adapter presence is not promoted into a recipe match.

The Materiality Catalog remained `STANDBY_USER_INVOKED_ONLY`: it was not inspected, consumed or used as fallback.

## NDC / Identity / application

No exact existing NDC binding was proven for these physical targets, so NDC remains `UNRESOLVED`; names were not used to invent NDC meaning. The existing Identity Shared UI adapter `identity::prisma.adapter.shared-ui.v1` is reused. Candidate rows remain `REGISTER_TARGET_FIRST`; unresolved/conflicting rows remain `BLOCKED`. None of this authorizes runtime/product mutation.

## Consumers

Observed PC, Mobile and Tablet consumers are retained as evidence only in `MANIFEST.json`. No consumer shard, product source, projection, global Identity registry, Target Index, projection manifest, Factory Ledger, Evidence Index or `FILES_MANIFEST.json` is edited.

## Validation

- baseHead fixed to `57b01ad8bda043ec25763203354b686341bace09`
- input target count = 70
- current physical = 70
- projection `CURRENT` = 70
- Atlasfin `NO_MATCH` = 70
- NDC `UNRESOLVED` = 70
- binding candidates = 40
- blocked bindings = 30
- output target IDs unique = 70
- broad rediscovery = false
- Materiality fallback = false
- writes outside Chat 4 ownership = false
- runtime certification claim = false
