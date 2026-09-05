# PRISMA Visual Promotion — Six Parallel Chat Prompts

Status: `CANONICAL_PARALLEL_CHAT_PROMPTS`

Current phase: `CANDIDATE_CORPUS_FINAL_AGGREGATION`

## How the user should invoke a chat

For a new chat, the user may give only the folder path and say:

> Go to this folder, read the mandatory startup documents, and execute **Chat N** from `PRISMA_VISUAL_PROMOTION_PARALLEL_CHAT_PROMPTS.md`.

For an existing Chat 1–6 that already completed its first lane phase, the user may now say only:

> Continue with your work. The canonical prompt in `prisma-html/docs/ops/visual-promotion-parallel/PRISMA_VISUAL_PROMOTION_PARALLEL_CHAT_PROMPTS.md` was updated. Re-read it, locate your assigned Chat number, read your current status mailbox, and follow the current continuation instructions exactly.

The chat must read the interoperability contract, vocabulary registry, current prompt and its own status mailbox before doing any lane work.

## Rules shared by all six chats

These rules are inherited by every chat below:

- Work from repository truth, not conversational memory.
- Read root `AGENTS.md`, Field Manual, Factory Ledger Agent Gate, Visual Change Master Map, Visual Core Contract, this folder's interoperability contract and vocabulary registry.
- Record exact `baseHead`.
- Use a fresh task-exact Authority Mesh/Layer Map when the lane intends repository mutation beyond its candidate/bridge/control-plane ownership.
- Reuse current Visual Control/Target Index census. Never treat `DISCOVERY_ONLY` as undiscovered.
- Atlasfin is the priority visual reference.
- The Surface Visual Governor Materiality Catalog is `STANDBY_USER_INVOKED_ONLY`. Do not inspect or consume it unless the repository owner explicitly invokes it for this named task.
- Do not mutate product runtime, product visual source, generated product projections, DB, Prisma, dev servers, ports or unrelated surfaces.
- Do not write global Identity recipe/binding registries, generated Target Index, visual-source-manifest, Factory Ledger/Evidence Index or `FILES_MANIFEST.json` in a worker lane.
- Do not invent canonical IDs. Existing IDs are immutable. Candidate keys are local; canonical composer assigns new global IDs.
- Do not merge into protected branches. Finish on the lane branch with exact changed paths, validation and commit SHA.
- No fake green. Unknown/ambiguous stays blocked or unresolved.
- Web, Chart Lab and Control Center are out of scope and protected.
- Read `status-channel/README.md` and `status-channel/STATUS_CHANNEL_CONTRACT.json`; publish status to the mailbox mapped to your assigned Chat number.
- Status reporting is separate from lane work: update only your dedicated `STATUS.json` and `LOG.md` on the mapped `status/vp-chat-XX-...` branch. Never put lane source/candidate changes on the status branch.
- Publish immediately when this instruction is received, whenever a blocker appears/clears, after a material finding/decision/milestone, and at completion. Include work branch/head, blockers, findings, validations and next action.


## CURRENT CONTINUATION PHASE — NORMATIVE OVERRIDE

Phase: `CANDIDATE_CORPUS_FINAL_AGGREGATION`

The five certification lanes are complete. Their remaining semantic unresolved/conflict states are **valid corpus states**, not certification failures. Do not ask Chats 1–5 to invent semantic authority merely to make the corpus look more complete.

Current certified handoffs:

| Chat | Lane | Certification branch | Certification head | Result |
|---|---|---|---|---|
| 1 | Tablet | `chat1/tablet-corpus-cert-20260904` | `fd111022438bab909151c2220b52e95aa5aa7eb3` | 929/929 valid, invalid=0, semanticMutationCount=0 |
| 2 | PC | `chat2/pc-corpus-cert-20260904` | `8cc979c141000fcedabf832f16468a6ee3e328e2` | 827/827 valid, invalid=0, semanticMutationCount=0 |
| 3 | Mobile | `chat3/mobile-corpus-cert-20260904` | `664035e83943ae48c923585765d3c505b1bd8c53` | 271/271 valid, invalid=0, semanticMutationCount=0 |
| 4 | Shared UI | `chat4/shared-ui-corpus-cert-20260904` | `553577aa74045c73ab9c92d1f81538e7e0a8c65a` | 70/70 valid, invalid=0, semanticMutationCount=0 |
| 5 | Atlasfin | `chat5/atlasfin-corpus-cert-20260904` | `6c7743f55434eb8d3429f286e2f9eae275d93d87` | 2,421/2,421 non-null refs valid, hardInvalidRefCount=0 |

Aggregate certified surface count is exactly `2,097`.

### Chats 1–5 continuation

Chats 1–5 are now `CERTIFIED_HOLD`.

They must:

1. preserve the exact certification branch/head above;
2. make no new certification mutation by initiative;
3. keep unresolved/conflict truth unchanged;
4. not touch `prisma-html/FILES_MANIFEST.json`;
5. not open or merge certification PRs;
6. not touch product/runtime/global authority;
7. respond only if Chat 6 reports a bounded, evidence-backed certification defect tied to an exact target/reference/provenance failure.

If Chat 6 asks for a correction, the owning Chat must:
- reproduce the failure against the exact certification head;
- fix only its owned certification directory;
- preserve original worker provenance;
- require invalid=0 and semanticMutationCount=0 after the correction;
- publish the new exact certification head to its mailbox.

Do not resolve semantic/product blockers in this phase. For example:
- Tablet's 788 unresolved and 2 physical DRIFT conflicts remain valid unresolved/blocker states;
- PC's selector conflict and 139 projection MISSING states remain valid;
- Mobile's 138 DRIFT records remain unresolved as to repair direction;
- Shared UI's 19 no-region and 11 multi-region cases remain valid unresolved/conflict states;
- Atlasfin recipe equality remains review evidence only.

### CHAT 6 — FINAL GLOBAL CORPUS AGGREGATION

Chat 6 is the only active assembly lane.

Current work branch:

`chat6/candidate-corpus-cert-20260904`

Existing Control Plane source:

- branch: `chat6/visual-promotion-control-plane-20260904`
- source head: `7cc48fa49906c8f443b267fd6c3590fd3f4340fb`
- validated equivalent code head: `cb21ca01ecf8ec755fe34820d3d5b34673f70581`

Chat 6 already has a successful task-exact corpus-certification Authority Mesh attempt recorded in its mailbox. Because this canonical prompt merge moves `main`, Chat 6 must **revalidate authority against the current HEAD** with AutoMesh v2 before mutation. Do not silently reuse the old HEAD-bound evidence.

If revalidation returns `PASS_ALREADY_CURRENT` or `PASS_NO_RELEVANT_DRIFT`, use only the resulting current-HEAD-bound attestation. Any relevant/non-ancestor/invalid drift requires a fresh Mesh.

#### Mandatory anti-rework gate

Before source mutation:

1. Read current `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json`.
2. Classify this exact bounded task against canonical capability IDs. At minimum re-evaluate `visual.generic_application_engine_v1`; include any additional capability only if current Ledger authority explicitly proves it is affected.
3. Run the universal anti-rework gate in `PROPOSAL` mode.
4. Do not rebuild `visual.generic_application_engine_v1` if it remains `DONE / SOURCE_READY / doNotRebuild=true`; use `REUSE`, `VERIFY` or `ADVANCE` according to the live Ledger/nextGate.
5. After current-HEAD Authority Mesh/revalidation evidence is available, run the same gate in `MUTATION` mode with the reviewed Mesh summary.
6. Only `PASS_ANTI_REWORK_GATE` permits the bounded Control Plane/corpus source mutation.

#### Exact accepted certification inputs

Consume by exact head-tree bytes, never by reconstructing history:

- Tablet certification: `fd111022438bab909151c2220b52e95aa5aa7eb3`
- PC certification: `8cc979c141000fcedabf832f16468a6ee3e328e2`
- Mobile certification: `664035e83943ae48c923585765d3c505b1bd8c53`
- Shared UI certification: `553577aa74045c73ab9c92d1f81538e7e0a8c65a`
- Atlasfin certification: `6c7743f55434eb8d3429f286e2f9eae275d93d87`

Also consume the exact original worker heads and Chat 5 source bridge head already recorded by the previous plan, so provenance remains independently verifiable.

#### Chat 6 must finish these unresolved tasks

1. Bring forward the exact Chat 6 owned-path bytes from `7cc48fa49906c8f443b267fd6c3590fd3f4340fb` by head-tree extraction.
2. Implement/test the fail-closed exact-head/hash-pinned intake normalizer.
3. Register only the exact known worker/certification heads and hashes. Unknown head/hash/shape fails closed.
4. Add the separate semantic reconciliation review key without weakening duplicate/collision fingerprints.
5. Verify all five certification handoffs independently before aggregation.
6. Generate the global certification corpus under:
   `prisma-html/governance/visual-promotion/contracts/corpus-certification/**`
7. Required global outputs remain:
   - `CORPUS_MANIFEST.json`
   - `CANDIDATE_CORPUS.jsonl`
   - `CERTIFICATION.jsonl`
   - `INVALID.jsonl`
   - `COLLISIONS.json`
   - `SEMANTIC_REVIEW_GROUPS.json`
   - `CURRENT_TRUTH.json`
   - `SURFACE_READINESS.json`
   - `SUMMARY.md`
8. Global invariants:
   - `2,097/2,097` normalized records;
   - `2,097/2,097` certification rows;
   - invalid=0;
   - missing=0;
   - extra=0;
   - duplicateTargetIds=0;
   - semanticMutationCount=0;
   - all source/certification heads and record hashes pinned;
   - unresolved/conflict semantics preserved;
   - `currentlyAuthorizedCanonicalPromotions=0`;
   - `GVAE_EXACT_APPLY=0`;
   - `runtimeVisualGreen=false`;
   - no whole surface APPLY_READY.
9. Rebuild/validate the Atlasfin Bridge snapshot only as a read-only consumer of the assembled corpus. Materiality remains completely uninspected.
10. Generate Current Truth and Surface Readiness from certified corpus evidence, not assumptions.
11. Assemble accepted bytes on one fresh integration branch from the then-current `main`.
12. Refresh `prisma-html/FILES_MANIFEST.json` exactly once, after every accepted `prisma-html` byte is present.
13. Run all required gates:
   - strict candidate/manifest/corpus schema validation;
   - closed vocabulary and authority-reference validation;
   - zero-loss/provenance/hash validation;
   - duplicate/collision + semantic-review validation;
   - Work Entry/no-broad-rediscovery gates;
   - Atlasfin bridge/static tests;
   - Current Truth / Surface Readiness no-fake-green checks;
   - Identity/RIFAT no-regression;
   - VISCORE;
   - CI;
   - ForgeOS Quality Gate;
   - Sync Sentinel.
14. Open **one** candidate-corpus-only integration PR.
15. If the exact final PR head is clean/mergeable and all required checks are green, merge it to `main` under the repository owner's standing merge authorization.
16. Verify merged `main` contains the exact accepted corpus/certification/control-plane bytes and the one final manifest.
17. Close PR #539 and/or #540 as superseded only if the merged corpus integration contains their intended accepted bytes byte-for-byte. Do not merge those PRs separately merely for history.
18. Update Chat 6 mailbox to `DONE` with:
   `PASS_CANDIDATE_CORPUS_CERTIFIED`

#### Fail-closed correction loop

If Chat 6 finds a real certification defect in Chats 1–5:

- identify the exact Chat, target/reference, file, head and failing invariant;
- publish the bounded correction request in Chat 6 mailbox;
- do not patch another Chat's owned certification bytes inside Chat 6;
- consume the corrected certification head only after the owning Chat reports invalid=0 and semanticMutationCount=0;
- resume aggregation without recensus or semantic reinvention.

#### Hard stop after successful corpus merge

This final aggregation still does **not** authorize:

- canonical Identity/RIFAT/NDC/Target Index promotion;
- new canonical `BND.*`, `TGT.*`, `LYR.*`, `VIS.*`, NDC or adapter IDs;
- product/runtime/CSS/TSX mutation;
- projection repair;
- Materiality Catalog use;
- claiming corpus-valid means APPLY_READY.

Completion of this phase means the entire candidate corpus is merged, strict-valid, provenance-complete and machine-queryable. It does not mean all semantic blockers have been solved.


---

# CHAT 1 — TABLET PROMOTION

## Mission

Promote the **existing Tablet census evidence** toward semantic/binding/application candidates without broad rediscovery and without visual/runtime mutation.

Tablet owns its current Target Index census records. The lane must account for every Tablet census input exactly once.

## Read authority

In addition to the shared startup set, read:

- `prisma-html/authority/rifat/prisma-ui/visual-control/target-index/tablet.json`
- Tablet rows in `prisma-html/authority/rifat/prisma-ui/visual-control/expanded/tablet/**`
- `prisma-html/authority/rifat/identity/registries/element-bindings.registry.json`
- `prisma-html/authority/rifat/identity/registries/recipe.registry.json`
- `prisma-html/authority/rifat/identity/registries/surface-adapters.registry.json`
- `prisma-html/authority/rifat/visual-source-manifest.json`
- NDC canon and ID grammar under `apps/terminal-de-venta-system/docs/ndc/`
- Atlasfin registries listed by the interoperability contract.

## Write ownership

Write only:

`prisma-html/governance/visual-promotion/candidates/tablet/**`

Do not modify Tablet product files, RIFAT authority, global Identity registries, Target Index, manifest or global repository manifests.

## Required analysis per target

For every Tablet census target:

1. preserve exact `targetId`;
2. determine whether physical evidence is current;
3. resolve existing route/region/slot/component/owner/layer evidence by reading current RIFAT/Visual Control, without recensus;
4. find existing NDC meaning when directly supported;
5. find the strongest supported Atlasfin match: exact, family, preset, recipe, ambiguous or none;
6. distinguish Atlasfin IDs from canonical Identity IDs;
7. reuse an existing Identity recipe/binding only if current registry authority proves it;
8. create candidate meaning/binding data when appropriate, never a new canonical ID;
9. classify projection status;
10. emit blockers and evidence refs.

## Required outputs

Under the owned directory produce deterministic:

- `MANIFEST.json`
- `CANDIDATES.jsonl`
- `UNRESOLVED.jsonl`
- `CONFLICTS.jsonl`
- `SUMMARY.md`

Accounting must reconcile exactly to Tablet census input count.

## Completion

Finish when every Tablet census target has exactly one outcome and there are zero writes outside the owned directory.

---

# CHAT 2 — PC PROMOTION

## Mission

Promote the **existing PC census evidence** toward semantic/binding/application candidates without broad rediscovery or product mutation.

Also classify the known class of PC census records that do not currently have a canonical projection/source match. Do not repair them in this lane.

## Read authority

Read the shared startup set plus:

- `prisma-html/authority/rifat/prisma-ui/visual-control/target-index/pc.json`
- PC rows in `prisma-html/authority/rifat/prisma-ui/visual-control/expanded/pc/**`
- canonical Identity binding/recipe/adapter registries;
- visual-source-manifest;
- NDC canon;
- Atlasfin registries.

## Write ownership

Write only:

`prisma-html/governance/visual-promotion/candidates/pc/**`

## Required analysis per target

Apply the same candidate logic as Chat 1.

For a PC record without proven canonical projection, use only:

- `MISSING` when evidence shows projection is required but absent;
- `NOT_REQUIRED` when evidence proves it is intentionally not a generated projection;
- `UNRESOLVED` when the lane cannot prove either.

Do not invent a canonical source and do not copy product bytes into RIFAT.

## Required outputs

Produce the five standard candidate files and reconcile every PC census input exactly once.

---

# CHAT 3 — MOBILE PROMOTION

## Mission

Promote existing Mobile census evidence and classify existing Mobile projection drift without broad rediscovery and without repairing runtime/source in this lane.

## Read authority

Read the shared startup set plus:

- `prisma-html/authority/rifat/prisma-ui/visual-control/target-index/mobile.json`
- Mobile rows in `prisma-html/authority/rifat/prisma-ui/visual-control/expanded/mobile/**`
- visual-source-manifest and current RIFAT Mobile canonical sources;
- current Mobile product projection files referenced by the manifest;
- Identity/NDC/Atlasfin registries.

## Write ownership

Write only:

`prisma-html/governance/visual-promotion/candidates/mobile/**`

## Drift policy

For every drifted Mobile target, classify evidence without choosing a repair direction merely to become green.

Use notes/blockers to distinguish, when provable:

- current canonical source vs changed product projection;
- legitimate newer runtime candidate requiring authority reconciliation;
- stale canonical authority candidate;
- ambiguous drift requiring review.

Do not overwrite Mobile product files. Do not overwrite RIFAT. Do not regenerate projections.

## Required outputs

Produce the five standard files, account for every Mobile census target and separately summarize projection-status counts.

---

# CHAT 4 — SHARED UI PROMOTION

## Mission

Promote existing Shared UI census evidence as neutral/shared visual-source candidates while preserving one source of semantic truth across consumers.

## Read authority

Read the shared startup set plus:

- `prisma-html/authority/rifat/prisma-ui/visual-control/target-index/shared-ui.json`
- Shared UI rows in `prisma-html/authority/rifat/prisma-ui/visual-control/expanded/shared-ui/**`
- Identity Shared UI adapter/binding sources;
- projection manifest;
- NDC canon;
- Atlasfin registries.

## Write ownership

Write only:

`prisma-html/governance/visual-promotion/candidates/shared-ui/**`

## Consumer policy

A Shared UI target may record that Tablet, PC, Mobile or an excluded surface consumes it, but this lane may not edit consumer shards or product surfaces.

Do not duplicate one Shared UI semantic source into separate canonical meanings solely because it has multiple consumers.

Out-of-scope consumer observations are evidence only.

## Required outputs

Produce the five standard files and zero-loss accounting for all Shared UI census targets.

---

# CHAT 5 — ATLASFIN BRIDGE

## Mission

Make `prisma-html/extras/atlasfin` the clear priority human cockpit/reference for the promotion system without turning Atlasfin into a competing editable authority or direct product writer.

The bridge must use the existing 418-element catalog and structured Atlasfin registries. It must not rebuild the catalog.

## Read authority

Read the shared startup set plus all current Atlasfin manifests, registries, schemas, validators, VISREC2 code, current Cobrar pilot/visual application evidence, Visual Core status feed and Identity/RIFAT contracts.

## Write ownership

Write only newly assigned bridge implementation under:

`prisma-html/extras/atlasfin/bridge/**`

Do not rewrite existing Atlasfin source registries unless a later separately authorized task explicitly requires it.

## Required bridge capabilities

Design/implement a read-only bridge model that can represent:

- Atlasfin catalog element;
- property/family/preset/recipe/state/variant;
- Atlasfin adapter;
- authority-qualified IDs;
- NDC refs;
- canonical visual meaning when resolved;
- exact target/RIFAT coordinates when available;
- projection status;
- binding/promotion status;
- blockers/evidence;
- Work Entry decision when present.

The bridge must tolerate candidate directories that do not yet exist. Missing worker data renders as pending/unresolved, never as error-created fake data.

It must not require Chats 1–4 to finish before this bridge can be implemented or validated with fixtures/current Atlasfin data.

## Materiality restriction

Do not inspect, import or fallback to the Surface Visual Governor Materiality Catalog.

## Validation

Use existing Atlasfin validators plus narrow bridge tests/fixtures. No product runtime mutation.

---

# CHAT 6 — VISUAL PROMOTION CONTROL PLANE

## Mission

Build the deterministic machine layer that makes parallel candidate outputs interoperable and prevents future anti-rework mistakes.

This lane must be buildable and testable entirely from schemas/fixtures/current authority. It does not wait for surface workers.

## Read authority

Read the shared startup set plus:

- `prisma-html/tools/visual_application/**`
- current Work Entry Gate and tests;
- Target Index generator;
- Identity binding resolver;
- Visual Core;
- NDC ID and edge registries;
- current Atlasfin registries.

## Write ownership

Primary ownership:

`prisma-html/tools/visual_promotion/**`

`prisma-html/governance/visual-promotion/contracts/**`

When the exact task authority permits bounded gate hardening, this lane may also modify:

`prisma-html/tools/visual_application/visual_work_entry_gate.py`

`prisma-html/tools/visual_application/tests/test_visual_work_entry_gate.py`

Do not populate Tablet/PC/Mobile/Shared UI candidate shards.

## Required control-plane capabilities

Implement deterministic contracts/tools for:

- candidate schema validation;
- vocabulary/enumeration validation;
- authority-qualified ID validation;
- disjoint write-ownership validation;
- base-head/source-hash validation;
- zero-loss surface accounting;
- duplicate/collision detection;
- Atlasfin candidate normalization;
- NDC/visual-meaning reconciliation candidates;
- canonical-composer planning without direct mutation;
- `Visual Current Truth` generation;
- `Surface Readiness` generation;
- explicit distinction between current census and genuine discovery need.

## Work Entry hardening

Preserve exactly the four existing decisions.

Add/test machine-readable reasons so current census cannot be mistaken for discovery work, including:

`REUSE_EXISTING_CENSUS_SEMANTIC_PROMOTION_REQUIRED`

`BROAD_REDISCOVERY_FORBIDDEN_CURRENT_CENSUS`

Add strict request-contract validation if it can be done without weakening existing behavior.

## Integration mode

Initial Control Plane work must finish without worker outputs.

Later, if the user explicitly returns with worker branch/commit refs, the same lane may run deterministic integration/reconciliation. That later assembly is not a prerequisite for any worker to start.

## Completion

Finish with control-plane code/contracts/tests on its own branch, no product visual mutation, no surface candidate writes, and no global canonical registry promotion unless a later separately authorized integration task requests it.
