# Chat 3 - Mobile Visual Promotion Candidate Shard

Base HEAD: `57b01ad8bda043ec25763203354b686341bace09`

## Scope and operating constraints

- Lane: Chat 3 - Mobile Promotion.
- Write root: `prisma-html/governance/visual-promotion/candidates/mobile/**`.
- Current Mobile Visual Control/Target Index census was reused. No broad rediscovery was performed.
- Atlasfin was reviewed first as the priority visual reference.
- Materiality Catalog remained `STANDBY_USER_INVOKED_ONLY` and was not inspected or consumed.
- No Mobile product file, RIFAT canonical source, generated projection, global Identity registry, Target Index, visual-source-manifest, Factory Ledger, Evidence Index, Web, Chart Lab or Control Center file was modified.
- Candidate-only output. No canonical ID was minted.

## Zero-loss target accounting

| Outcome file | Targets |
| --- | ---: |
| CANDIDATES.jsonl | 0 |
| UNRESOLVED.jsonl | 133 |
| CONFLICTS.jsonl | 138 |
| Total | 271 |

Input census targets: **271**. Every existing Mobile target ID appears exactly once.

## Target-level projection status

| projectionStatus | Targets |
| --- | ---: |
| CURRENT | 133 |
| DRIFT | 138 |
| MISSING | 0 |
| NOT_REQUIRED | 0 |
| UNRESOLVED | 0 |

All 138 DRIFT records are in `prisma-mobile-dashboard.module.css`. The current Target Index already carries `projection-hash-drift` on those targets.

The drift is not greened by choosing a repair direction. Governed Mobile cleanup commit `731574f97dba0ec46420369b777071500ce2f833` removed retired MultiContext residue from the product projection after the current RIFAT Mobile source was adopted. One census target, `TGT.CENSUS.MOBILE.C30F6FBF52AEFF7B5E02.V1`, directly intersects that rule change: `.crystalCommand, .multiContextRoot` became `.crystalCommand`. For the other drift records, this shard records file-level drift without asserting an unproven target-local selector change.

This supports two simultaneous observations without collapsing them into a fake green:

1. the changed Mobile product projection is a legitimate newer runtime/product candidate requiring authority reconciliation;
2. the current RIFAT canonical authority is stale for the retired MultiContext residue.

Chat 3 intentionally does not decide whether source or product should be repaired.

## Manifest-level projection observation

The current Mobile visual-source-manifest has eight Mobile projection entries. Exact current-file review found:

- 6 byte-current source/output pairs;
- 1 drifted pair: `prisma-mobile-dashboard.module.css`;
- 1 missing product output: `prisma-mobile-multi-context-switcher.module.css`, which was intentionally removed by the governed MultiContext cleanup and has no current census target.

The manifest-only missing output is reported here separately and is not fabricated into an extra census target.

## Physical evidence reuse

- Exact expanded-layer join: 271 / 271.
- Exact CSS-owner join: 271 / 271.
- Exact route ID proven without ambiguity: 11 targets.
- Exact region ID proven without ambiguity: 2 targets.
- Exact target-specific component and slot bindings were not provable from the current expanded Mobile rows, so those fields remain null.

## Atlasfin-first classification

Atlasfin exposes `ADP.MB.TOUCH.V2` for Mobile. Existing Atlasfin layer recipes also declare `SURF.MB.OWNER` compatibility, but their Mobile target bindings are `BLOCKED_BY_MISSING_ELEMENT_BINDING`. Therefore this shard records `atlasfinMatchStatus=AMBIGUOUS` and does not promote a family, preset or recipe merely from layer-name or selector similarity.

Materiality Catalog was not used as fallback.

## NDC and Identity

NDC already contains the Mobile surface projection `SURF.mb.owner_home`, which is retained only as a supporting qualified reference. No exact neutral primary meaning is proven per census target, so `ndcPrimaryId` remains null and `ndcResolutionStatus=UNRESOLVED`.

Identity already contains adapter `prisma.adapter.mobile.v1`, but there are no current Mobile element bindings and no current Mobile Identity recipes in the inspected canonical registries. The current adapter registry reports `BINDING_READY_SOURCE_ONLY`, while the adapter source file still says `DISCOVERY_REQUIRED`; Chat 3 records no repair and leaves binding/application blocked.

## Promotion result

All 271 records remain `promotionStatus=REGISTER_TARGET_FIRST` and `workEntryDecision=REGISTER_TARGET_FIRST`.

This is deliberate. Physical census evidence is current and reusable, but semantic meaning, exact recipe, exact binding and layer-application policy are not complete. The shard advances the control plane by preserving exact coordinates and classifying drift without inventing authority.
