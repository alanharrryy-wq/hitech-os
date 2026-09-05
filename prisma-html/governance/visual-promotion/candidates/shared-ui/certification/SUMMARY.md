# Chat 4 Shared UI corpus certification

Phase: `CANDIDATE_CORPUS_CERTIFICATION_PARALLEL`

- Certification branch base: `8cc1918c5e015d1408335c15313e7364e04859c2`
- Immutable source: `visual-promotion-chat4-shared-ui-20260904@57b502f1064571cebd917b36882ef9c11e9fa7d8`
- Source baseHead: `57b01ad8bda043ec25763203354b686341bace09`
- Strict Control Plane authority: `7cc48fa49906c8f443b267fd6c3590fd3f4340fb`

## Result

- **70/70 corpus-valid**
- **invalid = 0**
- **semanticMutationCount = 0**
- **unique target IDs = 70**
- source accounting preserved: **40 candidates + 19 unresolved + 11 conflicts**
- certification labels: **40 VALID_REGISTER_TARGET_FIRST + 30 VALID_BLOCKED**
- NDC `UNRESOLVED`: **70**
- Atlasfin `NO_MATCH`: **70**
- projection `CURRENT`: **70**
- promotion status: **40 REGISTER_TARGET_FIRST + 30 BLOCKED**
- Work Entry: **40 REGISTER_TARGET_FIRST + 30 BLOCKED**

## Normalization

Each derivative record adds `schema=prisma.visual-promotion.candidate.v1`. The Shared UI Atlasfin adapter field is represented as raw registry ID `ADP.SHARED.NEUTRAL.V2` instead of the source evidence form `atlasfin::ADP.SHARED.NEUTRAL.V2`. The current structured Atlasfin registry proves the raw ID exists. The original qualified value is retained in each certification row.

No semantic status changed. No NDC/VIS/BND/TGT/LYR/recipe/adapter ID was minted. No Atlasfin `NO_MATCH` was upgraded. No binding or region was resolved.

## Conflict preservation

- 19/19 no-region unresolved records remain unresolved.
- 11/11 multi-region records retain their conflict blocker.
- No region was chosen by inference.

## Provenance

Every certification row pins source head, source file, source line/logical record, source-file SHA-256 and SHA-256 of the exact source JSONL record.

Source shard SHA-256:
- `MANIFEST.json`: `c51394943b5ff2c06bcd714801122063cbd097498b2f467132d8d6b8d179b1c4`
- `CANDIDATES.jsonl`: `ff89e661faf98f80f1e09fe2157ba1e60e1c250ae5f9e5101a8baf9e482aae3f`
- `UNRESOLVED.jsonl`: `2f9b48426a6e60f82774751964ba5bd44c06eea714c8c530be687f8035f50055`
- `CONFLICTS.jsonl`: `b0f79b271c2314c7afb9d499cc471af414d2f662062561374a227549dd1edd31`
- `SUMMARY.md`: `fad3898873fc84f47e80ad39028d71c3402fd9ceb89b4388ba26811e5ffcdf96`

## Safety

Materiality Catalog remained `STANDBY_USER_INVOKED_ONLY` and uninspected. Broad rediscovery was not performed. Consumers/products/runtime/global authority and `prisma-html/FILES_MANIFEST.json` were not modified. Draft PR #539 was not merged. Chat 4 opens no certification-phase PR.
