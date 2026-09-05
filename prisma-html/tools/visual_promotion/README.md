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

The corpus-certification phase is fail-closed and candidate-only. It recognizes only the exact legacy worker heads and file hashes in `legacy-worker-intake.registry.json`, preserves original raw bytes as provenance, normalizes representation only, and refuses semantic mutation.

Run only after the four exact raw candidate shards are assembled at their canonical candidate paths:

```bash
PYTHONPATH=prisma-html/tools python -m visual_promotion.cli certify-corpus --repo-root .
```

Outputs are written under `prisma-html/governance/visual-promotion/contracts/corpus-certification/`. A corpus PASS never authorizes canonical promotion, product/runtime mutation, broad rediscovery, Materiality Catalog use, or whole-surface APPLY_READY.
