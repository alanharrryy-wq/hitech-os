# Chat 2 — PC Candidate Corpus Certification

Phase: `CANDIDATE_CORPUS_CERTIFICATION_PARALLEL`

## Result

PASS_PC_CANDIDATE_CORPUS_CERTIFIED

- source branch: `agent/chat2-pc-promotion-20260904`
- source head: `896f4a7f3463dc4ad1267f3e7d8f6a9fd70f4078`
- source base: `57b01ad8bda043ec25763203354b686341bace09`
- certification branch base: `8cc1918c5e015d1408335c15313e7364e04859c2`
- strict Control Plane source head: `7cc48fa49906c8f443b267fd6c3590fd3f4340fb`
- input records: 827
- normalized records: 827
- certification rows: 827
- invalid rows: 0
- duplicate target IDs: 0
- semanticMutationCount: 0
- source accounting: 186 candidates + 640 unresolved + 1 conflict
- certification labels: VALID_REGISTER_TARGET_FIRST=827
- physical status: CURRENT=826, DRIFT=1
- projection status: CURRENT=688, MISSING=139
- Atlasfin status: MATCHED_RECIPE=186, NO_MATCH=641
- NDC status: UNRESOLVED=827
- Identity binding status: BLOCKED=827
- promotion status: REGISTER_TARGET_FIRST=827
- Work Entry: REGISTER_TARGET_FIRST=827

## Normalization

The legacy PC source manifest was converted into the strict `prisma.visual-promotion.candidate-shard.v1` envelope for this derivative. The 827 source candidate records already conform to the strict candidate contract, so `NORMALIZED.jsonl` preserves every source record byte-for-byte excluding only original file-boundary placement. No record field was rewritten.

Each certification row pins source branch, source head, source base, source file, source bucket, source line, source file Git blob SHA, source file SHA-256 and deterministic source-record SHA-256. The record hash is SHA-256 over the exact UTF-8 JSON record bytes excluding the line terminator.

## Preserved blockers and unresolved truth

- `TGT.CENSUS.PC.097AB2F857F353CA4288.V1` remains a physical `DRIFT` conflict with Target Index selector `.supplier-readable-v07` and recorded expanded selector `.supplier-readable-v07 *`.
- All 139 projection `MISSING` states remain `MISSING`.
- All 827 NDC resolutions remain `UNRESOLVED`.
- All 827 Identity binding statuses remain `BLOCKED`.
- All 827 promotion and Work Entry decisions remain `REGISTER_TARGET_FIRST`.
- Bucket placement does not upgrade promotion readiness. The 186 source `CANDIDATES` records therefore certify as `VALID_REGISTER_TARGET_FIRST`, not as eligible or apply-ready.

## Authority and safety

Current structured Atlasfin recipe/adapter references and the PC Identity adapter reference validate. Target Index and expanded PC layer authority blobs remain identical to the worker-manifest provenance used for the source conflict.

Materiality Catalog was not inspected or consumed. No broad rediscovery, projection repair, canonical ID minting, product/runtime mutation, global authority mutation, or `prisma-html/FILES_MANIFEST.json` update was performed.

This certification proves record validity and provenance only. It does not authorize canonical promotion, GVAE APPLY, runtime visual readiness, or whole-surface readiness.
