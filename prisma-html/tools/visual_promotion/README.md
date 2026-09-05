# PRISMA Visual Promotion Control Plane

Chat 6 machine layer for the visual-promotion-parallel cohort.

This package validates and reconciles candidate-only promotion evidence. It does not write product runtime, populate surface candidate shards, assign canonical IDs, edit global authority registries, or claim runtime visual certification.

Core invariants:

- Cohort surfaces are tablet, pc, mobile, shared-ui.
- Web, Chart Lab and Control Center are protected.
- Existing Visual Control census / Target Index is reused. DISCOVERY_ONLY is not undiscovered.
- Atlasfin is the priority visual reference and matches require explicit structured-registry evidence.
- Materiality remains STANDBY_USER_INVOKED_ONLY and is rejected as automatic input.
- Cross-authority IDs require authority qualification.
- Candidate is not authority. Binding is not mutation authorization. Source-static is not runtime visual green.

Commands:

    PYTHONPATH=prisma-html/tools python -m visual_promotion.cli validate-write-ownership
    PYTHONPATH=prisma-html/tools python -m visual_promotion.cli validate-shard --manifest MANIFEST.json --candidates CANDIDATES.jsonl --unresolved UNRESOLVED.jsonl --conflicts CONFLICTS.jsonl --expected-head <sha>
    PYTHONPATH=prisma-html/tools python -m visual_promotion.cli current-truth --target-index <target-index.json>
    PYTHONPATH=prisma-html/tools python -m visual_promotion.cli plan --outcomes <CANDIDATES.jsonl>

The composer is proposal-only. canonicalMutationPerformed, canonicalIdsAssigned, runtimeVisualGreen and productionReady remain false.

## Candidate corpus certification

The raw-worker normalizer is fail-closed and recognizes only the exact legacy worker heads and file hashes in `legacy-worker-intake.registry.json`. Original worker bytes remain immutable and normalization may change representation only.

Final aggregation additionally requires every exact owner certification head/file in `certification-intake.registry.json`. Chat 6 independently regenerates each strict normalized record from raw evidence, proves object equality with the owner-certified derivative, proves each owner certification row points back to the same raw source head/file/line/record hash, validates Chat 5's 2,421 Atlasfin reference certifications, and then pins those certification row hashes into the global corpus.

After all accepted raw and certification bytes are assembled:

```bash
PYTHONPATH=prisma-html/tools python -m visual_promotion.cli certify-final-corpus --repo-root .
```

Outputs live under `prisma-html/governance/visual-promotion/contracts/corpus-certification/`. A corpus PASS never authorizes canonical promotion, product/runtime mutation, broad rediscovery, Materiality Catalog use, projection repair, or whole-surface APPLY_READY.
