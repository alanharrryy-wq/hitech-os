# Tablet Candidate Corpus Certification — Chat 1

**Phase:** `CANDIDATE_CORPUS_CERTIFICATION_PARALLEL`  
**Surface:** `tablet`  
**Certification branch base:** `8cc1918c5e015d1408335c15313e7364e04859c2`  
**Immutable source:** `chat1/tablet-visual-promotion-57b01ad8@1b669d98dc9063fe4d6f5f8ddc06262a6968e728`  
**Source base:** `57b01ad8bda043ec25763203354b686341bace09`  
**Control Plane contract head:** `7cc48fa49906c8f443b267fd6c3590fd3f4340fb`

## Certification result

- Corpus-valid: **929/929**
- Invalid: **0**
- Semantic mutations: **0**
- Unique target IDs: **929/929**
- Exact source-record provenance rows: **929/929**
- Source bucket accounting: `{"CANDIDATES":139,"CONFLICTS":2,"UNRESOLVED":788}`
- Certification labels: `{"VALID_BLOCKED":2,"VALID_ELIGIBLE_CANDIDATE":139,"VALID_REGISTER_TARGET_FIRST":788}`
- Result: **PASS_TABLET_CANDIDATE_CORPUS_CERTIFIED**

`INVALID.jsonl` is intentionally empty.

## Normalization

Tablet source rows already satisfy the strict candidate-record shape and closed vocabulary. No row-field rewrite is required. `NORMALIZED.jsonl` is therefore a deterministic identity pass-through of the exact source row bytes, concatenated in source-bucket order: `CANDIDATES`, `UNRESOLVED`, `CONFLICTS`.

The certification derivative normalizes the **manifest intake envelope** to `prisma.visual-promotion.candidate-shard.v1` and stores row-level provenance separately in `CERTIFICATION.jsonl`.

Each certification row pins:

- source head/base;
- exact source file and source bucket;
- exact source line;
- SHA-256 of the exact UTF-8 source record bytes excluding newline;
- normalized line/hash;
- certification label;
- strict-schema, vocabulary, reference and provenance validation result;
- `semanticMutation=false`.

## Semantic invariants preserved

- physicalStatus: `{"CURRENT":927,"DRIFT":2}`
- Atlasfin match: `{"MATCHED_RECIPE":138,"NOT_APPLICABLE":2,"NO_MATCH":789}`
- NDC resolution: `{"UNRESOLVED":929}`
- visual meaning: `{"CANDIDATE_REVIEW_REQUIRED":138,"RESOLVED_EXISTING":1,"UNRESOLVED":790}`
- binding: `{"BLOCKED":790,"CANDIDATE":138,"EXISTING_RESOLVED":1}`
- projection: `{"CURRENT":929}`
- promotion: `{"BLOCKED":2,"ELIGIBLE_CANDIDATE":139,"REGISTER_TARGET_FIRST":788}`
- Work Entry: `{"BLOCKED":2,"REGISTER_TARGET_FIRST":927}`

Both physical DRIFT records remain exact conflicts:

- `TGT.CENSUS.TABLET.3B2FED34BC21B5C9FEEC.V1`
- `TGT.CENSUS.TABLET.850AD4CEF4CCD12BCD05.V1`

The one proven existing Identity binding reuse remains unchanged:

- target: `TGT.CENSUS.TABLET.0DC6BC69B3278EC225CE.V1`
- binding: `BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1`
- visual meaning: `ACT.primary`
- Identity recipe: `REC.button.primary`
- application layer: `LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE`
- Work Entry: `REGISTER_TARGET_FIRST`

The resolved binding was checked against `BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1`. Its target authority proves route, region, slot, component UI, owner, selector and implementation layer; its layer ID matches the candidate application layer. The candidate `componentId` equals that proven component UI coordinate. This clears the only temporary reference-domain validation blocker without modifying source semantics.

## Provenance and drift

The five immutable worker source files are SHA-256 pinned in `MANIFEST.json`.

The read-only dry-run compared source base `57b01ad8bda043ec25763203354b686341bace09` to certification base `8cc1918c5e015d1408335c15313e7364e04859c2` and found:

- **0** changed paths among the **13** recorded Tablet authority snapshots;
- **0** changed paths among the **40** unique canonical-source/generated-output paths referenced by the 929 records.

Thus no relevant source/authority drift required recensus, recomputation or repair.

## Reference validation

- Target IDs: **929/929** present in the recorded/current-equivalent Tablet Target Index.
- Populated direct physical census coordinates: validated against recorded/current-equivalent Visual Control authority.
- Atlasfin recipe/adapter IDs: validated against recorded/current-equivalent Atlasfin registries.
- Identity adapter/recipe/binding IDs: validated against recorded/current-equivalent Identity registries.
- NDC: **0 populated NDC IDs/refs**; all 929 remain `UNRESOLVED`, so no neutral meaning was invented.
- Authority-qualified evidence references: strict domain syntax preserved.
- Existing-binding stronger coordinates: exact Identity binding proof used only for the one `EXISTING_RESOLVED` record.

## Guardrails held

- Materiality Catalog inspected/fallback: **no**
- broad rediscovery: **no**
- canonical IDs minted: **no**
- canonical Identity/RIFAT/NDC/Target Index mutation: **no**
- product/runtime mutation: **no**
- `prisma-html/FILES_MANIFEST.json` refresh: **no**
- PR opened: **no**
- runtime visual certification claimed: **no**

This derivative certifies corpus validity and provenance only. It does not upgrade promotion readiness or authorize canonical promotion / `GVAE_EXACT_APPLY`.
