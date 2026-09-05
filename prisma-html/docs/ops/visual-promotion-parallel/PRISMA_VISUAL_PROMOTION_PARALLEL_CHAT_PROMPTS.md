# PRISMA Visual Promotion — Six Parallel Chat Prompts

Status: `CANONICAL_PARALLEL_CHAT_PROMPTS`

Current phase: `CORPUS_FINAL_PARALLEL_VERIFICATION`

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

Phase: `CORPUS_FINAL_PARALLEL_VERIFICATION`

This phase parallelizes the remaining finalization without creating multiple writers for the same global corpus.

Repository truth at phase start:

- canonical main: `1cc4d0d45b3878ace2906d08fa67f325a3b98a9d`;
- Chat 6 work branch: `chat6/candidate-corpus-cert-20260904`;
- Chat 6 observed work head before this prompt update: `9fdc3545d8b3309395f9276723c81f9799b1c60f`;
- AutoMesh/current-head authority: PASS;
- fresh task-exact Mesh: `PASS_COMPOSED_AUTHORITY_MESH`;
- universal anti-rework PROPOSAL: PASS;
- universal anti-rework MUTATION: PASS;
- independent surface certification audit: `2,097/2,097` PASS with zero semantic/provenance mismatches;
- Atlasfin certification audit: `2,421/2,421` PASS, invalid=0;
- exact-head/hash-pinned normalizer/intake: implemented and fail-closed;
- Materiality Catalog remains uninspected;
- product/runtime mutation remains zero;
- canonical promotion remains zero.

The five certification heads remain immutable accepted evidence:

| Chat | Lane | Certification head |
|---|---|---|
| 1 | Tablet | `fd111022438bab909151c2220b52e95aa5aa7eb3` |
| 2 | PC | `8cc979c141000fcedabf832f16468a6ee3e328e2` |
| 3 | Mobile | `664035e83943ae48c923585765d3c505b1bd8c53` |
| 4 | Shared UI | `553577aa74045c73ab9c92d1f81538e7e0a8c65a` |
| 5 | Atlasfin | `6c7743f55434eb8d3429f286e2f9eae275d93d87` |

## Parallel verification architecture

There is one global writer and five independent witnesses.

- Chats 1–4 independently verify their certified surface truth and publish a deterministic witness receipt to their own status mailbox.
- Chat 5 independently verifies Atlasfin reference/snapshot expectations and publishes an Atlasfin witness receipt.
- Chat 6 remains the **only** writer/compositor for the global corpus, integration branch, one-time FILES_MANIFEST refresh, final PR and merge.
- Chats 1–5 do not wait for Chat 6 and do not mutate their certification branches.
- Chat 6 does not wait to materialize the corpus. It continues global generation immediately and consumes the five witness receipts before final PR closure.
- No Chat may modify another Chat's certification bytes or mailbox.

A witness receipt is coordination evidence, not canonical authority, Work Entry authorization or runtime certification.

### Common witness rules for Chats 1–5

Perform the verification read-only from exact Git head-tree bytes.

Write **only** to your existing dedicated status mailbox branch. Do not create source/certification commits.

Under `handoff.parallelWitness` publish at minimum:

- `phase: CORPUS_FINAL_PARALLEL_VERIFICATION`;
- `result`;
- `certificationHead`;
- `expectedInputCount`;
- exact certification output Git blob SHAs or SHA-256 digests used;
- `invalidCount`;
- `semanticMutationCount`;
- `duplicateTargetIds` where applicable;
- surface/reference-specific invariant counts;
- `materialityCatalogInspected: false`;
- `productRuntimeMutation: false`;
- `canonicalPromotionPerformed: false`;
- exact defects, if any.

A PASS receipt must be reproducible from the immutable certification head.

If a real defect exists, publish `FAIL_*_WITNESS` with the exact target/reference, source file/line/hash and violated invariant. Do not repair anything unless Chat 6 later issues a bounded correction request.

---

### CHAT 1 — TABLET FINAL WITNESS

Read only:

`chat1/tablet-corpus-cert-20260904@fd111022438bab909151c2220b52e95aa5aa7eb3`

Verify independently:

- NORMALIZED = 929;
- CERTIFICATION = 929;
- INVALID = 0;
- unique target IDs = 929;
- semanticMutationCount = 0;
- certification labels remain:
  - 139 `VALID_ELIGIBLE_CANDIDATE`;
  - 788 `VALID_REGISTER_TARGET_FIRST`;
  - 2 `VALID_BLOCKED`;
- physical partition remains 927 CURRENT + 2 DRIFT;
- both known Tablet DRIFT target IDs remain blocked;
- the existing Cobrar Identity binding reuse remains exact and is not promoted beyond its recorded state;
- source head/file/line/record-hash provenance is complete.

Publish:

`PASS_TABLET_CORPUS_WITNESS`

only if every invariant passes.

Then remain in `CERTIFIED_HOLD`.

---

### CHAT 2 — PC FINAL WITNESS

Read only:

`chat2/pc-corpus-cert-20260904@8cc979c141000fcedabf832f16468a6ee3e328e2`

Verify independently:

- NORMALIZED = 827;
- CERTIFICATION = 827;
- INVALID = 0;
- unique target IDs = 827;
- semanticMutationCount = 0;
- all 827 certification labels remain `VALID_REGISTER_TARGET_FIRST`;
- physical partition remains 826 CURRENT + 1 DRIFT;
- projection partition remains 688 CURRENT + 139 MISSING;
- selector conflict for `TGT.CENSUS.PC.097AB2F857F353CA4288.V1` remains exactly unresolved;
- no projection MISSING record was silently repaired;
- provenance hashes are complete.

Publish:

`PASS_PC_CORPUS_WITNESS`

only if every invariant passes.

Then remain in `CERTIFIED_HOLD`.

---

### CHAT 3 — MOBILE FINAL WITNESS

Read only:

`chat3/mobile-corpus-cert-20260904@664035e83943ae48c923585765d3c505b1bd8c53`

Verify independently:

- NORMALIZED = 271;
- CERTIFICATION = 271;
- INVALID = 0;
- unique target IDs = 271;
- semanticMutationCount = 0;
- all 271 certification labels remain `VALID_REGISTER_TARGET_FIRST`;
- projection partition remains exactly 133 CURRENT + 138 DRIFT;
- no RIFAT-vs-product repair direction was selected for the 138 DRIFT records;
- representation normalization preserved original qualified/raw values in provenance;
- strict NDC/Atlasfin/Identity references remain valid;
- all source and normalized record hashes reproduce.

Publish:

`PASS_MOBILE_CORPUS_WITNESS`

only if every invariant passes.

Then remain in `CERTIFIED_HOLD`.

---

### CHAT 4 — SHARED UI FINAL WITNESS

Read only:

`chat4/shared-ui-corpus-cert-20260904@553577aa74045c73ab9c92d1f81538e7e0a8c65a`

Verify independently:

- NORMALIZED = 70;
- CERTIFICATION = 70;
- INVALID = 0;
- unique target IDs = 70;
- semanticMutationCount = 0;
- certification labels remain 40 `VALID_REGISTER_TARGET_FIRST` + 30 `VALID_BLOCKED`;
- 19 no-region unresolved records remain unresolved;
- 11 multi-region conflicts remain conflicts;
- all 70 NDC outcomes remain UNRESOLVED;
- all 70 Atlasfin outcomes remain NO_MATCH;
- projection remains CURRENT for all 70;
- no consumer/product/global authority bytes changed.

Publish:

`PASS_SHARED_UI_CORPUS_WITNESS`

only if every invariant passes.

Then remain in `CERTIFIED_HOLD`.

---

### CHAT 5 — ATLASFIN FINAL WITNESS

Read only:

`chat5/atlasfin-corpus-cert-20260904@6c7743f55434eb8d3429f286e2f9eae275d93d87`

Use current structured Atlasfin authority and the immutable certification evidence.

Verify independently:

- source surface outcomes = 2,097;
- non-null Atlasfin references = 2,421;
- valid normalized references = 2,421;
- hard invalid references = 0;
- representation-only adapter normalizations = 341;
- semanticMutationCount = 0;
- every reference retains source head/file/line/hash provenance;
- recipe review groups are re-derived from evidence;
- recipe equality remains `semanticCoalescingAllowed=false`;
- all-null/NO_MATCH groups remain excluded from semantic coalescing;
- Materiality Catalog remains completely uninspected.

Prepare the expected read-only snapshot acceptance criteria that Chat 6 must satisfy after materializing the global corpus. Do not write the global snapshot yourself.

Publish:

`PASS_ATLASFIN_CORPUS_WITNESS`

only if every invariant passes.

Then remain in `CERTIFIED_HOLD`.

---

### CHAT 6 — GLOBAL COMPOSITOR + INTEGRATOR

Chat 6 continues immediately. Do not wait for witness receipts before materializing the corpus.

Current work branch:

`chat6/candidate-corpus-cert-20260904`

Preserve all current-head Authority Mesh and anti-rework evidence, but because this prompt update advances `main`, revalidate authority against the new canonical HEAD before any *new* mutation performed after that movement. Use AutoMesh v2 rules. Do not silently reuse stale HEAD-bound authority.

Remaining work:

1. Materialize the nine global corpus outputs:
   - `CORPUS_MANIFEST.json`
   - `CANDIDATE_CORPUS.jsonl`
   - `CERTIFICATION.jsonl`
   - `INVALID.jsonl`
   - `COLLISIONS.json`
   - `SEMANTIC_REVIEW_GROUPS.json`
   - `CURRENT_TRUTH.json`
   - `SURFACE_READINESS.json`
   - `SUMMARY.md`
2. Certify:
   - 2,097/2,097 normalized;
   - 2,097/2,097 certification;
   - invalid=0;
   - missing=0;
   - extra=0;
   - duplicateTargetIds=0;
   - semanticMutationCount=0;
   - `GVAE_EXACT_APPLY=0`;
   - `currentlyAuthorizedCanonicalPromotions=0`;
   - `runtimeVisualGreen=false`;
   - no whole surface APPLY_READY.
3. Rebuild/validate the Atlasfin snapshot only as a read-only consumer of the materialized corpus.
4. Continue using exact-head/hash-pinned fail-closed intake. Unknown head/hash/shape must fail closed.
5. Create a fresh integration branch from the then-current `main` and assemble only accepted exact head-tree bytes.
6. Before the final manifest refresh, re-read all five witness mailboxes.
7. Require these five independent receipts:
   - `PASS_TABLET_CORPUS_WITNESS`;
   - `PASS_PC_CORPUS_WITNESS`;
   - `PASS_MOBILE_CORPUS_WITNESS`;
   - `PASS_SHARED_UI_CORPUS_WITNESS`;
   - `PASS_ATLASFIN_CORPUS_WITNESS`.
8. Cross-check the materialized global corpus slices against those witness expectations. A witness mismatch is a hard stop, not a warning.
9. If a witness reports a real certification defect, issue a bounded correction request to the owning Chat. Do not patch its certification bytes inside Chat 6.
10. Once all accepted bytes and witness checks pass, refresh `prisma-html/FILES_MANIFEST.json` exactly once.
11. Run in parallel where CI infrastructure permits:
   - VISCORE;
   - CI;
   - ForgeOS Quality Gate;
   - Sync Sentinel;
   - Identity/RIFAT no-regression;
   - strict schemas/vocabulary/authority refs;
   - Work Entry/no-broad-rediscovery;
   - Atlasfin static/read-only;
   - Current Truth/Surface Readiness no-fake-green.
12. Open one candidate-corpus-only integration PR.
13. Merge only if the exact final PR head is clean/mergeable and every required gate is green. Standing repository-owner merge authorization applies.
14. Verify merged `main` contains the exact accepted corpus/control-plane/certification bytes and the one final FILES_MANIFEST.
15. Close PR #539/#540 only if byte-for-byte supersession is proven.
16. Publish `DONE / PASS_CANDIDATE_CORPUS_CERTIFIED` to the Chat 6 mailbox.

### Serial barriers that must not be faked

Only these steps remain intentionally serial:

`global corpus materialized -> five witness receipts cross-checked -> exact final assembly -> one FILES_MANIFEST refresh -> exact PR-head gates -> merge -> main verification`

Everything else above should proceed in parallel.

### Hard stop remains

This phase does not authorize canonical Identity/RIFAT/NDC/Target Index promotion, new canonical IDs, product/runtime/CSS/TSX mutation, projection repair, Materiality Catalog use or any claim that corpus-valid means APPLY_READY.


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
