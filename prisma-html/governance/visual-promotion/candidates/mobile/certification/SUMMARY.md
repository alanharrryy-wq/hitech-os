# Chat 3 - Mobile Candidate Corpus Certification

Phase: `CANDIDATE_CORPUS_CERTIFICATION_PARALLEL`

Certification branch base: `8cc1918c5e015d1408335c15313e7364e04859c2`

Immutable source worker: `visual-promotion-chat3-mobile-20260904` @ `7f32ce6f1b602a14781fa2f4f3f323035f8029ec`

Source base: `57b01ad8bda043ec25763203354b686341bace09`

## Result

- **271 / 271 corpus-valid**
- **invalid = 0**
- **semanticMutationCount = 0**
- **duplicate/missing/extra targets = 0 / 0 / 0**
- projection partition preserved exactly: **133 CURRENT + 138 DRIFT**
- certification: **271 VALID_REGISTER_TARGET_FIRST**
- no `GVAE_EXACT_APPLY`
- no canonical promotion
- no RIFAT-vs-product repair direction selected

## Representation-only normalization

The derivative changes only the strict intake representation already identified by the Control Plane:

1. the legacy top-level `projection` object is flattened into the strict candidate top-level projection fields;
2. `ndc.ndcRefs` moves from authority-qualified strings to the domain-scoped raw NDC IDs required by the strict candidate validator;
3. previously unqualified repository/path evidence is wrapped as strict authority-qualified evidence references while preserving every original raw value in `CERTIFICATION.jsonl`;
4. `atlasfin.atlasfinAdapterId` moves from `atlasfin::ADP.MB.TOUCH.V2` to raw `ADP.MB.TOUCH.V2`, with the original qualified value preserved in certification provenance.

No semantic field is promoted or repaired by these conversions.

## Provenance

Every normalized target records its exact original source head, source file, source line and SHA-256 of the original UTF-8 JSONL line. Each certification row also pins the normalized record hash.

The original worker bytes remain immutable at `7f32ce6f1b602a14781fa2f4f3f323035f8029ec`.

## Reference validation

- NDC `SURF.mb.owner_home`: present in the current NDC surface registry.
- Atlasfin `ADP.MB.TOUCH.V2`: present in the current Atlasfin surface-adapter registry.
- Identity `prisma.adapter.mobile.v1`: present in the current Identity surface-adapter registry.
- Materiality Catalog remained `STANDBY_USER_INVOKED_ONLY` and was not inspected.

## Guardrails preserved

- no broad rediscovery;
- no product/runtime/CSS/TSX mutation;
- no RIFAT or product projection rewrite;
- no canonical ID minting;
- no global Identity/NDC/Target Index/visual-source-manifest mutation;
- no `prisma-html/FILES_MANIFEST.json` refresh;
- no PR opened by Chat 3.

Chat 3 certification is a record-validity derivative only. It does not make any Mobile target APPLY_READY or runtime visually certified.
