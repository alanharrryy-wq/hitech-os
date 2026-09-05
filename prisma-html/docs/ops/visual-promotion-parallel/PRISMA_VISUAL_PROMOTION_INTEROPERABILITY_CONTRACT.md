---
title: PRISMA Visual Promotion Interoperability Contract
status: CANONICAL_PARALLEL_INTEROPERABILITY_CONTRACT
scope: Tablet, PC, Mobile, Shared UI, Atlasfin
owner_domain: PRISMA visual promotion
materiality_catalog: STANDBY_USER_INVOKED_ONLY
---

# PRISMA Visual Promotion Interoperability Contract

## 0. Purpose

This contract exists so multiple AI agents can work on PRISMA visual semantic/application promotion in real parallel without inventing different names, IDs, meanings, statuses, joins, authorities or write paths.

It governs **cross-domain interoperability**. It does not replace domain authorities.

The central operating sentence is:

> **Reuse physical truth. Resolve neutral meaning. Use Atlasfin as the priority visual reference. Preserve authority domains. Workers propose. Canonical composers assign. Unknown stays unknown.**

A second rule is mandatory:

> **An ID is never meaningful across systems without its authority domain.**

A third rule is mandatory:

> **The Surface Visual Governor Materiality Catalog is not an automatic source for this cohort. It is STANDBY / USER-INVOKED-ONLY until the repository owner explicitly invokes it for a named task.**

## 1. Authority precedence

When information conflicts, use this order:

1. machine-readable authority in its own domain;
2. the current task-exact Authority Mesh and Layer Map for authorized scope;
3. this interoperability contract for cross-domain naming, candidate exchange and parallel ownership;
4. the parallel-chat prompt for lane-specific responsibility;
5. README prose and historical evidence.

This contract must never be used to overwrite a stronger machine-readable authority. If a conflict is found, record it and block the affected candidate.

### Domain ownership

| Domain | Canonical job |
|---|---|
| Factory Ledger | capability maturity, anti-rework truth, next gate, doNotRebuild |
| Authority Mesh | task-exact scope and allowed/protected layers |
| Code Atlas / UIMAP | repository intelligence and physical UI census |
| NDC | neutral operational meaning, scope, provenance, canonical concepts |
| Identity | editable visual meaning, profiles, canonical recipes, tokens, assets, adapters |
| RIFAT / prisma-ui | exact surface/route/owner/region/slot/layer location truth |
| Visual Control | physical visual census and safety classification |
| Target Index | deterministic persistent application address book |
| Atlasfin | priority human visual cockpit/reference and portable visual intent |
| Projection manifest | canonical-source to generated-product projection truth |
| Work Entry Gate | pre-edit decision boundary |
| GVAE | governed exact visual writer after authorization |
| Runtime QA | proof of rendered outcome |

## 2. Scope of this cohort

Canonical `surfaceKey` values in this cohort are exactly:

`tablet`, `pc`, `mobile`, `shared-ui`.

Atlasfin is not a product `surfaceKey` in this cohort. It is the priority cockpit/reference.

The following surfaces are explicitly out of scope and protected:

`web`, `chart-lab`, `control-center`.

A worker may observe an out-of-scope consumer reference but may not promote, rewrite, recensus or mutate it.

## 3. Physical census reuse and anti-rework

The all-surface Visual Control census and generated Target Index already exist.

For this contract:

- `VISUAL_CONTROL_CENSUS_TARGET / DISCOVERY_ONLY` means the physical CSS/layer coordinate exists in governed census evidence but lacks complete exact application authority.
- `DISCOVERY_ONLY` never means `UNDISCOVERED`.
- No worker may run broad rediscovery merely because a target is `DISCOVERY_ONLY`.
- Existing `targetId`, selector, owner, source, layer and projection evidence must be reused when current.
- Broad discovery is allowed only when current authority proves that the target is genuinely absent, stale, drifted beyond reusable evidence, or explicitly requested by a separate authorized task.
- A worker that finds existing current census must set `physicalStatus=CURRENT` and continue to semantic/binding promotion.

## 4. Atlasfin-first policy

Atlasfin is the priority visual reference for this cohort.

Canonical Atlasfin sources include:

- `prisma-html/extras/atlasfin/assets/data/atlas.manifest.json`
- `visual-property.registry.json`
- `visual-family.registry.json`
- `visual-preset.registry.json`
- `visual-recipe.registry.json`
- `visual-state.registry.json`
- `visual-variant.registry.json`
- `surface-adapter.registry.json`
- `visual.recipe.registry.json`
- Atlasfin schemas, validators and generated cockpit evidence.

The 418 Atlasfin catalog elements are not assumed to be 418 recipes. An element may be a foundation, property, family, preset, recipe, state, variant, composition/pattern, reference-only item or another governed visual concept.

A worker may match a product target to an Atlasfin element/family/preset/recipe only when evidence supports the match. Name similarity alone is insufficient.

No Atlasfin record may silently become canonical Identity authority. Atlasfin may propose or reference. Canonical Identity/RIFAT authority must be separately resolved.

## 5. Surface Visual Governor Materiality Catalog standby

The Materiality Catalog exists and is intentionally preserved because it is rich and potentially valuable.

Canonical known location:

`apps/terminal-de-venta-system/products/pc/app/public/surface-visual-governor/reference-visual/latest/materiality-catalog.registry.json`

For this cohort its policy is:

- `status = STANDBY_USER_INVOKED_ONLY`
- automatic discovery: forbidden;
- automatic fallback after Atlasfin miss: forbidden;
- automatic recipe promotion: forbidden;
- automatic semantic inference: forbidden;
- automatic application source: forbidden;
- direct agent use requires explicit repository-owner invocation for a named task.

If Atlasfin has no match, record `atlasfinMatchStatus=NO_MATCH`. Do not inspect Materiality as a fallback.

## 6. Authority-qualified references

### 6.1 Human form

When prose needs a cross-authority ID, use:

`<authorityDomain>::<rawId>`

Examples:

`ndc::ACT.sale.checkout`

`atlasfin::REC.button.governed.v2`

`identity::REC.button.primary`

`target-index::TGT.CENSUS.TABLET.0123456789ABCDEF.V1`

`rifat::tablet.pos.route`

### 6.2 Machine form

Machine-readable cross-authority references use an object:

```json
{
  "authorityDomain": "atlasfin",
  "id": "REC.button.governed.v2",
  "version": "2.0.0",
  "sha256": null
}
```

`authorityDomain` and `id` are required. `version` and `sha256` are optional when not available.

### 6.3 Allowed authorityDomain values

The canonical set for this workflow is:

`ndc`, `atlasfin`, `identity`, `rifat`, `visual-control`, `target-index`, `projection-manifest`, `factory-ledger`, `code-atlas`, `work-entry-gate`, `gvae`.

Do not invent aliases such as `atlas`, `rifat-ui`, `ui-control` or `visual-db`.

## 7. ID immutability and who may create IDs

Existing IDs are immutable. Workers never rename an existing ID to make naming prettier.

### Surface workers may

- reuse an existing NDC ID;
- reuse an existing Atlasfin ID;
- reuse an existing Identity/RIFAT/Target Index ID;
- emit a candidate key local to their own candidate shard;
- emit a proposed semantic label/slug without assigning a new canonical ID.

### Surface workers may not

- create a new canonical `BND.*`;
- create a new exact `TGT.*`;
- create or hand-edit `TGT.CENSUS.*`;
- create a new canonical `LYR.*`;
- create a new canonical Identity `REC.*`, `FAM.*` or `PRESET.*`;
- create a new NDC neutral ID from intuition;
- create a new global surface adapter.

New canonical IDs are assigned only by a deterministic canonical composer after dedupe, collision checks and evidence review.

## 8. ID families and construction rules

### 8.1 NDC IDs

NDC keeps its existing canonical grammar unchanged:

`<PREFIX>.<namespace>.<slug>[.<qualifier>...]`

Official NDC prefixes remain defined by `apps/terminal-de-venta-system/docs/ndc/02_NDC_ID_GRAMMAR_AND_NAMING.md`.

Examples include `ENT.sale`, `EVT.sale.created`, `ACT.sale.checkout`, `MET.sales.today`, `SURF.pc.sales_control`, `WID.pc.sales.today_card`.

Workers must reuse existing NDC IDs when proven. New NDC IDs require NDC governance/curation and are never minted by a surface worker.

### 8.2 Visual meaning IDs

Purely visual meanings must not take an NDC prefix merely because the word sounds convenient.

Existing visual IDs remain immutable, including historical identifiers such as `identity::ACT.primary` and Atlasfin `VIS.*` IDs.

For future canonical visual meanings, the reserved visual prefix is `VIS.`. A worker does not assign the final new `VIS.*`; it proposes a semantic slug and evidence for composer/curation.

Never assume `ndc::ACT.*` and `identity::ACT.*` are the same domain.

### 8.3 Atlasfin catalog IDs

Atlasfin catalog element IDs such as `A.PALETA_BASE` or `B.PANEL_MATERIAL` remain Atlasfin catalog IDs.

Use field `atlasfinCatalogElementId`.

They are not product component IDs and are not Identity recipe IDs.

### 8.4 Atlasfin UI IDs

Atlasfin internal cockpit/control IDs such as `ATL-SMOKE-CONTROL-01` use field `atlasfinUiId`.

They locate Atlasfin UI only unless a separate contract proves another meaning.

### 8.5 Atlasfin families, presets and recipes

Use separate fields:

- `atlasfinFamilyId`
- `atlasfinPresetId`
- `atlasfinRecipeId`
- `atlasfinLegacyRecipeId` for historical `RCP.ATLAS.*` when needed.

Never put an Atlasfin recipe directly into `identityRecipeId` unless the canonical Identity registry explicitly contains that exact ID.

### 8.6 Identity IDs

Canonical Identity fields are distinct:

- `identityProfileId`
- `identityRecipeId`
- `identityAdapterId`

An `identityRecipeId` must point to the canonical Identity recipe registry, never merely to an Atlasfin registry.

### 8.7 Binding IDs

Existing canonical binding IDs use `existingBindingId`.

A worker that needs a new binding emits `bindingCandidateKey`, not a fabricated `BND.*`.

The composer alone assigns a canonical `BND.*` after dedupe and collision checks.

### 8.8 Target IDs

Generated census target IDs `TGT.CENSUS.*` are owned by the Target Index generator.

Surface workers must preserve them byte-for-byte.

Existing exact targets remain immutable.

New exact `TGT.*` IDs are composer-generated only after semantic/binding/application authority is proven.

### 8.9 Layers

Always distinguish:

- `implementationLayerId`: physical layer/location discovered by Visual Control/RIFAT;
- `applicationLayerId`: certified semantic/application layer used for exact application authority.

Never collapse both into a generic `layerId` in candidate exchange data.

### 8.10 Surface identifiers and adapters

Use `surfaceKey` for the canonical cohort key: `tablet`, `pc`, `mobile`, `shared-ui`.

Keep domain-specific identifiers separate:

- `ndcSurfaceId`
- `atlasfinSurfaceId`
- `identityAdapterId`
- `atlasfinAdapterId`

Do not normalize the raw ID itself. Normalize only the `surfaceKey`.

Atlasfin `shared_ui` normalizes to canonical `surfaceKey=shared-ui`; the raw Atlasfin value remains preserved in its authority-qualified record.

## 9. Canonical field vocabulary

Candidate exchange data uses explicit field names. Generic ambiguous fields are forbidden when a qualified field exists.

### Identity and location

- `baseHead`
- `candidateOnly`
- `surfaceKey`
- `targetId`
- `recordKind`
- `enforcement`
- `routeId`
- `regionId`
- `slotId`
- `componentId`
- `componentUiId`
- `ownerId`
- `ownerFile`
- `renderSourceFile`
- `styleSourceFile`
- `selector`
- `implementationLayerId`
- `applicationLayerId`

### Source/projection

- `canonicalSourcePath`
- `generatedOutputPath`
- `sourceSha256`
- `outputSha256`
- `projectionMode`
- `projectionStatus`

### Meaning

- `ndcPrimaryId`
- `ndcRefs`
- `visualMeaningId`
- `visualMeaningCandidate`

Do not use `semanticId` alone. It is too ambiguous.

### Atlasfin

- `atlasfinCatalogElementId`
- `atlasfinUiId`
- `atlasfinFamilyId`
- `atlasfinPresetId`
- `atlasfinRecipeId`
- `atlasfinLegacyRecipeId`
- `atlasfinAdapterId`
- `atlasfinMatchStatus`

### Canonical Identity/application

- `identityProfileId`
- `identityRecipeId`
- `identityAdapterId`
- `existingBindingId`
- `bindingCandidateKey`
- `bindingStatus`
- `promotionStatus`
- `workEntryDecision`

### Evidence

- `evidenceRefs`
- `confidence`
- `blockers`
- `notes`

Do not use a generic `status` when the dimension-specific status field exists.

## 10. Closed status vocabularies

### physicalStatus

`CURRENT`, `STALE`, `DRIFT`, `MISSING`, `NOT_APPLICABLE`

### atlasfinMatchStatus

`MATCHED_EXACT`, `MATCHED_FAMILY`, `MATCHED_PRESET`, `MATCHED_RECIPE`, `AMBIGUOUS`, `NO_MATCH`, `NOT_APPLICABLE`

A record uses the strongest directly supported match. A more general family match must not be upgraded to exact.

### ndcResolutionStatus

`RESOLVED_EXISTING`, `CANDIDATE_REVIEW_REQUIRED`, `UNRESOLVED`, `NOT_APPLICABLE`

### visualMeaningStatus

`RESOLVED_EXISTING`, `CANDIDATE_REVIEW_REQUIRED`, `UNRESOLVED`, `NOT_APPLICABLE`

### bindingStatus

`EXISTING_RESOLVED`, `CANDIDATE`, `BLOCKED`, `NOT_APPLICABLE`

### projectionStatus

`CURRENT`, `DRIFT`, `MISSING`, `NOT_REQUIRED`, `UNRESOLVED`

### promotionStatus

`ELIGIBLE_CANDIDATE`, `REGISTER_TARGET_FIRST`, `BLOCKED`, `NOT_APPLICABLE`

`ELIGIBLE_CANDIDATE` is not application authorization.

### confidence

Reuse NDC confidence vocabulary:

`low`, `medium`, `high`, `verified`.

A worker may not use `verified` unless direct machine-readable authority/evidence proves the relationship.

### Work Entry decision

The Work Entry Gate remains closed to exactly:

`GVAE_EXACT_APPLY`, `SURFACE_BATCH_PLAN`, `REGISTER_TARGET_FIRST`, `BLOCKED`.

No candidate status may masquerade as one of these decisions.

## 11. Relationship vocabulary

When modeling NDC/cross-system edges, reuse existing NDC edge verbs where applicable:

`belongs_to`, `scoped_by`, `claims_slot`, `enables`, `requires`, `emits`, `writes`, `reads`, `updates`, `projects_to`, `represented_by`, `derived_from`, `evidenced_by`, `observed_by`, `validated_by`, `curated_by`, `conflicts_with`, `reconciles`, `monetized_by`, `owned_by`, `blocks`, `supersedes`, `aliases`, `implements`, `exports`, `imports`.

Do not invent synonyms such as `mapsTo`, `linksTo`, `correspondsTo` or `connectsTo` when an existing edge type already expresses the relation.

## 12. Candidate record contract

Every surface candidate record must be candidate-only and preserve its original target identity.

Minimum conceptual shape:

```json
{
  "candidateOnly": true,
  "baseHead": "<40-char-git-sha>",
  "surfaceKey": "tablet",
  "targetId": "TGT.CENSUS.TABLET....V1",
  "physicalStatus": "CURRENT",
  "physical": {
    "routeId": null,
    "regionId": null,
    "slotId": null,
    "componentId": null,
    "componentUiId": null,
    "ownerId": null,
    "styleSourceFile": null,
    "selector": ".example",
    "implementationLayerId": "products....example"
  },
  "ndc": {
    "ndcPrimaryId": null,
    "ndcRefs": [],
    "ndcResolutionStatus": "UNRESOLVED"
  },
  "visual": {
    "visualMeaningId": null,
    "visualMeaningCandidate": null,
    "visualMeaningStatus": "UNRESOLVED"
  },
  "atlasfin": {
    "atlasfinCatalogElementId": null,
    "atlasfinFamilyId": null,
    "atlasfinPresetId": null,
    "atlasfinRecipeId": null,
    "atlasfinAdapterId": null,
    "atlasfinMatchStatus": "NO_MATCH"
  },
  "identity": {
    "identityProfileId": null,
    "identityRecipeId": null,
    "identityAdapterId": null,
    "existingBindingId": null,
    "bindingCandidateKey": null,
    "bindingStatus": "BLOCKED"
  },
  "application": {
    "applicationLayerId": null,
    "projectionStatus": "UNRESOLVED",
    "promotionStatus": "REGISTER_TARGET_FIRST",
    "workEntryDecision": "REGISTER_TARGET_FIRST"
  },
  "confidence": "low",
  "evidenceRefs": [],
  "blockers": [],
  "notes": []
}
```

Null is valid when authority is missing. Invented data is not.

## 13. Deduplication keys

Surface workers do not dedupe across surfaces by inventing a shared canonical ID.

They may emit deterministic candidate fingerprints composed from evidence such as:

- authority-qualified existing meaning IDs;
- Atlasfin family/preset/recipe references;
- normalized semantic labels;
- exact RIFAT coordinates;
- product selector/source evidence.

The canonical composer decides whether candidates from different surfaces represent one neutral meaning, one visual meaning, one recipe family, separate meanings or an unresolved collision.

## 14. Shared UI rules

Shared UI is a neutral/shared source surface and may have consumers in Tablet, PC, Mobile or excluded surfaces.

The Shared UI worker may record consumer references but may only write its own `shared-ui` candidate shard.

A consumer relationship never grants permission to write the consumer surface.

One Shared UI source should not be duplicated into separate semantic authorities merely because several product surfaces consume it.

## 15. Projection and drift rules

Projection status is independent from semantic readiness.

`CURRENT` means the known canonical-source/output relationship is current according to governing evidence.

`DRIFT` means source/output or current authority disagrees and requires reconciliation.

`MISSING` means a projection appears required but no governed mapping is proven.

`NOT_REQUIRED` means evidence proves the target is not a generated projection.

`UNRESOLVED` means the worker cannot prove which category applies.

Never repair projection drift merely to make a worker shard green. Never overwrite a newer legitimate runtime from stale authority.

## 16. Atlasfin match rules

Order of evidence preference:

1. exact Atlasfin element/recipe/preset match supported by semantics and target evidence;
2. exact family match;
3. compatible recipe/preset candidate with explicit ambiguity;
4. no match.

Text/name similarity alone is insufficient.

If multiple Atlasfin choices are plausible, set `AMBIGUOUS`.

If no Atlasfin choice is proven, set `NO_MATCH`.

No Materiality fallback is allowed.

## 17. Parallel write ownership

The six lanes have disjoint write ownership.

### Chat 1 Tablet

May write only:

`prisma-html/governance/visual-promotion/candidates/tablet/**`

### Chat 2 PC

May write only:

`prisma-html/governance/visual-promotion/candidates/pc/**`

### Chat 3 Mobile

May write only:

`prisma-html/governance/visual-promotion/candidates/mobile/**`

### Chat 4 Shared UI

May write only:

`prisma-html/governance/visual-promotion/candidates/shared-ui/**`

### Chat 5 Atlasfin Bridge

May write only new/assigned bridge content under:

`prisma-html/extras/atlasfin/bridge/**`

It may not rewrite Atlasfin source registries as part of bridge construction unless a later separately authorized task explicitly says so.

### Chat 6 Control Plane

May write:

`prisma-html/tools/visual_promotion/**`

`prisma-html/governance/visual-promotion/contracts/**`

and, when task authority specifically permits it, bounded Work Entry Gate code/tests needed for anti-rediscovery and schema enforcement.

It may not populate surface candidate shards.

### Status-channel exception to write ownership

Coordination status is the only cross-cutting write exception for all six lanes.

A worker may additionally update only its own mailbox under `apps/terminal-de-venta-system/docs/ops/visual-promotion-parallel-status/<chat-mailbox>/`, and only on the dedicated status branch defined by `status-channel/STATUS_CHANNEL_CONTRACT.json`.

Allowed status files: `STATUS.json` and `LOG.md` only.

The status branch must contain no product/runtime mutation, candidate shard, canonical authority change, `FILES_MANIFEST.json` change or another chat's mailbox change. Status is coordination/evidence only and never promotes a candidate, resolves a binding, authorizes GVAE or certifies runtime.


## 18. Files forbidden to parallel workers

During independent worker execution, none of the six lanes may hand-edit or regenerate:

- `prisma-html/authority/rifat/identity/registries/element-bindings.registry.json`
- `prisma-html/authority/rifat/identity/registries/recipe.registry.json`
- `prisma-html/authority/rifat/identity/compiled/**`
- `prisma-html/authority/rifat/prisma-ui/visual-control/target-index/**`
- `prisma-html/authority/rifat/visual-source-manifest.json`
- `prisma-html/FILES_MANIFEST.json`
- `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json`
- `PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json`

These are global integration outputs or global authority.

The integration stage refreshes `FILES_MANIFEST.json` once, after all accepted `prisma-html` bytes are assembled.

## 19. Base-head and drift protocol

Each lane records exact `baseHead` in every shard manifest.

All lanes should start from the same canonical main whenever practical, but no lane waits for another.

If base heads differ, integration must compare the exact input authorities used by each lane. Mixed-base candidates are accepted only if the relevant source/authority hashes remain equivalent or a fresh revalidation proves them.

No silent rebase may upgrade stale evidence.

## 20. Candidate shard layout

Surface workers should produce deterministic files under their owned directory:

`MANIFEST.json`

`CANDIDATES.jsonl`

`UNRESOLVED.jsonl`

`CONFLICTS.jsonl`

`SUMMARY.md`

The exact machine schema is owned by the Control Plane contract once implemented. Until then, the field names and enums in this document and the vocabulary registry are normative.

Each input census target must reconcile to exactly one outcome record. No target may disappear.

## 21. Required accounting

For each surface:

`input census count = candidate/resolved + unresolved + blocked/not-applicable`

Counts must reconcile exactly.

A worker must report:

- input target count;
- current physical count;
- Atlasfin match counts;
- NDC resolution counts;
- binding candidate counts;
- projection status counts;
- unresolved/blocker counts;
- output count.

Zero-loss accounting is mandatory.

## 22. No-fake-green rules

The following claims are forbidden unless separately proven:

- `DISCOVERY_ONLY` means unmapped;
- Atlasfin catalogued means canonical Identity recipe;
- family match means exact recipe match;
- candidate means resolved binding;
- resolved binding means authorized mutation;
- source-static green means runtime visual green;
- one product surface's semantic interpretation automatically governs another;
- a visual name implies NDC meaning;
- a projection drift should be repaired in a chosen direction without history/current-authority review.

## 23. Work Entry integration

The Work Entry Gate should eventually make anti-rework distinctions machine-readable.

Existing four decisions do not change.

For a current census target needing promotion, preferred reason vocabulary includes:

`REUSE_EXISTING_CENSUS_SEMANTIC_PROMOTION_REQUIRED`

For attempted unnecessary broad rediscovery over current census:

`BROAD_REDISCOVERY_FORBIDDEN_CURRENT_CENSUS`

These are reasons, not new gate decisions.

## 24. Control Plane responsibilities

The Control Plane is responsible for deterministic:

- candidate-schema validation;
- cross-authority reference validation;
- exact allowed-value validation;
- surface ownership validation;
- base-head/hash validation;
- duplicate/collision detection;
- NDC/visual-meaning reconciliation candidates;
- Atlasfin match reconciliation;
- canonical composer proposals;
- Current Truth generation;
- Surface Readiness generation;
- promotion accounting;
- anti-broad-rediscovery gate hardening.

It must be testable with fixtures and must not need surface-worker output to build or test its core.

## 25. Atlasfin Bridge responsibilities

The Atlasfin Bridge should expose, without becoming product authority:

- catalog element;
- family;
- preset;
- recipe;
- properties;
- states;
- variants;
- adapter;
- target/candidate matches;
- NDC references;
- visual meaning;
- physical RIFAT coordinates;
- projection status;
- binding/promotion status;
- blockers/evidence;
- Work Entry decision when available.

The bridge must tolerate absent candidate shards by showing a truthful pending/unresolved state.

## 26. Worker completion rule

A surface worker is complete when every owned input target has exactly one candidate/outcome record, all outputs validate against the cohort vocabulary, no global authority file was changed, no out-of-scope surface was modified, no Materiality fallback occurred, and the branch reports its exact base head and changed paths.

It does not need another worker to finish first.

## 27. Integration completion rule

Integration is a later deterministic assembly activity, not permission for workers to overlap writes.

Only after candidate reconciliation may integration propose canonical changes to Identity/RIFAT/Target Index/global readiness.

Canonical promotion must still pass normal Factory Ledger, task-exact Authority Mesh/Layer Map, Work Entry, CI and no-fake-green gates.

## 28. Terms that must never be used as loose synonyms

- `census` is not `binding`.
- `DISCOVERY_ONLY` is not `undiscovered`.
- `Atlasfin recipe` is not automatically `Identity recipe`.
- `implementationLayerId` is not `applicationLayerId`.
- `ndcPrimaryId` is not `visualMeaningId`.
- `surfaceKey` is not an Atlasfin/NDC surface ID.
- `candidate` is not `authority`.
- `projection` is not `runtime certification`.
- `READY` is not `SOURCE_READY`.

## 29. Final invariant

A new agent must be able to arrive with no conversational memory and determine, from repository files alone:

1. what already exists;
2. which terms are canonical;
3. which IDs belong to which authority;
4. which surface it owns;
5. which files it may write;
6. which files it may only read;
7. how Atlasfin is used;
8. why Materiality is excluded;
9. why the census must be reused;
10. what remains candidate versus canonical;
11. what is blocked rather than guessed.

If the repository cannot answer those questions, the workflow is not ready for parallel execution.
