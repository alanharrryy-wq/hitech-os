# Tablet Visual Promotion Candidate Shard — Chat 1

**Base head:** `57b01ad8bda043ec25763203354b686341bace09`  
**Surface:** `tablet`  
**Mode:** candidate-only, current-census reuse, no product/runtime mutation

## Scope and doctrine

This shard executes only Chat 1 from the parallel visual-promotion cohort. It reuses the current Tablet Target Index and expanded Visual Control evidence. It does not run broad rediscovery, does not edit RIFAT/Identity/Target Index/projection authority, and does not touch Tablet product/runtime files.

Atlasfin is used first as the priority visual reference. The Materiality Catalog was not inspected and was not used as fallback; it remains `STANDBY_USER_INVOKED_ONLY`.

## Zero-loss accounting

| Measure | Count |
|---|---:|
| Tablet Target Index total records | 933 |
| Chat 1 census inputs (`VISUAL_CONTROL_CENSUS_TARGET`) | 929 |
| Existing non-census exact targets excluded from worker input | 4 |
| `CANDIDATES.jsonl` | 141 |
| `UNRESOLVED.jsonl` | 786 |
| `CONFLICTS.jsonl` | 2 |
| Total Chat 1 outcomes | 929 |
| Duplicate target IDs | 0 |
| Missing target IDs | 0 |
| Extra target IDs | 0 |

Accounting result: **PASS_ZERO_LOSS**.

## Current physical evidence

- physicalStatus: `{"CURRENT":927,"DRIFT":2}`
- exact route resolved: 369
- exact region resolved: 363
- exact slot resolved: 1
- exact component resolved: 156
- owner resolved: 755
- projectionStatus: `{"CURRENT":929}`

A null route/slot/component is intentional when current machine evidence has multiple consumers/property-level slots or no unique coordinate. No ambiguity was converted into a guess.

## Atlasfin-first result

Atlasfin match accounting: `{"NO_MATCH":786,"MATCHED_RECIPE":143}`.

Recipe-level candidates are emitted only when the machine Visual Control `layerType` directly corresponds to a unique generic Atlasfin recipe kind among the reviewed Atlasfin family/recipe registries: card, table, panel, or overlay. Family/preset variants are deliberately left unset because multiple Atlasfin variants exist. No name-only match is upgraded to evidence.

## NDC / Identity / binding result

- NDC resolution: `{"UNRESOLVED":929}`
- visual meaning: `{"UNRESOLVED":787,"CANDIDATE_REVIEW_REQUIRED":141,"RESOLVED_EXISTING":1}`
- binding: `{"BLOCKED":787,"CANDIDATE":141,"EXISTING_RESOLVED":1}`
- promotion: `{"REGISTER_TARGET_FIRST":786,"ELIGIBLE_CANDIDATE":141,"BLOCKED":2}`
- Work Entry: `{"REGISTER_TARGET_FIRST":927,"BLOCKED":2}`

NDC stays unresolved unless a direct existing NDC authority relationship is proven. The worker mints no NDC, visual meaning, binding, target, application-layer, recipe, family, preset, or adapter IDs.

One existing resolved Identity binding may be reused only where the census coordinate exactly equals the binding's selector plus `implementationLayerId`. That relationship is emitted as existing authority and is explicitly marked for canonical dedupe against the already-existing exact target, not as a new binding.

## Guardrails held

- Materiality access/fallback: **none**
- broad rediscovery: **none**
- product/runtime writes: **none**
- Web / Chart Lab / Control Center writes: **none**
- global Identity/RIFAT/Target Index/Projection/Factory Ledger writes: **none**
- runtime visual certification claimed: **none**
- canonical IDs minted by Chat 1: **none**

This shard is candidate exchange data only. Candidate is not authority; source/static evidence is not runtime visual green.
