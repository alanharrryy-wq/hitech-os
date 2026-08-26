# PRISMA Change Intelligence — Cloud Center Vertical Contract V1

Status: `SOURCE_IMPLEMENTED / RUNTIME_GATE_REQUIRED / PRODUCTION_NOT_CERTIFIED`

## Purpose

PRISMA Change Intelligence is a new isolated PRISMA vertical surfaced through Prisma Cloud Center. It commercializes the governed Change Intelligence product model while preserving Code Atlas as the internal repository-intelligence engine.

The vertical exists to expose customer-facing views for:

- Overview
- Repositories
- Analysis Runs
- Discover
- Guard
- Control
- Authority Packs
- Evidence
- ROI
- Entitlements

The V1 surface is read-only and fail-closed. Repository, Analysis Run, Authority Pack and Evidence Report projection rows may appear only when bound to separately governed source evidence. Entitlements are source-mapped from the canonical licensing owner, but the current plan catalog contains no Change Assurance feature, so the projection remains explicitly not granted.

## Fresh authority

Initial task-exact Authority Mesh:

- base: `main@d14effee1a1223cc772247ea9d7ec8547dc15c78`
- run: `32156981312`
- artifact: `9332162633`
- profile: `ci-cloud-vertical-v3`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `5/5 PASS`
- required authority coverage: `100%`
- blockers: `0`
- Layer Map: present

Repository Registry adapter P1 authority:

- base: `main@081e014ee143e05ce72b06b5e2f5e9c0e89e69da`
- run: `32233951337`
- artifact: `9358279345`
- artifact digest: `sha256:5b06a7998076818e04c8268a7956c2d5cbdaf52e471c8cf18bb8f3c7097c8166`
- profile: `ci-cloud-repository-registry-adapter-p1-v1`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `2/2 PASS`
- required authority coverage: `100%`
- blockers: `0`

Analysis Runs adapter P2 authority:

- base: `main@28b0821d4a3c2b07041a0c4dfe18004f4f7d52ab`
- tree: `f02a5c495d982155d18febc0b81d8a11c0201144`
- Authority Mesh run: `32865050216`
- Authority Mesh artifact: `9569864211`
- Authority Mesh artifact digest: `sha256:677d5e2d93d9a5b23c5cc683e9572645bdd2763f575752af2c628dcb1df9d4ed`
- request digest: `bb146156461837525776f6f40e637a1215ba38581759da4ebb448aea97a08769`
- profile: `ci-cloud-analysis-run-projection-p2-v2`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `2/2 PASS`
- required authority coverage: `100%`
- blockers: `0`
- read-only authority: `true`
- production certified by this Mesh: `false`

Fresh immutable Code Atlas P2 evidence:

- workflow run: `32865503690`
- evidence artifact: `9569959132`
- evidence artifact digest: `sha256:cd8cd3b5f35a81e9608c0d8aae42fde76a9a822122d292a6a19c2a4973cf0868`
- engine artifact SHA-256: `2630c723aaa6d2f692218cb30648020fd41a5eade35d10f4d49129d0c5304103`
- engine result: `PASS_UNIVERSAL_INTELLIGENCE_SOURCE_READY`
- engine request digest: `08e828680e7a1afdb26d37cf44e23f2a9fd718249c7011095644b9e9da9e0460`
- snapshot digest: `7a2893d86119ad6d49bc7bb3bdff08689a6abcbb2c77343399a9cc671bc08913`
- exact source HEAD/tree: `28b0821d4a3c2b07041a0c4dfe18004f4f7d52ab` / `f02a5c495d982155d18febc0b81d8a11c0201144`
- read-only: `true`
- production certified: `false`

The Cloud projection preserves that engine result verbatim. It does not translate the result into edit authority or production certification.

## Ownership and anti-rework matrix

| Capability | Decision | Rule |
|---|---|---|
| Customer registration | `REUSE_AS_IS` | Existing owner remains `doNotRebuild=true`. |
| Licensing / entitlements | `SHARED_OWNER` | Adapt later; do not rebuild licensing. |
| Customer Setup | `SHARED_OWNER` | Setup codes are not repository authorization. |
| Commercial Billing | `SHARED_OWNER` | Do not rebuild collections, CFDI or payment records. |
| Private repository rental hardening | `ADAPT` | Reuse bounded ephemeral workspace and egress controls from PR #299. |
| Change Intelligence / Code Atlas engine | `REUSE_AS_IS` | Internal engine remains authoritative and `doNotRebuild=true`. |
| Existing Cloud Center runtime and UI | `DO_NOT_TOUCH` | Only the single navigation seam is allowed in the existing surface. |
| Change Intelligence web console | `NEW_OWNER` | Dedicated isolated document and projection modules. |
| Change Intelligence browser authority gate | `NEW_OWNER` | Dedicated source + Chromium runtime verification and evidence artifact. |

P1, P2, P3 and P4 are projection adapters only. They do not become new repository, analysis, Authority Pack generation, verification, evidence generation, licensing, billing or registration engines.

## Layer Map

The Change Intelligence surface owns a separate document and `pci-*` namespace.

1. `pci-shell`: document/background/topbar/layout.
2. `pci-navigation`: rail and view selection.
3. `pci-material`: cards, chips, alerts and glass treatment.
4. `pci-status`: PASS/BLOCKED/UNKNOWN/NOT_CONNECTED semantics.
5. `pci-evidence`: Authority Pack and evidence projection.
6. `pci-roi`: ROI and customer-input economic projection.
7. `pci-accessibility`: focus-visible, reduced-motion and reduced-transparency behavior.

The visual owner is `change_intelligence_center_style.js`. It injects exactly one `style[data-pci-style="v1"]` into the new document. This structure exists because the existing Commercial Billing Authority workflow intentionally rejects any `.css` path in a billing-sensitive PR. The billing workflow is not weakened or modified.

Rules:

- no `!important`
- no `.cc-*` selectors
- no wildcard/global override layer
- no mutation of `cloud_command_center.css`
- no mutation of `cloud_command_center.js`
- responsive navigation
- keyboard focus states
- reduced motion support
- reduced transparency support

## Analysis Runs P2 projection contract

A projected Analysis Run is admissible only when all of these facts are present and verifier-locked:

1. repository identity;
2. exact repository HEAD and tree;
3. engine intent and domain;
4. exact engine status without promotion or remapping;
5. request digest;
6. repository snapshot digest;
7. immutable engine artifact digest;
8. immutable workflow run/artifact reference and artifact digest;
9. `readOnly=true`;
10. `derivedIndexAuthoritative=false`;
11. `semanticRetrievalIsProof=false`;
12. `profileMayInventTruth=false`;
13. `productionCertified=false`;
14. explicit `doesNotProve` boundaries.

Missing, stale, contradictory or tampered provenance is fail-closed. An Analysis Run reference cannot authorize repository mutation.

P2 deliberately does not add a second runner, discovery engine, index, dashboard owner or mutation API. The existing Code Atlas neutral intelligence engine remains the source of the run evidence, and the existing Change Intelligence document renderer consumes the governed row.

## Authority Pack + Evidence P3 projection contract

P3 is a reference adapter over existing Code Atlas outputs. It does not add a second Authority Pack generator, verification engine, evidence bundle generator or mutation API.

Fresh P3 authority and mutation authorization:

- exact base: `main@0916227707aa65b673195d554297bf8f8565d356` / tree `ad0ff1770eadaee0e5ae717ba7c806da029f9287`
- Authority Mesh run: `32878086011`
- Authority Mesh artifact: `9574731927`
- Authority Mesh artifact digest: `sha256:001102f110e7075607c80fe5ab5b1343d88ee356e85fb08a88c32708d0118e9e`
- Authority Mesh request digest: `9113cb140ae64b2cc3e524908d365b8d7ed9144168a860e6909faca0558cdd74`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `2/2 PASS`
- required authority coverage: `100%`
- blockers: `0`
- exact mutation-gate run: `32878629219`
- mutation-gate artifact: `9574892311`
- mutation-gate artifact digest: `sha256:fde3bd4996cdf77e14637343975379a89ebb2de05d02711b9359d720bbdca4b7`

Fresh immutable Code Atlas P3 evidence:

- workflow run: `32878380486`
- evidence artifact: `9574817118`
- evidence artifact digest: `sha256:bf000fac916bc40034d2531a894ee855047c74cf5fb8db1dfe8f3770b73e8995`
- Authority Pack ID: `cap.5bc981d182e326a6b684`
- Authority Pack checksum: `sha256:9d225fc13e27a44dd33224112d8c7b7101e3c3ace529a970cdde42fae6874d3b`
- verification decision: `PASS`
- verification report digest: `sha256:31b36c5d7c19e790d625d104d5de0230339659d71b92e303ef50e35560ee8efa`
- portable evidence bundle manifest digest: `sha256:06167e8f02653ad82f0c410d39a5a5455be2bb201c305e7860bb404df07d4a20`
- `readOnly=true`
- `referenceOnly=true`
- `productionCertified=false`
- `certifiable=false`

The Cloud projection preserves `PASS` only as the bounded verification decision for that exact pack/snapshot. It does not prove authorization for the Cloud projection to mutate repository source, production readiness, hosted multi-tenant execution, enterprise IAM/security readiness, human usefulness or independent-agent verification. Missing, stale, contradictory or tampered pack/report provenance is fail-closed.

## Entitlements P4 projection contract

P4 is a read-only reference adapter over the existing licensing shared owner. It does not add a second licensing engine, alter license mutation semantics, change billing, touch Worker/D1 or create a product entitlement by inference.

Fresh P4 authority and mutation authorization:

- exact base: `main@c388cffd0c926295619d71a583876e5b66f37ceb` / tree `b68b47e1056a527bfa0097ab010c6a4184464703`
- Authority Mesh run: `32923210520`
- Authority Mesh artifact: `9590560387`
- Authority Mesh artifact digest: `sha256:ecced7dc954259787e5198002297e8c4fffd050f133f6646fff38c9fc4c6f88c`
- composed artifact SHA-256: `e737962f1aa137c7d7ceb3294fbc19eda7238412c39dcd2a11bf9b17fe20c957`
- request digest: `d9af6c2505490a0dfb9581bf6e426c5a921887f32ce056f68e259f01ee4ebc14`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `2/2 PASS`
- required authority coverage: `100%`
- blockers: `0`
- mutation-gate run: `32923389474`
- mutation-gate artifact: `9590600727`
- mutation-gate artifact digest: `sha256:9af868f16239fa98864d4441b6eaafd7731c185e5768db2ab0de8d4a3bf324e4`

Canonical source owner at capture:

- path: `apps/terminal-de-venta-system/shared/licensing/customer-setup-contract.ts`
- Git blob: `7bac39a02a7ffaed20f5a725a1c216da07087adf`
- catalog: `PLAN_BASED_PROVISIONING_CATALOG`
- protected capabilities: `licensing.source_contract_alignment`, `licensing.customer_setup.plan_based_onboarding`
- both owners remain reuse-only / do-not-rebuild for this adapter.

The captured catalog has four plans: `TABLET_SOLO`, `TABLET_PRO`, `TABLET_PC_MANAGED` and `TABLET_PC_MOBILE_MANAGED`. None contains a Change Assurance/Change Intelligence/Code Atlas entitlement feature. Therefore the only evidence-supported P4 state is `SOURCE_MAPPED_NOT_GRANTED` with `grantStatus=NOT_PRESENT_IN_CANONICAL_PLAN_FEATURES`.

This is deliberate fail-closed behavior. It does not prove or create an entitlement grant, live license enforcement, billing authorization or production readiness. A separately governed licensing and commercial decision must explicitly add the product feature before any live grant/enforcement claim is allowed.

## ROI P5 projection contract

P5 hardens the existing Cloud ROI placeholder into a read-only projection adapter over the canonical Code Atlas ROI owner. It does not add a second ROI engine, estimator, billing owner, pricing engine or customer-measurement store.

Fresh P5 authority and mutation authorization:

- exact base: `main@487459ab8901748673b86eaf3ad3a79322c7f266` / tree `4d1013c985cafe3e215237181d03797ee29deab3`
- Authority Mesh run/artifact: `32940529028` / `9596382236`
- Authority Mesh artifact digest: `sha256:849d76288db5034124c89f5e88d5b132cb8728cc36fa6b4574fdb333910af31c`
- composed artifact SHA-256: `b2e83b257537ab86437255a3b12743602361b2b17aa08d6c5ba4964e5648931d`
- request digest: `8f07a8f8302b604620f42f038bdc528c5cd3da59b746b148cb4c245d93bf1a21`
- result: `PASS_COMPOSED_AUTHORITY_MESH`, `2/2` lanes, `100%` required authority coverage, `0` blockers
- mutation-gate run/artifact: `32940817782` / `9596447828`
- mutation-gate artifact digest: `sha256:452c11f1015e7412b8077914c82a6f88f95881eaecae990bb2c56341de418303`

Canonical raw ROI instrumentation remains owned by `tools/code-atlas/src/code_atlas/change_intelligence/roi.py` and is reused as-is. No real customer baseline values or observed customer ROI events are present in this source projection. The safe state is therefore `INPUT_REQUIRED_NO_ESTIMATE` with `customerInputsPresent=false`, `estimateAllowed=false`, `observedEventsProjected=[]` and `financialEstimate=null`. Commercial price references are hypotheses or terms, never measured customer benefit.

P5 does not prove realized cash savings, profit, willingness to pay, human usefulness, production readiness, hosted multi-tenant readiness or enterprise readiness. Real customer baselines and observed events are the next ROI evidence gate. Independent-agent and human-usefulness gates remain separate.

## Browser/runtime authority gate

`.github/workflows/change-intelligence-cloud-authority.yml` is the permanent vertical gate.

It must:

1. run `verify-cloud-center-change-intelligence-01.py` against the exact source/diff contract;
2. install an isolated Playwright/Chromium runtime without mutating repository lockfiles;
3. serve only the checked-out Cloud Center tree on an ephemeral localhost port;
4. run `verify-cloud-center-change-intelligence-runtime-01.mjs` in desktop and mobile viewports;
5. exercise all ten navigation views;
6. require the governed config to load;
7. reject production/paid-pilot maturity inflation;
8. require fail-closed vocabulary (`UNKNOWN`, `NOT_CONNECTED`, or `BLOCKED`);
9. fail on page errors, console errors or same-origin HTTP failures;
10. upload runtime report, screenshots and HTTP log as evidence.

A successful browser gate raises only this isolated surface/projection to runtime-verified status. It does **not** make the Change Intelligence product production-certified or enterprise-certified.

## No-fake-green ceiling

Current underlying Change Intelligence evidence remains:

- engine: `LOCAL_VERIFIED`
- `certifiable=false`
- `productionCertified=false`
- `humanUsefulness=NOT_MEASURED`
- independent evaluator: `BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR`

This vertical must not claim:

- hosted multi-tenant execution
- paid-pilot readiness
- enterprise IAM/security certification
- legal/privacy compliance
- production certification
- measured human usefulness
- successful independent-agent replication

The P2 evidence also explicitly does not prove production readiness, hosted multi-tenant execution, enterprise IAM/security readiness, human usefulness, independent-agent verification, or authorization to mutate the repository.

The P3 Authority Pack/Evidence references additionally remain `readOnly` and `referenceOnly`; their bounded `PASS` verification result is not mutation authority and is not a production, enterprise, usefulness or independent-agent claim.

The P4 entitlement projection is source-mapped but not granted. Catalog absence is not interpreted as permission, and the Cloud surface cannot create licensing truth.

## Runtime and mutation boundary

The V1 vertical is read-only. It must not:

- mutate repository source;
- accept repository credentials in the browser;
- persist secrets in local/session storage;
- call POST/PUT/PATCH/DELETE from the browser projection;
- start or kill product dev servers;
- free ports;
- mutate Prisma/DB/D1;
- deploy Cloudflare or other infrastructure;
- touch Tablet, PC, Mobile, Chart Lab or Shared UI;
- rebuild licensing, registration or billing.

The CI browser test is an ephemeral test-only localhost server inside a GitHub Actions runner. It is not a product runtime, deploy or hosted environment.

## Commercial Billing Authority compatibility

The initial isolated surface used a standalone CSS file. Commercial Billing Authority correctly rejected the PR because its task-specific guard prohibits any `.css` path. The guard was preserved unchanged. The visual layer was moved into the isolated `change_intelligence_center_style.js` owner and the transient CSS file was removed from the effective diff.

Commercial billing and fiscal owners remain outside this vertical.

## Next implementation gates

Bounded progress:

1. read-only repository registry adapter: `DONE / SOURCE_VERIFIED_READ_ONLY`;
2. real Code Atlas analysis-run projection: `DONE / SOURCE_VERIFIED_READ_ONLY`;
3. Authority Pack and Evidence Report reference adapter: `DONE / SOURCE_VERIFIED_READ_ONLY`;
4. Change Assurance entitlement projection from the existing licensing owner: `IMPLEMENTED / SOURCE_MAPPED_NOT_GRANTED / SOURCE_AND_BROWSER_GATE_REQUIRED_ON_PR`;
5. customer-input ROI projection: `NEXT`, using existing raw ROI instrumentation and explicit real customer inputs only;
6. human usefulness evidence: external human required;
7. independent-agent evidence: external independent evaluator required;
8. separately governed hosted/enterprise productization: not claimed by this contract.

P4 reuses the existing licensing owners and projects their current catalog truth only. No Change Assurance feature exists in that catalog at this capture, so no entitlement is granted. The next internal gate is customer-input ROI projection; licensing mutation semantics remain outside this vertical.

## Governance closure

Factory Ledger and Evidence Index are not modified by this P4 implementation branch. P4 may be described as source/runtime verified only after the permanent source + Chromium workflow is green against the exact implementation head. The entitlement remains not granted until a separately governed licensing/commercial feature decision exists. Product maturity remains bounded by the no-fake-green ceiling above regardless of a green projection workflow.
