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

The V1 surface is read-only and fail-closed. Repository, run, Authority Pack and evidence datasets remain `NOT_CONNECTED` until real adapters are separately governed and implemented.

## Fresh authority

Task-exact Authority Mesh:

- base: `main@d14effee1a1223cc772247ea9d7ec8547dc15c78`
- run: `32156981312`
- artifact: `9332162633`
- profile: `ci-cloud-vertical-v3`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `5/5 PASS`
- required authority coverage: `100%`
- blockers: `0`
- Layer Map: present

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

A successful browser gate raises only this isolated surface to runtime-verified status. It does **not** make the Change Intelligence product production-certified or enterprise-certified.

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

After source and browser runtime are both green:

1. read-only repository registry adapter;
2. real Code Atlas analysis-run projection;
3. Authority Pack and Evidence Report reference adapter;
4. Change Intelligence entitlement projection from the existing licensing owner;
5. customer-input ROI instrumentation;
6. human usefulness evidence;
7. independent-agent evidence;
8. separately governed hosted/enterprise productization.

## Governance closure

Factory Ledger and Evidence Index are not modified by the initial implementation branch. Maturity registration belongs after source + runtime evidence is green and must preserve the evidence ceiling above.
