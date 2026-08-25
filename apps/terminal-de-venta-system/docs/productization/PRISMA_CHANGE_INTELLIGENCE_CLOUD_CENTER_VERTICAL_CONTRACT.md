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

The V1 surface is read-only and fail-closed. Repository and Analysis Run projection rows may appear only when bound to separately governed source evidence. Authority Pack and Evidence Report datasets remain `NOT_CONNECTED` until their real adapters are separately governed and implemented.

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

P1 and P2 are projection adapters only. They do not become new repository, analysis, authority, verification, licensing, billing or registration engines.

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
2. real Code Atlas analysis-run projection: `IMPLEMENTED / SOURCE_AND_BROWSER_GATE_REQUIRED_ON_PR`;
3. Authority Pack and Evidence Report reference adapter: `NEXT`;
4. Change Intelligence entitlement projection from the existing licensing owner: pending P3;
5. customer-input ROI instrumentation: pending entitlement-boundary review;
6. human usefulness evidence: external human required;
7. independent-agent evidence: external independent evaluator required;
8. separately governed hosted/enterprise productization: not claimed by this contract.

P3 must reuse the existing Authority Pack and Evidence Report owners and project references only. It must not reconstruct prepare/verify/reporting logic in Cloud Center.

## Governance closure

Factory Ledger and Evidence Index are not modified by this P2 implementation branch. P2 may be described as source/runtime verified only after the permanent source + Chromium workflow is green against the exact implementation head. Product maturity remains bounded by the no-fake-green ceiling above regardless of a green projection workflow.
